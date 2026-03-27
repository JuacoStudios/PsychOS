"""
Graph Visualizer for PsycheOS.

Visualizes and exports the knowledge graph for different visualization tools.
Supports export to D3.js format, GraphML, and basic statistics.
"""

import json
import logging
from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

import networkx as nx

logger = logging.getLogger(__name__)


class GraphVisualizer:
    """Visualizer for PsycheOS knowledge graph."""

    def __init__(self, graph: Optional[nx.Graph] = None):
        """
        Initialize graph visualizer.

        Args:
            graph: NetworkX graph to visualize (can be loaded later)
        """
        self.graph = graph

    def load_graph(self, graphml_path: Union[str, Path]) -> nx.Graph:
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

    def export_to_d3(self, output_path: Union[str, Path]) -> Path:
        """
        Export graph to D3.js compatible JSON format.

        Args:
            output_path: Path to save D3 JSON file

        Returns:
            Path to saved file
        """
        if self.graph is None:
            raise ValueError("No graph loaded. Call load_graph() first.")

        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Convert to D3 format
        d3_data = self._convert_to_d3_format()

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(d3_data, f, indent=2, ensure_ascii=False)

        logger.info(f"Exported D3.js graph to: {output_path}")
        return output_path

    def export_to_cytoscape(self, output_path: Union[str, Path]) -> Path:
        """
        Export graph to Cytoscape.js compatible JSON format.

        Args:
            output_path: Path to save Cytoscape JSON file

        Returns:
            Path to saved file
        """
        if self.graph is None:
            raise ValueError("No graph loaded. Call load_graph() first.")

        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Convert to Cytoscape format
        cytoscape_data = self._convert_to_cytoscape_format()

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(cytoscape_data, f, indent=2, ensure_ascii=False)

        logger.info(f"Exported Cytoscape.js graph to: {output_path}")
        return output_path

    def get_statistics(self) -> Dict:
        """
        Get comprehensive statistics about the graph.

        Returns:
            Dictionary containing graph statistics
        """
        if self.graph is None:
            raise ValueError("No graph loaded. Call load_graph() first.")

        stats = {
            "basic": self._get_basic_stats(),
            "node_types": self._get_node_type_stats(),
            "edge_types": self._get_edge_type_stats(),
            "centrality": self._get_centrality_stats(),
            "communities": self._get_community_stats(),
        }

        return stats

    def print_statistics(self) -> None:
        """Print graph statistics to console."""
        stats = self.get_statistics()

        print("=" * 60)
        print("PSYCHEOS KNOWLEDGE GRAPH STATISTICS")
        print("=" * 60)

        # Basic stats
        basic = stats["basic"]
        print(f"\n📊 BASIC STATISTICS")
        print(f"   Nodes: {basic['node_count']}")
        print(f"   Edges: {basic['edge_count']}")
        print(f"   Density: {basic['density']:.4f}")
        print(f"   Connected components: {basic['connected_components']}")
        if basic['is_directed']:
            print(f"   Graph type: Directed")
        else:
            print(f"   Graph type: Undirected")

        # Node types
        node_types = stats["node_types"]
        print(f"\n🎯 NODE TYPES ({len(node_types)} types)")
        for node_type, count in sorted(node_types.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / basic['node_count']) * 100
            print(f"   {node_type:15} {count:5} nodes ({percentage:5.1f}%)")

        # Edge types
        edge_types = stats["edge_types"]
        print(f"\n🔗 EDGE TYPES ({len(edge_types)} types)")
        for edge_type, count in sorted(edge_types.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / basic['edge_count']) * 100
            print(f"   {edge_type:15} {count:5} edges ({percentage:5.1f}%)")

        # Centrality
        centrality = stats["centrality"]
        print(f"\n⭐ TOP CENTRAL NODES (by degree centrality)")
        for i, (node_id, centrality_score) in enumerate(centrality['degree'][:5], 1):
            node_data = self.graph.nodes[node_id]
            node_name = node_data.get('name', node_data.get('title', node_id))
            print(f"   {i}. {node_name[:40]:40} centrality: {centrality_score:.3f}")

        # Communities
        communities = stats["communities"]
        if communities['community_count'] > 0:
            print(f"\n👥 COMMUNITY STRUCTURE")
            print(f"   Number of communities: {communities['community_count']}")
            print(f"   Modularity: {communities['modularity']:.3f}")
            print(f"   Largest community: {communities['largest_community_size']} nodes")

        print("\n" + "=" * 60)

    def _convert_to_d3_format(self) -> Dict:
        """Convert graph to D3.js force-directed graph format."""
        nodes = []
        edges = []

        # Add nodes
        for node_id, data in self.graph.nodes(data=True):
            node = {
                "id": node_id,
                **data
            }
            # Add size based on degree
            node["size"] = self.graph.degree(node_id)
            nodes.append(node)

        # Add edges
        for source, target, data in self.graph.edges(data=True):
            edge = {
                "source": source,
                "target": target,
                **data
            }
            edges.append(edge)

        return {
            "nodes": nodes,
            "links": edges,
            "metadata": self.graph.graph if hasattr(self.graph, "graph") else {},
        }

    def _convert_to_cytoscape_format(self) -> List[Dict]:
        """Convert graph to Cytoscape.js format."""
        elements = []

        # Add nodes
        for node_id, data in self.graph.nodes(data=True):
            element = {
                "data": {
                    "id": node_id,
                    **data
                }
            }
            elements.append(element)

        # Add edges
        edge_counter = 0
        for source, target, data in self.graph.edges(data=True):
            edge_id = f"e{edge_counter}"
            edge_counter += 1

            element = {
                "data": {
                    "id": edge_id,
                    "source": source,
                    "target": target,
                    **data
                }
            }
            elements.append(element)

        return elements

    def _get_basic_stats(self) -> Dict:
        """Get basic graph statistics."""
        if not self.graph:
            return {}

        is_directed = nx.is_directed(self.graph)

        stats = {
            "node_count": self.graph.number_of_nodes(),
            "edge_count": self.graph.number_of_edges(),
            "density": nx.density(self.graph),
            "is_directed": is_directed,
            "is_connected": nx.is_connected(self.graph.to_undirected())
            if self.graph.number_of_nodes() > 0 else False,
            "connected_components": nx.number_connected_components(self.graph.to_undirected())
            if self.graph.number_of_nodes() > 0 else 0,
        }

        # Add degree statistics
        degrees = [deg for _, deg in self.graph.degree()]
        if degrees:
            stats["average_degree"] = sum(degrees) / len(degrees)
            stats["max_degree"] = max(degrees)
            stats["min_degree"] = min(degrees)
        else:
            stats["average_degree"] = 0
            stats["max_degree"] = 0
            stats["min_degree"] = 0

        return stats

    def _get_node_type_stats(self) -> Dict:
        """Get statistics about node types."""
        if not self.graph:
            return {}

        node_types = Counter()
        for _, data in self.graph.nodes(data=True):
            node_type = data.get("type", "unknown")
            node_types[node_type] += 1

        return dict(node_types)

    def _get_edge_type_stats(self) -> Dict:
        """Get statistics about edge types."""
        if not self.graph:
            return {}

        edge_types = Counter()
        for _, _, data in self.graph.edges(data=True):
            edge_type = data.get("relationship", "unknown")
            edge_types[edge_type] += 1

        return dict(edge_types)

    def _get_centrality_stats(self) -> Dict:
        """Calculate centrality measures."""
        if not self.graph or self.graph.number_of_nodes() == 0:
            return {"degree": [], "betweenness": [], "closeness": []}

        # Convert to undirected for centrality calculations if needed
        if nx.is_directed(self.graph):
            G = self.graph.to_undirected()
        else:
            G = self.graph

        # Degree centrality
        degree_centrality = nx.degree_centrality(G)
        top_degree = sorted(
            degree_centrality.items(), key=lambda x: x[1], reverse=True
        )[:10]

        # Betweenness centrality (sample for large graphs)
        if G.number_of_nodes() < 1000:
            betweenness_centrality = nx.betweenness_centrality(G)
            top_betweenness = sorted(
                betweenness_centrality.items(), key=lambda x: x[1], reverse=True
            )[:10]
        else:
            # Use approximate betweenness for large graphs
            betweenness_centrality = nx.betweenness_centrality(G, k=100)
            top_betweenness = sorted(
                betweenness_centrality.items(), key=lambda x: x[1], reverse=True
            )[:10]

        # Closeness centrality
        if nx.is_connected(G):
            closeness_centrality = nx.closeness_centrality(G)
            top_closeness = sorted(
                closeness_centrality.items(), key=lambda x: x[1], reverse=True
            )[:10]
        else:
            # For disconnected graphs, calculate for largest component
            largest_cc = max(nx.connected_components(G), key=len)
            subgraph = G.subgraph(largest_cc)
            closeness_centrality = nx.closeness_centrality(subgraph)
            # Map back to original node IDs
            closeness_centrality_full = {
                node: closeness_centrality.get(node, 0) for node in G.nodes()
            }
            top_closeness = sorted(
                closeness_centrality_full.items(), key=lambda x: x[1], reverse=True
            )[:10]

        return {
            "degree": top_degree,
            "betweenness": top_betweenness,
            "closeness": top_closeness,
        }

    def _get_community_stats(self) -> Dict:
        """Detect and analyze communities in the graph."""
        if not self.graph or self.graph.number_of_nodes() < 10:
            return {
                "community_count": 0,
                "modularity": 0.0,
                "communities": [],
                "largest_community_size": 0,
            }

        try:
            import community as community_louvain  # python-louvain

            # Convert to undirected for community detection
            if nx.is_directed(self.graph):
                G = self.graph.to_undirected()
            else:
                G = self.graph

            # Detect communities using Louvain algorithm
            partition = community_louvain.best_partition(G)

            # Calculate modularity
            modularity = community_louvain.modularity(partition, G)

            # Group nodes by community
            communities = defaultdict(list)
            for node, community_id in partition.items():
                communities[community_id].append(node)

            # Get community sizes
            community_sizes = {
                comm_id: len(nodes) for comm_id, nodes in communities.items()
            }

            # Sort communities by size
            sorted_communities = sorted(
                community_sizes.items(), key=lambda x: x[1], reverse=True
            )

            return {
                "community_count": len(communities),
                "modularity": modularity,
                "communities": [
                    {"id": comm_id, "size": size, "nodes": communities[comm_id]}
                    for comm_id, size in sorted_communities[:10]  # Top 10 communities
                ],
                "largest_community_size": max(community_sizes.values()) if community_sizes else 0,
            }

        except ImportError:
            logger.warning("python-louvain not installed. Community detection skipped.")
            return {
                "community_count": 0,
                "modularity": 0.0,
                "communities": [],
                "largest_community_size": 0,
            }
        except Exception as e:
            logger.error(f"Community detection failed: {e}")
            return {
                "community_count": 0,
                "modularity": 0.0,
                "communities": [],
                "largest_community_size": 0,
            }


