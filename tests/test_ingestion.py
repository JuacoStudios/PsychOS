"""
Tests for PsycheOS ingestion modules.
"""

import json
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from ingestion.audio_transcriber import AudioTranscriber
from ingestion.pdf_parser import PDFParser
from ingestion.video_ingestion import YouTubeIngestor
from ingestion.web_scraper import WebScraper


class TestPDFParser:
    """Tests for PDF parser."""
    
    def test_init(self):
        """Test PDFParser initialization."""
        parser = PDFParser(output_dir="test_output")
        assert parser.output_dir == Path("test_output")
        assert parser.output_dir.exists()
    
    def test_parse_file_not_found(self):
        """Test parsing non-existent file."""
        parser = PDFParser()
        with pytest.raises(FileNotFoundError):
            parser.parse_file("nonexistent.pdf")
    
    @patch("ingestion.pdf_parser.pymupdf.open")
    def test_parse_with_pymupdf(self, mock_fitz):
        """Test PDF parsing with pymupdf."""
        # Mock PDF document
        mock_doc = MagicMock()
        mock_doc.metadata = {
            "title": "Test PDF",
            "author": "Test Author",
        }
        mock_doc.__len__.return_value = 1
        
        mock_page = MagicMock()
        mock_page.get_text.return_value = "Test content"
        mock_doc.load_page.return_value = mock_page
        
        mock_fitz.return_value.__enter__.return_value = mock_doc
        
        parser = PDFParser()
        text, metadata = parser._parse_with_pymupdf(Path("test.pdf"))
        
        assert text == "Test content"
        assert metadata["title"] == "Test PDF"
        assert metadata["author"] == "Test Author"
    
    def test_extract_metadata_from_text(self):
        """Test metadata extraction from text."""
        parser = PDFParser()
        
        text = """
        Title: Test Paper
        Authors: John Doe, Jane Smith
        Abstract: This is a test abstract about consciousness.
        Keywords: consciousness, test, psychology
        
        Introduction: This paper discusses...
        """
        
        metadata = {}
        enhanced = parser._extract_metadata_from_text(text, metadata)
        
        assert "title" in enhanced
        assert "authors" in enhanced
        assert "abstract" in enhanced
        assert "keywords" in enhanced


class TestYouTubeIngestor:
    """Tests for YouTube ingestor."""
    
    def test_init(self):
        """Test YouTubeIngestor initialization."""
        ingestor = YouTubeIngestor(
            output_dir="test_output",
            whisper_model="tiny",
            download_audio=False,
        )
        assert ingestor.output_dir == Path("test_output")
        assert ingestor.whisper_model == "tiny"
        assert ingestor.download_audio == False
    
    @patch("ingestion.video_ingestion.YoutubeDL")
    def test_get_video_metadata(self, mock_ydl):
        """Test getting video metadata."""
        mock_ydl_instance = MagicMock()
        mock_ydl_instance.extract_info.return_value = {
            "id": "test123",
            "title": "Test Video",
            "description": "Test description",
            "uploader": "Test Channel",
        }
        mock_ydl.return_value.__enter__.return_value = mock_ydl_instance
        
        ingestor = YouTubeIngestor()
        metadata = ingestor._get_video_metadata("https://youtube.com/watch?v=test123")
        
        assert metadata["id"] == "test123"
        assert metadata["title"] == "Test Video"
        assert metadata["uploader"] == "Test Channel"
    
    @patch("ingestion.video_ingestion.whisper.load_model")
    def test_transcribe_audio(self, mock_load_model):
        """Test audio transcription."""
        # Mock Whisper model
        mock_model = MagicMock()
        mock_model.transcribe.return_value = {
            "text": "Test transcription",
            "language": "en",
            "segments": [
                {"start": 0, "end": 5, "text": "Test transcription"}
            ],
        }
        mock_load_model.return_value = mock_model
        
        ingestor = YouTubeIngestor()
        ingestor.whisper = mock_model
        
        with tempfile.NamedTemporaryFile(suffix=".mp3") as temp_file:
            temp_path = Path(temp_file.name)
            transcription = ingestor._transcribe_audio(temp_path)
            
            assert transcription["text"] == "Test transcription"
            assert transcription["language"] == "en"
            assert len(transcription["segments"]) == 1


