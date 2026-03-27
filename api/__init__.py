"""
API module for PsycheOS.

This module provides the REST API for accessing and manipulating
the consciousness knowledge graph.
"""

from .main import app
from .endpoints import router

__all__ = [
    "app",
    "router",
]

__version__ = "0.1.0"