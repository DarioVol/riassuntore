"""
AI Meeting Agent - Web Application

Applicazione web basata su FastAPI per l'elaborazione di documenti
tramite interfaccia web user-friendly.
"""

import os
import sys
import tempfile
import uvicorn
from pathlib import Path
from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# Aggiungi utils al path per import
sys.path.append(os.path.join(os.path.dirname(__file__), 'utils'))

from main import AIAgent


# Inizializza FastAPI app
app = FastAPI(
    title="AI Meeting Agent",
    description="Sistema intelligente per generazione riassunti specializzati",
    version="1.0.0"
)

# Setup templates
templates = Jinja2Templates(directory="templates")

# Inizializza agente AI globale
agent = None
agent_error = None

try:
    agent = AIAgent()
    print("✅ AI Agent inizializzato con successo per webapp")
except Exception as e:
    agent_error = str(e)
    print(f"❌ Errore inizializzazione agente: {e}")


@app.on_event("startup")
async def startup_event():
    """Eventi di startup dell'applicazione"""
    print("🚀 AI Meeting Agent Web App avviata")
    if agent:
        system_info = agent.get_system_info()
        print(f"📋 Versione: {system_info['version']}")
        print(f"📄 Formati supportati: {', '.join(system_info['supported_formats'])}")


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Homepage con interfaccia di upload"""
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "agent_available": agent is not None,
            "agent_error": agent_error
        }
    )


@app.post("/process_text")
async def process_text_endpoint(text: str = Form(...)):
    """
    Endpoint per processare testo diretto

    Args:
        text: Testo da processare

    Returns:
        JSON con risultati del processing
    """
    if not agent:
        raise HTTPException(
            status_code=500,
            detail=f"Agente AI non disponibile: {agent_error}"
        )

    if not text.strip():
        raise HTTPException(status_code=400, detail="Testo vuoto")

    try:
        result = agent.process_text(text)

        return {
            "success": True,
            "source": f"Testo diretto ({len(text)} caratteri)",
            "results": {
                "didactic": result.didactic,
                "client": result.client,
                "developers": result.developers,
                "management": result.management
            },
            "metadata": result.metadata
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Errore nel processing del testo: {str(e)}"
        )


@app.post("/process_file")
async def process_file_endpoint(file: UploadFile = File(...)):
    """
    Endpoint per processare file uploadato

    Args:
        file: File uploadato (PDF, DOCX, TXT)

    Returns:
        JSON con risultati del processing
    """
    if not agent:
        raise HTTPException(
            status_code=500,
            detail=f"Agente AI non disponibile: {agent_error}"
        )

    # Validazione file
    if not file.filename:
        raise HTTPException(status_code=400, detail="Nessun file selezionato")

    # Controlla estensione file
    allowed_extensions = agent.get_supported_formats()
    file_extension = Path(file.filename).suffix.lower()

    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Formato file '{file_extension}' non supportato. "
                   f"Formati supportati: {', '.join(allowed_extensions)}"
        )

    # Salva file temporaneo
    tmp_file_path = None
    try:
        # Leggi contenuto file
        content = await file.read()

        # Validazione dimensione
        file_size_mb = len(content) / (1024 * 1024)
        processing_config = agent.config_manager.get_processing_config()
        max_size_mb = processing_config['max_file_size_mb']

        if file_size_mb > max_size_mb:
            raise HTTPException(
                status_code=400,
                detail=f"File troppo grande ({file_size_mb:.1f}MB). "
                       f"Massimo consentito: {max_size_mb}MB"
            )

        # Crea file temporaneo
        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=file_extension,
            prefix="ai_agent_"
        ) as tmp_file:
            tmp_file.write(content)
            tmp_file_path = tmp_file.name

        # Processa file
        result = agent.process_file(tmp_file_path)

        return {
            "success": True,
            "filename": file.filename,
            "size_mb": round(file_size_mb, 2),
            "results": {
                "didactic": result.didactic,
                "client": result.client,
                "developers": result.developers,
                "management": result.management
            },
            "metadata": result.metadata
        }

    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Errore nel processing del file: {str(e)}"
        )
    finally:
        # Cleanup file temporaneo
        if tmp_file_path and os.path.exists(tmp_file_path):
            try:
                os.unlink(tmp_file_path)
            except:
                pass  # Ignore cleanup errors


@app.get("/health")
async def health_check():
    """Health check endpoint per monitoring"""
    if agent:
        stats = agent.ai_processor.get_processing_stats()
        system_info = agent.get_system_info()

        return {
            "status": "healthy",
            "agent_available": True,
            "version": system_info['version'],
            "config_valid": system_info['config_valid'],
            "processing_stats": stats
        }
    else:
        return {
            "status": "unhealthy",
            "agent_available": False,
            "error": agent_error
        }


@app.get("/api/info")
async def api_info():
    """Informazioni API e sistema"""
    if not agent:
        raise HTTPException(
            status_code=500,
            detail=f"Agente AI non disponibile: {agent_error}"
        )

    system_info = agent.get_system_info()
    return {
        "version": system_info['version'],
        "supported_formats": system_info['supported_formats'],
        "processing_config": system_info['processing_config'],
        "endpoints": [
            {"path": "/", "method": "GET", "description": "Web interface"},
            {"path": "/process_text", "method": "POST", "description": "Process direct text"},
            {"path": "/process_file", "method": "POST", "description": "Process uploaded file"},
            {"path": "/health", "method": "GET", "description": "Health check"},
            {"path": "/api/info", "method": "GET", "description": "API information"}
        ]
    }


@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    """Handler per 404 errors"""
    return JSONResponse(
        status_code=404,
        content={
            "error": "Endpoint non trovato",
            "message": f"L'endpoint '{request.url.path}' non esiste",
            "available_endpoints": ["/", "/process_text", "/process_file", "/health", "/api/info"]
        }
    )


@app.exception_handler(500)
async def internal_error_handler(request: Request, exc):
    """Handler per errori interni del server"""
    return JSONResponse(
        status_code=500,
        content={
            "error": "Errore interno del server",
            "message": "Si è verificato un errore imprevisto",
            "agent_available": agent is not None
        }
    )


def main():
    """Avvia il server web"""
    print("🌐 Avvio AI Meeting Agent Web Server")
    print("=" * 50)

    # Verifica agent status
    if agent:
        system_info = agent.get_system_info()
        print(f"✅ Agent status: OK")
        print(f"📦 Versione: {system_info['version']}")
        print(f"📄 Formati supportati: {', '.join(system_info['supported_formats'])}")
    else:
        print(f"❌ Agent status: ERROR")
        print(f"🚨 Errore: {agent_error}")
        print("⚠️  L'applicazione web sarà avviata ma non funzionale")

    # Ottieni configurazione webapp
    webapp_config = {"host": "0.0.0.0", "port": 8000, "debug": False}

    if agent:
        try:
            webapp_config = agent.config_manager.get_webapp_config()
        except:
            print("⚠️  Usando configurazione webapp di default")

    print(f"\n🚀 Server in avvio su http://{webapp_config['host']}:{webapp_config['port']}")
    print("📱 Premi Ctrl+C per fermare il server")
    print("=" * 50)

    # Avvia server
    uvicorn.run(
        app,
        host=webapp_config['host'],
        port=webapp_config['port'],
        reload=webapp_config['debug'],
        log_level="info" if not webapp_config['debug'] else "debug"
    )


if __name__ == "__main__":
    main()