"""
Evolutionary Psychology Models for PsycheOS.

Defines data structures for linking psychological traits and consciousness
to evolutionary hypotheses and adaptive functions.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Set


class EvolutionaryPressure(Enum):
    """Types of evolutionary pressures that shape traits."""

    SURVIVAL = "survival"  # Avoiding predators, finding food
    REPRODUCTION = "reproduction"  # Mating, parenting
    SOCIAL = "social"  # Group living, cooperation, competition
    ENVIRONMENTAL = "environmental"  # Climate, geography, resources
    SEXUAL_SELECTION = "sexual_selection"  # Mate choice
    KIN_SELECTION = "kin_selection"  # Helping relatives
    RECIPROCAL_ALTRUISM = "reciprocal_altruism"  # Mutual benefit


class TimeScale(Enum):
    """Evolutionary timescales."""

    PHYLOGENETIC = "phylogenetic"  # Deep evolutionary history (millions of years)
    HISTORICAL = "historical"  # Human history (thousands of years)
    ONTOGENETIC = "ontogenetic"  # Individual development
    EPIGENETIC = "epigenetic"  # Gene expression changes


class EvidenceType(Enum):
    """Types of evidence for evolutionary hypotheses."""

    COMPARATIVE = "comparative"  # Cross-species comparisons
    ARCHAEOLOGICAL = "archaeological"  # Fossil and artifact evidence
    GENETIC = "genetic"  # Genetic studies
    CROSS_CULTURAL = "cross_cultural"  # Universal human patterns
    DEVELOPMENTAL = "developmental"  # Developmental trajectories
    EXPERIMENTAL = "experimental"  # Laboratory experiments
    COMPUTATIONAL = "computational"  # Modeling and simulations


@dataclass
class EvolutionaryEvidence:
    """Evidence supporting an evolutionary hypothesis."""

    description: str
    evidence_type: EvidenceType
    strength: float = 0.5  # 0.0 to 1.0
    source: Optional[str] = None
    year: Optional[int] = None
    limitations: Optional[str] = None


@dataclass
class EvolutionaryHypothesis:
    """An evolutionary hypothesis for a psychological trait."""

    name: str
    description: str
    trait_explained: str  # The psychological trait being explained
    adaptive_function: str  # Proposed adaptive function
    evolutionary_pressures: List[EvolutionaryPressure] = field(default_factory=list)
    timescale: TimeScale = TimeScale.PHYLOGENETIC

    # Evidence
    supporting_evidence: List[EvolutionaryEvidence] = field(default_factory=list)
    contradictory_evidence: List[EvolutionaryEvidence] = field(default_factory=list)
    alternative_hypotheses: List[str] = field(default_factory=list)

    # Relationships
    related_traits: List[str] = field(default_factory=list)
    consciousness_links: List[str] = field(default_factory=list)  # Links to consciousness
    modern_manifestations: List[str] = field(default_factory=list)

    # Metadata
    confidence: float = 0.5  # 0.0 to 1.0
    controversy_level: str = "moderate"  # low, moderate, high
    tags: Set[str] = field(default_factory=set)
    sources: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict:
        """Convert hypothesis to dictionary for serialization."""
        return {
            "name": self.name,
            "description": self.description,
            "trait_explained": self.trait_explained,
            "adaptive_function": self.adaptive_function,
            "evolutionary_pressures": [p.value for p in self.evolutionary_pressures],
            "timescale": self.timescale.value,
            "supporting_evidence": [
                {
                    "description": e.description,
                    "evidence_type": e.evidence_type.value,
                    "strength": e.strength,
                    "source": e.source,
                    "year": e.year,
                    "limitations": e.limitations,
                }
                for e in self.supporting_evidence
            ],
            "contradictory_evidence": [
                {
                    "description": e.description,
                    "evidence_type": e.evidence_type.value,
                    "strength": e.strength,
                    "source": e.source,
                    "year": e.year,
                    "limitations": e.limitations,
                }
                for e in self.contradictory_evidence
            ],
            "alternative_hypotheses": self.alternative_hypotheses,
            "related_traits": self.related_traits,
            "consciousness_links": self.consciousness_links,
            "modern_manifestations": self.modern_manifestations,
            "confidence": self.confidence,
            "controversy_level": self.controversy_level,
            "tags": list(self.tags),
            "sources": self.sources,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "EvolutionaryHypothesis":
        """Create hypothesis from dictionary."""
        # Convert evidence lists
        supporting_evidence = []
        for e_data in data.get("supporting_evidence", []):
            evidence = EvolutionaryEvidence(
                description=e_data["description"],
                evidence_type=EvidenceType(e_data["evidence_type"]),
                strength=e_data.get("strength", 0.5),
                source=e_data.get("source"),
                year=e_data.get("year"),
                limitations=e_data.get("limitations"),
            )
            supporting_evidence.append(evidence)

        contradictory_evidence = []
        for e_data in data.get("contradictory_evidence", []):
            evidence = EvolutionaryEvidence(
                description=e_data["description"],
                evidence_type=EvidenceType(e_data["evidence_type"]),
                strength=e_data.get("strength", 0.5),
                source=e_data.get("source"),
                year=e_data.get("year"),
                limitations=e_data.get("limitations"),
            )
            contradictory_evidence.append(evidence)

        return cls(
            name=data["name"],
            description=data["description"],
            trait_explained=data["trait_explained"],
            adaptive_function=data["adaptive_function"],
            evolutionary_pressures=[
                EvolutionaryPressure(p) for p in data.get("evolutionary_pressures", [])
            ],
            timescale=TimeScale(data.get("timescale", "phylogenetic")),
            supporting_evidence=supporting_evidence,
            contradictory_evidence=contradictory_evidence,
            alternative_hypotheses=data.get("alternative_hypotheses", []),
            related_traits=data.get("related_traits", []),
            consciousness_links=data.get("consciousness_links", []),
            modern_manifestations=data.get("modern_manifestations", []),
            confidence=data.get("confidence", 0.5),
            controversy_level=data.get("controversy_level", "moderate"),
            tags=set(data.get("tags", [])),
            sources=data.get("sources", []),
        )

    def add_evidence(
        self,
        description: str,
        evidence_type: EvidenceType,
        supports: bool = True,
        strength: float = 0.5,
        **kwargs,
    ) -> None:
        """Add evidence to the hypothesis."""
        evidence = EvolutionaryEvidence(
            description=description,
            evidence_type=evidence_type,
            strength=strength,
            **kwargs,
        )

        if supports:
            self.supporting_evidence.append(evidence)
        else:
            self.contradictory_evidence.append(evidence)

    def update_confidence(self) -> None:
        """Update confidence based on evidence balance."""
        if not self.supporting_evidence and not self.contradictory_evidence:
            self.confidence = 0.3
            return

        total_strength = 0
        count = 0

        for evidence in self.supporting_evidence:
            total_strength += evidence.strength
            count += 1

        for evidence in self.contradictory_evidence:
            total_strength -= evidence.strength
            count += 1

        if count > 0:
            base_confidence = max(0.0, min(1.0, 0.5 + (total_strength / count)))
        else:
            base_confidence = 0.5

        # Adjust for controversy
        if self.controversy_level == "high":
            self.confidence = base_confidence * 0.7
        elif self.controversy_level == "moderate":
            self.confidence = base_confidence * 0.85
        else:  # low
            self.confidence = base_confidence


@dataclass
class EvolutionaryLayer:
    """A layer in the evolutionary development of consciousness."""

    name: str
    description: str
    timescale: TimeScale
    approximate_years_ago: Optional[str] = None  # e.g., "2 million years"

    # Characteristics
    cognitive_abilities: List[str] = field(default_factory=list)
    social_complexity: str = "simple"  # simple, moderate, complex
    brain_changes: List[str] = field(default_factory=list)
    consciousness_aspects: List[str] = field(default_factory=list)

    # Evidence
    fossil_evidence: List[str] = field(default_factory=list)
    archaeological_evidence: List[str] = field(default_factory=list)
    comparative_evidence: List[str] = field(default_factory=list)

    # Relationships
    preceding_layer: Optional[str] = None
    following_layer: Optional[str] = None
    modern_vestiges: List[str] = field(default_factory=list)  # Modern remnants

    # Metadata
    confidence: float = 0.5
    tags: Set[str] = field(default_factory=set)
    sources: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict:
        """Convert layer to dictionary for serialization."""
        return {
            "name": self.name,
            "description": self.description,
            "timescale": self.timescale.value,
            "approximate_years_ago": self.approximate_years_ago,
            "cognitive_abilities": self.cognitive_abilities,
            "social_complexity": self.social_complexity,
            "brain_changes": self.brain_changes,
            "consciousness_aspects": self.consciousness_aspects,
            "fossil_evidence": self.fossil_evidence,
            "archaeological_evidence": self.archaeological_evidence,
            "comparative_evidence": self.comparative_evidence,
            "preceding_layer": self.preceding_layer,
            "following_layer": self.following_layer,
            "modern_vestiges": self.modern_vestiges,
            "confidence": self.confidence,
            "tags": list(self.tags),
            "sources": self.sources,
        }


# Pre-loaded evolutionary hypotheses
def get_evolutionary_hypotheses() -> List[EvolutionaryHypothesis]:
    """Get pre-loaded examples of evolutionary hypotheses."""
    hypotheses = []

    # 1. Theory of Mind evolution
    tom = EvolutionaryHypothesis(
        name="Theory of Mind as Social Adaptation",
        description=(
            "The ability to attribute mental states to oneself and others "
            "evolved as an adaptation for complex social living, enabling "
            "prediction of others' behavior, cooperation, and deception detection."
        ),
        trait_explained="Theory of Mind (mentalizing)",
        adaptive_function="Enhanced social coordination and prediction",
        evolutionary_pressures=[
            EvolutionaryPressure.SOCIAL,
            EvolutionaryPressure.COOPERATION,
            EvolutionaryPressure.RECIPROCAL_ALTRUISM,
        ],
        timescale=TimeScale.PHYLOGENETIC,
        consciousness_links=[
            "Self-awareness",
            "Meta-cognition",
            "Social consciousness",
        ],
        modern_manifestations=[
            "Empathy",
            "Perspective-taking",
            "Social intuition",
        ],
        tags={"social", "cognition", "primates", "cooperation"},
        controversy_level="low",
    )
    tom.add_evidence(
        description="Comparative studies show ToM in great apes and other social mammals",
        evidence_type=EvidenceType.COMPARATIVE,
        strength=0.8,
        source="Premack & Woodruff (1978). Does the chimpanzee have a theory of mind?",
        year=1978,
    )
    tom.add_evidence(
        description="Neuroimaging shows specialized brain regions for mentalizing",
        evidence_type=EvidenceType.EXPERIMENTAL,
        strength=0.7,
        source="Saxe & Kanwisher (2003). People thinking about thinking people",
    )
    tom.update_confidence()
    hypotheses.append(tom)

    # 2. Consciousness as Integrated Information
    consciousness_iit = EvolutionaryHypothesis(
        name="Consciousness as Evolutionary Integration",
        description=(
            "Consciousness evolved as a solution to the integration problem - "
            "how to combine information from specialized modules into a unified "
            "representation that guides adaptive behavior."
        ),
        trait_explained="Unified conscious experience",
        adaptive_function="Integrated decision-making and behavioral flexibility",
        evolutionary_pressures=[
            EvolutionaryPressure.SURVIVAL,
            EvolutionaryPressure.ENVIRONMENTAL,
        ],
        timescale=TimeScale.PHYLOGENETIC,
        consciousness_links=[
            "Unity of consciousness",
            "Global workspace",
            "Integrated information",
        ],
        modern_manifestations=[
            "Multi-tasking ability",
            "Complex problem solving",
            "Creative synthesis",
        ],
        tags={"integration", "iit", "evolution", "unified"},
        controversy_level="moderate",
    )
    consciousness_iit.add_evidence(
        description="Increasing brain connectivity correlates with behavioral flexibility",
        evidence_type=EvidenceType.COMPARATIVE,
        strength=0.6,
    )
    consciousness_iit.update_confidence()
    hypotheses.append(consciousness_iit)

    # 3. Emotions as Adaptive Programs
    emotions = EvolutionaryHypothesis(
        name="Emotions as Evolved Adaptive Programs",
        description=(
            "Basic emotions evolved as coordinated response programs to "
            "recurrent adaptive challenges, with specific physiological, "
            "cognitive, and behavioral components."
        ),
        trait_explained="Basic emotions (fear, anger, joy, sadness, disgust, surprise)",
        adaptive_function="Rapid, coordinated response to fitness-relevant situations",
        evolutionary_pressures=[
            EvolutionaryPressure.SURVIVAL,
            EvolutionaryPressure.REPRODUCTION,
            EvolutionaryPressure.SOCIAL,
        ],
        timescale=TimeScale.PHYLOGENETIC,
        consciousness_links=[
            "Affective consciousness",
            "Emotional experience",
            "Bodily awareness",
        ],
        modern_manifestations=[
            "Emotional disorders when mismatched to modern environment",
            "Cross-cultural emotion recognition",
        ],
        tags={"emotion", "adaptation", "basic", "evolutionary"},
        controversy_level="moderate",
    )
    emotions.add_evidence(
        description="Cross-cultural studies show universal basic emotions",
        evidence_type=EvidenceType.CROSS_CULTURAL,
        strength=0.8,
        source="Ekman (1992). An argument for basic emotions",
        year=1992,
    )
    emotions.add_evidence(
        description="Distinct neural circuits for different emotions",
        evidence_type=EvidenceType.EXPERIMENTAL,
        strength=0.7,
    )
    emotions.update_confidence()
    hypotheses.append(emotions)

    # 4. Sleep and Dream Evolution
    sleep = EvolutionaryHypothesis(
        name="Sleep and Dreaming as Cognitive Maintenance",
        description=(
            "Sleep evolved for multiple functions including memory consolidation, "
            "neural maintenance, and threat simulation. Dreaming may serve as "
            "offline processing and threat rehearsal."
        ),
        trait_explained="Sleep and dreaming",
        adaptive_function="Cognitive maintenance and memory processing",
        evolutionary_pressures=[
            EvolutionaryPressure.SURVIVAL,
            EvolutionaryPressure.ENVIRONMENTAL,
        ],
        timescale=TimeScale.PHYLOGENETIC,
        consciousness_links=[
            "Altered states of consciousness",
            "Dream consciousness",
            "Memory consolidation",
        ],
        modern_manifestations=[
            "Sleep disorders",
            "Lucid dreaming",
            "Creative insight during sleep",
        ],
        tags={"sleep", "dreaming", "memory", "maintenance"},
        controversy_level="moderate",
    )
    sleep.add_evidence(
        description="Sleep deprivation impairs cognitive function",
        evidence_type=EvidenceType.EXPERIMENTAL,
        strength=0.9,
    )
    sleep.add_evidence(
        description="REM sleep correlates with memory consolidation",
        evidence_type=EvidenceType.EXPERIMENTAL,
        strength=0.7,
    )
    sleep.update_confidence()
    hypotheses.append(sleep)

    # 5. Language and Symbolic Consciousness
    language = EvolutionaryHypothesis(
        name="Language as Catalyst for Symbolic Consciousness",
        description=(
            "The evolution of language enabled symbolic thought, abstract reasoning, "
            "and temporal projection, fundamentally transforming human consciousness "
            "and enabling culture, planning, and collective intentionality."
        ),
        trait_explained="Symbolic thought and language",
        adaptive_function="Enhanced communication, cooperation, and cultural transmission",
        evolutionary_pressures=[
            EvolutionaryPressure.SOCIAL,
            EvolutionaryPressure.COOPERATION,
            EvolutionaryPressure.SEXUAL_SELECTION,
        ],
        timescale=TimeScale.PHYLOGENETIC,
        consciousness_links=[
            "Symbolic consciousness",
            "Narrative self",
            "Temporal projection",
        ],
        modern_manifestations=[
            "Inner speech",
            "Cultural diversity",
            "Scientific and artistic achievement",
        ],
        tags={"language", "symbolic", "culture", "human"},
        controversy_level="moderate",
    )
    language.add_evidence(
        description="Archaeological evidence of symbolic artifacts coincides with language evolution",
        evidence_type=EvidenceType.ARCHAEOLOGICAL,
        strength=0.6,
    )
    language.update_confidence()
    hypotheses.append(language)

    return hypotheses


# Pre-loaded evolutionary layers
def get_evolutionary_layers() -> List[EvolutionaryLayer]:
    """Get pre-loaded examples of evolutionary layers of consciousness."""
    layers = []

    # 1. Basic Sensory Awareness
    sensory = EvolutionaryLayer(
        name="Basic Sensory Awareness",
        description=(
            "Foundational layer present in most animals: capacity for sensory "
            "experience and basic awareness of environment without complex "
            "integration or self-awareness."
        ),
        timescale=TimeScale.PHYLOGENETIC,
        approximate_years_ago="500+ million years",
        cognitive_abilities=[
            "Sensory perception",
            "Basic learning (habituation, sensitization)",
            "Stimulus-response associations",
        ],
        social_complexity="simple",
        brain_changes=[
            "Development of sensory systems",
            "Basic neural networks for perception",
        ],
        consciousness_aspects=[
            "Sensory qualia",
            "Present-moment awareness",
            "No self-reflection",
        ],
        fossil_evidence=["Early nervous system fossils"],
        comparative_evidence=["Present in insects, fish, reptiles"],
        following_layer="Emotional Consciousness",
        modern_vestiges=[
            "Automatic sensory processing",
            "Reflex responses",
            "Basic perceptual awareness",
        ],
        tags={"sensory", "basic", "animal", "foundational"},
        confidence=0.8,
    )
    layers.append(sensory)

    # 2. Emotional Consciousness
    emotional = EvolutionaryLayer(
        name="Emotional Consciousness",
        description=(
            "Layer emerging in mammals: capacity for affective experience, "
            "basic emotions, and valence (pleasure/pain) guiding behavior "
            "toward fitness-enhancing outcomes."
        ),
        timescale=TimeScale.PHYLOGENETIC,
        approximate_years_ago="200 million years",
        cognitive_abilities=[
            "Emotional experience",
            "Approach/avoidance based on affect",
            "Social bonding",
        ],
        social_complexity="moderate",
        brain_changes=[
            "Limbic system development",
            "Emotion circuits",
            "Social brain networks",
        ],
        consciousness_aspects=[
            "Affective experience",
            "Emotional valence",
            "Basic social awareness",
        ],
        fossil_evidence=["Mammalian brain structure fossils"],
        comparative_evidence=["Present in mammals, especially social species"],
        preceding_layer="Basic Sensory Awareness",
        following_layer="Self-Awareness",
        modern_vestiges=[
            "Basic emotions",
            "Social attachments",
            "Affective decision-making",
        ],
        tags={"emotional", "mammalian", "affective", "social"},
        confidence=0.7,
    )
    layers.append(emotional)

    # 3. Self-Awareness
    self_aware = EvolutionaryLayer(
        name="Self-Awareness",
        description=(
            "Layer present in great apes and some other species: capacity for "
            "self-recognition, understanding of self as distinct entity, "
            "and basic theory of mind."
        ),
        timescale=TimeScale.PHYLOGENETIC,
        approximate_years_ago="10-20 million years",
        cognitive_abilities=[
            "Mirror self-recognition",
            "Basic theory of mind",
            "Deferred imitation",
        ],
        social_complexity="complex",
        brain_changes=[
            "Prefrontal cortex expansion",
            "Default mode network precursors",
            "Advanced social cognition areas",
        ],
        consciousness_aspects=[
            "Self-recognition",
            "Social perspective-taking",
            "Basic metacognition",
        ],
        fossil_evidence=["Great ape endocasts showing brain expansion"],
        comparative_evidence=["Mirror test in great apes, dolphins, elephants"],
        preceding_layer="Emotional Consciousness",
        following_layer="Symbolic Consciousness",
        modern_vestiges=[
            "Self-conscious emotions",
            "Social comparison",
            "Personal identity",
        ],
        tags={"self", "great-apes", "metacognition", "social"},
        confidence=0.6,
    )
    layers.append(self_aware)

    # 4. Symbolic Consciousness
    symbolic = EvolutionaryLayer(
        name="Symbolic Consciousness",
        description=(
            "Uniquely human layer: capacity for symbolic thought, language, "
            "abstract reasoning, and temporal projection. Enables culture, "
            "art, science, and complex social organization."
        ),
        timescale=TimeScale.PHYLOGENETIC,
        approximate_years_ago="100,000-200,000 years",
        cognitive_abilities=[
            "Language",
            "Abstract reasoning",
            "Temporal projection (past/future)",
            "Symbolic representation",
        ],
        social_complexity="highly complex",
        brain_changes=[
            "Language areas (Broca's, Wernicke's)",
            "Prefrontal cortex expansion",
            "Default mode network",
        ],
        consciousness_aspects=[
            "Inner speech",
            "Narrative self",
            "Cultural identity",
            "Abstract thought",
        ],
        archaeological_evidence=[
            "Cave art",
            "Symbolic artifacts",
            "Burial practices",
        ],
        preceding_layer="Self-Awareness",
        modern_vestiges=[
            "All human culture",
            "Science and technology",
            "Art and religion",
        ],
        tags={"human", "symbolic", "language", "culture"},
        confidence=0.7,
    )
    layers.append(symbolic)

    return layers
