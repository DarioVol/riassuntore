"""
Setup script per AI Meeting Agent

Automatizza l'installazione e configurazione iniziale del sistema.
"""

import os
import sys
import subprocess
from pathlib import Path


def install_requirements():
    """Installa le dipendenze richieste."""
    requirements = [
        "openai==1.12.0",
        "fastapi==0.109.0",
        "uvicorn==0.27.0",
        "python-multipart==0.0.6",
        "PyPDF2==3.0.1",
        "python-docx==1.1.0",
        "configparser==6.0.0",
        "click==8.1.7",
        "jinja2==3.1.3",
        "gunicorn==21.2.0"
    ]

    print("📦 Installando dipendenze...")
    for req in requirements:
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", req])
            print(f"✅ {req}")
        except subprocess.CalledProcessError:
            print(f"❌ Errore installazione {req}")
            return False

    return True


def setup_directories():
    """Crea le directory necessarie."""
    directories = ["config", "utils", "templates", "tests"]

    for dir_name in directories:
        Path(dir_name).mkdir(exist_ok=True)
        print(f"📁 Directory {dir_name} creata/verificata")


def create_config_example():
    """Crea file di configurazione di esempio."""
    config_example_content = """[openai]
# Inserisci qui la tua API key OpenAI
api_key = YOUR_OPENAI_API_KEY_HERE
model = gpt-4
max_tokens = 2000
temperature = 0.3

[processing]
# Dimensione massima file in MB
max_file_size_mb = 50
# Formati supportati (comma separated)
supported_formats = pdf,docx,doc,txt
# Abilita cache per documenti
cache_enabled = true

[webapp]
# Configurazione server web
host = 0.0.0.0
port = 8000
debug = false
"""

    config_example_path = Path("config/api_keys.ini.example")

    try:
        with open(config_example_path, 'w') as f:
            f.write(config_example_content)
        print(f"✅ File di esempio creato: {config_example_path}")
        return True
    except Exception as e:
        print(f"❌ Errore nella creazione del file di esempio: {e}")
        return False


def setup_configuration():
    """Setup configurazione iniziale."""
    try:
        # Aggiungi utils al path per import
        sys.path.append(os.path.join(os.path.dirname(__file__), 'utils'))
        from utils.config_manager import setup_initial_config

        print("⚙️ Setup configurazione...")
        if setup_initial_config():
            print("✅ Configurazione inizializzata")
            print("❗ IMPORTANTE: Configura la tua API key OpenAI in config/api_keys.ini")
            return True
        else:
            print("❌ Errore nel setup configurazione")
            return False
    except ImportError:
        print("⚠️ Moduli utils non ancora disponibili, verrà configurato al primo avvio")
        return True
    except Exception as e:
        print(f"❌ Errore nel setup configurazione: {e}")
        return False


def create_gitignore():
    """Crea file .gitignore."""
    gitignore_content = """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# Virtual Environment
venv/
env/
ENV/
.env

# API Keys e Config
config/api_keys.ini
*.key

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# Logs
*.log
logs/

# Temp files
*.tmp
*.temp
temp/
.cache/

# Test coverage
htmlcov/
.coverage
.coverage.*
coverage.xml
*.cover
.hypothesis/
.pytest_cache/

# Jupyter
.ipynb_checkpoints

# Docker
.dockerignore

# Upload directory
uploads/
"""

    try:
        with open('.gitignore', 'w') as f:
            f.write(gitignore_content)
        print("✅ File .gitignore creato")
        return True
    except Exception as e:
        print(f"❌ Errore nella creazione di .gitignore: {e}")
        return False


def run_basic_tests():
    """Esegue test di base del sistema."""
    try:
        print("🧪 Eseguendo test di base...")

        # Test import moduli utils (se esistono)
        try:
            sys.path.append(os.path.join(os.path.dirname(__file__), 'utils'))
            from utils.document_processor import DocumentProcessor
            from utils.config_manager import ConfigManager
            print("✅ Import moduli utils OK")
        except ImportError as e:
            print(f"⚠️ Alcuni moduli utils non disponibili: {e}")

        # Verifica struttura directory
        required_dirs = ['config', 'utils', 'templates']
        for dir_name in required_dirs:
            if Path(dir_name).exists():
                print(f"✅ Directory {dir_name} presente")
            else:
                print(f"❌ Directory {dir_name} mancante")
                return False

        # Verifica file principali
        required_files = ['main.py', 'cli.py', 'webapp.py']
        for file_name in required_files:
            if Path(file_name).exists():
                print(f"✅ File {file_name} presente")
            else:
                print(f"⚠️ File {file_name} non trovato")

        print("✅ Test di base completati")
        return True

    except Exception as e:
        print(f"❌ Errore nei test: {e}")
        return False


def main():
    """Setup principale del sistema."""
    print("🚀 AI Meeting Agent - Setup Automatico")
    print("=" * 50)

    steps = [
        ("Creazione directory", setup_directories),
        ("Installazione dipendenze", install_requirements),
        ("Creazione .gitignore", create_gitignore),
        ("Creazione config esempio", create_config_example),
        ("Setup configurazione", setup_configuration),
        ("Test di base", run_basic_tests)
    ]

    for step_name, step_func in steps:
        print(f"\n📋 {step_name}...")
        if not step_func():
            print(f"❌ Setup fallito durante: {step_name}")
            return 1

    print("\n" + "=" * 50)
    print("✅ Setup completato con successo!")
    print("\n📋 PROSSIMI PASSI:")
    print("1. 🔑 Configura la tua API key OpenAI:")
    print("   - Copia: cp config/api_keys.ini.example config/api_keys.ini")
    print("   - Modifica config/api_keys.ini con la tua API key")
    print("2. 🧪 Testa il sistema: python main.py")
    print("3. 💻 Usa CLI: python cli.py --help")
    print("4. 🌐 Avvia webapp: python webapp.py")
    print("5. 📚 Leggi la documentazione: README.md")

    return 0


if __name__ == "__main__":
    sys.exit(main())