def main():
    """Command-line interface for graph visualizer."""
    import argparse
    import sys

    parser = argparse.ArgumentParser(description="Visualize PsycheOS knowledge graph")
    parser.add_argument(
        "graphml_file", help="Path to GraphML file"
    )
    parser.add_argument(
        "--output-dir", default="data/graph", help="Directory to save visualization files"
    )
    parser.add_argument(
        "--format", choices=["d3", "cytoscape", "both"], default="both",
        help="Output format for visualization"
    )
    parser.add_argument(
        "--stats", action="store_true", help="Print graph statistics"
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

    visualizer = GraphVisualizer()

    try:
        # Load graph
        visualizer.load_graph(args.graphml_file)

        # Print statistics if requested
        if args.stats:
            visualizer.print_statistics()

        # Export to requested formats
        output_dir = Path(args.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        graph_name = Path(args.graphml_file).stem

        if args.format in ["d3", "both"]:
            d3_path = output_dir / f"{graph_name}_d3.json"
            visualizer.export_to_d3(d3_path)
            print(f"Exported D3.js format to: {d3_path}")

        if args.format in ["cytoscape", "both"]:
            cytoscape_path = output_dir / f"{graph_name}_cytoscape.json"
            visualizer.export_to_cytoscape(cytoscape_path)
            print(f"Exported Cytoscape.js format to: {cytoscape_path}")

        print(f"\nGraph visualization files saved to: {output_dir}")

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()