class TestAudioTranscriber:
    """Tests for audio transcriber."""
    
    def test_init(self):
        """Test AudioTranscriber initialization."""
        transcriber = AudioTranscriber(
            output_dir="test_output",
            whisper_model="tiny",
        )
        assert transcriber.output_dir == Path("test_output")
        assert transcriber.whisper_model == "tiny"
    
    def test_unsupported_file_format(self):
        """Test handling of unsupported file formats."""
        transcriber = AudioTranscriber()
        
        with tempfile.NamedTemporaryFile(suffix=".txt") as temp_file:
            with pytest.raises(ValueError, match="Unsupported file format"):
                transcriber.transcribe_file(temp_file.name)
    
    @patch("ingestion.audio_transcriber.whisper.load_model")
    def test_transcribe_file(self, mock_load_model):
        """Test audio file transcription."""
        # Mock Whisper model
        mock_model = MagicMock()
        mock_model.transcribe.return_value = {
            "text": "Test audio transcription",
            "language": "en",
            "segments": [
                {"start": 0, "end": 10, "text": "Test audio transcription"}
            ],
        }
        mock_load_model.return_value = mock_model
        
        transcriber = AudioTranscriber()
        
        with tempfile.NamedTemporaryFile(suffix=".mp3") as temp_file:
            # Write some dummy content
            temp_file.write(b"dummy audio data")
            temp_file.flush()
            
            result = transcriber.transcribe_file(temp_file.name)
            
            assert result["transcription"]["text"] == "Test audio transcription"
            assert result["transcription"]["language"] == "en"
            assert "whisper_model" in result


class TestWebScraper:
    """Tests for web scraper."""
    
    def test_init(self):
        """Test WebScraper initialization."""
        scraper = WebScraper(
            output_dir="test_output",
            timeout=5,
            language="es",
        )
        assert scraper.output_dir == Path("test_output")
        assert scraper.timeout == 5
        assert scraper.language == "es"
    
    def test_is_valid_url(self):
        """Test URL validation."""
        scraper = WebScraper()
        
        assert scraper._is_valid_url("https://example.com") == True
        assert scraper._is_valid_url("http://example.com/path") == True
        assert scraper._is_valid_url("not-a-url") == False
        assert scraper._is_valid_url("") == False
    
    def test_extract_publication_date(self):
        """Test publication date extraction."""
        scraper = WebScraper()
        
        # Mock article
        mock_article = MagicMock()
        mock_article.publish_date = None
        mock_article.text = "Published on January 15, 2023"
        
        url = "https://example.com/2023/01/15/test-article"
        date = scraper._extract_publication_date(mock_article, url)
        
        # Should extract date from URL
        assert date is not None
    
    def test_clean_text(self):
        """Test text cleaning."""
        scraper = WebScraper()
        
        dirty_text = """
        Line 1
        
        
        Line 2    with   extra   spaces
        
        Line 3
        """
        
        clean_text = scraper._clean_text(dirty_text)
        
        # Should remove excessive whitespace
        lines = clean_text.split("\n")
        assert len(lines) == 3
        assert "  " not in clean_text  # No double spaces


class TestIntegration:
    """Integration tests for ingestion pipeline."""
    
    def test_end_to_end_pdf_processing(self, tmp_path):
        """Test end-to-end PDF processing."""
        # Create a dummy PDF file
        pdf_content = b"%PDF-1.4\ntest pdf content"
        pdf_file = tmp_path / "test.pdf"
        pdf_file.write_bytes(pdf_content)
        
        # Create output directory
        output_dir = tmp_path / "output"
        
        # Parse PDF (will fail on actual parsing but should handle gracefully)
        parser = PDFParser(output_dir=output_dir)
        
        # This should raise an error since it's not a valid PDF
        # but we're testing the integration flow
        with pytest.raises(Exception):
            parser.parse_file(pdf_file)
    
    def test_data_directory_structure(self):
        """Test that data directories exist."""
        assert Path("data").exists()
        assert Path("data/sources").exists()
        assert Path("data/processed").exists()
        assert Path("data/graph").exists()
    
    def test_save_json_output(self, tmp_path):
        """Test JSON output saving."""
        output_dir = tmp_path / "output"
        output_dir.mkdir()
        
        test_data = {
            "test": "data",
            "number": 123,
            "list": [1, 2, 3],
        }
        
        output_file = output_dir / "test.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(test_data, f, indent=2)
        
        assert output_file.exists()
        
        # Verify it can be loaded back
        with open(output_file, "r", encoding="utf-8") as f:
            loaded_data = json.load(f)
        
        assert loaded_data == test_data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])