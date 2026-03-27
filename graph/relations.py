"""
Relationship definitions for PsycheOS knowledge graph.

Defines relationship types between entities in the consciousness knowledge graph.
Each relationship has a type, weight (confidence), and optional metadata.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Union


class RelationshipType(Enum):
    """Types of relationships between entities in the knowledge graph."""

    # Core relationship types
    SUPPORTS = "supports"  # Entity A provides evidence for Entity B
    CONTRADICTS = "contradicts"  # Entity A contradicts Entity B
    EXTENDS = "extends"  # Entity A builds upon or extends Entity B
    CITES = "cites"  # Entity A references/cites Entity B
    RELATED_TO = "related_to"  # General relationship between entities

    # Specialized relationship types
    IS_A = "is_a"  # Entity A is a type of Entity B (taxonomy)
    PART_OF = "part_of"  # Entity A is part of Entity B
    CAUSES = "causes"  # Entity A causes Entity B
    TREATS = "treats"  # Entity A treats Entity B (for mental health)
    PREDICTS = "predicts"  # Entity A predicts Entity B
    EXPLAINS = "explains"  # Entity A explains Entity B
    MEASURES = "measures"  # Entity A measures Entity B
    INFLUENCES = "influences"  # Entity A influences Entity B

    # Temporal relationships
    PRECEDES = "precedes"  # Entity A comes before Entity B in time
    FOLLOWS = "follows"  # Entity A comes after Entity B in time
    CO_OCCURS = "co_occurs"  # Entity A and B occur together

    # Strength/modality relationships
    STRONGER_THAN = "stronger_than"  # Entity A is stronger than Entity B
    WEAKER_THAN = "weaker_than"  # Entity A is weaker than Entity B
    SIMILAR_TO = "similar_to"  # Entity A is similar to Entity B

    @classmethod
    def from_string(cls, value: str) -> "RelationshipType":
        """Convert string to RelationshipType."""
        value = value.lower().replace(" ", "_")
        for member in cls:
            if member.value == value:
                return member
        raise ValueError(f"Unknown relationship type: {value}")

    def __str__(self) -> str:
        return self.value


@dataclass
class Relationship:
    """A relationship between two entities in the knowledge graph."""

    source_id: str
    target_id: str
    relationship_type: RelationshipType
    weight: float = 1.0  # Confidence/strength of relationship (0.0 to 1.0)
    metadata: Optional[Dict] = None
    sources: Optional[List[str]] = None  # IDs of sources supporting this relationship

    def __post_init__(self):
        """Validate relationship after initialization."""
        if not 0.0 <= self.weight <= 1.0:
            raise ValueError(f"Weight must be between 0.0 and 1.0, got {self.weight}")

        if self.metadata is None:
            self.metadata = {}

        if self.sources is None:
            self.sources = []

    def to_dict(self) -> Dict:
        """Convert relationship to dictionary."""
        return {
            "source_id": self.source_id,
            "target_id": self.target_id,
            "relationship_type": self.relationship_type.value,
            "weight": self.weight,
            "metadata": self.metadata,
            "sources": self.sources,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "Relationship":
        """Create relationship from dictionary."""
        return cls(
            source_id=data["source_id"],
            target_id=data["target_id"],
            relationship_type=RelationshipType.from_string(data["relationship_type"]),
            weight=data.get("weight", 1.0),
            metadata=data.get("metadata", {}),
            sources=data.get("sources", []),
        )

    def is_symmetric(self) -> bool:
        """Check if relationship type is symmetric."""
        symmetric_types = {
            RelationshipType.RELATED_TO,
            RelationshipType.SIMILAR_TO,
            RelationshipType.CO_OCCURS,
        }
        return self.relationship_type in symmetric_types

    def inverse(self) -> "Relationship":
        """Get inverse relationship (if applicable)."""
        inverse_map = {
            RelationshipType.SUPPORTS: RelationshipType.SUPPORTS,  # Self-inverse for undirected
            RelationshipType.CONTRADICTS: RelationshipType.CONTRADICTS,
            RelationshipType.EXTENDS: None,  # No clear inverse
            RelationshipType.CITES: None,  # No clear inverse
            RelationshipType.RELATED_TO: RelationshipType.RELATED_TO,
            RelationshipType.IS_A: None,  # Inverse would be "has_instance"
            RelationshipType.PART_OF: None,  # Inverse would be "has_part"
            RelationshipType.CAUSES: None,  # Inverse would be "caused_by"
            RelationshipType.TREATS: None,  # Inverse would be "treated_by"
            RelationshipType.PREDICTS: None,  # Inverse would be "predicted_by"
            RelationshipType.EXPLAINS: None,  # Inverse would be "explained_by"
            RelationshipType.MEASURES: None,  # Inverse would be "measured_by"
            RelationshipType.INFLUENCES: None,  # Inverse would be "influenced_by"
            RelationshipType.PRECEDES: RelationshipType.FOLLOWS,
            RelationshipType.FOLLOWS: RelationshipType.PRECEDES,
            RelationshipType.CO_OCCURS: RelationshipType.CO_OCCURS,
            RelationshipType.STRONGER_THAN: RelationshipType.WEAKER_THAN,
            RelationshipType.WEAKER_THAN: RelationshipType.STRONGER_THAN,
            RelationshipType.SIMILAR_TO: RelationshipType.SIMILAR_TO,
        }

        inverse_type = inverse_map.get(self.relationship_type)
        if inverse_type is None:
            raise ValueError(f"No inverse defined for {self.relationship_type}")

        return Relationship(
            source_id=self.target_id,
            target_id=self.source_id,
            relationship_type=inverse_type,
            weight=self.weight,
            metadata=self.metadata,
            sources=self.sources,
        )


# Pre-defined relationship templates for common patterns
RELATIONSHIP_TEMPLATES = {
    "theory_supports_theory": {
        "description": "Theory A provides evidence for Theory B",
        "type": RelationshipType.SUPPORTS,
        "default_weight": 0.7,
    },
    "theory_contradicts_theory": {
        "description": "Theory A contradicts Theory B",
        "type": RelationshipType.CONTRADICTS,
        "default_weight": 0.8,
    },
    "theory_extends_theory": {
        "description": "Theory A builds upon Theory B",
        "type": RelationshipType.EXTENDS,
        "default_weight": 0.9,
    },
    "paper_cites_paper": {
        "description": "Paper A cites Paper B",
        "type": RelationshipType.CITES,
        "default_weight": 1.0,
    },
    "author_wrote_paper": {
        "description": "Author wrote Paper",
        "type": RelationshipType.CITES,
        "default_weight": 1.0,
    },
    "concept_related_to_concept": {
        "description": "Concept A is related to Concept B",
        "type": RelationshipType.RELATED_TO,
        "default_weight": 0.5,
    },
    "symptom_of_disorder": {
        "description": "Symptom is a symptom of Disorder",
        "type": RelationshipType.IS_A,
        "default_weight": 0.8,
    },
    "treatment_for_disorder": {
        "description": "Treatment is for Disorder",
        "type": RelationshipType.TREATS,
        "default_weight": 0.7,
    },
    "study_supports_hypothesis": {
        "description": "Study supports Hypothesis",
        "type": RelationshipType.SUPPORTS,
        "default_weight": 0.6,
    },
}


def create_relationship_from_template(
    template_name: str,
    source_id: str,
    target_id: str,
    weight: Optional[float] = None,
    metadata: Optional[Dict] = None,
    sources: Optional[List[str]] = None,
) -> Relationship:
    """
    Create a relationship using a pre-defined template.

    Args:
        template_name: Name of template from RELATIONSHIP_TEMPLATES
        source_id: Source entity ID
        target_id: Target entity ID
        weight: Optional custom weight (uses template default if not provided)
        metadata: Optional additional metadata
        sources: Optional list of source IDs supporting this relationship

    Returns:
        Relationship object
    """
    if template_name not in RELATIONSHIP_TEMPLATES:
        raise ValueError(f"Unknown template: {template_name}. "
                       f"Available: {list(RELATIONSHIP_TEMPLATES.keys())}")

    template = RELATIONSHIP_TEMPLATES[template_name]

    return Relationship(
        source_id=source_id,
        target_id=target_id,
        relationship_type=template["type"],
        weight=weight if weight is not None else template["default_weight"],
        metadata=metadata or {},
        sources=sources or [],
    )


def validate_relationship(
    source_type: str,
    target_type: str,
    relationship_type: RelationshipType,
) -> bool:
    """
    Validate if a relationship type is appropriate for given entity types.

    Args:
        source_type: Type of source entity
        target_type: Type of target entity
        relationship_type: Type of relationship

    Returns:
        True if relationship is valid, False otherwise
    """
    # Define valid relationships between entity types
    valid_relationships = {
        # (source_type, target_type): [valid_relationship_types]
        ("theory", "theory"): [
            RelationshipType.SUPPORTS,
            RelationshipType.CONTRADICTS,
            RelationshipType.EXTENDS,
            RelationshipType.RELATED_TO,
            RelationshipType.SIMILAR_TO,
        ],
        ("paper", "paper"): [
            RelationshipType.CITES,
            RelationshipType.RELATED_TO,
        ],
        ("author", "paper"): [
            RelationshipType.CITES,
        ],
        ("concept", "concept"): [
            RelationshipType.RELATED_TO,
            RelationshipType.IS_A,
            RelationshipType.PART_OF,
            RelationshipType.CAUSES,
            RelationshipType.SIMILAR_TO,
        ],
        ("symptom", "disorder"): [
            RelationshipType.IS_A,
            RelationshipType.RELATED_TO,
        ],
        ("treatment", "disorder"): [
            RelationshipType.TREATS,
        ],
        ("study", "hypothesis"): [
            RelationshipType.SUPPORTS,
            RelationshipType.CONTRADICTS,
        ],
        # Add more type pairs as needed
    }

    key = (source_type, target_type)
    if key in valid_relationships:
        return relationship_type in valid_relationships[key]

    # If not explicitly defined, allow general relationships
    general_types = {RelationshipType.RELATED_TO, RelationshipType.CITES}
    return relationship_type in general_types


def get_relationship_description(relationship_type: RelationshipType) -> str:
    """Get human-readable description of relationship type."""
    descriptions = {
        RelationshipType.SUPPORTS: "provides evidence for",
        RelationshipType.CONTRADICTS: "contradicts",
        RelationshipType.EXTENDS: "builds upon",
        RelationshipType.CITES: "cites",
        RelationshipType.RELATED_TO: "is related to",
        RelationshipType.IS_A: "is a type of",
        RelationshipType.PART_OF: "is part of",
        RelationshipType.CAUSES: "causes",
        RelationshipType.TREATS: "treats",
        RelationshipType.PREDICTS: "predicts",
        RelationshipType.EXPLAINS: "explains",
        RelationshipType.MEASURES: "measures",
        RelationshipType.INFLUENCES: "influences",
        RelationshipType.PRECEDES: "comes before",
        RelationshipType.FOLLOWS: "comes after",
        RelationshipType.CO_OCCURS: "occurs with",
        RelationshipType.STRONGER_THAN: "is stronger than",
        RelationshipType.WEAKER_THAN: "is weaker than",
        RelationshipType.SIMILAR_TO: "is similar to",
    }
    return descriptions.get(relationship_type, str(relationship_type.value))