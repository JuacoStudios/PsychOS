"""
Video Ingestion for PsycheOS.

Downloads and transcribes YouTube videos using yt-dlp for metadata
and OpenAI Whisper for transcription.
"""

import json
import logging
import subprocess
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Union

try:
    import whisper  # type: ignore
except Exception:  # pragma: no cover
    class _WhisperPlaceholder:
        @staticmethod
        def load_model(*_args, **_kwargs):
            raise ImportError(
                "Missing optional dependency: openai-whisper (and its runtime deps)"
            )

    whisper = _WhisperPlaceholder()  # type: ignore

try:
    from yt_dlp import YoutubeDL  # type: ignore
except Exception:  # pragma: no cover
    class YoutubeDL:  # type: ignore
        def __init__(self, *_args, **_kwargs):
            raise ImportError("Missing optional dependency: yt-dlp")

logger = logging.getLogger(__name__)


class YouTubeIngestor:
    """Ingestor for YouTube videos."""

    def __init__(
        self,
        output_dir: Union[str, Path] = "data/processed",
        whisper_model: str = "base",
        download_audio: bool = True,
    ):
        """
        Initialize YouTube ingestor.

        Args:
            output_dir: Directory to save extracted JSON files
            whisper_model: Whisper model size (tiny, base, small, medium, large)
            download_audio: Whether to download audio for transcription
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.whisper_model = whisper_model
        self.download_audio = download_audio
        self.whisper = None  # Lazy load

    def ingest_video(self, url: str) -> Dict:
        """
        Ingest a single YouTube video.

        Args:
            url: YouTube video URL

        Returns:
            Dictionary containing video metadata and transcription

        Raises:
            ValueError: If video cannot be downloaded or transcribed
        """
        logger.info(f"Ingesting YouTube video: {url}")

        # Get video metadata
        metadata = self._get_video_metadata(url)
        if not metadata:
            raise ValueError(f"Could not retrieve metadata for: {url}")

        video_id = metadata.get("id", "unknown")
        logger.info(f"Video ID: {video_id}, Title: {metadata.get('title', 'Unknown')}")

        # Download audio if requested
        transcription = None
        if self.download_audio:
            try:
                audio_path = self._download_audio(url, video_id)
                transcription = self._transcribe_audio(audio_path)
            except Exception as e:
                logger.error(f"Failed to transcribe audio for {video_id}: {e}")
                # Continue without transcription

        # Create output structure
        result = {
            "source_type": "youtube",
            "source_url": url,
            "video_id": video_id,
            "ingestion_date": datetime.now().isoformat(),
            "metadata": metadata,
            "transcription": transcription,
        }

        # Save to JSON file
        output_file = self.output_dir / f"{video_id}_youtube.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)

        logger.info(f"Saved video data to: {output_file}")
        return result

    def ingest_playlist(self, playlist_url: str, max_videos: int = 10) -> List[Dict]:
        """
        Ingest videos from a YouTube playlist.

        Args:
            playlist_url: YouTube playlist URL
            max_videos: Maximum number of videos to ingest

        Returns:
            List of ingested video data dictionaries
        """
        logger.info(f"Ingesting playlist: {playlist_url}")

        # Get playlist video URLs
        video_urls = self._get_playlist_videos(playlist_url, max_videos)
        if not video_urls:
            logger.warning(f"No videos found in playlist: {playlist_url}")
            return []

        logger.info(f"Found {len(video_urls)} videos in playlist")

        results = []
        for i, url in enumerate(video_urls, 1):
            logger.info(f"Processing video {i}/{len(video_urls)}: {url}")
            try:
                result = self.ingest_video(url)
                results.append(result)
            except Exception as e:
                logger.error(f"Failed to ingest video {url}: {e}")
                continue

        return results

    def _get_video_metadata(self, url: str) -> Optional[Dict]:
        """Extract metadata from YouTube video."""
        ydl_opts = {
            "quiet": True,
            "no_warnings": True,
            "extract_flat": False,
            "force_generic_extractor": False,
        }

        try:
            with YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)

                if info is None:
                    logger.error(f"Could not extract info for: {url}")
                    return None

                # Extract relevant metadata
                metadata = {
                    "id": info.get("id"),
                    "title": info.get("title"),
                    "description": info.get("description"),
                    "upload_date": info.get("upload_date"),
                    "uploader": info.get("uploader"),
                    "uploader_id": info.get("uploader_id"),
                    "channel": info.get("channel"),
                    "channel_id": info.get("channel_id"),
                    "duration": info.get("duration"),
                    "view_count": info.get("view_count"),
                    "like_count": info.get("like_count"),
                    "comment_count": info.get("comment_count"),
                    "categories": info.get("categories"),
                    "tags": info.get("tags"),
                    "webpage_url": info.get("webpage_url"),
                    "thumbnail": info.get("thumbnail"),
                    "resolution": info.get("resolution"),
                    "extractor": info.get("extractor"),
                    "extractor_key": info.get("extractor_key"),
                }

                # Clean up empty values
                metadata = {k: v for k, v in metadata.items() if v not in (None, "", [])}

                return metadata

        except Exception as e:
            logger.error(f"Error getting metadata for {url}: {e}")
            return None

    def _download_audio(self, url: str, video_id: str) -> Path:
        """Download audio from YouTube video."""
        with tempfile.TemporaryDirectory() as temp_dir:
            ydl_opts = {
                "format": "bestaudio/best",
                "outtmpl": f"{temp_dir}/%(id)s.%(ext)s",
                "quiet": True,
                "no_warnings": True,
                "postprocessors": [
                    {
                        "key": "FFmpegExtractAudio",
                        "preferredcodec": "mp3",
                        "preferredquality": "192",
                    }
                ],
            }

            try:
                with YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])

                # Find the downloaded file
                audio_file = Path(temp_dir) / f"{video_id}.mp3"
                if not audio_file.exists():
                    # Try to find any audio file
                    audio_files = list(Path(temp_dir).glob("*.mp3"))
                    if audio_files:
                        audio_file = audio_files[0]
                    else:
                        raise FileNotFoundError(f"No audio file found for {video_id}")

                return audio_file

            except Exception as e:
                logger.error(f"Error downloading audio for {video_id}: {e}")
                raise

    def _transcribe_audio(self, audio_path: Path) -> Optional[Dict]:
        """Transcribe audio using Whisper."""
        if self.whisper is None:
            logger.info(f"Loading Whisper model: {self.whisper_model}")
            try:
                self.whisper = whisper.load_model(self.whisper_model)
            except Exception as e:
                logger.error(f"Failed to load Whisper model: {e}")
                return None

        try:
            logger.info(f"Transcribing audio: {audio_path.name}")
            result = self.whisper.transcribe(str(audio_path))

            # Format transcription with timestamps
            transcription = {
                "text": result.get("text", ""),
                "language": result.get("language", "unknown"),
                "segments": [],
            }

            for segment in result.get("segments", []):
                transcription["segments"].append({
                    "start": segment.get("start"),
                    "end": segment.get("end"),
                    "text": segment.get("text", ""),
                })

            return transcription

        except Exception as e:
            logger.error(f"Error transcribing audio {audio_path}: {e}")
            return None

    def _get_playlist_videos(self, playlist_url: str, max_videos: int) -> List[str]:
        """Get video URLs from a playlist."""
        ydl_opts = {
            "quiet": True,
            "no_warnings": True,
            "extract_flat": True,
            "playlistend": max_videos,
        }

        try:
            with YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(playlist_url, download=False)

                if info is None:
                    logger.error(f"Could not extract playlist info: {playlist_url}")
                    return []

                videos = []
                for entry in info.get("entries", []):
                    if entry and entry.get("url"):
                        videos.append(entry["url"])

                return videos[:max_videos]

        except Exception as e:
            logger.error(f"Error getting playlist videos: {e}")
            return []


def main():
    """Command-line interface for YouTube ingestion."""
    import argparse
    import sys

    parser = argparse.ArgumentParser(description="Ingest YouTube videos for PsycheOS")
    parser.add_argument(
        "--url", required=True, help="YouTube video URL or playlist URL"
    )
    parser.add_argument(
        "--output", default="data/processed", help="Output directory for JSON files"
    )
    parser.add_argument(
        "--model",
        default="base",
        choices=["tiny", "base", "small", "medium", "large"],
        help="Whisper model size",
    )
    parser.add_argument(
        "--no-audio",
        action="store_true",
        help="Skip audio download and transcription",
    )
    parser.add_argument(
        "--max-videos",
        type=int,
        default=10,
        help="Maximum number of videos for playlist ingestion",
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

    ingestor = YouTubeIngestor(
        output_dir=args.output,
        whisper_model=args.model,
        download_audio=not args.no_audio,
    )

    try:
        # Check if it's a playlist
        if "playlist" in args.url.lower() or "list=" in args.url.lower():
            results = ingestor.ingest_playlist(args.url, args.max_videos)
            print(f"Successfully ingested {len(results)} videos from playlist")
            for result in results:
                video_id = result.get("video_id", "unknown")
                title = result.get("metadata", {}).get("title", "Unknown")
                print(f"  - {video_id}: {title}")
        else:
            result = ingestor.ingest_video(args.url)
            video_id = result.get("video_id", "unknown")
            title = result.get("metadata", {}).get("title", "Unknown")
            print(f"Successfully ingested video: {title}")
            print(f"Video ID: {video_id}")
            print(f"Saved to: data/processed/{video_id}_youtube.json")

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()