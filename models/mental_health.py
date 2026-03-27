"""
Mental Health Models for PsycheOS.

Defines data structures for representing mental health concepts,
disorders, symptoms, treatments, and their relationships to consciousness theories.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Set


class ConceptCategory(Enum):
    """Categories of mental health concepts."""

    DISORDER = "disorder"  # Clinical disorders (DSM/ICD)
    SYMPTOM = "symptom"  # Individual symptoms
    SYNDROME = "syndrome"  # Symptom clusters
    TRAIT = "trait"  # Personality traits, temperament
    STATE = "state"  # Transient mental states
    PROCESS = "process"  # Cognitive/emotional processes
    TREATMENT = "treatment"  # Interventions, therapies
    RISK_FACTOR = "risk_factor"  # Risk factors
    PROTECTIVE_FACTOR = "protective_factor"  # Protective factors
    MECHANISM = "mechanism"  # Underlying mechanisms


class SeverityLevel(Enum):
    """Severity levels for symptoms or disorders."""

    MILD = "mild"
    MODERATE = "moderate"
    SEVERE = "severe"


class TreatmentModality(Enum):
    """Modalities of treatment."""

    PSYCHOTHERAPY = "psychotherapy"
    PHARMACOTHERAPY = "pharmacotherapy"  # Medication
    NEUROMODULATION = "neuromodulation"  # TMS, ECT, etc.
    LIFESTYLE = "lifestyle"  # Exercise, diet, sleep
    SOCIAL = "social"  # Social support, community
    DIGITAL = "digital"  # Apps, online therapy
    COMBINATION = "combination"  # Multiple modalities


@dataclass
class Symptom:
    """A symptom of a mental health condition."""

    name: str
    description: str
    severity: SeverityLevel = SeverityLevel.MODERATE
    frequency: Optional[str] = None  # e.g., "episodic", "chronic"
    triggers: List[str] = field(default_factory=list)
    impact: Optional[str] = None  # Impact on functioning


@dataclass
class Treatment:
    """A treatment for mental health conditions."""

    name: str
    description: str
    modality: TreatmentModality
    efficacy: float = 0.5  # 0.0 to 1.0
    evidence_level: str = "moderate"  # strong, moderate, weak
    mechanisms: List[str] = field(default_factory=list)  # How it works
    side_effects: List[str] = field(default_factory=list)
    contraindications: List[str] = field(default_factory=list)


@dataclass
class MentalHealthConcept:
    """A mental health concept (disorder, symptom, treatment, etc.)."""

    # Core identification
    name: str
    category: ConceptCategory
    description: str

    # Classification
    diagnostic_criteria: List[str] = field(default_factory=list)
    dsm_code: Optional[str] = None  # DSM-5 code
    icd_code: Optional[str] = None  # ICD-11 code
    prevalence: Optional[str] = None  # e.g., "1-2% of population"
    onset: Optional[str] = None  # Typical age of onset
    course: Optional[str] = None  # Typical course (episodic, chronic, etc.)

    # Components
    symptoms: List[Symptom] = field(default_factory=list)
    treatments: List[Treatment] = field(default_factory=list)
    risk_factors: List[str] = field(default_factory=list)
    protective_factors: List[str] = field(default_factory=list)

    # Relationships to consciousness theories
    related_theories: List[str] = field(default_factory=list)
    consciousness_correlates: List[str] = field(default_factory=list)
    altered_states: List[str] = field(default_factory=list)  # Related altered states

    # Evidence and research
    evidence_base: str = "moderate"  # strong, moderate, weak, controversial
    research_directions: List[str] = field(default_factory=list)
    open_questions: List[str] = field(default_factory=list)

    # Metadata
    tags: Set[str] = field(default_factory=set)
    sources: List[str] = field(default_factory=list)
    last_updated: str = field(default_factory=lambda: "2024-01-01")

    def to_dict(self) -> Dict:
        """Convert concept to dictionary for serialization."""
        return {
            "name": self.name,
            "category": self.category.value,
            "description": self.description,
            "diagnostic_criteria": self.diagnostic_criteria,
            "dsm_code": self.dsm_code,
            "icd_code": self.icd_code,
            "prevalence": self.prevalence,
            "onset": self.onset,
            "course": self.course,
            "symptoms": [
                {
                    "name": s.name,
                    "description": s.description,
                    "severity": s.severity.value,
                    "frequency": s.frequency,
                    "triggers": s.triggers,
                    "impact": s.impact,
                }
                for s in self.symptoms
            ],
            "treatments": [
                {
                    "name": t.name,
                    "description": t.description,
                    "modality": t.modality.value,
                    "efficacy": t.efficacy,
                    "evidence_level": t.evidence_level,
                    "mechanisms": t.mechanisms,
                    "side_effects": t.side_effects,
                    "contraindications": t.contraindications,
                }
                for t in self.treatments
            ],
            "risk_factors": self.risk_factors,
            "protective_factors": self.protective_factors,
            "related_theories": self.related_theories,
            "consciousness_correlates": self.consciousness_correlates,
            "altered_states": self.altered_states,
            "evidence_base": self.evidence_base,
            "research_directions": self.research_directions,
            "open_questions": self.open_questions,
            "tags": list(self.tags),
            "sources": self.sources,
            "last_updated": self.last_updated,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "MentalHealthConcept":
        """Create concept from dictionary."""
        # Convert symptoms
        symptoms = []
        for s_data in data.get("symptoms", []):
            symptom = Symptom(
                name=s_data["name"],
                description=s_data["description"],
                severity=SeverityLevel(s_data.get("severity", "moderate")),
                frequency=s_data.get("frequency"),
                triggers=s_data.get("triggers", []),
                impact=s_data.get("impact"),
            )
            symptoms.append(symptom)

        # Convert treatments
        treatments = []
        for t_data in data.get("treatments", []):
            treatment = Treatment(
                name=t_data["name"],
                description=t_data["description"],
                modality=TreatmentModality(t_data["modality"]),
                efficacy=t_data.get("efficacy", 0.5),
                evidence_level=t_data.get("evidence_level", "moderate"),
                mechanisms=t_data.get("mechanisms", []),
                side_effects=t_data.get("side_effects", []),
                contraindications=t_data.get("contraindications", []),
            )
            treatments.append(treatment)

        return cls(
            name=data["name"],
            category=ConceptCategory(data["category"]),
            description=data["description"],
            diagnostic_criteria=data.get("diagnostic_criteria", []),
            dsm_code=data.get("dsm_code"),
            icd_code=data.get("icd_code"),
            prevalence=data.get("prevalence"),
            onset=data.get("onset"),
            course=data.get("course"),
            symptoms=symptoms,
            treatments=treatments,
            risk_factors=data.get("risk_factors", []),
            protective_factors=data.get("protective_factors", []),
            related_theories=data.get("related_theories", []),
            consciousness_correlates=data.get("consciousness_correlates", []),
            altered_states=data.get("altered_states", []),
            evidence_base=data.get("evidence_base", "moderate"),
            research_directions=data.get("research_directions", []),
            open_questions=data.get("open_questions", []),
            tags=set(data.get("tags", [])),
            sources=data.get("sources", []),
            last_updated=data.get("last_updated", "2024-01-01"),
        )

    def add_symptom(
        self,
        name: str,
        description: str,
        severity: SeverityLevel = SeverityLevel.MODERATE,
        **kwargs,
    ) -> None:
        """Add a symptom to the concept."""
        symptom = Symptom(
            name=name,
            description=description,
            severity=severity,
            **kwargs,
        )
        self.symptoms.append(symptom)

    def add_treatment(
        self,
        name: str,
        description: str,
        modality: TreatmentModality,
        efficacy: float = 0.5,
        **kwargs,
    ) -> None:
        """Add a treatment to the concept."""
        treatment = Treatment(
            name=name,
            description=description,
            modality=modality,
            efficacy=efficacy,
            **kwargs,
        )
        self.treatments.append(treatment)

    def get_treatment_efficacy_summary(self) -> Dict[str, float]:
        """Get summary of treatment efficacies."""
        summary = {}
        for treatment in self.treatments:
            summary[treatment.name] = treatment.efficacy
        return summary

    def link_to_theory(self, theory_name: str, relationship: str = "related") -> None:
        """Link this concept to a consciousness theory."""
        if theory_name not in self.related_theories:
            self.related_theories.append(theory_name)


# Pre-loaded mental health concept examples
def get_mental_health_examples() -> List[MentalHealthConcept]:
    """Get pre-loaded examples of mental health concepts."""
    concepts = []

    # 1. Major Depressive Disorder
    mdd = MentalHealthConcept(
        name="Major Depressive Disorder (MDD)",
        category=ConceptCategory.DISORDER,
        description=(
            "A mood disorder characterized by persistent feelings of sadness, "
            "hopelessness, and loss of interest or pleasure in activities. "
            "Significantly impairs daily functioning."
        ),
        dsm_code="296.xx",
        icd_code="F32",
        prevalence="7-8% of adults annually",
        onset="Late adolescence to mid-adulthood",
        course="Episodic, with recurrent episodes common",
        evidence_base="strong",
        tags={"mood", "depression", "affective", "clinical"},
    )
    mdd.add_symptom(
        name="Depressed mood",
        description="Persistent sadness, emptiness, or hopelessness",
        severity=SeverityLevel.SEVERE,
        frequency="daily",
        impact="Significant distress and impairment",
    )
    mdd.add_symptom(
        name="Anhedonia",
        description="Markedly diminished interest or pleasure in activities",
        severity=SeverityLevel.MODERATE,
    )
    mdd.add_treatment(
        name="Cognitive Behavioral Therapy (CBT)",
        description="Psychotherapy focusing on changing negative thought patterns",
        modality=TreatmentModality.PSYCHOTHERAPY,
        efficacy=0.7,
        evidence_level="strong",
        mechanisms=["Cognitive restructuring", "Behavioral activation"],
    )
    mdd.add_treatment(
        name="SSRI Antidepressants",
        description="Selective serotonin reuptake inhibitors",
        modality=TreatmentModality.PHARMACOTHERAPY,
        efficacy=0.6,
        evidence_level="strong",
        side_effects=["Nausea", "Sexual dysfunction", "Weight gain"],
    )
    mdd.link_to_theory("Predictive Processing (Free Energy Principle)")
    mdd.link_to_theory("Global Workspace Theory (GWT)")
    concepts.append(mdd)

    # 2. Generalized Anxiety Disorder (GAD)
    gad = MentalHealthConcept(
        name="Generalized Anxiety Disorder (GAD)",
        category=ConceptCategory.DISORDER,
        description=(
            "Excessive, uncontrollable worry about everyday things, "
            "disproportionate to the actual source of worry."
        ),
        dsm_code="300.02",
        icd_code="F41.1",
        prevalence="3-5% of population",
        onset="Variable, often early adulthood",
        course="Chronic, with waxing and waning symptoms",
        evidence_base="strong",
        tags={"anxiety", "worry", "clinical"},
    )
    gad.add_symptom(
        name="Excessive worry",
        description="Difficult to control worry about multiple domains",
        severity=SeverityLevel.MODERATE,
        frequency="daily",
    )
    gad.add_symptom(
        name="Restlessness",
        description="Feeling keyed up or on edge",
        severity=SeverityLevel.MILD,
    )
    gad.add_treatment(
        name="Mindfulness-Based Stress Reduction (MBSR)",
        description="Meditation-based program for stress and anxiety",
        modality=TreatmentModality.PSYCHOTHERAPY,
        efficacy=0.65,
        evidence_level="strong",
    )
    gad.link_to_theory("Predictive Processing (Free Energy Principle)")
    concepts.append(gad)

    # 3. Mindfulness
    mindfulness = MentalHealthConcept(
        name="Mindfulness",
        category=ConceptCategory.PROCESS,
        description=(
            "The psychological process of bringing one's attention to experiences "
            "occurring in the present moment, developed through meditation practice."
        ),
        evidence_base="strong",
        tags={"meditation", "attention", "wellbeing", "process"},
    )
    mindfulness.add_treatment(
        name="Mindfulness Meditation",
        description="Formal practice of focusing attention on present moment",
        modality=TreatmentModality.LIFESTYLE,
        efficacy=0.7,
        evidence_level="strong",
        mechanisms=["Attention regulation", "Emotion regulation", "Body awareness"],
    )
    mindfulness.consciousness_correlates = [
        "Increased meta-awareness",
        "Altered sense of self",
        "Changes in time perception",
    ]
    mindfulness.link_to_theory("Attention Schema Theory (AST)")
    mindfulness.link_to_theory("Predictive Processing (Free Energy Principle)")
    concepts.append(mindfulness)

    # 4. Flow State
    flow = MentalHealthConcept(
        name="Flow State",
        category=ConceptCategory.STATE,
        description=(
            "A state of complete immersion and focused energy in an activity, "
            "characterized by loss of self-consciousness and distorted sense of time."
        ),
        evidence_base="moderate",
        tags={"positive", "peak experience", "creativity", "state"},
    )
    flow.consciousness_correlates = [
        "Altered time perception",
        "Reduced self-referential processing",
        "Increased task focus",
    ]
    flow.link_to_theory("Global Workspace Theory (GWT)")
    concepts.append(flow)

    # 5. Trauma
    trauma = MentalHealthConcept(
        name="Psychological Trauma",
        category=ConceptCategory.PROCESS,
        description=(
            "Emotional response to a terrible event, often involving "
            "threat to life or safety, with lasting effects on mental functioning."
        ),
        evidence_base="strong",
        tags={"trauma", "stress", "memory", "process"},
    )
    trauma.altered_states = [
        "Dissociation",
        "Flashbacks",
        "Hypervigilance",
    ]
    trauma.link_to_theory("Predictive Processing (Free Energy Principle)")
    concepts.append(trauma)

    return concepts


# Convenience function to get concept by name
def get_concept_by_name(name: str) -> Optional[MentalHealthConcept]:
    """Get a pre-loaded concept by name."""
    for concept in get_mental_health_examples():
        if concept.name.lower() == name.lower():
            return concept
    return None


# Function to get concepts by category
def get_concepts_by_category(category: ConceptCategory) -> List[MentalHealthConcept]:
    """Get all pre-loaded concepts in a category."""
    return [
        concept for concept in get_mental_health_examples()
        if concept.category == category
    ]