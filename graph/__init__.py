"""
Knowledge graph module for PsycheOS.

This module handles construction, analysis, and visualization
of the consciousness knowledge graph.
"""

from .builder import KnowledgeGraphBuilder
from .relations import Relationship, RelationshipType
from .visualizer import GraphVisualizer

__all__ = [
    "KnowledgeGraphBuilder",
    "Relationship",
    "RelationshipType",
    "GraphVisualizer",
]

__version__ = "0.1.0"