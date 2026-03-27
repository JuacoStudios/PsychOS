"""
Consciousness Theory Models for PsycheOS.

Defines data structures for representing consciousness theories,
including core claims, evidence, criticisms, and relationships.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Set


class TheoryCategory(Enum):
    """Categories of consciousness theories."""

    NEUROSCIENTIFIC = "neuroscientific"  # Brain-based theories
    PHILOSOPHICAL = "philosophical"  # Philosophical theories
    COGNITIVE = "cognitive"  # Cognitive/psychological theories
    INTEGRATIVE = "integrative"  # Integrative/multi-disciplinary theories
    SPIRITUAL = "spiritual"  # Spiritual/meditative traditions
    COMPUTATIONAL = "computational"  # AI/computational theories
    QUANTUM = "quantum"  # Quantum consciousness theories


class EvidenceStrength(Enum):
    """Strength of evidence supporting a theory."""

    STRONG = "strong"  # Multiple replicated studies, consensus
    MODERATE = "moderate"  # Some supporting evidence, ongoing research
    WEAK = "weak"  # Preliminary or controversial evidence
    SPECULATIVE = "speculative"  # Theoretical, little empirical support
    CONTRADICTED = "contradicted"  # Evidence contradicts the theory


@dataclass
class Evidence:
    """Evidence supporting or contradicting a theory."""

    description: str
    source: str  # Paper, study, or source reference
    year: Optional[int] = None
    strength: EvidenceStrength = EvidenceStrength.MODERATE
    methodology: Optional[str] = None  # Experimental method used
    findings: Optional[str] = None  # Key findings
    limitations: Optional[str] = None  # Limitations of the evidence


@dataclass
class Criticism:
    """Criticism or challenge to a theory."""

    description: str
    source: Optional[str] = None
    year: Optional[int] = None
    severity: str = "moderate"  # mild, moderate, severe
    response: Optional[str] = None  # How proponents respond to this criticism


@dataclass
class ConsciousnessTheory:
    """A theory of consciousness."""

    # Core identification
    name: str
    category: TheoryCategory
    description: str

    # Proponents and history
    key_proponents: List[str] = field(default_factory=list)
    year_developed: Optional[int] = None
    historical_context: Optional[str] = None

    # Core claims
    core_claims: List[str] = field(default_factory=list)

    # Evidence and support
    supporting_evidence: List[Evidence] = field(default_factory=list)
    contradictory_evidence: List[Evidence] = field(default_factory=list)

    # Criticisms and debates
    criticisms: List[Criticism] = field(default_factory=list)
    ongoing_debates: List[str] = field(default_factory=list)

    # Relationships to other concepts
    related_theories: List[str] = field(default_factory=list)
    applications: List[str] = field(default_factory=list)  # Practical applications
    tags: Set[str] = field(default_factory=set)

    # Metadata
    sources: List[str] = field(default_factory=list)  # Source references
    last_updated: str = field(default_factory=lambda: datetime.now().isoformat())
    confidence: float = 0.5  # Overall confidence in theory (0.0 to 1.0)

    def to_dict(self) -> Dict:
        """Convert theory to dictionary for serialization."""
        return {
            "name": self.name,
            "category": self.category.value,
            "description": self.description,
            "key_proponents": self.key_proponents,
            "year_developed": self.year_developed,
            "historical_context": self.historical_context,
            "core_claims": self.core_claims,
            "supporting_evidence": [
                {
                    "description": e.description,
                    "source": e.source,
                    "year": e.year,
                    "strength": e.strength.value,
                    "methodology": e.methodology,
                    "findings": e.findings,
                    "limitations": e.limitations,
                }
                for e in self.supporting_evidence
            ],
            "contradictory_evidence": [
                {
                    "description": e.description,
                    "source": e.source,
                    "year": e.year,
                    "strength": e.strength.value,
                    "methodology": e.methodology,
                    "findings": e.findings,
                    "limitations": e.limitations,
                }
                for e in self.contradictory_evidence
            ],
            "criticisms": [
                {
                    "description": c.description,
                    "source": c.source,
                    "year": c.year,
                    "severity": c.severity,
                    "response": c.response,
                }
                for c in self.criticisms
            ],
            "ongoing_debates": self.ongoing_debates,
            "related_theories": self.related_theories,
            "applications": self.applications,
            "tags": list(self.tags),
            "sources": self.sources,
            "last_updated": self.last_updated,
            "confidence": self.confidence,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "ConsciousnessTheory":
        """Create theory from dictionary."""
        # Convert evidence lists
        supporting_evidence = []
        for e_data in data.get("supporting_evidence", []):
            evidence = Evidence(
                description=e_data["description"],
                source=e_data["source"],
                year=e_data.get("year"),
                strength=EvidenceStrength(e_data.get("strength", "moderate")),
                methodology=e_data.get("methodology"),
                findings=e_data.get("findings"),
                limitations=e_data.get("limitations"),
            )
            supporting_evidence.append(evidence)

        contradictory_evidence = []
        for e_data in data.get("contradictory_evidence", []):
            evidence = Evidence(
                description=e_data["description"],
                source=e_data["source"],
                year=e_data.get("year"),
                strength=EvidenceStrength(e_data.get("strength", "moderate")),
                methodology=e_data.get("methodology"),
                findings=e_data.get("findings"),
                limitations=e_data.get("limitations"),
            )
            contradictory_evidence.append(evidence)

        # Convert criticisms
        criticisms = []
        for c_data in data.get("criticisms", []):
            criticism = Criticism(
                description=c_data["description"],
                source=c_data.get("source"),
                year=c_data.get("year"),
                severity=c_data.get("severity", "moderate"),
                response=c_data.get("response"),
            )
            criticisms.append(criticism)

        return cls(
            name=data["name"],
            category=TheoryCategory(data["category"]),
            description=data["description"],
            key_proponents=data.get("key_proponents", []),
            year_developed=data.get("year_developed"),
            historical_context=data.get("historical_context"),
            core_claims=data.get("core_claims", []),
            supporting_evidence=supporting_evidence,
            contradictory_evidence=contradictory_evidence,
            criticisms=criticisms,
            ongoing_debates=data.get("ongoing_debates", []),
            related_theories=data.get("related_theories", []),
            applications=data.get("applications", []),
            tags=set(data.get("tags", [])),
            sources=data.get("sources", []),
            last_updated=data.get("last_updated", datetime.now().isoformat()),
            confidence=data.get("confidence", 0.5),
        )

    def add_evidence(
        self,
        description: str,
        source: str,
        supports: bool = True,
        year: Optional[int] = None,
        strength: EvidenceStrength = EvidenceStrength.MODERATE,
        **kwargs,
    ) -> None:
        """Add evidence to the theory."""
        evidence = Evidence(
            description=description,
            source=source,
            year=year,
            strength=strength,
            **kwargs,
        )

        if supports:
            self.supporting_evidence.append(evidence)
        else:
            self.contradictory_evidence.append(evidence)

    def add_criticism(
        self,
        description: str,
        source: Optional[str] = None,
        year: Optional[int] = None,
        severity: str = "moderate",
        response: Optional[str] = None,
    ) -> None:
        """Add criticism to the theory."""
        criticism = Criticism(
            description=description,
            source=source,
            year=year,
            severity=severity,
            response=response,
        )
        self.criticisms.append(criticism)

    def get_evidence_strength(self) -> Dict[EvidenceStrength, int]:
        """Get count of evidence by strength."""
        strength_counts = {strength: 0 for strength in EvidenceStrength}

        for evidence in self.supporting_evidence:
            strength_counts[evidence.strength] += 1

        return strength_counts

    def update_confidence(self) -> None:
        """Update confidence score based on evidence and criticisms."""
        # Simple heuristic for confidence
        # This should be refined with more sophisticated algorithms
        total_evidence = len(self.supporting_evidence) + len(self.contradictory_evidence)

        if total_evidence == 0:
            self.confidence = 0.3  # Low confidence without evidence
            return

        # Weight evidence by strength
        evidence_weight = 0
        for evidence in self.supporting_evidence:
            if evidence.strength == EvidenceStrength.STRONG:
                evidence_weight += 2
            elif evidence.strength == EvidenceStrength.MODERATE:
                evidence_weight += 1
            elif evidence.strength == EvidenceStrength.WEAK:
                evidence_weight += 0.5

        # Reduce weight for contradictory evidence
        for evidence in self.contradictory_evidence:
            if evidence.strength == EvidenceStrength.STRONG:
                evidence_weight -= 2
            elif evidence.strength == EvidenceStrength.MODERATE:
                evidence_weight -= 1
            elif evidence.strength == EvidenceStrength.WEAK:
                evidence_weight -= 0.5

        # Adjust for criticisms
        criticism_factor = 1.0
        for criticism in self.criticisms:
            if criticism.severity == "severe":
                criticism_factor *= 0.7
            elif criticism.severity == "moderate":
                criticism_factor *= 0.85
            elif criticism.severity == "mild":
                criticism_factor *= 0.95

        # Calculate final confidence (0.0 to 1.0)
        base_confidence = max(0.0, min(1.0, evidence_weight / total_evidence))
        self.confidence = base_confidence * criticism_factor


# Pre-loaded theory examples
def get_theory_examples() -> List[ConsciousnessTheory]:
    """Get pre-loaded examples of consciousness theories."""
    theories = []

    # 1. Integrated Information Theory (IIT)
    iit = ConsciousnessTheory(
        name="Integrated Information Theory (IIT)",
        category=TheoryCategory.NEUROSCIENTIFIC,
        description=(
            "A mathematical theory that defines consciousness as integrated information "
            "measured by Φ (phi). Proposes that any system with sufficient Φ is conscious, "
            "and the quality of consciousness is determined by the structure of cause-effect "
            "repertoires within the system."
        ),
        key_proponents=["Giulio Tononi", "Christof Koch"],
        year_developed=2004,
        core_claims=[
            "Consciousness corresponds to the capacity of a system to integrate information",
            "The quantity of consciousness is measured by Φ (phi)",
            "The quality of consciousness is determined by the structure of cause-effect repertoires",
            "Any system with sufficient Φ is conscious, regardless of substrate",
        ],
        tags={"neuroscience", "mathematical", "phi", "tononi", "koch"},
    )
    iit.add_evidence(
        description="Empirical predictions about which brain regions contribute to consciousness",
        source="Tononi & Koch (2015). Consciousness: here, there and everywhere?",
        year=2015,
        strength=EvidenceStrength.MODERATE,
    )
    iit.add_criticism(
        description="Φ is computationally intractable to calculate for complex systems",
        source="Scott Aaronson's critique",
        severity="moderate",
        response="IIT proponents acknowledge computational challenges but argue for theoretical importance",
    )
    iit.update_confidence()
    theories.append(iit)

    # 2. Global Workspace Theory (GWT)
    gwt = ConsciousnessTheory(
        name="Global Workspace Theory (GWT)",
        category=TheoryCategory.COGNITIVE,
        description=(
            "Proposes consciousness arises from a 'global workspace' in the brain "
            "where information becomes globally available to multiple cognitive systems. "
            "Conscious contents are those that win competition for access to this workspace."
        ),
        key_proponents=["Bernard Baars", "Stanislas Dehaene"],
        year_developed=1983,
        core_claims=[
            "Consciousness functions as a global workspace for information integration",
            "Unconscious processors compete for access to the global workspace",
            "Conscious contents are globally broadcast to multiple cognitive systems",
            "Attention gates access to the global workspace",
        ],
        tags={"cognitive", "workspace", "baars", "dehaene", "attention"},
    )
    gwt.add_evidence(
        description="Neural correlates of conscious access in prefrontal and parietal cortex",
        source="Dehaene et al. (2006). Conscious, preconscious, and subliminal processing",
        year=2006,
        strength=EvidenceStrength.STRONG,
    )
    gwt.add_criticism(
        description="Doesn't explain qualitative aspects of consciousness (qualia)",
        severity="moderate",
        response="GWT focuses on cognitive access rather than qualitative experience",
    )
    gwt.update_confidence()
    theories.append(gwt)

    # 3. Predictive Processing / Free Energy Principle
    pp = ConsciousnessTheory(
        name="Predictive Processing (Free Energy Principle)",
        category=TheoryCategory.NEUROSCIENTIFIC,
        description=(
            "The brain is a hierarchical prediction machine that minimizes prediction error. "
            "Conscious perception is the brain's 'best guess' about the causes of sensory input, "
            "with precision-weighted prediction errors driving updates to the model."
        ),
        key_proponents=["Karl Friston", "Anil Seth"],
        year_developed=2010,
        core_claims=[
            "The brain constantly generates predictions about sensory input",
            "Conscious perception reflects the brain's best hypothesis about causes",
            "Prediction errors drive learning and perception updates",
            "Attention corresponds to precision-weighting of prediction errors",
        ],
        tags={"friston", "seth", "prediction", "bayesian", "free-energy"},
    )
    pp.add_evidence(
        description="Explains various perceptual phenomena like binocular rivalry",
        source="Hohwy et al. (2008). Predictive coding explains binocular rivalry",
        year=2008,
        strength=EvidenceStrength.MODERATE,
    )
    pp.add_criticism(
        description="The framework is very general and difficult to falsify",
        severity="moderate",
        response="Proponents argue it provides a unifying framework for neuroscience",
    )
    pp.update_confidence()
    theories.append(pp)

    # 4. Higher-Order Thought Theory (HOT)
    hot = ConsciousnessTheory(
        name="Higher-Order Thought Theory (HOT)",
        category=TheoryCategory.PHILOSOPHICAL,
        description=(
            "Consciousness requires a higher-order mental state that represents "
            "a first-order mental state. A mental state is conscious only if one is "
            "aware of being in that state via a higher-order thought."
        ),
        key_proponents=["David Rosenthal", "Uriah Kriegel"],
        year_developed=1986,
        core_claims=[
            "Consciousness requires meta-representation",
            "First-order states become conscious when targeted by higher-order thoughts",
            "Higher-order thoughts are themselves unconscious",
            "Explains the difference between conscious and unconscious mental states",
        ],
        tags={"philosophical", "rosenthal", "meta-representation", "higher-order"},
    )
    hot.add_evidence(
        description="Explains cases of blindsight and subliminal perception",
        source="Rosenthal (2005). Consciousness and Mind",
        year=2005,
        strength=EvidenceStrength.MODERATE,
    )
    hot.add_criticism(
        description="Leads to infinite regress (what makes higher-order thoughts conscious?)",
        severity="moderate",
        response="Higher-order thoughts are intrinsically conscious or require no further representation",
    )
    hot.update_confidence()
    theories.append(hot)

    # 5. Attention Schema Theory (AST)
    ast = ConsciousnessTheory(
        name="Attention Schema Theory (AST)",
        category=TheoryCategory.NEUROSCIENTIFIC,
        description=(
            "Consciousness arises from the brain's model of its own attention. "
            "The brain constructs a simplified schema representing what attention is doing, "
            "and this schema gives rise to subjective experience."
        ),
        key_proponents=["Michael Graziano"],
        year_developed=2013,
        core_claims=[
            "The brain constructs models of its own attentional processes",
            "These models (attention schemas) give rise to subjective experience",
            "Explains why consciousness feels like something",
            "Provides a functional account of consciousness",
        ],
        tags={"graziano", "attention", "schema", "neuroscience"},
    )
    ast.add_evidence(
        description="Neural evidence for attention networks that could support such schemas",
        source="Graziano & Webb (2015). The attention schema theory",
        year=2015,
        strength=EvidenceStrength.WEAK,
    )
    ast.add_criticism(
        description="Doesn't fully explain qualitative aspects of consciousness",
        severity="mild",
    )
    ast.update_confidence()
    theories.append(ast)

    return theories


# Convenience function to get theory by name
def get_theory_by_name(name: str) -> Optional[ConsciousnessTheory]:
    """Get a pre-loaded theory by name."""
    for theory in get_theory_examples():
        if theory.name.lower() == name.lower():
            return theory
    return None