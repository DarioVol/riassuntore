"""
AI Meeting Agent - Utils Package

Moduli di utilità per l'elaborazione di documenti e AI processing.
"""

__version__ = "1.0.0"
__author__ = "AI Meeting Agent Team"

from .document_processor import DocumentProcessor
from .ai_processor import AIProcessor, ProcessingResult
from .config_manager import ConfigManager

__all__ = [
    'DocumentProcessor',
    'AIProcessor',
    'ProcessingResult',
    'ConfigManager'
]