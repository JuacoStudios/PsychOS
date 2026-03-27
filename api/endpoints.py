"""
API Endpoints for PsycheOS.

Defines REST endpoints for accessing and manipulating the consciousness knowledge graph.
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional

from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import JSONResponse

from ..graph.builder import KnowledgeGraphBuilder
from ..graph.visualizer import GraphVisualizer
from ..ingestion.audio_transcriber import AudioTranscriber
from ..ingestion.pdf_parser import PDFParser
from ..ingestion.video_ingestion import YouTubeIngestor
from ..ingestion.web_scraper import WebScraper
from ..models.consciousness import get_theory_examples
from ..models.evolution import get_evolutionary_hypotheses, get_evolutionary_layers
from ..models.mental_health import get_mental_health_examples

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/theories")
async def get_theories() -> Dict:
    """
    Get all consciousness theories.
    
    Returns:
        List of consciousness theories with metadata
    """
    theories = get_theory_examples()
    return {
        "count": len(theories),
        "theories": [theory.to_dict() for theory in theories],
    }


@router.get("/theories/{theory_name}")
async def get_theory(theory_name: str) -> Dict:
    """
    Get a specific consciousness theory by name.
    
    Args:
        theory_name: Name of the theory to retrieve
        
    Returns:
        Theory details
        
    Raises:
        HTTPException: If theory not found
    """
    theories = get_theory_examples()
    for theory in theories:
        if theory.name.lower() == theory_name.lower():
            return theory.to_dict()
    
    raise HTTPException(status_code=404, detail=f"Theory '{theory_name}' not found")


@router.get("/mental-health")
async def get_mental_health_concepts() -> Dict:
    """
    Get all mental health concepts.
    
    Returns:
        List of mental health concepts
    """
    concepts = get_mental_health_examples()
    return {
        "count": len(concepts),
        "concepts": [concept.to_dict() for concept in concepts],
    }


@router.get("/evolution/hypotheses")
async def get_evolution_hypotheses() -> Dict:
    """
    Get all evolutionary hypotheses.
    
    Returns:
        List of evolutionary hypotheses
    """
    hypotheses = get_evolutionary_hypotheses()
    return {
        "count": len(hypotheses),
        "hypotheses": [hypothesis.to_dict() for hypothesis in hypotheses],
    }


@router.get("/evolution/layers")
async def get_evolution_layers() -> Dict:
    """
    Get all evolutionary layers of consciousness.
    
    Returns:
        List of evolutionary layers
    """
    layers = get_evolutionary_layers()
    return {
        "count": len(layers),
        "layers": [layer.to_dict() for layer in layers],
    }


@router.get("/graph/stats")
async def get_graph_stats() -> Dict:
    """
    Get statistics about the knowledge graph.
    
    Returns:
        Graph statistics
    """
    try:
        # Check if graph exists
        graph_dir = Path("data/graph")
        graph_files = list(graph_dir.glob("*.graphml"))
        
        if not graph_files:
            return {
                "status": "no_graph",
                "message": "No graph found. Build graph first using /api/v1/graph/build",
            }
        
        # Load the most recent graph
        latest_graph = max(graph_files, key=lambda p: p.stat().st_mtime)
        visualizer = GraphVisualizer()
        visualizer.load_graph(latest_graph)
        
        stats = visualizer.get_statistics()
        return {
            "status": "success",
            "graph_file": str(latest_graph),
            "stats": stats,
        }
        
    except Exception as e:
        logger.error(f"Error getting graph stats: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting graph stats: {e}")


@router.post("/graph/build")
async def build_graph() -> Dict:
    """
    Build knowledge graph from processed data.
    
    Returns:
        Build status and graph information
    """
    try:
        builder = KnowledgeGraphBuilder()
        graph = builder.build_from_directory()
        
        # Save graph
        graphml_path, json_path = builder.save_graph()
        
        return {
            "status": "success",
            "message": "Graph built successfully",
            "nodes": graph.number_of_nodes(),
            "edges": graph.number_of_edges(),
            "graphml_file": str(graphml_path),
            "json_file": str(json_path),
        }
        
    except Exception as e:
        logger.error(f"Error building graph: {e}")
        raise HTTPException(status_code=500, detail=f"Error building graph: {e}")


@router.post("/ingest/pdf")
async def ingest_pdf(
    file: UploadFile = File(...),
    output_dir: Optional[str] = "data/processed",
) -> Dict:
    """
    Ingest a PDF file.
    
    Args:
        file: PDF file to ingest
        output_dir: Directory to save processed data
        
    Returns:
        Ingestion results
    """
    try:
        # Save uploaded file temporarily
        temp_path = Path("data/sources") / file.filename
        temp_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(temp_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        # Parse PDF
        parser = PDFParser(output_dir=output_dir)
        result = parser.parse_file(temp_path)
        
        return {
            "status": "success",
            "message": f"PDF ingested successfully: {file.filename}",
            "file": file.filename,
            "metadata": result["metadata"],
            "text_length": len(result["text"]),
            "output_file": f"{Path(file.filename).stem}_pdf.json",
        }
        
    except Exception as e:
        logger.error(f"Error ingesting PDF: {e}")
        raise HTTPException(status_code=500, detail=f"Error ingesting PDF: {e}")


@router.post("/ingest/video")
async def ingest_video(
    url: str,
    download_audio: bool = True,
    whisper_model: str = "base",
) -> Dict:
    """
    Ingest a YouTube video.
    
    Args:
        url: YouTube video URL
        download_audio: Whether to download and transcribe audio
        whisper_model: Whisper model to use for transcription
        
    Returns:
        Ingestion results
    """
    try:
        ingestor = YouTubeIngestor(
            download_audio=download_audio,
            whisper_model=whisper_model,
        )
        
        result = ingestor.ingest_video(url)
        
        return {
            "status": "success",
            "message": f"YouTube video ingested successfully",
            "video_id": result["video_id"],
            "title": result["metadata"].get("title", "Unknown"),
            "has_transcription": result["transcription"] is not None,
            "output_file": f"{result['video_id']}_youtube.json",
        }
        
    except Exception as e:
        logger.error(f"Error ingesting video: {e}")
        raise HTTPException(status_code=500, detail=f"Error ingesting video: {e}")


@router.post("/ingest/audio")
async def ingest_audio(
    file: UploadFile = File(...),
    whisper_model: str = "base",
) -> Dict:
    """
    Ingest an audio file.
    
    Args:
        file: Audio file to transcribe
        whisper_model: Whisper model to use for transcription
        
    Returns:
        Transcription results
    """
    try:
        # Save uploaded file temporarily
        temp_path = Path("data/sources") / file.filename
        temp_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(temp_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        # Transcribe audio
        transcriber = AudioTranscriber(whisper_model=whisper_model)
        result = transcriber.transcribe_file(temp_path)
        
        return {
            "status": "success",
            "message": f"Audio transcribed successfully: {file.filename}",
            "file": file.filename,
            "language": result["transcription"]["language"],
            "text_length": len(result["transcription"]["text"]),
            "output_file": f"{Path(file.filename).stem}_audio.json",
        }
        
    except Exception as e:
        logger.error(f"Error transcribing audio: {e}")
        raise HTTPException(status_code=500, detail=f"Error transcribing audio: {e}")


@router.post("/ingest/web")
async def ingest_web(
    url: str,
    timeout: int = 10,
) -> Dict:
    """
    Scrape a web article.
    
    Args:
        url: URL to scrape
        timeout: Request timeout in seconds
        
    Returns:
        Scraping results
    """
    try:
        scraper = WebScraper(timeout=timeout)
        result = scraper.scrape_url(url)
        
        if not result:
            raise HTTPException(status_code=400, detail=f"Could not scrape URL: {url}")
        
        return {
            "status": "success",
            "message": f"Web page scraped successfully",
            "url": url,
            "title": result["metadata"].get("title", "Unknown"),
            "text_length": result["stats"]["text_length"],
            "output_file": f"web_{hash(url) % 1000000}_*.json",
        }
        
    except Exception as e:
        logger.error(f"Error scraping web page: {e}")
        raise HTTPException(status_code=500, detail=f"Error scraping web page: {e}")


@router.get("/search")
async def search(
    query: str,
    max_results: int = 10,
) -> Dict:
    """
    Search the knowledge graph (basic implementation).
    
    Note: This is a basic search implementation. In production,
    you would use proper search engines or vector databases.
    
    Args:
        query: Search query
        max_results: Maximum number of results to return
        
    Returns:
        Search results
    """
    try:
        # Simple search across theories
        theories = get_theory_examples()
        results = []
        
        query_lower = query.lower()
        
        for theory in theories:
            # Simple keyword matching
            score = 0
            if query_lower in theory.name.lower():
                score += 3
            if query_lower in theory.description.lower():
                score += 2
            for claim in theory.core_claims:
                if query_lower in claim.lower():
                    score += 1
            
            if score > 0:
                results.append({
                    "type": "theory",
                    "name": theory.name,
                    "description": theory.description[:200] + "...",
                    "score": score,
                })
        
        # Sort by score and limit results
        results.sort(key=lambda x: x["score"], reverse=True)
        results = results[:max_results]
        
        return {
            "status": "success",
            "query": query,
            "count": len(results),
            "results": results,
        }
        
    except Exception as e:
        logger.error(f"Error searching: {e}")
        raise HTTPException(status_code=500, detail=f"Error searching: {e}")


@router.get("/data/processed")
async def list_processed_files() -> Dict:
    """
    List all processed data files.
    
    Returns:
        List of processed files with metadata
    """
    try:
        processed_dir = Path("data/processed")
        if not processed_dir.exists():
            return {
                "status": "no_data",
                "message": "No processed data found",
                "files": [],
            }
        
        files = []
        for file_path in processed_dir.glob("*.json"):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                
                files.append({
                    "filename": file_path.name,
                    "source_type": data.get("source_type", "unknown"),
                    "size": file_path.stat().st_size,
                    "modified": file_path.stat().st_mtime,
                })
            except Exception as e:
                logger.warning(f"Could not read {file_path}: {e}")
                continue
        
        return {
            "status": "success",
            "count": len(files),
            "files": files,
        }
        
    except Exception as e:
        logger.error(f"Error listing processed files: {e}")
        raise HTTPException(status_code=500, detail=f"Error listing processed files: {e}")