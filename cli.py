"""
AI Meeting Agent - Command Line Interface

Interfaccia a riga di comando per l'elaborazione di documenti e testi.
"""

import click
import json
import sys
import os
from pathlib import Path

# Aggiungi utils al path per import
sys.path.append(os.path.join(os.path.dirname(__file__), 'utils'))

from main import AIAgent


@click.command()
@click.option('--file', '-f', type=click.Path(exists=True), help='File da processare (PDF, DOCX, TXT)')
@click.option('--text', '-t', type=str, help='Testo diretto da processare')
@click.option('--output', '-o', type=click.Path(), help='File di output (opzionale)')
@click.option('--format', type=click.Choice(['json', 'txt']), default='txt', help='Formato output')
@click.option('--config', type=click.Path(), help='Percorso file di configurazione custom')
@click.option('--verbose', '-v', is_flag=True, help='Output verboso')
def main(file, text, output, format, config, verbose):
    """
    AI Meeting Agent - Processore di testi e riunioni

    Genera riassunti specializzati in 4 stili diversi:
    📚 Didattico, 🤝 Cliente, 💻 Sviluppatori, 📈 Management

    Esempi:
        python cli.py --file meeting.pdf --output result.txt
        python cli.py --text "Contenuto riunione..." --format json
        python cli.py --file documento.docx --verbose
    """

    # Validazione input
    if not file and not text:
        click.echo("❌ Errore: Specifica --file o --text")
        click.echo("Usa --help per vedere tutti i comandi disponibili")
        return 1

    if file and text:
        click.echo("❌ Errore: Specifica solo --file o --text, non entrambi")
        return 1

    try:
        # Inizializza agente
        if verbose:
            click.echo("🚀 Inizializzando AI Agent...")

        agent = AIAgent(config_path=config)

        if verbose:
            system_info = agent.get_system_info()
            click.echo(f"✅ Agente inizializzato (versione {system_info['version']})")
            click.echo(f"📋 Formati supportati: {', '.join(system_info['supported_formats'])}")

        # Processa input
        if file:
            if verbose:
                click.echo(f"📄 Processando file: {file}")
            result = agent.process_file(file)
            source_info = f"File: {Path(file).name}"
        else:
            if verbose:
                click.echo(f"📝 Processando testo ({len(text)} caratteri)...")
            result = agent.process_text(text)
            source_info = f"Testo diretto ({len(text)} caratteri)"

        # Prepara output
        if format == 'json':
            output_data = {
                'source': source_info,
                'results': {
                    'didactic': result.didactic,
                    'client': result.client,
                    'developers': result.developers,
                    'management': result.management
                },
                'metadata': result.metadata
            }
            output_content = json.dumps(output_data, indent=2, ensure_ascii=False)
        else:
            output_content = format_text_output(result, source_info)

        # Salva o stampa output
        if output:
            with open(output, 'w', encoding='utf-8') as f:
                f.write(output_content)
            click.echo(f"✅ Risultati salvati in: {output}")

            if verbose:
                # Mostra statistiche
                stats = agent.ai_processor.get_processing_stats()
                click.echo(f"\n📊 Statistiche processing:")
                click.echo(f"   • Richieste API: {stats['total_requests']}")
                click.echo(f"   • Success rate: {stats['success_rate']:.1%}")
        else:
            click.echo(output_content)

    except Exception as e:
        click.echo(f"❌ Errore: {e}")
        if verbose:
            import traceback
            click.echo("\n🔍 Traceback completo:")
            click.echo(traceback.format_exc())
        return 1

    return 0


def format_text_output(result, source_info):
    """
    Formatta i risultati in output testuale leggibile.

    Args:
        result: ProcessingResult con i riassunti
        source_info: Informazioni sulla sorgente

    Returns:
        str: Output formattato
    """
    output_lines = [
        "=" * 80,
        "🤖 AI MEETING AGENT - RISULTATI",
        "=" * 80,
        f"\n📄 SORGENTE: {source_info}",
        ""
    ]

    # Metadata se presente
    if result.metadata:
        output_lines.extend([
            "📊 METADATA:",
            f"   • Lunghezza input: {result.metadata.get('input_length', 'N/A')} caratteri",
            f"   • Parole: {result.metadata.get('input_words', 'N/A')}",
            f"   • Stili processati: {', '.join(result.metadata.get('styles_processed', []))}",
            ""
        ])

        if result.metadata.get('processing_errors'):
            output_lines.extend([
                f"   ⚠️  Errori: {len(result.metadata['processing_errors'])}",
                ""
            ])

    # Sezioni dei risultati
    sections = [
        ("📚 STILE DIDATTICO", result.didactic),
        ("🤝 STILE CLIENTE", result.client),
        ("💻 STILE SVILUPPATORI", result.developers),
        ("📈 STILE MANAGEMENT", result.management)
    ]

    for title, content in sections:
        output_lines.extend([
            f"{title}",
            "-" * 50,
            content,
            "",
            "=" * 80,
            ""
        ])

    return "\n".join(output_lines)


@click.group()
def cli():
    """AI Meeting Agent - Suite di comandi"""
    pass


@cli.command()
@click.option('--config', type=click.Path(), help='Percorso file di configurazione')
def info(config):
    """Mostra informazioni di sistema e configurazione"""
    try:
        agent = AIAgent(config_path=config)
        system_info = agent.get_system_info()

        click.echo("🤖 AI Meeting Agent - Informazioni Sistema")
        click.echo("=" * 50)
        click.echo(f"📦 Versione: {system_info['version']}")
        click.echo(f"⚙️  Configurazione: {'✅ Valida' if system_info['config_valid'] else '❌ Non valida'}")
        click.echo(f"📄 Formati supportati: {', '.join(system_info['supported_formats'])}")
        click.echo(f"📂 Config path: {system_info['config_path']}")

        proc_config = system_info['processing_config']
        click.echo(f"\n🔧 Configurazione Processing:")
        click.echo(f"   • Max file size: {proc_config['max_file_size_mb']}MB")
        click.echo(f"   • Cache abilitata: {proc_config['cache_enabled']}")

        ai_stats = system_info.get('ai_stats', {})
        if ai_stats.get('total_requests', 0) > 0:
            click.echo(f"\n📊 Statistiche AI:")
            click.echo(f"   • Richieste totali: {ai_stats['total_requests']}")
            click.echo(f"   • Success rate: {ai_stats.get('success_rate', 0):.1%}")

    except Exception as e:
        click.echo(f"❌ Errore: {e}")


@cli.command()
def setup():
    """Setup iniziale del sistema"""
    try:
        from utils.config_manager import setup_initial_config

        click.echo("🚀 Setup AI Meeting Agent")
        click.echo("=" * 30)

        if setup_initial_config():
            click.echo("✅ Setup completato!")
            click.echo("\n📝 Prossimi passi:")
            click.echo("1. Configura la tua API key OpenAI in config/api_keys.ini")
            click.echo("2. Testa il sistema: python cli.py info")
            click.echo("3. Processa un documento: python cli.py --file documento.pdf")
        else:
            click.echo("❌ Setup fallito")
            return 1

    except Exception as e:
        click.echo(f"❌ Errore nel setup: {e}")
        return 1


if __name__ == '__main__':
    # Se chiamato direttamente, usa il comando principale
    if len(sys.argv) == 1:
        main(['--help'])
    elif '--help' in sys.argv or '-h' in sys.argv:
        main()
    elif any(arg in ['info', 'setup'] for arg in sys.argv):
        cli()
    else:
        sys.exit(main())