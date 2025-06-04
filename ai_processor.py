"""
Modulo per l'integrazione con OpenAI GPT-4 e generazione di riassunti specializzati.

Gestisce la comunicazione con l'API OpenAI e la generazione di contenuti
in 4 stili diversi: didattico, cliente, sviluppatori, management.
"""

import configparser
from typing import Dict, List, Optional
from dataclasses import dataclass
from openai import OpenAI


@dataclass
class ProcessingResult:
    """
    Risultato del processing AI contenente tutti gli stili di output.

    Attributes:
        didactic (str): Riassunto in stile didattico/formativo
        client (str): Riassunto per comunicazione con clienti
        developers (str): Task e informazioni per sviluppatori
        management (str): Riassunto esecutivo per management
        original_text (str): Testo originale processato
        metadata (dict): Metadati aggiuntivi (token utilizzati, tempo, etc.)
    """
    didactic: str
    client: str
    developers: str
    management: str
    original_text: str
    metadata: Optional[Dict] = None


class PromptManager:
    """
    Manager per i prompt specializzati per ogni stile di output.

    Centralizza la gestione dei prompt per garantire consistenza
    e facilità di manutenzione.
    """

    @staticmethod
    def get_system_prompts() -> Dict[str, str]:
        """
        Restituisce i prompt di sistema per ogni stile di output.

        Returns:
            Dict[str, str]: Dizionario con prompt per ogni stile
        """
        return {
            "didactic": """Sei un esperto formatore e instructional designer.
            Trasforma il contenuto in un formato didattico chiaro, strutturato e formativo.

            OBIETTIVI:
            - Organizzare le informazioni in sezioni logiche e progressive
            - Aggiungere spiegazioni contestuali e definizioni quando necessario
            - Evidenziare concetti chiave e takeaway principali
            - Creare una struttura facile da seguire per l'apprendimento
            - Includere esempi pratici quando appropriato

            FORMATO RICHIESTO:
            - Usa intestazioni chiare e gerarchia logica
            - Includi punti salienti evidenziati
            - Mantieni un tono professionale ma accessibile
            - Aggiungi note esplicative per concetti complessi""",

            "client": """Sei un account manager senior esperto in comunicazione business.
            Trasforma il contenuto in una comunicazione professionale ottimizzata per i clienti.

            OBIETTIVI:
            - Usare linguaggio business-friendly e professionale
            - Evidenziare benefici, valore aggiunto e ROI
            - Rimuovere dettagli tecnici interni non rilevanti
            - Focalizzarti su risultati concreti e prossimi passi
            - Mantenere un tono positivo e orientato alla soluzione

            FORMATO RICHIESTO:
            - Executive summary in apertura
            - Sezioni chiare con benefici evidenziati
            - Linguaggio orientato al business value
            - Call-to-action concrete quando appropriate""",

            "developers": """Sei un tech lead senior con expertise in project management.
            Trasforma il contenuto in task specifici e actionable per il team di sviluppo.

            OBIETTIVI:
            - Creare una lista di task concrete e actionable
            - Specificare priorità, dipendenze e stime quando possibile
            - Includere dettagli tecnici rilevanti e specifiche
            - Definire criteri di accettazione e definition of done
            - Identificare rischi tecnici e blockers potenziali

            FORMATO RICHIESTO:
            - Task breakdown structure chiara
            - Priorità indicate (P0, P1, P2...)
            - Stime effort quando possibili
            - Note tecniche e considerazioni architetturali
            - Dependencies e blockers evidenziati""",

            "management": """Sei un senior executive con expertise in strategic management.
            Trasforma il contenuto in un riassunto esecutivo per il management e leadership.

            OBIETTIVI:
            - Evidenziare decisioni chiave e impatti strategici
            - Includere metriche, KPI e timeline rilevanti
            - Focalizzarti su rischi, opportunità e trade-off
            - Mantenere il contenuto ad alto livello e strategic
            - Evidenziare impatti su budget, risorse e obiettivi

            FORMATO RICHIESTO:
            - Executive summary con key decisions
            - Impatti su budget e timeline
            - Risk assessment e mitigation
            - Strategic recommendations
            - Next steps con ownership chiaro"""
        }

    @staticmethod
    def get_user_prompt_template() -> str:
        """
        Template per il prompt utente da inviare a GPT.

        Returns:
            str: Template del prompt utente
        """
        return """Analizza e riassumi il seguente contenuto seguendo rigorosamente le linee guida del tuo ruolo:

CONTENUTO DA ANALIZZARE:
{content}

ISTRUZIONI AGGIUNTIVE:
- Mantieni la massima fedeltà al contenuto originale
- Non inventare informazioni non presenti nel testo
- Se alcune informazioni non sono chiare, evidenzialo
- Organizza il contenuto in modo logico e strutturato
- Lunghezza target: 300-800 parole"""


