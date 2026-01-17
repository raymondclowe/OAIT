"""Pedagogical tools for AI reasoning about student state."""

import re
import ast
import operator
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)


class PedagogicalTools:
    """Collection of tools for AI to use when analyzing student work."""

    # Safe mathematical operators for expression evaluation
    _SAFE_OPERATORS = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.Pow: operator.pow,
        ast.USub: operator.neg,
        ast.UAdd: operator.pos,
    }

    @staticmethod
    def _safe_eval(node: ast.AST) -> float:
        """Safely evaluate a mathematical expression AST node.
        
        Args:
            node: AST node to evaluate
            
        Returns:
            Evaluated result as float
            
        Raises:
            ValueError: If expression contains unsafe operations
        """
        if isinstance(node, ast.Constant):  # Python 3.8+
            return float(node.value)
        elif isinstance(node, ast.BinOp):
            left = PedagogicalTools._safe_eval(node.left)
            right = PedagogicalTools._safe_eval(node.right)
            op = PedagogicalTools._SAFE_OPERATORS.get(type(node.op))
            if op is None:
                raise ValueError(f"Unsupported operator: {type(node.op).__name__}")
            return op(left, right)
        elif isinstance(node, ast.UnaryOp):
            operand = PedagogicalTools._safe_eval(node.operand)
            op = PedagogicalTools._SAFE_OPERATORS.get(type(node.op))
            if op is None:
                raise ValueError(f"Unsupported unary operator: {type(node.op).__name__}")
            return op(operand)
        else:
            raise ValueError(f"Unsupported expression type: {type(node).__name__}")

    @staticmethod
    def verify_calculation(expression: str, student_answer: str) -> Dict[str, Any]:
        """Verify if a mathematical calculation is correct.
        
        Args:
            expression: Mathematical expression (e.g., "2 + 2")
            student_answer: Student's answer (e.g., "4")
            
        Returns:
            Dictionary with verification results
        """
        try:
            # Clean inputs
            expression = expression.strip()
            student_answer = student_answer.strip()
            
            # Replace ^ with ** for power operator
            expression = expression.replace("^", "**")
            
            # Parse expression using AST (safe - no code execution)
            try:
                tree = ast.parse(expression, mode='eval')
            except SyntaxError as e:
                return {
                    "valid": False,
                    "error": f"Invalid expression syntax: {str(e)}",
                    "correct": False
                }
            
            # Evaluate using safe AST evaluation (no eval() - no arbitrary code execution)
            try:
                correct_answer = PedagogicalTools._safe_eval(tree.body)
            except ValueError as e:
                return {
                    "valid": False,
                    "error": str(e),
                    "correct": False
                }
            except ZeroDivisionError:
                return {
                    "valid": False,
                    "error": "Division by zero",
                    "correct": False
                }
            except Exception as e:
                return {
                    "valid": False,
                    "error": f"Evaluation error: {str(e)}",
                    "correct": False
                }
            
            # Try to parse student answer
            try:
                student_value = float(student_answer)
            except ValueError:
                return {
                    "valid": True,
                    "correct_answer": correct_answer,
                    "student_answer": student_answer,
                    "correct": False,
                    "error": "Student answer is not a number"
                }
            
            # Check if correct (with small tolerance for floating point)
            is_correct = abs(correct_answer - student_value) < 0.0001
            
            return {
                "valid": True,
                "correct_answer": correct_answer,
                "student_answer": student_value,
                "correct": is_correct,
                "difference": abs(correct_answer - student_value)
            }
            
        except Exception as e:
            logger.error(f"Error verifying calculation: {e}")
            return {
                "valid": False,
                "error": str(e),
                "correct": False
            }

    @staticmethod
    def assess_confusion_level(transcript: str) -> Dict[str, Any]:
        """Analyze transcript for confusion indicators.
        
        Args:
            transcript: Recent speech transcript
            
        Returns:
            Dictionary with confusion assessment
        """
        confusion_indicators = [
            "i don't understand",
            "i'm confused",
            "what does this mean",
            "i don't get it",
            "huh",
            "wait",
            "um",
            "uh",
            "hmm",
            "i'm not sure",
            "i think maybe",
            "is this right",
            "i don't know"
        ]
        
        transcript_lower = transcript.lower()
        
        # Count confusion indicators
        indicator_count = sum(
            transcript_lower.count(indicator)
            for indicator in confusion_indicators
        )
        
        # Count hesitation words
        hesitation_words = ["um", "uh", "hmm", "err"]
        hesitation_count = sum(
            transcript_lower.count(word)
            for word in hesitation_words
        )
        
        # Count question marks
        question_count = transcript.count("?")
        
        # Calculate confusion score (0.0 to 1.0)
        total_words = len(transcript.split())
        if total_words == 0:
            confusion_score = 0.0
        else:
            confusion_score = min(
                1.0,
                (indicator_count * 0.3 + hesitation_count * 0.1 + question_count * 0.2)
            )
        
        # Determine confusion level
        if confusion_score < 0.2:
            level = "low"
        elif confusion_score < 0.5:
            level = "medium"
        else:
            level = "high"
        
        return {
            "confusion_score": confusion_score,
            "confusion_level": level,
            "indicator_count": indicator_count,
            "hesitation_count": hesitation_count,
            "question_count": question_count,
            "indicators_found": [
                ind for ind in confusion_indicators
                if ind in transcript_lower
            ]
        }

    @staticmethod
    def detect_question(transcript: str) -> Dict[str, Any]:
        """Detect if the student asked a question.
        
        Args:
            transcript: Recent speech transcript
            
        Returns:
            Dictionary with question detection results
        """
        question_indicators = [
            "how do i",
            "what is",
            "what does",
            "why is",
            "why does",
            "can you help",
            "could you help",
            "i need help",
            "help me",
            "can you explain",
            "could you explain"
        ]
        
        transcript_lower = transcript.lower()
        
        # Check for question marks
        has_question_mark = "?" in transcript
        
        # Check for question indicators
        has_question_indicator = any(
            indicator in transcript_lower
            for indicator in question_indicators
        )
        
        # Check for question words at start
        question_words = ["who", "what", "where", "when", "why", "how"]
        starts_with_question = any(
            transcript_lower.strip().startswith(word)
            for word in question_words
        )
        
        is_question = has_question_mark or has_question_indicator or starts_with_question
        
        return {
            "is_question": is_question,
            "has_question_mark": has_question_mark,
            "has_question_indicator": has_question_indicator,
            "starts_with_question_word": starts_with_question,
            "confidence": 0.9 if has_question_mark else 0.7 if has_question_indicator else 0.5
        }

    @staticmethod
    def detect_stuck_pattern(
        transcript: str,
        silence_duration: float,
        whiteboard_unchanged_duration: float
    ) -> Dict[str, Any]:
        """Detect if student appears stuck.
        
        Args:
            transcript: Recent speech transcript
            silence_duration: How long student has been silent (seconds)
            whiteboard_unchanged_duration: How long whiteboard hasn't changed (seconds)
            
        Returns:
            Dictionary with stuck detection results
        """
        stuck_indicators = [
            "i'm stuck",
            "i can't figure this out",
            "i don't know what to do",
            "where do i start",
            "i give up"
        ]
        
        transcript_lower = transcript.lower()
        
        # Check for explicit stuck indicators
        has_stuck_indicator = any(
            indicator in transcript_lower
            for indicator in stuck_indicators
        )
        
        # Check for long silence
        long_silence = silence_duration > 10.0
        
        # Check for unchanged whiteboard
        unchanged_whiteboard = whiteboard_unchanged_duration > 15.0
        
        # Check for repeated phrases (might indicate trying same thing multiple times)
        words = transcript_lower.split()
        word_freq = {}
        for word in words:
            if len(word) > 3:  # Only count significant words
                word_freq[word] = word_freq.get(word, 0) + 1
        
        has_repetition = any(count > 3 for count in word_freq.values())
        
        # Calculate stuck score
        stuck_score = 0.0
        if has_stuck_indicator:
            stuck_score += 0.5  # Increased weight for explicit stuck indicators
        if long_silence:
            stuck_score += 0.3  # Increased weight for silence
        if unchanged_whiteboard:
            stuck_score += 0.3  # Increased weight for unchanged whiteboard
        if has_repetition:
            stuck_score += 0.2
        
        stuck_score = min(1.0, stuck_score)
        
        is_stuck = stuck_score > 0.4  # Lowered threshold from 0.5 to 0.4
        
        return {
            "is_stuck": is_stuck,
            "stuck_score": stuck_score,
            "has_stuck_indicator": has_stuck_indicator,
            "long_silence": long_silence,
            "unchanged_whiteboard": unchanged_whiteboard,
            "has_repetition": has_repetition,
            "indicators_found": [
                ind for ind in stuck_indicators
                if ind in transcript_lower
            ]
        }

    @staticmethod
    def suggest_intervention_strategy(
        confusion_level: str,
        is_question: bool,
        is_stuck: bool,
        error_detected: bool
    ) -> str:
        """Suggest the best intervention strategy.
        
        Args:
            confusion_level: "low", "medium", or "high"
            is_question: Whether student asked a question
            is_stuck: Whether student appears stuck
            error_detected: Whether an error was detected in their work
            
        Returns:
            Intervention strategy name
        """
        # Explicit question -> answer it
        if is_question:
            return "direct"
        
        # Stuck with high confusion -> provide scaffolding
        if is_stuck and confusion_level == "high":
            return "scaffolding"
        
        # Error detected -> use Socratic questioning
        if error_detected and confusion_level == "low":
            return "socratic"
        
        # Error with confusion -> give a hint
        if error_detected and confusion_level in ["medium", "high"]:
            return "hint"
        
        # Stuck but not confused -> guide with questions
        if is_stuck and confusion_level == "low":
            return "socratic"
        
        # High confusion without being stuck -> provide example
        if confusion_level == "high" and not is_stuck:
            return "example"
        
        # Default -> Socratic questioning
        return "socratic"


