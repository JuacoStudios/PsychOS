"""
Knowledge Graph Builder for PsycheOS.

Builds a knowledge graph from ingested data using NetworkX.
Extracts entities, concepts, and relationships from processed JSON files.
"""

import json
import logging
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Union

import networkx as nx

from .relations import Relationship, RelationshipType

logger = logging.getLogger(__name__)


class KnowledgeGraphBuilder:
    """Builder for consciousness knowledge graph."""

    def __init__(self, data_dir: Union[str, Path] = "data/processed"):
        """
        Initialize knowledge graph builder.

        Args:
            data_dir: Directory containing processed JSON files
        """
        self.data_dir = Path(data_dir)
        self.graph = nx.MultiDiGraph()
        self.entity_counter = defaultdict(int)
        self.relationship_counter = defaultdict(int)

    def build_from_directory(self) -> nx.MultiDiGraph:
        """
        Build knowledge graph from all JSON files in data directory.

        Returns:
            NetworkX MultiDiGraph containing the knowledge graph
        """
        if not self.data_dir.exists():
            raise FileNotFoundError(f"Data directory not found: {self.data_dir}")

        # Find all JSON files
        json_files = list(self.data_dir.glob("*.json"))
        logger.info(f"Found {len(json_files)} JSON files in {self.data_dir}")

        if not json_files:
            logger.warning("No JSON files found to build graph from")
            return self.graph

        # Process each file
        for i, json_file in enumerate(json_files, 1):
            logger.info(f"Processing file {i}/{len(json_files)}: {json_file.name}")
            try:
                self._process_file(json_file)
            except Exception as e:
                logger.error(f"Failed to process {json_file.name}: {e}")
                continue

        # Add graph metadata
        self._add_graph_metadata()

        logger.info(f"Graph built successfully: {self.graph.number_of_nodes()} nodes, "
                   f"{self.graph.number_of_edges()} edges")
        return self.graph

    def build_from_files(self, file_paths: List[Union[str, Path]]) -> nx.MultiDiGraph:
        """
        Build knowledge graph from specific JSON files.

        Args:
            file_paths: List of paths to JSON files

        Returns:
            NetworkX MultiDiGraph containing the knowledge graph
        """
        for i, file_path in enumerate(file_paths, 1):
            logger.info(f"Processing file {i}/{len(file_paths)}: {Path(file_path).name}")
            try:
                self._process_file(file_path)
            except Exception as e:
                logger.error(f"Failed to process {file_path}: {e}")
                continue

        self._add_graph_metadata()
        return self.graph

    def save_graph(self, output_dir: Union[str, Path] = "data/graph") -> Tuple[Path, Path]:
        """
        Save graph to files.

        Args:
            output_dir: Directory to save graph files

        Returns:
            Tuple of (graphml_path, json_path)
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Save as GraphML
        graphml_path = output_dir / f"psyche_graph_{timestamp}.graphml"
        nx.write_graphml(self.graph, graphml_path)
        logger.info(f"Saved graph to GraphML: {graphml_path}")

        # Save as JSON (custom format for easier loading)
        json_path = output_dir / f"psyche_graph_{timestamp}.json"
        graph_data = self._graph_to_dict()
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(graph_data, f, indent=2, ensure_ascii=False)
        logger.info(f"Saved graph to JSON: {json_path}")

        return graphml_path, json_path

    def load_graph(self, graphml_path: Union[str, Path]) -> nx.MultiDiGraph:
        """
        Load graph from GraphML file.

        Args:
            graphml_path: Path to GraphML file

        Returns:
            Loaded NetworkX graph
        """
        graphml_path = Path(graphml_path)
        if not graphml_path.exists():
            raise FileNotFoundError(f"GraphML file not found: {graphml_path}")

        self.graph = nx.read_graphml(graphml_path)
        logger.info(f"Loaded graph: {self.graph.number_of_nodes()} nodes, "
                   f"{self.graph.number_of_edges()} edges")
        return self.graph

    def _process_file(self, file_path: Union[str, Path]) -> None:
        """Process a single JSON file and add to graph."""
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        source_type = data.get("source_type", "unknown")
        source_id = self._get_source_id(data)

        # Add source node
        source_node_id = f"source_{source_id}"
        self.graph.add_node(
            source_node_id,
            type="source",
            source_type=source_type,
            **self._extract_source_metadata(data)
        )

        # Extract and add entities based on source type
        if source_type == "pdf":
            self._process_pdf(data, source_node_id)
        elif source_type == "youtube":
            self._process_youtube(data, source_node_id)
        elif source_type == "audio":
            self._process_audio(data, source_node_id)
        elif source_type == "web":
            self._process_web(data, source_node_id)
        else:
            logger.warning(f"Unknown source type: {source_type}")

    def _get_source_id(self, data: Dict) -> str:
        """Generate unique source ID from data."""
        source_type = data.get("source_type", "unknown")

        if source_type == "pdf":
            return Path(data.get("source_path", "")).stem
        elif source_type == "youtube":
            return data.get("video_id", "unknown")
        elif source_type == "audio":
            return Path(data.get("source_path", "")).stem
        elif source_type == "web":
            url = data.get("source_url", "")
            return str(hash(url) % 1000000)
        else:
            return str(hash(str(data)) % 1000000)

    def _extract_source_metadata(self, data: Dict) -> Dict:
        """Extract metadata for source node."""
        metadata = {
            "ingestion_date": data.get("extraction_date", data.get("ingestion_date", "")),
        }

        if "metadata" in data:
            metadata.update(data["metadata"])

        return {k: v for k, v in metadata.items() if v not in (None, "", [])}

    def _process_pdf(self, data: Dict, source_node_id: str) -> None:
        """Process PDF data."""
        text = data.get("text", "")
        metadata = data.get("metadata", {})

        # Add author nodes
        authors = metadata.get("authors", [])
        if isinstance(authors, str):
            authors = [authors]

        for author in authors:
            if author:
                author_id = f"author_{hash(author) % 1000000}"
                self.graph.add_node(author_id, type="person", name=author)
                self.graph.add_edge(
                    source_node_id,
                    author_id,
                    relationship=RelationshipType.CITES.value,
                    weight=1.0,
                )

        # Extract concepts from text (simple keyword extraction)
        concepts = self._extract_concepts(text)
        for concept in concepts:
            concept_id = f"concept_{hash(concept) % 1000000}"
            self.graph.add_node(concept_id, type="concept", name=concept)
            self.graph.add_edge(
                source_node_id,
                concept_id,
                relationship=RelationshipType.RELATED_TO.value,
                weight=0.5,
            )

        # Add title as concept
        title = metadata.get("title", "")
        if title:
            title_id = f"title_{hash(title) % 1000000}"
            self.graph.add_node(title_id, type="title", text=title)
            self.graph.add_edge(
                source_node_id,
                title_id,
                relationship=RelationshipType.CITES.value,
                weight=1.0,
            )

    def _process_youtube(self, data: Dict, source_node_id: str) -> None:
        """Process YouTube data."""
        metadata = data.get("metadata", {})
        transcription = data.get("transcription", {})

        # Add uploader as person
        uploader = metadata.get("uploader")
        if uploader:
            uploader_id = f"person_{hash(uploader) % 1000000}"
            self.graph.add_node(uploader_id, type="person", name=uploader)
            self.graph.add_edge(
                source_node_id,
                uploader_id,
                relationship=RelationshipType.CITES.value,
                weight=1.0,
            )

        # Extract concepts from title and description
        text_parts = []
        if metadata.get("title"):
            text_parts.append(metadata["title"])
        if metadata.get("description"):
            text_parts.append(metadata["description"])
        if transcription.get("text"):
            text_parts.append(transcription["text"])

        text = " ".join(text_parts)
        concepts = self._extract_concepts(text)

        for concept in concepts:
            concept_id = f"concept_{hash(concept) % 1000000}"
            self.graph.add_node(concept_id, type="concept", name=concept)
            self.graph.add_edge(
                source_node_id,
                concept_id,
                relationship=RelationshipType.RELATED_TO.value,
                weight=0.5,
            )

    def _process_audio(self, data: Dict, source_node_id: str) -> None:
        """Process audio data."""
        transcription = data.get("transcription", {})
        text = transcription.get("text", "")

        concepts = self._extract_concepts(text)
        for concept in concepts:
            concept_id = f"concept_{hash(concept) % 1000000}"
            self.graph.add_node(concept_id, type="concept", name=concept)
            self.graph.add_edge(
                source_node_id,
                concept_id,
                relationship=RelationshipType.RELATED_TO.value,
                weight=0.5,
            )

    def _process_web(self, data: Dict, source_node_id: str) -> None:
        """Process web article data."""
        metadata = data.get("metadata", {})
        content = data.get("content", {})
        text = content.get("text", "")

        # Add author nodes
        authors = metadata.get("authors", [])
        for author in authors:
            if author:
                author_id = f"author_{hash(author) % 1000000}"
                self.graph.add_node(author_id, type="person", name=author)
                self.graph.add_edge(
                    source_node_id,
                    author_id,
                    relationship=RelationshipType.CITES.value,
                    weight=1.0,
                )

        # Extract concepts
        concepts = self._extract_concepts(text)
        for concept in concepts:
            concept_id = f"concept_{hash(concept) % 1000000}"
            self.graph.add_node(concept_id, type="concept", name=concept)
            self.graph.add_edge(
                source_node_id,
                concept_id,
                relationship=RelationshipType.RELATED_TO.value,
                weight=0.5,
            )

    def _extract_concepts(self, text: str, max_concepts: int = 20) -> List[str]:
        """
        Extract concepts from text (simple implementation).

        Note: This is a simple keyword extraction. In production,
        you would use NLP techniques like named entity recognition,
        topic modeling, or keyword extraction algorithms.

        Args:
            text: Text to extract concepts from
            max_concepts: Maximum number of concepts to extract

        Returns:
            List of extracted concepts
        """
        if not text:
            return []

        # Simple approach: extract capitalized phrases and frequent terms
        # This should be replaced with proper NLP in production
        words = text.split()
        concepts = set()

        # Look for capitalized phrases (potential proper nouns/concepts)
        for i in range(len(words) - 1):
            if words[i][0].isupper() and words[i + 1][0].isupper():
                concept = f"{words[i]} {words[i + 1]}"
                concepts.add(concept)

        # Also add individual capitalized words (excluding common words)
        common_words = {"the", "and", "but", "for", "nor", "or", "so", "yet", "a", "an"}
        for word in words:
            if (word[0].isupper() and len(word) > 2 and
                word.lower() not in common_words):
                concepts.add(word)

        return list(concepts)[:max_concepts]

    def _add_graph_metadata(self) -> None:
        """Add metadata to graph."""
        self.graph.graph["name"] = "PsycheOS Knowledge Graph"
        self.graph.graph["description"] = "Consciousness and mental health knowledge graph"
        self.graph.graph["creation_date"] = datetime.now().isoformat()
        self.graph.graph["version"] = "1.0"
        self.graph.graph["node_count"] = self.graph.number_of_nodes()
        self.graph.graph["edge_count"] = self.graph.number_of_edges()

        # Count node types
        node_types = defaultdict(int)
        for _, data in self.graph.nodes(data=True):
            node_type = data.get("type", "unknown")
            node_types[node_type] += 1

        self.graph.graph["node_types"] = dict(node_types)

    def _graph_to_dict(self) -> Dict:
        """Convert graph to dictionary for JSON serialization."""
        nodes = []
        for node_id, data in self.graph.nodes(data=True):
            nodes.append({
                "id": node_id,
                **data
            })

        edges = []
        for source, target, key, data in self.graph.edges(data=True, keys=True):
            edges.append({
                "source": source,
                "target": target,
                "key": key,
                **data
            })

        return {
            "metadata": self.graph.graph,
            "nodes": nodes,
            "edges": edges,
        }


def main():
    """Command-line interface for graph builder."""
    import argparse
    import sys

    parser = argparse.ArgumentParser(description="Build knowledge graph for PsycheOS")
    parser.add_argument(
        "--data-dir", default="data/processed", help="Directory containing processed JSON files"
    )
    parser.add_argument(
        "--output-dir", default="data/graph", help="Directory to save graph files"
    )
    parser.add_argument(
        "--load", help="Load existing graph from GraphML file instead of building"
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

    builder = KnowledgeGraphBuilder(data_dir=args.data_dir)

    try:
        if args.load:
            graph = builder.load_graph(args.load)
        else:
            graph = builder.build_from_directory()

        # Save graph
        graphml_path, json_path = builder.save_graph(args.output_dir)

        # Print stats
        print(f"Graph built successfully!")
        print(f"Nodes: {graph.number_of_nodes()}")
        print(f"Edges: {graph.number_of_edges()}")
        print(f"Saved to:")
        print(f"  - {graphml_path}")
        print(f"  - {json_path}")

        # Print node type distribution
        node_types = defaultdict(int)
        for _, data in graph.nodes(data=True):
            node_type = data.get("type", "unknown")
            node_types[node_type] += 1

        print("\nNode types:")
        for node_type, count in sorted(node_types.items()):
            print(f"  {node_type}: {count}")

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()