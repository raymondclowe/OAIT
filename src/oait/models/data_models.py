"""Data models for OAIT student and session state."""

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field


class LearningStyle(str, Enum):
    """Student's preferred learning style."""

    VISUAL = "visual"
    VERBAL = "verbal"
    KINESTHETIC = "kinesthetic"


class PatienceLevel(str, Enum):
    """How patient the student is with interventions."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class CompetencyLevel(str, Enum):
    """Student's competency in a topic."""

    UNKNOWN = "unknown"
    STRUGGLING = "struggling"
    MASTERED = "mastered"


class PedagogyProfile(BaseModel):
    """Pedagogy profile for a student."""

    patience_level: PatienceLevel = PatienceLevel.MEDIUM
    preferred_learning_style: LearningStyle = LearningStyle.VISUAL
    preferred_analogies: str = ""
    response_to_correction: str = ""
    optimal_intervention_delay: float = 3.0  # seconds


class SessionHistoryEntry(BaseModel):
    """A single session history entry."""

    date: datetime
    topics_covered: List[str] = Field(default_factory=list)
    breakthroughs: List[str] = Field(default_factory=list)
    persistent_errors: List[str] = Field(default_factory=list)


class StudentModel(BaseModel):
    """Long-term student model persisted across sessions."""

    student_id: str
    competencies: Dict[str, CompetencyLevel] = Field(default_factory=dict)
    pedagogy_profile: PedagogyProfile = Field(default_factory=PedagogyProfile)
    session_history: List[SessionHistoryEntry] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    def update_competency(self, topic: str, level: CompetencyLevel) -> None:
        """Update competency level for a topic."""
        self.competencies[topic] = level
        self.updated_at = datetime.now()

    def add_session(self, entry: SessionHistoryEntry) -> None:
        """Add a session history entry."""
        self.session_history.append(entry)
        self.updated_at = datetime.now()


class StudentState(str, Enum):
    """Current state of the student."""

    ENGAGED = "engaged"
    CONFUSED = "confused"
    STUCK = "stuck"
    MAKING_PROGRESS = "making_progress"


class ErrorType(str, Enum):
    """Type of error detected."""

    NONE = "none"
    CONCEPTUAL = "conceptual"
    COMPUTATIONAL = "computational"
    NOTATION = "notation"


class ErrorSeverity(str, Enum):
    """Severity of detected error."""

    NONE = "none"
    MINOR = "minor"
    MODERATE = "moderate"
    CRITICAL = "critical"


class ActionDecision(str, Enum):
    """Decision on what action to take."""

    WAIT = "WAIT"
    UPDATE_DB = "UPDATE_DB"
    SPEAK = "SPEAK"


class InterventionStrategy(str, Enum):
    """Pedagogical intervention strategy."""

    SOCRATIC = "socratic"
    DIRECT = "direct"
    HINT = "hint"
    EXAMPLE = "example"


class TranscriptEntry(BaseModel):
    """A single transcript entry with timestamp."""

    text: str
    timestamp: float


class Observation(BaseModel):
    """Aggregated observation from audio and visual streams."""

    visual: str = ""  # Description of whiteboard
    audio: str = ""  # Summary of recent speech
    context: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.now)


class Analysis(BaseModel):
    """Analysis of current student state."""

    student_state: StudentState
    error_detected: bool = False
    error_type: ErrorType = ErrorType.NONE
    error_severity: ErrorSeverity = ErrorSeverity.NONE
    explicit_question: bool = False
    confidence: float = 0.0


class Decision(BaseModel):
    """Decision on intervention."""

    action: ActionDecision
    reasoning: str
    confidence: float
    strategy: Optional[InterventionStrategy] = None
    estimated_duration: float = 0.0  # seconds
    fallback_plan: str = ""
    response_text: Optional[str] = None  # Text to speak if action is SPEAK


class InternalMonologue(BaseModel):
    """AI's internal thought process."""

    timestamp: datetime = Field(default_factory=datetime.now)
    observation: Observation
    analysis: Analysis
    decision: Decision


class SessionState(BaseModel):
    """Working memory for current tutoring session."""

    session_id: str
    student_id: str
    current_problem_image: Optional[str] = None  # Base64 or path
    last_significant_change: float = 0.0
    student_speech_buffer: List[TranscriptEntry] = Field(default_factory=list)
    silence_duration: float = 0.0
    ai_internal_monologue: List[InternalMonologue] = Field(default_factory=list)
    current_problem_analysis: Dict[str, Any] = Field(default_factory=dict)
    intervention_candidates: List[str] = Field(default_factory=list)
    student_is_speaking: bool = False
    student_is_writing: bool = False
    last_intervention_time: float = 0.0
    started_at: datetime = Field(default_factory=datetime.now)
    
    # Runtime components (not serialized)
    transcript_buffer: Any = Field(default=None, exclude=True)
    silence_detector: Any = Field(default=None, exclude=True)

    def add_transcript(self, text: str, timestamp: float) -> None:
        """Add a transcript entry."""
        self.student_speech_buffer.append(TranscriptEntry(text=text, timestamp=timestamp))

    def add_monologue(self, monologue: InternalMonologue) -> None:
        """Add an internal monologue entry."""
        self.ai_internal_monologue.append(monologue)

    def get_recent_transcripts(self, duration: float) -> List[TranscriptEntry]:
        """Get transcripts from the last N seconds."""
        cutoff = datetime.now().timestamp() - duration
        return [entry for entry in self.student_speech_buffer if entry.timestamp > cutoff]
