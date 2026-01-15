"""AI Tool definitions and handlers for the OODA loop.

The AI tutor uses these tools to:
- Observe: Get audio, whiteboard, camera, student data
- Act: Speak, update models, send messages
- Control: Wait for events, set intervals

Tools follow OpenRouter/OpenAI function calling format.
"""

import logging
import asyncio
import time
import json
from typing import Dict, List, Any, Optional, Callable, Awaitable
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


# ============================================================================
# TOOL DEFINITIONS (OpenAI Function Calling Format)
# ============================================================================

OBSERVATION_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_audio_transcript",
            "description": "Get recent speech transcripts from the student. Returns text of what the student said recently.",
            "parameters": {
                "type": "object",
                "properties": {
                    "seconds": {
                        "type": "number",
                        "description": "How many seconds of recent transcripts to retrieve (default 30)",
                        "default": 30
                    }
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_whiteboard",
            "description": "Get the current whiteboard image to see what the student is working on. Returns image description or analysis.",
            "parameters": {
                "type": "object",
                "properties": {
                    "analyze": {
                        "type": "boolean",
                        "description": "If true, analyze the image content. If false, just check if it changed.",
                        "default": True
                    }
                },
                "required": []
            }
        }
    },
    {
        "type": "function", 
        "function": {
            "name": "get_camera_feed",
            "description": "Get the student's camera feed to observe their facial expressions and body language.",
            "parameters": {
                "type": "object",
                "properties": {
                    "camera_id": {
                        "type": "string",
                        "description": "Which camera to get feed from (default 'student_face')",
                        "default": "student_face"
                    },
                    "analyze_emotion": {
                        "type": "boolean",
                        "description": "If true, analyze emotional state from facial expression",
                        "default": False
                    }
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_student_profile",
            "description": "Get the student's pedagogical profile including learning style, patience level, and history.",
            "parameters": {
                "type": "object",
                "properties": {
                    "include_history": {
                        "type": "boolean",
                        "description": "Include recent session history",
                        "default": False
                    }
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_session_status",
            "description": "Get current session status including silence duration, last interaction time, and activity state.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_observation_mode",
            "description": "Get the current observation mode and polling interval.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
]

ACTION_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "speak",
            "description": "Say something aloud to the student via text-to-speech. Use this to provide hints, ask questions, or give feedback.",
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "The text to speak aloud to the student"
                    },
                    "tone": {
                        "type": "string",
                        "enum": ["encouraging", "neutral", "questioning", "excited"],
                        "description": "The emotional tone to use",
                        "default": "neutral"
                    }
                },
                "required": ["text"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "update_student_model",
            "description": "Update the student's pedagogical model based on observations. Call this when you learn something about the student.",
            "parameters": {
                "type": "object",
                "properties": {
                    "understanding_delta": {
                        "type": "number",
                        "description": "Change in understanding level (-1 to +1)",
                    },
                    "frustration_delta": {
                        "type": "number",
                        "description": "Change in frustration level (-1 to +1)",
                    },
                    "engagement_delta": {
                        "type": "number",
                        "description": "Change in engagement level (-1 to +1)",
                    },
                    "note": {
                        "type": "string",
                        "description": "A note about what you observed",
                    },
                    "concept_mastery": {
                        "type": "object",
                        "description": "Update specific concept mastery levels",
                        "additionalProperties": {"type": "number"}
                    }
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "send_visual_hint",
            "description": "Display a visual hint or diagram on the student's screen.",
            "parameters": {
                "type": "object",
                "properties": {
                    "hint_type": {
                        "type": "string",
                        "enum": ["highlight", "diagram", "formula", "example"],
                        "description": "Type of visual hint to show"
                    },
                    "content": {
                        "type": "string",
                        "description": "The content to display (text, LaTeX, or description)"
                    },
                    "position": {
                        "type": "string",
                        "enum": ["corner", "center", "near_problem"],
                        "description": "Where to show the hint",
                        "default": "corner"
                    }
                },
                "required": ["hint_type", "content"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "log_observation",
            "description": "Log an internal observation or thought for debugging and learning. Does not affect the student.",
            "parameters": {
                "type": "object",
                "properties": {
                    "category": {
                        "type": "string",
                        "enum": ["hypothesis", "decision", "observation", "error"],
                        "description": "Category of the log entry"
                    },
                    "message": {
                        "type": "string",
                        "description": "The observation or thought to log"
                    }
                },
                "required": ["category", "message"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "update_student_profile",
            "description": "Update the student's persistent pedagogical profile settings like learning style, patience level, and intervention preferences.",
            "parameters": {
                "type": "object",
                "properties": {
                    "learning_style": {
                        "type": "string",
                        "enum": ["visual", "auditory", "reading_writing", "kinesthetic"],
                        "description": "Preferred learning style"
                    },
                    "patience_level": {
                        "type": "number",
                        "description": "Patience level from 0.0 (impatient) to 1.0 (very patient)"
                    },
                    "optimal_intervention_delay": {
                        "type": "number",
                        "description": "Seconds to wait before intervening when student is stuck"
                    },
                    "hint_preference": {
                        "type": "string",
                        "enum": ["minimal", "moderate", "detailed"],
                        "description": "How detailed hints should be"
                    },
                    "encouragement_frequency": {
                        "type": "number",
                        "description": "How often to give encouragement (0.0 to 1.0)"
                    }
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "draw_on_whiteboard",
            "description": "Draw or write something on the student's whiteboard to demonstrate a concept or highlight an area.",
            "parameters": {
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string",
                        "enum": ["draw_arrow", "circle_area", "write_text", "draw_diagram", "highlight", "clear"],
                        "description": "What to draw on the whiteboard"
                    },
                    "content": {
                        "type": "string",
                        "description": "Text to write or description of what to draw"
                    },
                    "position": {
                        "type": "object",
                        "properties": {
                            "x": {"type": "number", "description": "X position (0-100%)"},
                            "y": {"type": "number", "description": "Y position (0-100%)"}
                        },
                        "description": "Where to draw (optional, defaults to center)"
                    },
                    "color": {
                        "type": "string",
                        "description": "Color to use (e.g., 'red', 'blue', '#FF0000')",
                        "default": "blue"
                    }
                },
                "required": ["action"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "clear_visual_hint",
            "description": "Clear/dismiss the currently displayed visual hint.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
]

CONTROL_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "wait_for_event",
            "description": "Wait until a specific event occurs or timeout. Use this to pause observation until something interesting happens.",
            "parameters": {
                "type": "object",
                "properties": {
                    "events": {
                        "type": "array",
                        "items": {
                            "type": "string",
                            "enum": ["speech", "silence", "whiteboard_change", "any_activity"]
                        },
                        "description": "Events to wait for (any of these will trigger)"
                    },
                    "timeout_seconds": {
                        "type": "number",
                        "description": "Maximum time to wait in seconds",
                        "default": 30
                    },
                    "min_wait_seconds": {
                        "type": "number",
                        "description": "Minimum time to wait even if event occurs",
                        "default": 0
                    }
                },
                "required": ["events"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "set_observation_mode",
            "description": "Change the observation mode and polling frequency.",
            "parameters": {
                "type": "object",
                "properties": {
                    "mode": {
                        "type": "string",
                        "enum": ["active", "passive", "intervention"],
                        "description": "active=frequent checks, passive=infrequent, intervention=continuous"
                    },
                    "interval_seconds": {
                        "type": "number",
                        "description": "Override the polling interval (optional)"
                    }
                },
                "required": ["mode"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "end_observation_cycle",
            "description": "End the current observation cycle. Call this when you've gathered enough information and made a decision.",
            "parameters": {
                "type": "object",
                "properties": {
                    "next_action": {
                        "type": "string",
                        "enum": ["wait", "speak", "observe_again"],
                        "description": "What to do next"
                    },
                    "reasoning": {
                        "type": "string",
                        "description": "Brief explanation of your decision"
                    }
                },
                "required": ["next_action", "reasoning"]
            }
        }
    },
]

# All tools combined
ALL_TOOLS = OBSERVATION_TOOLS + ACTION_TOOLS + CONTROL_TOOLS


# ============================================================================
# TOOL HANDLER CONTEXT (passed to handlers)
# ============================================================================

@dataclass
class ToolContext:
    """Context passed to tool handlers."""
    session_state: Any  # SessionState
    student_model: Any  # StudentModel
    websocket: Any  # WebSocket connection
    repository: Any  # StudentModelRepository
    whisper_stt: Any  # WhisperSTT
    vision_analyzer: Any  # VisionAnalyzer
    openrouter: Any  # OpenRouterClient
    
    # Pending requests for async communication with client
    pending_requests: Dict[str, asyncio.Future] = None
    request_counter: int = 0
    
    # Event state for wait_for_event
    last_speech_time: float = 0
    last_whiteboard_change: float = 0
    
    def __post_init__(self):
        if self.pending_requests is None:
            self.pending_requests = {}


# ============================================================================
# TOOL HANDLERS
# ============================================================================

class AIToolHandlers:
    """Handlers for AI tool calls."""
    
    def __init__(self, context: ToolContext):
        self.ctx = context
        self._observation_mode = "active"
        self._observation_interval = 5.0
        
    def get_handlers(self) -> Dict[str, Callable[..., Awaitable[Any]]]:
        """Get dict mapping tool names to handler functions."""
        return {
            # Observation tools
            "get_audio_transcript": self.get_audio_transcript,
            "get_whiteboard": self.get_whiteboard,
            "get_camera_feed": self.get_camera_feed,
            "get_student_profile": self.get_student_profile,
            "get_session_status": self.get_session_status,
            "get_observation_mode": self.get_observation_mode,
            
            # Action tools
            "speak": self.speak,
            "update_student_model": self.update_student_model,
            "update_student_profile": self.update_student_profile,
            "send_visual_hint": self.send_visual_hint,
            "clear_visual_hint": self.clear_visual_hint,
            "draw_on_whiteboard": self.draw_on_whiteboard,
            "log_observation": self.log_observation,
            
            # Control tools
            "wait_for_event": self.wait_for_event,
            "set_observation_mode": self.set_observation_mode,
            "end_observation_cycle": self.end_observation_cycle,
        }
    
    # -------------------------------------------------------------------------
    # OBSERVATION TOOLS
    # -------------------------------------------------------------------------
    
    async def get_audio_transcript(self, seconds: float = 30) -> Dict[str, Any]:
        """Get recent audio transcripts from the student."""
        logger.info(f"[TOOL] get_audio_transcript(seconds={seconds})")
        
        # Request audio from client via WebSocket
        response = await self._request_from_client("audio", timeout=5.0)
        
        if response.get("error"):
            return {"transcripts": [], "has_speech": False, "error": response["error"]}
        
        # If there's audio data, transcribe it
        if response.get("has_speech") and response.get("data"):
            import base64
            import tempfile
            
            audio_data = base64.b64decode(response["data"])
            duration_ms = response.get("duration_ms", 0)
            
            if duration_ms < 200:
                return {"transcripts": [], "has_speech": False, "duration_ms": duration_ms}
            
            try:
                with tempfile.NamedTemporaryFile(suffix=".wav", delete=True) as f:
                    f.write(audio_data)
                    f.flush()
                    text = await self.ctx.whisper_stt.transcribe(f.name)
                
                if text and text.strip():
                    # Update session state
                    timestamp = time.time()
                    self.ctx.session_state.add_transcript(text, timestamp)
                    self.ctx.last_speech_time = timestamp
                    
                    return {
                        "transcripts": [{"text": text, "timestamp": timestamp}],
                        "has_speech": True,
                        "duration_ms": duration_ms,
                    }
            except Exception as e:
                logger.error(f"[TOOL] Transcription error: {e}")
                return {"transcripts": [], "has_speech": False, "error": str(e)}
        
        # Also get recent transcripts from session state
        recent = self.ctx.session_state.get_recent_transcripts(seconds)
        transcripts = [{"text": t.text, "timestamp": t.timestamp} for t in recent]
        
        return {
            "transcripts": transcripts,
            "has_speech": len(transcripts) > 0,
            "total_in_buffer": len(transcripts),
        }
    
    async def get_whiteboard(self, analyze: bool = True) -> Dict[str, Any]:
        """Get the current whiteboard state."""
        logger.info(f"[TOOL] get_whiteboard(analyze={analyze})")
        
        response = await self._request_from_client("whiteboard", timeout=5.0)
        
        if response.get("error"):
            return {"has_content": False, "error": response["error"]}
        
        has_changes = response.get("has_changes", False)
        image_data = response.get("data", "")
        
        if has_changes:
            self.ctx.last_whiteboard_change = time.time()
        
        result = {
            "has_content": bool(image_data),
            "has_changes": has_changes,
            "last_change": response.get("last_change"),
        }
        
        # Optionally analyze the image
        if analyze and image_data and self.ctx.vision_analyzer:
            try:
                import base64
                from PIL import Image
                import io
                
                img_bytes = base64.b64decode(image_data)
                image = Image.open(io.BytesIO(img_bytes))
                
                # Use vision to analyze
                analysis = await self.ctx.vision_analyzer.analyze_student_work(
                    image,
                    context="whiteboard content"
                )
                result["analysis"] = analysis
            except Exception as e:
                logger.error(f"[TOOL] Whiteboard analysis error: {e}")
                result["analysis_error"] = str(e)
        
        return result
    
    async def get_camera_feed(
        self, 
        camera_id: str = "student_face",
        analyze_emotion: bool = False
    ) -> Dict[str, Any]:
        """Get camera feed from student."""
        logger.info(f"[TOOL] get_camera_feed(camera={camera_id}, emotion={analyze_emotion})")
        
        response = await self._request_from_client("camera", timeout=5.0, camera_id=camera_id)
        
        if response.get("error"):
            return {"available": False, "error": response["error"]}
        
        result = {
            "available": response.get("available", False),
            "camera_id": camera_id,
        }
        
        if analyze_emotion and response.get("data"):
            # TODO: Integrate emotion analysis model
            result["emotion"] = "neutral"  # Placeholder
            result["confidence"] = 0.5
        
        return result
    
    async def get_student_profile(self, include_history: bool = False) -> Dict[str, Any]:
        """Get the student's pedagogical profile."""
        logger.info(f"[TOOL] get_student_profile(include_history={include_history})")
        
        model = self.ctx.student_model
        if not model:
            return {"error": "No student model loaded"}
        
        profile = {
            "student_id": model.student_id,
            "learning_style": model.pedagogy_profile.preferred_learning_style.value,
            "patience_level": model.pedagogy_profile.patience_level,
            "optimal_intervention_delay": model.pedagogy_profile.optimal_intervention_delay,
            "hint_preference": model.pedagogy_profile.hint_preference.value,
            "encouragement_frequency": model.pedagogy_profile.encouragement_frequency,
        }
        
        if include_history and hasattr(model, 'session_history'):
            profile["recent_sessions"] = len(model.session_history)
        
        return profile
    
    async def get_session_status(self) -> Dict[str, Any]:
        """Get current session status."""
        logger.info("[TOOL] get_session_status()")
        
        state = self.ctx.session_state
        now = time.time()
        
        return {
            "session_id": state.session_id,
            "student_id": state.student_id,
            "silence_duration": state.silence_duration,
            "student_is_speaking": state.student_is_speaking,
            "student_is_writing": state.student_is_writing,
            "time_since_last_speech": now - self.ctx.last_speech_time if self.ctx.last_speech_time else None,
            "time_since_whiteboard_change": now - self.ctx.last_whiteboard_change if self.ctx.last_whiteboard_change else None,
            "transcript_count": len(state.transcripts) if hasattr(state, 'transcripts') else 0,
            "observation_mode": self._observation_mode,
        }
    
    # -------------------------------------------------------------------------
    # ACTION TOOLS
    # -------------------------------------------------------------------------
    
    async def speak(self, text: str, tone: str = "neutral") -> Dict[str, Any]:
        """Say something aloud to the student."""
        logger.info(f"[TOOL] speak(text='{text[:50]}...', tone={tone})")
        
        # Send to client for TTS
        await self._send_to_client({
            "type": "ai_response",
            "text": text,
            "tone": tone,
            "speak": True,  # Trigger TTS
        })
        
        # Update session state
        self.ctx.session_state.last_intervention_time = time.time()
        
        return {"spoken": True, "text": text, "tone": tone}
    
    async def update_student_model(
        self,
        understanding_delta: float = None,
        frustration_delta: float = None,
        engagement_delta: float = None,
        note: str = None,
        concept_mastery: Dict[str, float] = None,
    ) -> Dict[str, Any]:
        """Update the student's pedagogical model."""
        logger.info(f"[TOOL] update_student_model(note='{note}')")
        
        model = self.ctx.student_model
        if not model:
            return {"error": "No student model loaded"}
        
        updates = {}
        
        # Apply deltas (clamped to valid ranges)
        if understanding_delta is not None:
            # Store in session context or model
            updates["understanding_delta"] = understanding_delta
            
        if frustration_delta is not None:
            updates["frustration_delta"] = frustration_delta
            
        if engagement_delta is not None:
            updates["engagement_delta"] = engagement_delta
            
        if note:
            updates["note"] = note
            # Could add to model's notes/history
            
        if concept_mastery:
            updates["concept_mastery"] = concept_mastery
        
        # Save to repository
        if self.ctx.repository and updates:
            try:
                await self.ctx.repository.save(model)
                updates["saved"] = True
            except Exception as e:
                logger.error(f"[TOOL] Error saving student model: {e}")
                updates["save_error"] = str(e)
        
        return {"updated": True, "changes": updates}
    
    async def send_visual_hint(
        self,
        hint_type: str,
        content: str,
        position: str = "corner"
    ) -> Dict[str, Any]:
        """Display a visual hint on the student's screen."""
        logger.info(f"[TOOL] send_visual_hint(type={hint_type}, pos={position})")
        
        await self._send_to_client({
            "type": "visual_hint",
            "hint_type": hint_type,
            "content": content,
            "position": position,
        })
        
        return {"sent": True, "hint_type": hint_type}
    
    async def log_observation(self, category: str, message: str) -> Dict[str, Any]:
        """Log an internal observation."""
        logger.info(f"[TOOL] log_observation({category}): {message}")
        
        # Also send to client debug panel
        await self._send_to_client({
            "type": "debug",
            "message": f"[{category.upper()}] {message}",
            "timestamp": time.time(),
        })
        
        return {"logged": True, "category": category}
    
    async def update_student_profile(
        self,
        learning_style: str = None,
        patience_level: float = None,
        optimal_intervention_delay: float = None,
        hint_preference: str = None,
        encouragement_frequency: float = None,
    ) -> Dict[str, Any]:
        """Update the student's persistent pedagogical profile."""
        logger.info(f"[TOOL] update_student_profile()")
        
        model = self.ctx.student_model
        if not model:
            return {"error": "No student model loaded"}
        
        updates = {}
        profile = model.pedagogy_profile
        
        if learning_style is not None:
            from ..models.data_models import LearningStyle
            try:
                profile.preferred_learning_style = LearningStyle(learning_style)
                updates["learning_style"] = learning_style
            except ValueError:
                updates["learning_style_error"] = f"Invalid style: {learning_style}"
        
        if patience_level is not None:
            profile.patience_level = max(0.0, min(1.0, patience_level))
            updates["patience_level"] = profile.patience_level
        
        if optimal_intervention_delay is not None:
            profile.optimal_intervention_delay = max(0.0, optimal_intervention_delay)
            updates["optimal_intervention_delay"] = profile.optimal_intervention_delay
        
        if hint_preference is not None:
            from ..models.data_models import HintPreference
            try:
                profile.hint_preference = HintPreference(hint_preference)
                updates["hint_preference"] = hint_preference
            except ValueError:
                updates["hint_preference_error"] = f"Invalid preference: {hint_preference}"
        
        if encouragement_frequency is not None:
            profile.encouragement_frequency = max(0.0, min(1.0, encouragement_frequency))
            updates["encouragement_frequency"] = profile.encouragement_frequency
        
        # Save to repository
        if self.ctx.repository and updates:
            try:
                await self.ctx.repository.save(model)
                updates["saved"] = True
            except Exception as e:
                logger.error(f"[TOOL] Error saving student profile: {e}")
                updates["save_error"] = str(e)
        
        return {"updated": True, "changes": updates}
    
    async def draw_on_whiteboard(
        self,
        action: str,
        content: str = None,
        position: Dict[str, float] = None,
        color: str = "blue",
    ) -> Dict[str, Any]:
        """Draw on the student's whiteboard."""
        logger.info(f"[TOOL] draw_on_whiteboard(action={action})")
        
        await self._send_to_client({
            "type": "whiteboard_draw",
            "action": action,
            "content": content,
            "position": position or {"x": 50, "y": 50},
            "color": color,
        })
        
        return {"drawn": True, "action": action}
    
    async def clear_visual_hint(self) -> Dict[str, Any]:
        """Clear the currently displayed visual hint."""
        logger.info("[TOOL] clear_visual_hint()")
        
        await self._send_to_client({
            "type": "clear_visual_hint",
        })
        
        return {"cleared": True}
    
    async def get_observation_mode(self) -> Dict[str, Any]:
        """Get the current observation mode and interval."""
        logger.info("[TOOL] get_observation_mode()")
        
        return {
            "mode": self._observation_mode,
            "interval_seconds": self._observation_interval,
        }
    
    # -------------------------------------------------------------------------
    # CONTROL TOOLS
    # -------------------------------------------------------------------------
    
    async def wait_for_event(
        self,
        events: List[str],
        timeout_seconds: float = 30,
        min_wait_seconds: float = 0,
    ) -> Dict[str, Any]:
        """Wait for an event to occur."""
        logger.info(f"[TOOL] wait_for_event(events={events}, timeout={timeout_seconds}s)")
        
        start_time = time.time()
        triggered_event = None
        
        # Minimum wait
        if min_wait_seconds > 0:
            await asyncio.sleep(min_wait_seconds)
        
        # Poll for events
        poll_interval = 0.5
        while (time.time() - start_time) < timeout_seconds:
            # Check for each event type
            if "speech" in events:
                response = await self._request_from_client("status", timeout=1.0)
                if response.get("data", {}).get("audio_segments", 0) > 0:
                    triggered_event = "speech"
                    break
                    
            if "whiteboard_change" in events:
                response = await self._request_from_client("whiteboard", timeout=1.0)
                if response.get("has_changes"):
                    triggered_event = "whiteboard_change"
                    break
                    
            if "silence" in events:
                # Check if silence has been long enough
                status = await self.get_session_status()
                if status.get("silence_duration", 0) > 3.0:
                    triggered_event = "silence"
                    break
                    
            if "any_activity" in events:
                response = await self._request_from_client("status", timeout=1.0)
                data = response.get("data", {})
                if data.get("audio_segments", 0) > 0 or data.get("whiteboard_has_changes"):
                    triggered_event = "any_activity"
                    break
            
            await asyncio.sleep(poll_interval)
        
        elapsed = time.time() - start_time
        
        return {
            "triggered": triggered_event is not None,
            "event": triggered_event,
            "timeout_reached": triggered_event is None,
            "wait_duration": elapsed,
        }
    
    async def set_observation_mode(
        self,
        mode: str,
        interval_seconds: float = None
    ) -> Dict[str, Any]:
        """Change the observation mode."""
        logger.info(f"[TOOL] set_observation_mode(mode={mode})")
        
        self._observation_mode = mode
        
        if interval_seconds is not None:
            self._observation_interval = interval_seconds
        elif mode == "active":
            self._observation_interval = 3.0
        elif mode == "passive":
            self._observation_interval = 10.0
        elif mode == "intervention":
            self._observation_interval = 1.0
        
        return {
            "mode": mode,
            "interval_seconds": self._observation_interval,
        }
    
    async def end_observation_cycle(
        self,
        next_action: str,
        reasoning: str
    ) -> Dict[str, Any]:
        """End the current observation cycle."""
        logger.info(f"[TOOL] end_observation_cycle(action={next_action}, reason={reasoning})")
        
        return {
            "cycle_ended": True,
            "next_action": next_action,
            "reasoning": reasoning,
        }
    
    # -------------------------------------------------------------------------
    # HELPER METHODS
    # -------------------------------------------------------------------------
    
    async def _request_from_client(
        self, 
        resource: str, 
        timeout: float = 5.0,
        **extra_params
    ) -> Dict[str, Any]:
        """Send a request to the client and wait for response."""
        if not self.ctx.websocket:
            return {"error": "No WebSocket connection"}
        
        self.ctx.request_counter += 1
        request_id = f"tool_req_{self.ctx.request_counter}"
        
        # Create future for response
        future = asyncio.get_event_loop().create_future()
        self.ctx.pending_requests[request_id] = future
        
        try:
            # Send request
            await self.ctx.websocket.send_json({
                "type": "request",
                "request_id": request_id,
                "resource": resource,
                **extra_params,
            })
            
            # Wait for response
            response = await asyncio.wait_for(future, timeout=timeout)
            return response
            
        except asyncio.TimeoutError:
            return {"error": "timeout"}
        except Exception as e:
            return {"error": str(e)}
        finally:
            self.ctx.pending_requests.pop(request_id, None)
    
    async def _send_to_client(self, message: Dict[str, Any]) -> None:
        """Send a message to the client."""
        if self.ctx.websocket:
            try:
                await self.ctx.websocket.send_json(message)
            except Exception as e:
                logger.error(f"[TOOL] Error sending to client: {e}")


# ============================================================================
# SYSTEM PROMPT FOR AI TUTOR
# ============================================================================

AI_TUTOR_SYSTEM_PROMPT = """You are an expert AI tutor observing a student working on problems.

You have access to tools that let you:
- OBSERVE: Get audio transcripts, see the whiteboard, check student's camera, get their profile
- ACT: Speak to the student, update their model, send visual hints
- CONTROL: Wait for events, change observation frequency

Your role is to:
1. Observe what the student is doing (use get_audio_transcript, get_whiteboard, get_session_status)
2. Analyze if they need help or are doing well
3. Decide whether to intervene or keep watching
4. If intervening, use the speak tool with appropriate pedagogy

IMPORTANT PEDAGOGICAL PRINCIPLES:
- Don't interrupt if the student is making progress
- Wait for them to struggle briefly (builds problem-solving skills)
- Use Socratic questioning - ask guiding questions rather than giving answers
- Encourage effort and process, not just results
- Adapt to the student's learning style and patience level

WORKFLOW:
1. First, call get_session_status to understand the current state
2. Call get_audio_transcript to hear what the student said recently
3. If they're working on something, call get_whiteboard to see their work
4. Based on observations, decide:
   - If student asked a question or is stuck → speak with a helpful hint
   - If student is working well → use wait_for_event to watch for changes
   - If you learned something about the student → update_student_model
5. Call end_observation_cycle with your decision

Be patient, supportive, and remember: the goal is to help the student LEARN, not just get the right answer."""
