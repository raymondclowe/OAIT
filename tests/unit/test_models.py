"""Basic unit tests for data models."""

import pytest
from datetime import datetime
from oait.models.data_models import (
    StudentModel,
    SessionState,
    PedagogyProfile,
    CompetencyLevel,
    TranscriptEntry,
    Observation,
    Analysis,
    Decision,
    StudentState,
    ActionDecision,
)


def test_student_model_creation() -> None:
    """Test creating a student model."""
    model = StudentModel(student_id="student_001")
    
    assert model.student_id == "student_001"
    assert len(model.competencies) == 0
    assert model.pedagogy_profile is not None
    assert len(model.session_history) == 0


def test_student_model_update_competency() -> None:
    """Test updating competency."""
    model = StudentModel(student_id="student_001")
    
    model.update_competency("algebra", CompetencyLevel.MASTERED)
    
    assert model.competencies["algebra"] == CompetencyLevel.MASTERED
    assert model.updated_at > model.created_at


def test_session_state_creation() -> None:
    """Test creating a session state."""
    state = SessionState(
        session_id="session_001",
        student_id="student_001",
    )
    
    assert state.session_id == "session_001"
    assert state.student_id == "student_001"
    assert len(state.student_speech_buffer) == 0
    assert state.silence_duration == 0.0


def test_session_state_add_transcript() -> None:
    """Test adding transcripts to session state."""
    state = SessionState(
        session_id="session_001",
        student_id="student_001",
    )
    
    timestamp = datetime.now().timestamp()
    state.add_transcript("Hello world", timestamp)
    
    assert len(state.student_speech_buffer) == 1
    assert state.student_speech_buffer[0].text == "Hello world"


def test_observation_creation() -> None:
    """Test creating an observation."""
    obs = Observation(
        visual="Student working on problem",
        audio="Student mumbling",
    )
    
    assert obs.visual == "Student working on problem"
    assert obs.audio == "Student mumbling"
    assert isinstance(obs.timestamp, datetime)


def test_analysis_creation() -> None:
    """Test creating an analysis."""
    analysis = Analysis(
        student_state=StudentState.ENGAGED,
        error_detected=False,
        confidence=0.8,
    )
    
    assert analysis.student_state == StudentState.ENGAGED
    assert not analysis.error_detected
    assert analysis.confidence == 0.8


def test_decision_creation() -> None:
    """Test creating a decision."""
    decision = Decision(
        action=ActionDecision.WAIT,
        reasoning="Student is making progress",
        confidence=0.7,
    )
    
    assert decision.action == ActionDecision.WAIT
    assert decision.reasoning == "Student is making progress"
    assert decision.confidence == 0.7
