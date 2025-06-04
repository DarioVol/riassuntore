# riassuntore
# 🤖 AI Meeting Agent

Sistema intelligente per la generazione automatica di riassunti e minute da documenti e trascrizioni di riunioni in 4 stili specializzati.

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![OpenAI GPT-4](https://img.shields.io/badge/OpenAI-GPT--4-green.svg)](https://openai.com)

## ✨ Caratteristiche Principali

- **📄 Multi-formato**: Supporta PDF, DOCX, DOC, TXT
- **🎯 4 Stili di Output**:
  - 📚 **Didattico**: Per formazione e comprensione
  - 🤝 **Cliente**: Comunicazione business-friendly  
  - 💻 **Sviluppatori**: Task tecnici actionable
  - 📈 **Management**: Riassunto esecutivo strategico
- **🚀 Interfacce Multiple**: CLI, Web App, API Programmatica
- **🔧 Architettura Modulare**: Facilmente estendibile e manutenibile
- **⚡ Performance Ottimizzate**: Caching, error handling, monitoring

## 🏗️ Architettura

```
ai-meeting-agent/
├── main.py                    # ✨ Coordinatore principale
├── utils/                     # 🛠️ Moduli specializzati
│   ├── document_processor.py  # 📄 Estrazione testo
│   ├── ai_processor.py        # 🤖 Processing GPT-4  
│   └── config_manager.py      # ⚙️ Gestione config
├── cli.py                     # 💻 Command Line Interface
├── webapp.py                  # 🌐 Web Application
├── setup.py                   # 📦 Script di installazione
└── templates/                 # 🎨 Template HTML
    └── index.html
```

## 🚀 Quick Start

### 1. Clone e Setup
```bash
# Clone del repository
git clone https://github.com/your-username/ai-meeting-agent.git
cd ai-meeting-agent

# Setup automatico (installa dipendenze + configurazione)
python setup.py
```

### 2. Configurazione API Key
```bash
# Copia il file di esempio
cp config/api_keys.ini.example config/api_keys.ini

# Modifica con la tua API key OpenAI
# [openai]
# api_key = sk-your-actual-openai-api-key-here
```

### 3. Test del Sistema
```bash
# Test con esempio integrato
python main.py
```

## 💡 Modalità di Utilizzo

### 🖥️ Command Line Interface
```bash
# Processa file PDF
python cli.py --file meeting.pdf --output risultati.txt

# Processa testo diretto in formato JSON
python cli.py --text "Contenuto riunione..." --format json

# Output diretto su console
python cli.py --file documento.docx --verbose
```

### 🌐 Web Application
```bash
# Avvia server web
python webapp.py

# Apri browser su http://localhost:8000
# Interface drag & drop per upload file e text input
```

### 🔧 API Programmatica  
```python
from main import AIAgent

# Inizializza agente
agent = AIAgent()

# Processa file
result = agent.process_file("meeting.pdf")

# Processa testo diretto
result = agent.process_text("Contenuto della riunione...")

# Accesso ai risultati
print("📚 Didattico:", result.didactic)
print("🤝 Cliente:", result.client)  
print("💻 Sviluppatori:", result.developers)
print("📈 Management:", result.management)
```

## 🎯 Esempi di Output

### Input Example:
```
Riunione Team Development - 4 Giugno 2025

DECISIONI:
- Deployment produzione: fine giugno
- Budget API: 1000€/mese
- Utilizzo Docker per containerizzazione

ACTION ITEMS:
- Mario: Testing sistema (deadline: 10 giugno)
- Anna: Documentazione utente (deadline: 15 giugno)  
- Luca: Setup produzione (deadline: 20 giugno)
```

### 📚 Output Didattico:
```
## Panoramica della Riunione

La riunione del team di sviluppo ha definito la roadmap per il deployment...

### Decisioni Principali
1. **Timeline di Rilascio**: Il deployment in produzione è schedulato per fine giugno...
2. **Budget Operativo**: Approvato budget di 1000€/mese per costi API...

### Aspetti Tecnici  
L'utilizzo di Docker garantirà...
```

### 🤝 Output Cliente:
```
## Executive Summary

Il progetto procede secondo i piani stabiliti con deployment previsto per fine giugno...

### Benefici per il Cliente
- Piattaforma disponibile in produzione entro fine mese
- Investimento contenuto con ROI stimato in 6 mesi...
```

### 💻 Output Sviluppatori:
```
## Task Breakdown

### P0 - Critical Path
- [ ] **Testing sistema** (Owner: Mario, Deadline: 10/06)
  - Unit tests completamento
  - Integration testing
  - Performance testing...

### P1 - Important  
- [ ] **Setup ambiente produzione** (Owner: Luca, Deadline: 20/06)...
```

### 📈 Output Management:
```
## Strategic Summary

### Key Decisions
- **Go-Live Date**: Fine giugno 2025 - timeline aggressiva ma achievable
- **Investment**: 1000€/mese operational cost - allineato con budget Q2...

### Risk Assessment
- **Technical Risk**: Medium - dipendenza da servizi esterni
- **Timeline Risk**: High - deadline aggressive...
```

## 🐳 Deploy con Docker

```bash
# Build immagine
docker build -t ai-meeting-agent .

# Run container
docker run -p 8000:8000 -v $(pwd)/config:/app/config ai-meeting-agent

# O usa docker-compose
docker-compose up
```

## 📋 Requisiti

- Python 3.8+
- OpenAI API Key con accesso a GPT-4
- 2GB RAM (raccomandati 4GB)

## ⚙️ Configurazione Avanzata

### File di Configurazione
```ini
[openai]
api_key = sk-your-key-here
model = gpt-4  
max_tokens = 2000
temperature = 0.3

[processing]  
max_file_size_mb = 50
supported_formats = pdf,docx,doc,txt
cache_enabled = true

[webapp]
host = 0.0.0.0
port = 8000
debug = false
```

### Personalizzazione Prompt
Modifica `utils/ai_processor.py` → `PromptManager.get_system_prompts()` per customizzare i prompt per ogni stile.

### Estensione Formati
Aggiungi nuovi formati in `utils/document_processor.py` → `DocumentProcessor`

## 🧪 Testing

```bash
# Informazioni sistema
python cli.py info

# Test specifico con file
python cli.py --file documento.pdf --verbose

# Avvia webapp in modalità debug
python webapp.py
```

## 📄 Licenza

MIT License - Vedi [LICENSE](LICENSE) per dettagli.

## 🤝 Contributi

1. Fork del repository
2. Feature branch: `git checkout -b feature/nome-feature`
3. Commit: `git commit -m 'Add feature'`
4. Push: `git push origin feature/nome-feature`  
5. Pull Request

## 🆘 Support

- 🐛 Issues: [GitHub Issues](https://github.com/your-username/ai-meeting-agent/issues)
- 📖 Docs: [DOCUMENTATION.md](DOCUMENTATION.md)

## 🔄 Roadmap

- [ ] Batch processing multiple file
- [ ] Webhook integration
- [ ] Custom user-defined styles  
- [ ] Analytics dashboard
- [ ] Multi-language support
- [ ] Plugin system per custom extractors

---

**Sviluppato con ❤️ per automatizzare la gestione di meeting e documenti**
