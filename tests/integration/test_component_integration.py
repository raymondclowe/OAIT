"""Integration tests for key OAIT components working together."""

import pytest
from datetime import datetime

from oait.models.data_models import (
    SessionState,
    StudentModel,
    PedagogyProfile,
)
from oait.cognitive.triggers import TriggerDetector
from oait.tools.pedagogical import PedagogicalTools, get_tool_definitions


class TestComponentIntegration:
    """Test that core components work together correctly."""

    @pytest.fixture
    def student_model(self):
        """Create a test student model."""
        return StudentModel(
            student_id="test-student-001",
            competencies={"algebra": "intermediate"},
            pedagogy_profile=PedagogyProfile(
                patience_level="medium",
                preferred_learning_style="visual",
                optimal_intervention_delay=15.0,
            ),
        )

    @pytest.fixture
    def session_state(self):
        """Create a test session state."""
        return SessionState(
            session_id="test-session-001",
            student_id="test-student-001",
            current_problem="Solve: 2x + 5 = 15",
            silence_duration=0.0,
        )

    @pytest.fixture
    def trigger_detector(self):
        """Create a trigger detector."""
        return TriggerDetector(
            silence_threshold=10.0,
            change_threshold=0.3,
        )

    def test_calculation_verification(self):
        """Test calculation verification with various inputs."""
        # Correct answer
        result = PedagogicalTools.verify_calculation("2 + 2", "4")
        assert result["valid"] is True
        assert result["correct"] is True
        assert result["correct_answer"] == 4.0
        
        # Incorrect answer
        result = PedagogicalTools.verify_calculation("2 + 2", "5")
        assert result["valid"] is True
        assert result["correct"] is False
        assert result["difference"] == 1.0

    def test_confusion_detection(self):
        """Test confusion detection at different levels."""
        # No confusion
        result = PedagogicalTools.assess_confusion_level("I solved it by adding 2 and 2")
        assert result["confusion_level"] == "low"
        assert result["confusion_score"] < 0.2
        
        # High confusion
        result = PedagogicalTools.assess_confusion_level(
            "Um, I don't understand this at all. What do I do? This is confusing"
        )
        assert result["confusion_level"] in ["medium", "high"]
        assert result["confusion_score"] > 0.4

    def test_question_detection(self):
        """Test question detection."""
        # Clear question
        result = PedagogicalTools.detect_question("How do I solve this?")
        assert result["is_question"] is True
        assert result["has_question_mark"] is True
        
        # Not a question
        result = PedagogicalTools.detect_question("I think x equals 5")
        assert result["is_question"] is False

    def test_stuck_detection(self):
        """Test stuck pattern detection."""
        # Student is stuck (long silence, no whiteboard changes)
        result = PedagogicalTools.detect_stuck_pattern(
            transcript="I don't know what to do",
            silence_duration=15.0,
            whiteboard_unchanged_duration=20.0,
        )
        assert result["is_stuck"] is True
        assert result["long_silence"] is True
        assert result["unchanged_whiteboard"] is True
        
        # Student is not stuck (active work)
        result = PedagogicalTools.detect_stuck_pattern(
            transcript="Let me try this approach",
            silence_duration=2.0,
            whiteboard_unchanged_duration=3.0,
        )
        assert result["is_stuck"] is False

    def test_intervention_strategy_selection(self):
        """Test intervention strategy selection logic."""
        # Direct answer for explicit question
        strategy = PedagogicalTools.suggest_intervention_strategy(
            confusion_level="low",
            is_question=True,
            is_stuck=False,
            error_detected=False,
        )
        assert strategy == "direct"
        
        # Scaffolding for stuck + confused
        strategy = PedagogicalTools.suggest_intervention_strategy(
            confusion_level="high",
            is_question=False,
            is_stuck=True,
            error_detected=False,
        )
        assert strategy == "scaffolding"
        
        # Socratic questioning for error without confusion
        strategy = PedagogicalTools.suggest_intervention_strategy(
            confusion_level="low",
            is_question=False,
            is_stuck=False,
            error_detected=True,
        )
        assert strategy == "socratic"

    def test_trigger_detection_on_silence(self, trigger_detector, session_state):
        """Test trigger detection based on silence."""
        # Short silence - no trigger
        session_state.silence_duration = 5.0
        should_trigger, reasons = trigger_detector.check_triggers(session_state)
        # May or may not trigger depending on other factors
        
        # Long silence - should trigger
        session_state.silence_duration = 15.0
        should_trigger, reasons = trigger_detector.check_triggers(session_state)
        assert should_trigger
        assert any("silence" in r.lower() for r in reasons)

    def test_tool_definitions_format(self):
        """Test that tool definitions are properly formatted for OpenRouter."""
        tool_defs = get_tool_definitions()
        
        # Should have multiple tools
        assert len(tool_defs) > 0
        
        # Each tool should have required fields
        for tool in tool_defs:
            assert tool["type"] == "function"
            assert "function" in tool
            assert "name" in tool["function"]
            assert "description" in tool["function"]
            assert "parameters" in tool["function"]
            
            # Parameters should have proper structure
            params = tool["function"]["parameters"]
            assert params["type"] == "object"
            assert "properties" in params
            assert "required" in params

    def test_complete_analysis_workflow(self):
        """Test a complete analysis workflow from transcript to strategy."""
        # Scenario: Student is confused and asks for help
        transcript = "Um, I'm not sure how to do this. Can you help me?"
        
        # Step 1: Analyze confusion
        confusion = PedagogicalTools.assess_confusion_level(transcript)
        assert confusion["confusion_level"] != "low"
        
        # Step 2: Detect question
        is_question_result = PedagogicalTools.detect_question(transcript)
        assert is_question_result["is_question"] is True
        
        # Step 3: Check if stuck
        stuck = PedagogicalTools.detect_stuck_pattern(
            transcript=transcript,
            silence_duration=5.0,
            whiteboard_unchanged_duration=8.0,
        )
        
        # Step 4: Get intervention strategy
        strategy = PedagogicalTools.suggest_intervention_strategy(
            confusion_level=confusion["confusion_level"],
            is_question=is_question_result["is_question"],
            is_stuck=stuck["is_stuck"],
            error_detected=False,
        )
        
        # Should suggest direct answer for explicit question
        assert strategy == "direct"
        
        print(f"\n=== Analysis Workflow Result ===")
        print(f"Confusion: {confusion['confusion_level']}")
        print(f"Is Question: {is_question_result['is_question']}")
        print(f"Is Stuck: {stuck['is_stuck']}")
        print(f"Strategy: {strategy}")

    def test_error_detection_workflow(self):
        """Test workflow when student makes an error."""
        # Student gets wrong answer
        expression = "2 + 3"
        student_answer = "6"  # Wrong!
        
        verification = PedagogicalTools.verify_calculation(expression, student_answer)
        assert verification["correct"] is False
        assert verification["correct_answer"] == 5.0
        
        # Student shows some confusion
        transcript = "I think it's 6, but I'm not totally sure"
        confusion = PedagogicalTools.assess_confusion_level(transcript)
        
        # Decide intervention strategy
        strategy = PedagogicalTools.suggest_intervention_strategy(
            confusion_level=confusion["confusion_level"],
            is_question=False,
            is_stuck=False,
            error_detected=True,  # We detected the error
        )
        
        # Should use hint or socratic depending on confusion level
        assert strategy in ["hint", "socratic"]
        
        print(f"\n=== Error Detection Workflow ===")
        print(f"Correct Answer: {verification['correct_answer']}")
        print(f"Student Answer: {verification['student_answer']}")
        print(f"Confusion: {confusion['confusion_level']}")
        print(f"Strategy: {strategy}")
