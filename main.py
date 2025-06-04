"""
AI Meeting Agent - Applicazione principale

Script principale che coordina tutti i moduli per il processing
di documenti e generazione di riassunti specializzati.
"""

import os
import sys
from pathlib import Path
from typing import Optional

# Aggiungi utils al path per import
sys.path.append(os.path.join(os.path.dirname(__file__), 'utils'))

from utils.document_processor import DocumentProcessor
from utils.ai_processor import AIProcessor, ProcessingResult
from utils.config_manager import ConfigManager, setup_initial_config


class AIAgent:
    """
    Agente AI principale per il processing di documenti e testi.
    
    Coordina DocumentProcessor e AIProcessor per fornire
    un'interfaccia unificata per l'elaborazione di contenuti.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Inizializza l'agente AI.
        
        Args:
            config_path (Optional[str]): Percorso custom del file config
            
        Raises:
            Exception: Se inizializzazione fallisce
        """
        self.config_manager = ConfigManager(config_path)
        self.document_processor = DocumentProcessor()
        self.ai_processor = None
        
        # Setup e validazione configurazione
        self._setup_configuration()
        
        # Inizializza AI processor
        self._initialize_ai_processor()
        
        print("✅ AI Agent inizializzato con successo")
    
    def _setup_configuration(self):
        """
        Setup e validazione della configurazione.
        
        Raises:
            Exception: Se configurazione non valida
        """
        # Carica configurazione esistente o crea default
        if not self.config_manager.load_config():
            print("📝 Configurazione non trovata, creando default...")
            if not setup_initial_config(self.config_manager.config_path):
                raise Exception("Impossibile creare configurazione di default")
        
        # Valida configurazione
        validation = self.config_manager.validate_config()
        if not validation['is_valid']:
            print("❌ Configurazione non valida:")
            for error in validation['errors']:
                print(f"  - {error}")
            raise Exception(
                f"Configurazione non valida in {self.config_manager.config_path}. "
                "Configura correttamente l'API key OpenAI."
            )
        
        # Mostra warning se presenti
        if validation['warnings']:
            for warning in validation['warnings']:
                print(f"⚠️  {warning}")
    
    def _initialize_ai_processor(self):
        """
        Inizializza il processore AI.
        
        Raises:
            Exception: Se inizializzazione AI processor fallisce
        """
        try:
            self.ai_processor = AIProcessor(self.config_manager.config_path)
        except Exception as e:
            raise Exception(f"Errore nell'inizializzazione del processore AI: {e}")
    
    def process_file(self, file_path: str) -> ProcessingResult:
        """
        Processa un file estraendo testo e generando riassunti.
        
        Args:
            file_path (str): Percorso del file da processare
            
        Returns:
            ProcessingResult: Risultati del processing
            
        Raises:
            FileNotFoundError: Se file non trovato
            ValueError: Se formato non supportato o file vuoto
            Exception: Per altri errori di processing
        """
        file_path = str(file_path)
        
        # Validazioni preliminari
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File non trovato: {file_path}")
        
        # Ottieni informazioni sul file
        file_info = self.document_processor.get_file_info(file_path)
        
        if not file_info['is_supported']:
            raise ValueError(
                f"Formato file '{file_info['extension']}' non supportato. "
                f"Formati supportati: {', '.join(DocumentProcessor.SUPPORTED_EXTENSIONS)}"
            )
        
        # Verifica dimensione file
        processing_config = self.config_manager.get_processing_config()
        max_size_mb = processing_config['max_file_size_mb']
        
        if file_info['size_mb'] > max_size_mb:
            raise ValueError(f"File troppo grande ({file_info['size_mb']}MB). Massimo consentito: {max_size_mb}MB")
        
        print(f"📄 Processando file: {file_info['filename']} ({file_info['size_mb']}MB)")
        
        try:
            # Estrai testo dal file
            extracted_text = self.document_processor.extract_text(file_path)
            
            if not extracted_text.strip():
                raise ValueError("Il file non contiene testo estraibile")
            
            print(f"📝 Testo estratto: {len(extracted_text)} caratteri, {len(extracted_text.split())} parole")
            
            # Processa con AI
            return self.ai_processor.process_text(extracted_text)
            
        except Exception as e:
            raise Exception(f"Errore nel processing del file '{file_path}': {str(e)}")
    
    def process_text(self, text: str) -> ProcessingResult:
        """
        Processa testo diretto generando riassunti.
        
        Args:
            text (str): Testo da processare
            
        Returns:
            ProcessingResult: Risultati del processing
            
        Raises:
            ValueError: Se testo non valido
            Exception: Per errori di processing
        """
        if not text or not text.strip():
            raise ValueError("Testo vuoto o non valido")
        
        print(f"📝 Processando testo: {len(text)} caratteri, {len(text.split())} parole")
        
        try:
            return self.ai_processor.process_text(text)
        except Exception as e:
            raise Exception(f"Errore nel processing del testo: {str(e)}")
    
    def get_supported_formats(self) -> list:
        """
        Restituisce i formati file supportati.
        
        Returns:
            list: Lista delle estensioni supportate
        """
        return list(DocumentProcessor.SUPPORTED_EXTENSIONS)
    
    def get_system_info(self) -> dict:
        """
        Restituisce informazioni di sistema e configurazione.
        
        Returns:
            dict: Informazioni di sistema
        """
        ai_stats = self.ai_processor.get_processing_stats() if self.ai_processor else {}
        
        return {
            'config_path': self.config_manager.config_path,
            'config_valid': self.config_manager.validate_config()['is_valid'],
            'supported_formats': self.get_supported_formats(),
            'processing_config': self.config_manager.get_processing_config(),
            'ai_stats': ai_stats,
            'version': '1.0.0'
        }


