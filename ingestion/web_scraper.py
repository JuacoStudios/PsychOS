"""
Web Scraper for PsycheOS.

Scrapes web articles, blog posts, and academic pages using newspaper3k.
Extracts main content, title, author, publication date, and other metadata.
"""

import json
import logging
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Union
from urllib.parse import urlparse

try:
    import newspaper  # type: ignore
    from newspaper import Article, Config  # type: ignore
except Exception:  # pragma: no cover
    class _NewspaperPlaceholder:
        class ArticleException(Exception):
            pass

    newspaper = _NewspaperPlaceholder()  # type: ignore

    class Config:  # type: ignore
        def __init__(self):
            pass

    class Article:  # type: ignore
        def __init__(self, *_args, **_kwargs):
            raise ImportError("Missing optional dependency: newspaper3k")

try:
    import requests  # type: ignore
except Exception:  # pragma: no cover
    class _RequestsPlaceholder:
        class RequestException(Exception):
            pass

    requests = _RequestsPlaceholder()  # type: ignore

logger = logging.getLogger(__name__)


class WebScraper:
    """Scraper for web articles and academic content."""

    def __init__(
        self,
        output_dir: Union[str, Path] = "data/processed",
        timeout: int = 10,
        language: str = "en",
    ):
        """
        Initialize web scraper.

        Args:
            output_dir: Directory to save extracted JSON files
            timeout: Request timeout in seconds
            language: Language for article parsing
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.timeout = timeout
        self.language = language

        # Configure newspaper3k
        self.config = Config()
        self.config.browser_user_agent = (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        )
        self.config.request_timeout = timeout
        self.config.memoize_articles = False

    def scrape_url(self, url: str) -> Optional[Dict]:
        """
        Scrape a single URL.

        Args:
            url: URL to scrape

        Returns:
            Dictionary containing extracted content and metadata, or None if failed

        Raises:
            ValueError: If URL is invalid or scraping fails
        """
        if not self._is_valid_url(url):
            raise ValueError(f"Invalid URL: {url}")

        logger.info(f"Scraping URL: {url}")

        try:
            # Create article object
            article = Article(url, config=self.config)
            article.download()
            article.parse()

            # Try to extract additional metadata
            article.nlp()  # This extracts keywords and summary

            # Get publication date if available
            publish_date = self._extract_publication_date(article, url)

            # Extract domain from URL
            domain = urlparse(url).netloc

            # Create metadata structure
            metadata = {
                "title": article.title,
                "authors": article.authors,
                "publish_date": publish_date,
                "source_url": url,
                "domain": domain,
                "language": self.language,
                "extraction_date": datetime.now().isoformat(),
                "keywords": article.keywords,
                "summary": article.summary,
                "meta_keywords": article.meta_keywords,
                "meta_description": article.meta_description,
                "meta_lang": article.meta_lang,
                "meta_favicon": article.meta_favicon,
                "meta_site_name": article.meta_site_name,
                "canonical_link": article.canonical_link,
            }

            # Clean text (remove excessive whitespace)
            clean_text = self._clean_text(article.text)

            # Create output structure
            result = {
                "source_type": "web",
                "source_url": url,
                "extraction_date": datetime.now().isoformat(),
                "metadata": metadata,
                "content": {
                    "text": clean_text,
                    "html": article.html if hasattr(article, "html") else None,
                    "images": list(article.images) if article.images else [],
                    "videos": list(article.movies) if hasattr(article, "movies") else [],
                },
                "stats": {
                    "text_length": len(clean_text),
                    "word_count": len(clean_text.split()),
                    "image_count": len(article.images) if article.images else 0,
                    "keyword_count": len(article.keywords),
                },
            }

            # Save to JSON file
            # Create filename from URL (replace special characters)
            url_hash = hash(url) % 1000000  # Simple hash for filename
            output_file = self.output_dir / f"web_{url_hash}_{datetime.now().strftime('%Y%m%d')}.json"
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(result, f, indent=2, ensure_ascii=False)

            logger.info(f"Saved scraped data to: {output_file}")
            logger.info(f"Extracted {len(clean_text)} characters from {url}")

            return result

        except newspaper.ArticleException as e:
            logger.error(f"Article parsing failed for {url}: {e}")
            raise ValueError(f"Could not parse article: {e}") from e
        except requests.RequestException as e:
            logger.error(f"Network error for {url}: {e}")
            raise ValueError(f"Network error: {e}") from e
        except Exception as e:
            logger.error(f"Unexpected error scraping {url}: {e}")
            raise ValueError(f"Scraping failed: {e}") from e

    def scrape_urls(self, urls: List[str], max_urls: Optional[int] = None) -> List[Dict]:
        """
        Scrape multiple URLs.

        Args:
            urls: List of URLs to scrape
            max_urls: Maximum number of URLs to scrape

        Returns:
            List of scraped data dictionaries
        """
        if max_urls:
            urls = urls[:max_urls]

        logger.info(f"Scraping {len(urls)} URLs")

        results = []
        for i, url in enumerate(urls, 1):
            logger.info(f"Processing URL {i}/{len(urls)}: {url}")
            try:
                result = self.scrape_url(url)
                if result:
                    results.append(result)
            except Exception as e:
                logger.error(f"Failed to scrape {url}: {e}")
                continue

        return results

    def scrape_from_file(self, file_path: Union[str, Path]) -> List[Dict]:
        """
        Scrape URLs from a text file (one URL per line).

        Args:
            file_path: Path to text file containing URLs

        Returns:
            List of scraped data dictionaries
        """
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        with open(file_path, "r", encoding="utf-8") as f:
            urls = [line.strip() for line in f if line.strip()]

        logger.info(f"Loaded {len(urls)} URLs from {file_path}")
        return self.scrape_urls(urls)

    def _is_valid_url(self, url: str) -> bool:
        """Check if URL is valid."""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except Exception:
            return False

    def _extract_publication_date(self, article: Article, url: str) -> Optional[str]:
        """Extract publication date from article or URL."""
        # First try article's publish_date
        if article.publish_date:
            if isinstance(article.publish_date, datetime):
                return article.publish_date.isoformat()
            return str(article.publish_date)

        # Try to extract date from URL (common pattern for blogs/news)
        date_patterns = [
            r"/(\d{4})/(\d{2})/(\d{2})/",  # /2023/12/25/
            r"/(\d{4})-(\d{2})-(\d{2})/",  # /2023-12-25/
            r"(\d{4})(\d{2})(\d{2})",      # 20231225
        ]

        for pattern in date_patterns:
            match = re.search(pattern, url)
            if match:
                if len(match.groups()) == 3:
                    year, month, day = match.groups()
                    try:
                        date_obj = datetime(int(year), int(month), int(day))
                        return date_obj.isoformat()
                    except ValueError:
                        continue

        # Try to find date in text
        text = article.text[:5000]  # Search first 5000 characters
        date_patterns_text = [
            r"\b(\d{1,2})\s+(January|February|March|April|May|June|July|"
            r"August|September|October|November|December)\s+(\d{4})\b",
            r"\b(January|February|March|April|May|June|July|August|"
            r"September|October|November|December)\s+(\d{1,2}),?\s+(\d{4})\b",
            r"\b(\d{4})-\d{2}-\d{2}\b",  # ISO format in text
            r"\b\d{1,2}/\d{1,2}/(\d{4})\b",  # MM/DD/YYYY or DD/MM/YYYY
        ]

        for pattern in date_patterns_text:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                # Return the matched string (parsing dates from text is complex)
                return match.group(0)

        return None

    def _clean_text(self, text: str) -> str:
        """Clean extracted text."""
        if not text:
            return ""

        # Remove excessive whitespace
        lines = text.split("\n")
        cleaned_lines = []
        for line in lines:
            line = line.strip()
            if line:  # Keep non-empty lines
                # Collapse multiple spaces
                line = re.sub(r"\s+", " ", line)
                cleaned_lines.append(line)

        return "\n".join(cleaned_lines)


def main():
    """Command-line interface for web scraper."""
    import argparse
    import sys

    parser = argparse.ArgumentParser(description="Scrape web articles for PsycheOS")
    parser.add_argument(
        "--url", help="Single URL to scrape (or use --file for multiple)"
    )
    parser.add_argument(
        "--file", help="Text file containing URLs (one per line)"
    )
    parser.add_argument(
        "--output", default="data/processed", help="Output directory for JSON files"
    )
    parser.add_argument(
        "--timeout", type=int, default=10, help="Request timeout in seconds"
    )
    parser.add_argument(
        "--language", default="en", help="Language for article parsing"
    )
    parser.add_argument(
        "--max-urls", type=int, help="Maximum number of URLs to scrape"
    )
    parser.add_argument(
        "--verbose", action="store_true", help="Enable verbose logging"
    )

    args = parser.parse_args()

    # Validate arguments
    if not args.url and not args.file:
        parser.error("Either --url or --file must be specified")

    # Setup logging
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    scraper = WebScraper(
        output_dir=args.output,
        timeout=args.timeout,
        language=args.language,
    )

    try:
        if args.url:
            result = scraper.scrape_url(args.url)
            print(f"Successfully scraped: {args.url}")
            print(f"Title: {result['metadata'].get('title', 'Unknown')}")
            print(f"Text length: {result['stats']['text_length']} characters")
            url_hash = hash(args.url) % 1000000
            print(f"Saved to: data/processed/web_{url_hash}_*.json")
        elif args.file:
            results = scraper.scrape_from_file(args.file)
            print(f"Successfully scraped {len(results)} URLs from {args.file}")
            for result in results:
                url = result['source_url']
                title = result['metadata'].get('title', 'Unknown')[:50]
                text_len = result['stats']['text_length']
                print(f"  - {title}... ({text_len} chars)")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()