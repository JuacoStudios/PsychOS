"""
Data models for PsycheOS.

This module defines the core data structures for representing
consciousness theories, mental health concepts, and evolutionary layers.
"""

from .consciousness import ConsciousnessTheory, get_theory_examples, get_theory_by_name
from .mental_health import MentalHealthConcept, ConceptCategory, get_mental_health_examples, get_concept_by_name
from .evolution import EvolutionaryLayer, EvolutionaryHypothesis, get_evolutionary_hypotheses, get_evolutionary_layers

__all__ = [
    "ConsciousnessTheory",
    "TheoryExample",
    "MentalHealthConcept",
    "ConceptCategory",
    "EvolutionaryLayer",
    "EvolutionaryHypothesis",
]

__version__ = "0.1.0"