def print_result_summary(result: ProcessingResult):
    """
    Stampa un riassunto dei risultati in formato leggibile.
    
    Args:
        result (ProcessingResult): Risultati da stampare
    """
    print("\n" + "="*80)
    print("🤖 AI MEETING AGENT - RISULTATI DEL PROCESSING")
    print("="*80)
    
    # Metadata se presente
    if result.metadata:
        print(f"\n📊 METADATA:")
        print(f"   • Lunghezza input: {result.metadata.get('input_length', 'N/A')} caratteri")
        print(f"   • Parole input: {result.metadata.get('input_words', 'N/A')}")
        print(f"   • Stili processati: {', '.join(result.metadata.get('styles_processed', []))}")
        if result.metadata.get('processing_errors'):
            print(f"   • Errori: {len(result.metadata['processing_errors'])}")
    
    # Sezioni dei risultati
    sections = [
        ("📚 STILE DIDATTICO", result.didactic),
        ("🤝 STILE CLIENTE", result.client),
        ("💻 STILE SVILUPPATORI", result.developers),
        ("📈 STILE MANAGEMENT", result.management)
    ]
    
    for title, content in sections:
        print(f"\n{title}")
        print("-" * 50)
        if content.startswith("[ERRORE]"):
            print(f"❌ {content}")
        else:
            # Limita output per readability
            if len(content) > 500:
                print(content[:500] + "\n... [CONTENUTO TRONCATO] ...")
            else:
                print(content)
    
    print("\n" + "="*80)


def main():
    """
    Funzione principale per test e demo dell'applicazione.
    """
    print("🚀 Avvio AI Meeting Agent")
    
    try:
        # Inizializza agente
        agent = AIAgent()
        
        # Mostra informazioni di sistema
        system_info = agent.get_system_info()
        print(f"\n📋 INFORMAZIONI SISTEMA:")
        print(f"   • Versione: {system_info['version']}")
        print(f"   • Configurazione: {'✅ Valida' if system_info['config_valid'] else '❌ Non valida'}")
        print(f"   • Formati supportati: {', '.join(system_info['supported_formats'])}")
        
        # Test con testo di esempio
        sample_text = """
        Riunione del Team Development - 4 Giugno 2025
        
        Partecipanti: Mario Rossi (Tech Lead), Anna Verdi (Product Manager), Luca Bianchi (CTO)
        
        AGENDA:
        1. Review implementazione sistema di trascrizione automatica
        2. Integrazione con API GPT-4 per generazione riassunti
        3. Sviluppo interfaccia web con FastAPI
        4. Planning timeline di rilascio
        
        DISCUSSIONI PRINCIPALI:
        
        Sistema di Trascrizione:
        - Completata integrazione con servizio speech-to-text
        - Accuratezza del 95% in condizioni ottimali
        - Necessario miglioramento per audio con rumore di fondo
        - Supporto per italiano e inglese implementato
        
        Integrazione GPT-4:
        - API funzionante con rate limiting appropriato
        - Implementati 4 stili di output come richiesto
        - Costi stimati: 0.50€ per trascrizione media
        - Necessario monitoraggio usage per controllo budget
        
        Interfaccia Web:
        - Prototipo FastAPI funzionante
        - UI responsive implementata
        - Upload file e processing in tempo reale
        - Testing cross-browser completato
        
        DECISIONI PRESE:
        - Deployment in produzione schedulato per fine giugno
        - Budget approvato per 1000€/mese per API costs
        - Utilizzo di Docker per containerizzazione
        - Setup CI/CD pipeline con GitHub Actions
        
        ACTION ITEMS:
        - Mario: Finalizzare testing sistema (deadline: 10 giugno)
        - Anna: Preparare documentazione utente (deadline: 15 giugno)
        - Luca: Setup ambiente produzione (deadline: 20 giugno)
        - Team: Code review finale (deadline: 25 giugno)
        
        RISCHI IDENTIFICATI:
        - Possibili problemi di performance con file grandi
        - Dipendenza critica da servizi esterni (OpenAI)
        - Necessità formazione utenti per adoption
        
        PROSSIMA RIUNIONE: 11 giugno 2025, ore 14:00
        """
        
        print(f"\n🧪 TESTING CON TESTO DI ESEMPIO...")
        result = agent.process_text(sample_text)
        
        # Mostra risultati
        print_result_summary(result)
        
        # Mostra statistiche finali
        final_stats = agent.ai_processor.get_processing_stats()
        print(f"\n📊 STATISTICHE PROCESSING:")
        print(f"   • Richieste totali: {final_stats['total_requests']}")
        print(f"   • Successi: {final_stats['successful_requests']}")
        print(f"   • Errori: {final_stats['failed_requests']}")
        print(f"   • Success rate: {final_stats['success_rate']:.1%}")
        
        print(f"\n✅ Test completato con successo!")
        
    except Exception as e:
        print(f"\n❌ ERRORE: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
