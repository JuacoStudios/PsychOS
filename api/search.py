"""
Search Module for PsycheOS.

Provides semantic search capabilities over the knowledge graph.
This is a basic implementation - in production, you would use
vector embeddings and proper search engines.
"""

import json
import logging
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class SemanticSearch:
    """Basic semantic search for PsycheOS knowledge graph."""
    
    def __init__(self, data_dir: str = "data/processed"):
        """
        Initialize semantic search.
        
        Args:
            data_dir: Directory containing processed JSON files
        """
        self.data_dir = Path(data_dir)
        self.index = {}
        self.load_data()
    
    def load_data(self) -> None:
        """Load and index processed data."""
        if not self.data_dir.exists():
            logger.warning(f"Data directory not found: {self.data_dir}")
            return
        
        json_files = list(self.data_dir.glob("*.json"))
        logger.info(f"Loading {len(json_files)} files for search index")
        
        for file_path in json_files:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                
                # Extract searchable content
                content = self._extract_search_content(data)
                if content:
                    self.index[file_path.name] = {
                        "content": content,
                        "metadata": self._extract_metadata(data),
                        "source_type": data.get("source_type", "unknown"),
                    }
                    
            except Exception as e:
                logger.error(f"Error loading {file_path}: {e}")
                continue
        
        logger.info(f"Search index created with {len(self.index)} documents")
    
    def _extract_search_content(self, data: Dict) -> str:
        """Extract searchable content from data."""
        content_parts = []
        
        # Extract based on source type
        source_type = data.get("source_type", "")
        
        if source_type == "pdf":
            content_parts.append(data.get("text", ""))
            metadata = data.get("metadata", {})
            content_parts.append(metadata.get("title", ""))
            content_parts.append(metadata.get("abstract", ""))
            content_parts.extend(metadata.get("keywords", []))
            
        elif source_type == "youtube":
            metadata = data.get("metadata", {})
            content_parts.append(metadata.get("title", ""))
            content_parts.append(metadata.get("description", ""))
            transcription = data.get("transcription", {})
            content_parts.append(transcription.get("text", ""))
            
        elif source_type == "audio":
            transcription = data.get("transcription", {})
            content_parts.append(transcription.get("text", ""))
            
        elif source_type == "web":
            metadata = data.get("metadata", {})
            content_parts.append(metadata.get("title", ""))
            content = data.get("content", {})
            content_parts.append(content.get("text", ""))
            
        else:
            # Fallback: try to extract any text fields
            content_parts.append(json.dumps(data, ensure_ascii=False))
        
        return " ".join(str(part) for part in content_parts if part)
    
    def _extract_metadata(self, data: Dict) -> Dict:
        """Extract metadata for search results."""
        metadata = {
            "source_type": data.get("source_type", "unknown"),
        }
        
        if "metadata" in data:
            metadata.update(data["metadata"])
        
        # Add specific fields
        if data.get("source_type") == "pdf":
            metadata["type"] = "paper"
        elif data.get("source_type") == "youtube":
            metadata["type"] = "video"
        elif data.get("source_type") == "audio":
            metadata["type"] = "audio"
        elif data.get("source_type") == "web":
            metadata["type"] = "article"
        
        return metadata
    
    def search(self, query: str, max_results: int = 10) -> List[Dict]:
        """
        Search for documents matching the query.
        
        Args:
            query: Search query
            max_results: Maximum number of results to return
            
        Returns:
            List of search results with relevance scores
        """
        if not self.index:
            return []
        
        query_lower = query.lower()
        query_terms = re.findall(r'\w+', query_lower)
        
        results = []
        
        for filename, doc_data in self.index.items():
            content = doc_data["content"].lower()
            metadata = doc_data["metadata"]
            
            # Calculate relevance score
            score = 0
            
            # Exact phrase match
            if query_lower in content:
                score += 5
            
            # Term frequency
            for term in query_terms:
                term_count = content.count(term)
                score += term_count * 0.1
            
            # Title match (weighted higher)
            title = metadata.get("title", "").lower()
            if query_lower in title:
                score += 3
            for term in query_terms:
                if term in title:
                    score += 1
            
            if score > 0:
                # Extract snippet
                snippet = self._extract_snippet(content, query_lower)
                
                results.append({
                    "filename": filename,
                    "title": metadata.get("title", "Untitled"),
                    "snippet": snippet,
                    "score": score,
                    "type": doc_data.get("source_type", "unknown"),
                    "metadata": {
                        k: v for k, v in metadata.items()
                        if k in ["authors", "year", "uploader", "publish_date"]
                    },
                })
        
        # Sort by score and limit results
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:max_results]
    
    def _extract_snippet(self, content: str, query: str, max_length: int = 200) -> str:
        """Extract a relevant snippet from content."""
        if not content:
            return ""
        
        # Find query in content
        query_lower = query.lower()
        content_lower = content.lower()
        
        # Try to find exact query
        pos = content_lower.find(query_lower)
        if pos == -1:
            # Find any query term
            query_terms = re.findall(r'\w+', query_lower)
            for term in query_terms:
                pos = content_lower.find(term)
                if pos != -1:
                    break
        
        if pos == -1:
            # No match found, return beginning
            return content[:max_length] + "..." if len(content) > max_length else content
        
        # Extract snippet around match
        start = max(0, pos - 50)
        end = min(len(content), pos + 150)
        
        snippet = content[start:end]
        if start > 0:
            snippet = "..." + snippet
        if end < len(content):
            snippet = snippet + "..."
        
        return snippet
    
    def search_by_type(self, query: str, source_type: str, max_results: int = 10) -> List[Dict]:
        """
        Search for documents of a specific type.
        
        Args:
            query: Search query
            source_type: Type of document to search (pdf, youtube, audio, web)
            max_results: Maximum number of results to return
            
        Returns:
            List of search results
        """
        all_results = self.search(query, max_results * 3)  # Get more, then filter
        filtered = [r for r in all_results if r["type"] == source_type]
        return filtered[:max_results]


