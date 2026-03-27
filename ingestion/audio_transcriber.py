"""
Audio Transcriber for PsycheOS.

Transcribes local audio files using OpenAI Whisper.
Supports various audio formats: mp3, wav, m4a, flac, etc.
"""

import json
import logging
import mimetypes
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

logger = logging.getLogger(__name__)

# Supported audio file extensions
SUPPORTED_EXTENSIONS = {
    ".mp3", ".wav", ".m4a", ".flac", ".ogg", ".aac", ".wma", ".opus",
    ".mp4", ".m4b", ".m4p", ".m4r", ".3gp", ".3g2", ".amr",
}


class AudioTranscriber:
    """Transcriber for local audio files."""

    def __init__(
        self,
        output_dir: Union[str, Path] = "data/processed",
        whisper_model: str = "base",
    ):
        """
        Initialize audio transcriber.

        Args:
            output_dir: Directory to save transcription JSON files
            whisper_model: Whisper model size (tiny, base, small, medium, large)
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.whisper_model = whisper_model
        self.whisper = None  # Lazy load

    def transcribe_file(self, audio_path: Union[str, Path]) -> Dict:
        """
        Transcribe a single audio file.

        Args:
            audio_path: Path to audio file

        Returns:
            Dictionary containing transcription and metadata

        Raises:
            FileNotFoundError: If audio file doesn't exist
            ValueError: If file format is not supported or transcription fails
        """
        audio_path = Path(audio_path)
        if not audio_path.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        # Check file extension
        if audio_path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            # Try to determine MIME type as fallback
            mime_type, _ = mimetypes.guess_type(str(audio_path))
            if not mime_type or not mime_type.startswith("audio/"):
                raise ValueError(
                    f"Unsupported file format: {audio_path.suffix}. "
                    f"Supported formats: {', '.join(sorted(SUPPORTED_EXTENSIONS))}"
                )

        logger.info(f"Transcribing audio file: {audio_path.name}")

        # Load Whisper model if not already loaded
        if self.whisper is None:
            logger.info(f"Loading Whisper model: {self.whisper_model}")
            try:
                self.whisper = whisper.load_model(self.whisper_model)
            except Exception as e:
                logger.error(f"Failed to load Whisper model: {e}")
                raise ValueError(f"Could not load Whisper model: {e}") from e

        # Get file metadata
        file_stats = audio_path.stat()
        file_metadata = {
            "file_name": audio_path.name,
            "file_size": file_stats.st_size,
            "file_extension": audio_path.suffix.lower(),
            "created_time": datetime.fromtimestamp(file_stats.st_ctime).isoformat(),
            "modified_time": datetime.fromtimestamp(file_stats.st_mtime).isoformat(),
        }

        # Transcribe audio
        try:
            logger.info(f"Starting transcription of {audio_path.name}")
            result = self.whisper.transcribe(str(audio_path))

            # Format transcription
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

            # Create output structure
            output = {
                "source_type": "audio",
                "source_path": str(audio_path),
                "transcription_date": datetime.now().isoformat(),
                "file_metadata": file_metadata,
                "transcription": transcription,
                "whisper_model": self.whisper_model,
            }

            # Save to JSON file
            output_file = self.output_dir / f"{audio_path.stem}_audio.json"
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(output, f, indent=2, ensure_ascii=False)

            logger.info(f"Saved transcription to: {output_file}")

            # Log transcription stats
            text_length = len(transcription["text"])
            num_segments = len(transcription["segments"])
            logger.info(
                f"Transcription complete: {text_length} characters, "
                f"{num_segments} segments, language: {transcription['language']}"
            )

            return output

        except Exception as e:
            logger.error(f"Error transcribing audio file {audio_path}: {e}")
            raise ValueError(f"Transcription failed: {e}") from e

    def transcribe_directory(self, directory: Union[str, Path]) -> List[Dict]:
        """
        Transcribe all audio files in a directory.

        Args:
            directory: Directory containing audio files

        Returns:
            List of transcription dictionaries
        """
        directory = Path(directory)
        if not directory.exists():
            raise FileNotFoundError(f"Directory not found: {directory}")

        # Find all supported audio files
        audio_files = []
        for ext in SUPPORTED_EXTENSIONS:
            audio_files.extend(directory.glob(f"*{ext}"))
            audio_files.extend(directory.glob(f"*{ext.upper()}"))

        logger.info(f"Found {len(audio_files)} audio files in {directory}")

        results = []
        for audio_file in audio_files:
            try:
                result = self.transcribe_file(audio_file)
                results.append(result)
            except Exception as e:
                logger.error(f"Failed to transcribe {audio_file.name}: {e}")
                continue

        return results

    def batch_transcribe(
        self, file_paths: List[Union[str, Path]], max_files: Optional[int] = None
    ) -> List[Dict]:
        """
        Transcribe multiple audio files from a list of paths.

        Args:
            file_paths: List of paths to audio files
            max_files: Maximum number of files to transcribe

        Returns:
            List of transcription dictionaries
        """
        if max_files:
            file_paths = file_paths[:max_files]

        logger.info(f"Batch transcribing {len(file_paths)} audio files")

        results = []
        for i, file_path in enumerate(file_paths, 1):
            logger.info(f"Processing file {i}/{len(file_paths)}: {Path(file_path).name}")
            try:
                result = self.transcribe_file(file_path)
                results.append(result)
            except Exception as e:
                logger.error(f"Failed to transcribe {file_path}: {e}")
                continue

        return results


def main():
    """Command-line interface for audio transcription."""
    import argparse
    import sys

    parser = argparse.ArgumentParser(description="Transcribe audio files for PsycheOS")
    parser.add_argument(
        "--path", required=True, help="Path to audio file or directory"
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
        "--max-files",
        type=int,
        help="Maximum number of files to transcribe (for directory/batch mode)",
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

    transcriber = AudioTranscriber(output_dir=args.output, whisper_model=args.model)
    path = Path(args.path)

    try:
        if path.is_file():
            result = transcriber.transcribe_file(path)
            print(f"Successfully transcribed: {path.name}")
            print(f"Language: {result['transcription']['language']}")
            print(f"Text length: {len(result['transcription']['text'])} characters")
            print(f"Saved to: data/processed/{path.stem}_audio.json")
        elif path.is_dir():
            results = transcriber.transcribe_directory(path)
            print(f"Successfully transcribed {len(results)} audio files")
            for result in results:
                file_name = Path(result['source_path']).name
                lang = result['transcription']['language']
                text_len = len(result['transcription']['text'])
                print(f"  - {file_name}: {lang}, {text_len} chars")
        else:
            print(f"Error: {args.path} is not a file or directory")
            sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()