"""OpenRouter API client for LLM interactions."""

import logging
from typing import Dict, List, Optional, Any
import httpx
from PIL import Image
import base64
import io

logger = logging.getLogger(__name__)


class OpenRouterClient:
    """Client for OpenRouter API (OpenAI-compatible)."""

    def __init__(self, api_key: str, model: str = "google/gemini-3.0-pro"):
        """Initialize the OpenRouter client.

        Args:
            api_key: OpenRouter API key
            model: Model to use (default: Gemini 3 Pro)
        """
        self.api_key = api_key
        self.model = model
        self.base_url = "https://openrouter.ai/api/v1"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "HTTP-Referer": "https://github.com/raymondclowe/OAIT",
            "X-Title": "OAIT - Observational AI Tutor",
        }

    async def chat(
        self,
        messages: List[Dict[str, Any]],
        tools: Optional[List[Dict[str, Any]]] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Send a chat completion request.

        Args:
            messages: List of message dicts with 'role' and 'content'
            tools: Optional list of tool definitions for function calling
            temperature: Sampling temperature (0.0 to 1.0)
            max_tokens: Maximum tokens to generate

        Returns:
            Response dict from the API
        """
        payload: Dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
        }

        if tools:
            payload["tools"] = tools

        if max_tokens:
            payload["max_tokens"] = max_tokens

        async with httpx.AsyncClient(timeout=60.0) as client:
            try:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=self.headers,
                    json=payload,
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as e:
                logger.error(f"OpenRouter API error: {e}")
                raise

    async def vision(
        self,
        image: Image.Image,
        prompt: str,
        context: Optional[str] = None,
    ) -> str:
        """Analyze an image with vision capabilities.

        Args:
            image: PIL Image to analyze
            prompt: Prompt describing what to analyze
            context: Optional additional context

        Returns:
            Analysis text from the model
        """
        # Convert image to base64
        buffer = io.BytesIO()
        image.save(buffer, format="PNG")
        image_base64 = base64.b64encode(buffer.getvalue()).decode()

        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/png;base64,{image_base64}"},
                    },
                ],
            }
        ]

        if context:
            messages.insert(
                0,
                {"role": "system", "content": context},
            )

        response = await self.chat(messages=messages)

        try:
            return response["choices"][0]["message"]["content"]
        except (KeyError, IndexError) as e:
            logger.error(f"Failed to parse vision response: {e}")
            raise

    async def generate_internal_monologue(
        self,
        observation: Dict[str, Any],
        student_model: Dict[str, Any],
        session_state: Dict[str, Any],
        tools: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """Generate internal monologue about student state.

        Args:
            observation: Current observation data
            student_model: Student model data
            session_state: Current session state
            tools: Optional tools for function calling

        Returns:
            Internal monologue with analysis and decision
        """
        system_prompt = """You are an expert AI tutor observing a student working on a problem.
        
Your role is to:
1. Analyze what the student is doing
2. Determine if they need help
3. Decide whether to intervene or continue observing

Think carefully about pedagogical best practices:
- Don't interrupt if the student is making progress
- Wait for them to struggle briefly before helping
- Use Socratic questioning when appropriate
- Only intervene when truly necessary

Respond with your internal analysis and decision."""

        user_prompt = f"""Current Observation:
- Visual: {observation.get('visual', 'No visual data')}
- Audio: {observation.get('audio', 'No audio data')}
- Context: {observation.get('context', {})}

Student Profile:
- Patience Level: {student_model.get('pedagogy_profile', {}).get('patience_level', 'unknown')}
- Learning Style: {student_model.get('pedagogy_profile', {}).get('preferred_learning_style', 'unknown')}

Session State:
- Silence Duration: {session_state.get('silence_duration', 0)} seconds
- Last Intervention: {session_state.get('last_intervention_time', 0)} seconds ago

Analyze the situation and decide what to do."""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        response = await self.chat(messages=messages, tools=tools, temperature=0.3)

        return response