# Graph-aware search (would be expanded in production)
class GraphSearch:
    """Search that considers knowledge graph structure."""
    
    def __init__(self, graphml_path: Optional[str] = None):
        """
        Initialize graph search.
        
        Args:
            graphml_path: Path to GraphML file (optional)
        """
        self.graph = None
        if graphml_path and Path(graphml_path).exists():
            try:
                import networkx as nx
                self.graph = nx.read_graphml(graphml_path)
                logger.info(f"Loaded graph with {self.graph.number_of_nodes()} nodes")
            except Exception as e:
                logger.error(f"Error loading graph: {e}")
    
    def search_nodes(self, query: str, max_results: int = 10) -> List[Dict]:
        """
        Search for nodes in the graph.
        
        Args:
            query: Search query
            max_results: Maximum number of results to return
            
        Returns:
            List of matching nodes
        """
        if not self.graph:
            return []
        
        query_lower = query.lower()
        results = []
        
        for node_id, data in self.graph.nodes(data=True):
            score = 0
            
            # Check node attributes
            for key, value in data.items():
                if isinstance(value, str) and query_lower in value.lower():
                    score += 1
            
            if score > 0:
                results.append({
                    "node_id": node_id,
                    "data": data,
                    "score": score,
                    "degree": self.graph.degree(node_id),
                })
        
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:max_results]
    
    def find_related(self, node_id: str, max_depth: int = 2) -> List[Dict]:
        """
        Find nodes related to a given node.
        
        Args:
            node_id: ID of the starting node
            max_depth: Maximum distance to search
            
        Returns:
            List of related nodes with relationship information
        """
        if not self.graph or node_id not in self.graph:
            return []
        
        try:
            import networkx as nx
            
            # Find nodes within max_depth
            related = []
            for target_id in nx.single_source_shortest_path_length(self.graph, node_id, cutoff=max_depth):
                if target_id == node_id:
                    continue
                
                # Get relationship data
                edge_data = self.graph.get_edge_data(node_id, target_id)
                if edge_data:
                    for key, data in edge_data.items():
                        related.append({
                            "target_id": target_id,
                            "target_data": self.graph.nodes[target_id],
                            "relationship": data.get("relationship", "related"),
                            "weight": data.get("weight", 1.0),
                            "distance": nx.shortest_path_length(self.graph, node_id, target_id),
                        })
            
            return related
            
        except Exception as e:
            logger.error(f"Error finding related nodes: {e}")
            return []


def main():
    """Command-line interface for search."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Search PsycheOS knowledge base")
    parser.add_argument("query", help="Search query")
    parser.add_argument("--max-results", type=int, default=10, help="Maximum results")
    parser.add_argument("--type", choices=["pdf", "youtube", "audio", "web", "all"], 
                       default="all", help="Type of content to search")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    
    args = parser.parse_args()
    
    # Setup logging
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    
    search = SemanticSearch()
    
    if args.type == "all":
        results = search.search(args.query, args.max_results)
    else:
        results = search.search_by_type(args.query, args.type, args.max_results)
    
    print(f"Search results for '{args.query}':")
    print(f"Found {len(results)} results")
    print()
    
    for i, result in enumerate(results, 1):
        print(f"{i}. {result['title']}")
        print(f"   Type: {result['type']}")
        print(f"   File: {result['filename']}")
        print(f"   Score: {result['score']:.2f}")
        if result.get('metadata'):
            meta_str = ", ".join(f"{k}: {v}" for k, v in result['metadata'].items() if v)
            if meta_str:
                print(f"   Metadata: {meta_str}")
        print(f"   Snippet: {result['snippet']}")
        print()


if __name__ == "__main__":
    main()