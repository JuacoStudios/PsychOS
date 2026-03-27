"""
PDF Parser for PsycheOS.

Extracts text and metadata from PDF files, primarily academic papers.
Uses pymupdf (fitz) as primary parser with pdfplumber as fallback.
"""

import json
import logging
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Union

try:
    import pdfplumber  # type: ignore
except Exception:  # pragma: no cover
    class _PDFPlumberPlaceholder:
        @staticmethod
        def open(*_args, **_kwargs):
            raise ImportError("Missing optional dependency: pdfplumber")

    pdfplumber = _PDFPlumberPlaceholder()  # type: ignore

try:
    import pymupdf  # type: ignore
except Exception:  # pragma: no cover
    class _PyMuPDFPlaceholder:
        @staticmethod
        def open(*_args, **_kwargs):
            raise ImportError("Missing optional dependency: pymupdf")

    pymupdf = _PyMuPDFPlaceholder()  # type: ignore

logger = logging.getLogger(__name__)


class PDFParser:
    """Parser for extracting text and metadata from PDF files."""

    def __init__(self, output_dir: Union[str, Path] = "data/processed"):
        """
        Initialize PDF parser.

        Args:
            output_dir: Directory to save extracted JSON files
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def parse_file(self, pdf_path: Union[str, Path]) -> Dict:
        """
        Parse a single PDF file.

        Args:
            pdf_path: Path to PDF file

        Returns:
            Dictionary containing extracted text and metadata

        Raises:
            FileNotFoundError: If PDF file doesn't exist
            ValueError: If PDF cannot be parsed
        """
        pdf_path = Path(pdf_path)
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")

        logger.info(f"Parsing PDF: {pdf_path.name}")

        # Try pymupdf first (faster, better for text extraction)
        try:
            text, metadata = self._parse_with_pymupdf(pdf_path)
        except Exception as e:
            logger.warning(f"pymupdf failed for {pdf_path.name}: {e}")
            # Fall back to pdfplumber
            try:
                text, metadata = self._parse_with_pdfplumber(pdf_path)
            except Exception as e2:
                logger.error(f"Both parsers failed for {pdf_path.name}: {e2}")
                raise ValueError(f"Could not parse PDF: {pdf_path.name}") from e2

        # Extract additional metadata from text
        enhanced_metadata = self._extract_metadata_from_text(text, metadata)

        # Create output structure
        result = {
            "source_type": "pdf",
            "source_path": str(pdf_path),
            "file_name": pdf_path.name,
            "file_size": pdf_path.stat().st_size,
            "extraction_date": datetime.now().isoformat(),
            "text": text,
            "metadata": enhanced_metadata,
        }

        # Save to JSON file
        output_file = self.output_dir / f"{pdf_path.stem}_pdf.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)

        logger.info(f"Saved extracted data to: {output_file}")
        return result

    def parse_directory(self, directory: Union[str, Path]) -> List[Dict]:
        """
        Parse all PDF files in a directory.

        Args:
            directory: Directory containing PDF files

        Returns:
            List of extracted data dictionaries
        """
        directory = Path(directory)
        if not directory.exists():
            raise FileNotFoundError(f"Directory not found: {directory}")

        pdf_files = list(directory.glob("*.pdf"))
        logger.info(f"Found {len(pdf_files)} PDF files in {directory}")

        results = []
        for pdf_file in pdf_files:
            try:
                result = self.parse_file(pdf_file)
                results.append(result)
            except Exception as e:
                logger.error(f"Failed to parse {pdf_file.name}: {e}")
                continue

        return results

    def _parse_with_pymupdf(self, pdf_path: Path) -> tuple[str, Dict]:
        """Parse PDF using pymupdf (fitz)."""
        text_parts = []
        metadata = {}

        with pymupdf.open(pdf_path) as doc:
            # Extract metadata
            metadata = doc.metadata
            if metadata is None:
                metadata = {}

            # Extract text from each page
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                text = page.get_text()
                text_parts.append(text)

        full_text = "\n".join(text_parts)
        return full_text, metadata

    def _parse_with_pdfplumber(self, pdf_path: Path) -> tuple[str, Dict]:
        """Parse PDF using pdfplumber."""
        text_parts = []
        metadata = {}

        with pdfplumber.open(pdf_path) as pdf:
            # Extract metadata
            metadata = pdf.metadata if hasattr(pdf, "metadata") else {}

            # Extract text from each page
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    text_parts.append(text)

        full_text = "\n".join(text_parts)
        return full_text, metadata

    def _extract_metadata_from_text(self, text: str, existing_metadata: Dict) -> Dict:
        """
        Extract additional metadata from text content.

        Args:
            text: Extracted text from PDF
            existing_metadata: Metadata from PDF parser

        Returns:
            Enhanced metadata dictionary
        """
        enhanced = existing_metadata.copy()

        # Extract title (often first non-empty line)
        lines = text.strip().split("\n")
        for line in lines[:10]:  # Check first 10 lines
            line = line.strip()
            if line and len(line) > 10 and len(line) < 200:
                if "title" not in enhanced or not enhanced["title"]:
                    enhanced["title"] = line
                break

        # Extract authors (look for common patterns)
        author_patterns = [
            r"by\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*(?:\s+et al\.)?)",
            r"Authors?:\s*([^\n]+)",
            r"([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+and\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)",
        ]

        for pattern in author_patterns:
            matches = re.findall(pattern, text[:2000], re.IGNORECASE)
            if matches:
                if isinstance(matches[0], tuple):
                    authors = list(matches[0])
                else:
                    authors = matches
                enhanced["authors"] = authors
                break

        # Extract year (look for 4-digit years)
        year_match = re.search(r"\b(19|20)\d{2}\b", text[:1000])
        if year_match:
            enhanced["year"] = year_match.group()

        # Extract abstract (look for common abstract markers)
        abstract_markers = ["abstract", "summary", "a b s t r a c t"]
        text_lower = text.lower()

        for marker in abstract_markers:
            if marker in text_lower:
                start_idx = text_lower.find(marker)
                # Find end of abstract (often before "keywords" or "introduction")
                end_markers = ["keywords", "key words", "introduction", "1."]
                end_idx = len(text)

                for end_marker in end_markers:
                    if end_marker in text_lower[start_idx:]:
                        potential_end = text_lower.find(end_marker, start_idx)
                        if potential_end < end_idx:
                            end_idx = potential_end

                abstract = text[start_idx + len(marker) : end_idx].strip()
                if len(abstract) > 10 and len(abstract) < 2000:
                    enhanced["abstract"] = abstract
                    break

        # Extract keywords
        keyword_markers = ["keywords:", "key words:", "index terms:"]
        for marker in keyword_markers:
            if marker in text_lower:
                start_idx = text_lower.find(marker) + len(marker)
                # Keywords often end with a newline or punctuation
                end_idx = text.find("\n", start_idx)
                if end_idx == -1:
                    end_idx = start_idx + 200  # Limit length

                keywords_text = text[start_idx:end_idx].strip()
                # Split by commas, semicolons, or newlines
                keywords = [
                    k.strip()
                    for k in re.split(r"[,\n;]", keywords_text)
                    if k.strip()
                ]
                if keywords:
                    enhanced["keywords"] = keywords
                    break

        return enhanced


def main():
    """Command-line interface for PDF parser."""
    import argparse
    import sys

    parser = argparse.ArgumentParser(description="Parse PDF files for PsycheOS")
    parser.add_argument(
        "--path", required=True, help="Path to PDF file or directory"
    )
    parser.add_argument(
        "--output", default="data/processed", help="Output directory for JSON files"
    )
    parser.add_argument(
        "--verbose", action="store_true", help="Enable verbose logging"
    )

    args = parser.parse_args()

    # Setup logging
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    parser = PDFParser(output_dir=args.output)
    path = Path(args.path)

    try:
        if path.is_file() and path.suffix.lower() == ".pdf":
            result = parser.parse_file(path)
            print(f"Successfully parsed: {path.name}")
            print(f"Title: {result['metadata'].get('title', 'Unknown')}")
            print(f"Saved to: data/processed/{path.stem}_pdf.json")
        elif path.is_dir():
            results = parser.parse_directory(path)
            print(f"Successfully parsed {len(results)} PDF files")
        else:
            print(f"Error: {args.path} is not a PDF file or directory")
            sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()