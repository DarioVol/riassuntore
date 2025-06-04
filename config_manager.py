"""
Modulo per la gestione delle configurazioni del sistema.

Centralizza la gestione di configurazioni, validazioni e impostazioni
per garantire coerenza e facilità di manutenzione.
"""

import os
import configparser
from pathlib import Path
from typing import Dict, Any, Optional


class ConfigManager:
    """
    Manager centralizzato per le configurazioni del sistema.

    Gestisce la lettura, validazione e creazione di file di configurazione
    per l'applicazione AI Meeting Agent.
    """

    DEFAULT_CONFIG_PATH = "config/api_keys.ini"
    DEFAULT_CONFIG_DIR = "config"

    def __init__(self, config_path: Optional[str] = None):
        """
        Inizializza il config manager.

        Args:
            config_path (Optional[str]): Percorso custom del file config
        """
        self.config_path = config_path or self.DEFAULT_CONFIG_PATH
        self.config = configparser.ConfigParser()
        self._ensure_config_directory()

    def _ensure_config_directory(self):
        """Crea la directory di configurazione se non esiste."""
        config_dir = Path(self.config_path).parent
        config_dir.mkdir(exist_ok=True)

    def load_config(self) -> bool:
        """
        Carica la configurazione dal file.

        Returns:
            bool: True se caricamento avvenuto con successo
        """
        try:
            if not os.path.exists(self.config_path):
                return False

            self.config.read(self.config_path)
            return True

        except Exception as e:
            print(f"Errore nel caricamento della configurazione: {e}")
            return False

    def create_default_config(self) -> bool:
        """
        Crea un file di configurazione di default.

        Returns:
            bool: True se creazione avvenuta con successo
        """
        try:
            self.config['openai'] = {
                'api_key': 'YOUR_OPENAI_API_KEY_HERE',
                'model': 'gpt-4',
                'max_tokens': '2000',
                'temperature': '0.3'
            }

            self.config['processing'] = {
                'max_file_size_mb': '50',
                'supported_formats': 'pdf,docx,doc,txt',
                'cache_enabled': 'true'
            }

            self.config['webapp'] = {
                'host': '0.0.0.0',
                'port': '8000',
                'debug': 'false'
            }

            with open(self.config_path, 'w') as configfile:
                self.config.write(configfile)

            print(f"File di configurazione creato in: {self.config_path}")
            print("IMPORTANTE: Configura la tua API key OpenAI nel file!")
            return True

        except Exception as e:
            print(f"Errore nella creazione del file di configurazione: {e}")
            return False

    def validate_config(self) -> Dict[str, Any]:
        """
        Valida la configurazione corrente.

        Returns:
            Dict: Risultato della validazione con dettagli
        """
        validation_result = {
            'is_valid': True,
            'errors': [],
            'warnings': [],
            'config_exists': os.path.exists(self.config_path)
        }

        if not validation_result['config_exists']:
            validation_result['is_valid'] = False
            validation_result['errors'].append(f"File di configurazione non trovato: {self.config_path}")
            return validation_result

        # Carica config se non già fatto
        if not self.config.sections():
            self.load_config()

        # Validazione sezione OpenAI
        if 'openai' not in self.config:
            validation_result['is_valid'] = False
            validation_result['errors'].append("Sezione [openai] mancante")
        else:
            api_key = self.config.get('openai', 'api_key', fallback='')
            if not api_key or api_key == 'YOUR_OPENAI_API_KEY_HERE':
                validation_result['is_valid'] = False
                validation_result['errors'].append("API key OpenAI non configurata")

        # Validazione sezione processing (opzionale ma con warning)
        if 'processing' not in self.config:
            validation_result['warnings'].append("Sezione [processing] mancante - verranno usati i default")

        return validation_result

    def get_openai_config(self) -> Dict[str, str]:
        """
        Restituisce la configurazione OpenAI.

        Returns:
            Dict: Configurazione OpenAI con defaults
        """
        if not self.config.sections():
            self.load_config()

        return {
            'api_key': self.config.get('openai', 'api_key', fallback=''),
            'model': self.config.get('openai', 'model', fallback='gpt-4'),
            'max_tokens': self.config.getint('openai', 'max_tokens', fallback=2000),
            'temperature': self.config.getfloat('openai', 'temperature', fallback=0.3)
        }

    def get_processing_config(self) -> Dict[str, Any]:
        """
        Restituisce la configurazione di processing.

        Returns:
            Dict: Configurazione processing con defaults
        """
        if not self.config.sections():
            self.load_config()

        return {
            'max_file_size_mb': self.config.getint('processing', 'max_file_size_mb', fallback=50),
            'supported_formats': self.config.get('processing', 'supported_formats', fallback='pdf,docx,doc,txt').split(','),
            'cache_enabled': self.config.getboolean('processing', 'cache_enabled', fallback=True)
        }

    def get_webapp_config(self) -> Dict[str, Any]:
        """
        Restituisce la configurazione webapp.

        Returns:
            Dict: Configurazione webapp con defaults
        """
        if not self.config.sections():
            self.load_config()

        return {
            'host': self.config.get('webapp', 'host', fallback='0.0.0.0'),
            'port': self.config.getint('webapp', 'port', fallback=8000),
            'debug': self.config.getboolean('webapp', 'debug', fallback=False)
        }

    def update_api_key(self, api_key: str) -> bool:
        """
        Aggiorna l'API key nel file di configurazione.

        Args:
            api_key (str): Nuova API key

        Returns:
            bool: True se aggiornamento avvenuto con successo
        """
        try:
            if not self.config.sections():
                self.load_config()

            if 'openai' not in self.config:
                self.config['openai'] = {}

            self.config['openai']['api_key'] = api_key

            with open(self.config_path, 'w') as configfile:
                self.config.write(configfile)

            return True

        except Exception as e:
            print(f"Errore nell'aggiornamento dell'API key: {e}")
            return False


def setup_initial_config(config_path: Optional[str] = None) -> bool:
    """
    Funzione di utility per setup iniziale della configurazione.

    Args:
        config_path (Optional[str]): Percorso custom del file config

    Returns:
        bool: True se setup completato con successo
    """
    config_manager = ConfigManager(config_path)

    # Verifica se configurazione esiste già
    if os.path.exists(config_manager.config_path):
        validation = config_manager.validate_config()
        if validation['is_valid']:
            print("Configurazione già presente e valida.")
            return True
        else:
            print("Configurazione presente ma non valida:")
            for error in validation['errors']:
                print(f"  - {error}")

    # Crea configurazione di default
    print(f"Creando configurazione di default in {config_manager.config_path}")
    return config_manager.create_default_config()