class AIProcessor:
    """
    Processore AI per la generazione di riassunti specializzati usando OpenAI GPT-4.

    Gestisce l'integrazione con l'API OpenAI e coordina la generazione
    di contenuti in diversi stili specializzati.
    """

    def __init__(self, config_path: str = "config/api_keys.ini"):
        """
        Inizializza il processore AI.

        Args:
            config_path (str): Percorso del file di configurazione con API key

        Raises:
            ValueError: Se API key non configurata correttamente
            Exception: Per errori di inizializzazione OpenAI client
        """
        self.config_path = config_path
        self.client = None
        self.prompt_manager = PromptManager()
        self.processing_stats = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0
        }

        self._initialize_openai_client()

    def _initialize_openai_client(self):
        """
        Inizializza il client OpenAI leggendo la configurazione.

        Raises:
            ValueError: Se configurazione non valida
            Exception: Per errori di inizializzazione
        """
        try:
            config = configparser.ConfigParser()
            config.read(self.config_path)

            if 'openai' not in config.sections():
                raise ValueError(f"Sezione [openai] non trovata in {self.config_path}")

            api_key = config.get('openai', 'api_key', fallback=None)

            if not api_key or api_key == "YOUR_OPENAI_API_KEY_HERE":
                raise ValueError(
                    f"API key OpenAI non configurata correttamente in {self.config_path}. "
                    "Assicurati di inserire una chiave API valida nella sezione [openai]."
                )

            self.client = OpenAI(api_key=api_key)

            # Test della connessione
            self._test_api_connection()

        except configparser.Error as e:
            raise ValueError(f"Errore nella lettura della configurazione: {e}")
        except Exception as e:
            raise Exception(f"Errore nell'inizializzazione del client OpenAI: {e}")

    def _test_api_connection(self):
        """
        Testa la connessione all'API OpenAI con una richiesta minimale.

        Raises:
            Exception: Se test di connessione fallisce
        """
        try:
            # Richiesta di test minimale
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": "Test"}],
                max_tokens=1
            )
            # Se arriviamo qui, la connessione è ok
        except Exception as e:
            raise Exception(f"Test connessione API OpenAI fallito: {e}")

    def _generate_summary_for_style(self, text: str, style: str) -> str:
        """
        Genera riassunto per uno stile specifico usando GPT-4.

        Args:
            text (str): Testo da riassumere
            style (str): Stile richiesto (didactic, client, developers, management)

        Returns:
            str: Riassunto generato

        Raises:
            ValueError: Se stile non supportato
            Exception: Per errori di generazione
        """
        system_prompts = self.prompt_manager.get_system_prompts()

        if style not in system_prompts:
            raise ValueError(f"Stile '{style}' non supportato. Stili disponibili: {list(system_prompts.keys())}")

        user_prompt_template = self.prompt_manager.get_user_prompt_template()
        user_prompt = user_prompt_template.format(content=text)

        try:
            self.processing_stats['total_requests'] += 1

            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompts[style]},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=2000,
                temperature=0.3,
                top_p=0.9,
                frequency_penalty=0.0,
                presence_penalty=0.0
            )

            generated_content = response.choices[0].message.content.strip()

            if not generated_content:
                raise Exception(f"GPT-4 ha restituito contenuto vuoto per stile '{style}'")

            self.processing_stats['successful_requests'] += 1
            return generated_content

        except Exception as e:
            self.processing_stats['failed_requests'] += 1
            error_msg = f"Errore nella generazione per stile '{style}': {str(e)}"
            print(f"WARNING: {error_msg}")
            return f"[ERRORE] {error_msg}"

    def process_text(self, text: str, styles: Optional[List[str]] = None) -> ProcessingResult:
        """
        Processa testo generando riassunti in tutti gli stili richiesti.

        Args:
            text (str): Testo da processare
            styles (Optional[List[str]]): Lista stili da generare (default: tutti)

        Returns:
            ProcessingResult: Risultati del processing

        Raises:
            ValueError: Se input non valido
            Exception: Per errori di processing
        """
        if not text or not text.strip():
            raise ValueError("Testo di input vuoto o non valido")

        # Validazione lunghezza testo
        if len(text.strip()) < 50:
            raise ValueError("Testo troppo corto (minimo 50 caratteri)")

        if len(text) > 50000:  # Limite per evitare problemi con token limit
            print("WARNING: Testo molto lungo, potrebbero esserci problemi con il token limit")

        # Default: tutti gli stili
        if styles is None:
            styles = ["didactic", "client", "developers", "management"]

        # Validazione stili richiesti
        valid_styles = set(self.prompt_manager.get_system_prompts().keys())
        invalid_styles = set(styles) - valid_styles
        if invalid_styles:
            raise ValueError(f"Stili non validi: {invalid_styles}. Stili supportati: {valid_styles}")

        results = {}
        processing_metadata = {
            'input_length': len(text),
            'input_words': len(text.split()),
            'styles_processed': [],
            'processing_errors': []
        }

        # Genera riassunto per ogni stile
        for style in styles:
            try:
                print(f"Generando riassunto in stile: {style}")
                result = self._generate_summary_for_style(text, style)
                results[style] = result
                processing_metadata['styles_processed'].append(style)

            except Exception as e:
                error_msg = f"Errore nel processing stile '{style}': {str(e)}"
                results[style] = f"[ERRORE] {error_msg}"
                processing_metadata['processing_errors'].append(error_msg)
                print(f"ERROR: {error_msg}")

        # Assicura che tutti gli stili richiesti siano presenti
        for style in ["didactic", "client", "developers", "management"]:
            if style not in results:
                results[style] = "[NON GENERATO] Stile non richiesto"

        return ProcessingResult(
            didactic=results["didactic"],
            client=results["client"],
            developers=results["developers"],
            management=results["management"],
            original_text=text,
            metadata=processing_metadata
        )

    def get_processing_stats(self) -> Dict:
        """
        Restituisce statistiche del processing.

        Returns:
            Dict: Statistiche delle richieste API
        """
        stats = self.processing_stats.copy()
        if stats['total_requests'] > 0:
            stats['success_rate'] = stats['successful_requests'] / stats['total_requests']
        else:
            stats['success_rate'] = 0.0

        return stats

    def reset_stats(self):
        """Reset delle statistiche di processing."""
        self.processing_stats = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0
        }