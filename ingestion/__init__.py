"""
Ingestion module for PsycheOS.

This module handles ingestion of various data sources:
- PDF documents (academic papers, books)
- Video content (YouTube, lectures)
- Audio files (podcasts, interviews)
- Web articles (blogs, news, academic sites)
"""

from .pdf_parser import PDFParser
from .video_ingestion import YouTubeIngestor
from .audio_transcriber import AudioTranscriber
from .web_scraper import WebScraper

__all__ = [
    "PDFParser",
    "YouTubeIngestor",
    "AudioTranscriber",
    "WebScraper",
]

__version__ = "0.1.0"