def get_tool_definitions() -> List[Dict[str, Any]]:
    """Get tool definitions for LLM function calling.
    
    Returns:
        List of tool definitions in OpenAI function calling format
    """
    return [
        {
            "type": "function",
            "function": {
                "name": "verify_calculation",
                "description": "Verify if a mathematical calculation is correct",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "expression": {
                            "type": "string",
                            "description": "Mathematical expression to evaluate (e.g., '2 + 2')"
                        },
                        "student_answer": {
                            "type": "string",
                            "description": "Student's answer to check"
                        }
                    },
                    "required": ["expression", "student_answer"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "assess_confusion_level",
                "description": "Analyze student speech for confusion indicators",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "transcript": {
                            "type": "string",
                            "description": "Recent speech transcript to analyze"
                        }
                    },
                    "required": ["transcript"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "detect_question",
                "description": "Detect if the student asked a question",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "transcript": {
                            "type": "string",
                            "description": "Recent speech transcript"
                        }
                    },
                    "required": ["transcript"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "detect_stuck_pattern",
                "description": "Detect if the student appears to be stuck",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "transcript": {
                            "type": "string",
                            "description": "Recent speech transcript"
                        },
                        "silence_duration": {
                            "type": "number",
                            "description": "How long student has been silent in seconds"
                        },
                        "whiteboard_unchanged_duration": {
                            "type": "number",
                            "description": "How long whiteboard hasn't changed in seconds"
                        }
                    },
                    "required": ["transcript", "silence_duration", "whiteboard_unchanged_duration"]
                }
            }
        }
    ]
