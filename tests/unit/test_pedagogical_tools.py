"""Tests for pedagogical tools."""

import pytest
from oait.tools.pedagogical import PedagogicalTools, get_tool_definitions


class TestVerifyCalculation:
    """Tests for verify_calculation tool."""
    
    def test_correct_addition(self):
        result = PedagogicalTools.verify_calculation("2 + 2", "4")
        assert result["valid"] is True
        assert result["correct"] is True
        assert result["correct_answer"] == 4
        assert result["student_answer"] == 4.0
    
    def test_incorrect_addition(self):
        result = PedagogicalTools.verify_calculation("2 + 2", "5")
        assert result["valid"] is True
        assert result["correct"] is False
        assert result["correct_answer"] == 4
        assert result["student_answer"] == 5.0
    
    def test_multiplication(self):
        result = PedagogicalTools.verify_calculation("3 * 7", "21")
        assert result["valid"] is True
        assert result["correct"] is True
    
    def test_complex_expression(self):
        result = PedagogicalTools.verify_calculation("(5 + 3) * 2", "16")
        assert result["valid"] is True
        assert result["correct"] is True
    
    def test_invalid_student_answer(self):
        result = PedagogicalTools.verify_calculation("2 + 2", "four")
        assert result["valid"] is True
        assert result["correct"] is False
        assert "error" in result
    
    def test_invalid_expression(self):
        result = PedagogicalTools.verify_calculation("2 + abc", "4")
        assert result["valid"] is False


class TestAssessConfusionLevel:
    """Tests for assess_confusion_level tool."""
    
    def test_no_confusion(self):
        result = PedagogicalTools.assess_confusion_level(
            "I solved this problem by adding two and two"
        )
        assert result["confusion_level"] == "low"
        assert result["confusion_score"] < 0.2
    
    def test_medium_confusion(self):
        result = PedagogicalTools.assess_confusion_level(
            "Um, I think maybe this is right? I'm not sure"
        )
        assert result["confusion_level"] in ["medium", "high"]
        assert result["hesitation_count"] > 0
    
    def test_high_confusion(self):
        result = PedagogicalTools.assess_confusion_level(
            "I don't understand this at all. Um, what does this mean? I'm confused"
        )
        assert result["confusion_level"] == "high"
        assert result["confusion_score"] > 0.5
        assert len(result["indicators_found"]) > 0
    
    def test_empty_transcript(self):
        result = PedagogicalTools.assess_confusion_level("")
        assert result["confusion_score"] == 0.0


class TestDetectQuestion:
    """Tests for detect_question tool."""
    
    def test_question_mark(self):
        result = PedagogicalTools.detect_question("What is two plus two?")
        assert result["is_question"] is True
        assert result["has_question_mark"] is True
        assert result["starts_with_question_word"] is True
    
    def test_question_indicator(self):
        result = PedagogicalTools.detect_question("Can you help me with this")
        assert result["is_question"] is True
        assert result["has_question_indicator"] is True
    
    def test_question_word_start(self):
        result = PedagogicalTools.detect_question("How do I solve this problem")
        assert result["is_question"] is True
        assert result["starts_with_question_word"] is True
    
    def test_not_a_question(self):
        result = PedagogicalTools.detect_question("I solved the problem correctly")
        assert result["is_question"] is False
    
    def test_implicit_question(self):
        result = PedagogicalTools.detect_question("I need help with this")
        assert result["is_question"] is True


class TestDetectStuckPattern:
    """Tests for detect_stuck_pattern tool."""
    
    def test_not_stuck(self):
        result = PedagogicalTools.detect_stuck_pattern(
            transcript="I'm working through this problem step by step",
            silence_duration=2.0,
            whiteboard_unchanged_duration=5.0
        )
        assert result["is_stuck"] is False
        assert result["stuck_score"] < 0.5
    
    def test_stuck_with_indicator(self):
        result = PedagogicalTools.detect_stuck_pattern(
            transcript="I'm stuck and don't know what to do",
            silence_duration=5.0,
            whiteboard_unchanged_duration=10.0
        )
        assert result["is_stuck"] is True
        assert result["has_stuck_indicator"] is True
    
    def test_stuck_from_silence(self):
        result = PedagogicalTools.detect_stuck_pattern(
            transcript="",
            silence_duration=15.0,
            whiteboard_unchanged_duration=20.0
        )
        assert result["is_stuck"] is True
        assert result["long_silence"] is True
        assert result["unchanged_whiteboard"] is True
    
    def test_repetition_pattern(self):
        result = PedagogicalTools.detect_stuck_pattern(
            transcript="maybe this maybe this maybe this maybe this",
            silence_duration=5.0,
            whiteboard_unchanged_duration=5.0
        )
        assert result["has_repetition"] is True


class TestSuggestInterventionStrategy:
    """Tests for suggest_intervention_strategy tool."""
    
    def test_direct_for_question(self):
        strategy = PedagogicalTools.suggest_intervention_strategy(
            confusion_level="low",
            is_question=True,
            is_stuck=False,
            error_detected=False
        )
        assert strategy == "direct"
    
    def test_scaffolding_for_stuck_and_confused(self):
        strategy = PedagogicalTools.suggest_intervention_strategy(
            confusion_level="high",
            is_question=False,
            is_stuck=True,
            error_detected=False
        )
        assert strategy == "scaffolding"
    
    def test_socratic_for_error_without_confusion(self):
        strategy = PedagogicalTools.suggest_intervention_strategy(
            confusion_level="low",
            is_question=False,
            is_stuck=False,
            error_detected=True
        )
        assert strategy == "socratic"
    
    def test_hint_for_error_with_confusion(self):
        strategy = PedagogicalTools.suggest_intervention_strategy(
            confusion_level="high",
            is_question=False,
            is_stuck=False,
            error_detected=True
        )
        assert strategy == "hint"


class TestGetToolDefinitions:
    """Tests for get_tool_definitions function."""
    
    def test_returns_list(self):
        tools = get_tool_definitions()
        assert isinstance(tools, list)
        assert len(tools) > 0
    
    def test_all_tools_have_required_fields(self):
        tools = get_tool_definitions()
        for tool in tools:
            assert "type" in tool
            assert tool["type"] == "function"
            assert "function" in tool
            assert "name" in tool["function"]
            assert "description" in tool["function"]
            assert "parameters" in tool["function"]
    
    def test_verify_calculation_tool_exists(self):
        tools = get_tool_definitions()
        tool_names = [t["function"]["name"] for t in tools]
        assert "verify_calculation" in tool_names
    
    def test_assess_confusion_tool_exists(self):
        tools = get_tool_definitions()
        tool_names = [t["function"]["name"] for t in tools]
        assert "assess_confusion_level" in tool_names
