# Text-to-Speech Implementation Plan

## Overview

Use Replicate's Chatterbox TTS model for AI voice responses to students.

## API Details

**Model**: `resemble-ai/chatterbox-turbo`  
Supported paralinguistic tags you can include in your text:
[clear throat], [sigh], [sush], [cough], [groan], [sniff], [gasp], [chuckle], [laugh]
**Provider**: Replicate  
**Token**: `REPLICATE_API_TOKEN` (stored in `.env`)

## Basic Usage

```python
import replicate

input = {
    "text": "Your text here",
    "voice": "Abigail",  # Voice selection
    "reference_audio": "https://replicate.delivery/pbxt/OEt67TSAP4l1Aq36bC3DSaRR1oQ5VT5prVkVh0yioOWJBTiO/voice.wav"
}

output = replicate.run(
    "resemble-ai/chatterbox-turbo",
    input=input
)

# Get file URL
print(output.url)  # "https://replicate.delivery/.../output.wav"

# Save to disk
with open("output.wav", "wb") as file:
    file.write(output.read())
```

## Caching Strategy

### Purpose
- **Cost savings**: Avoid regenerating common phrases
- **Latency reduction**: Serve cached audio instantly

### Cache Table Schema

```python
# Suggested schema for tts_cache table
class TTSCacheEntry:
    text_hash: str        # SHA256 of normalized text
    text: str             # Original text (for debugging)
    voice: str            # Voice used (e.g., "Abigail")
    wav_path: str         # Local path to cached .wav file
    created_at: datetime  # When cached
    last_used: datetime   # For LRU eviction
    use_count: int        # Usage statistics
```

### Common Phrases to Pre-cache

**Encouragements:**
- "Great job!"
- "That's correct!"
- "Excellent work!"
- "You're doing well!"
- "Perfect!"
- "Nice thinking!"

**Gentle Corrections:**
- "Not quite, let's try again."
- "Close! Think about it a bit more."
- "That's a good attempt, but not quite right."

**Prompts:**
- "What do you think?"
- "Can you explain your reasoning?"
- "Take your time."
- "Let's work through this together."
- "Show me your work on the whiteboard."

**Transitions:**
- "Let's move on to the next problem."
- "Now let's try something different."
- "Ready for the next one?"

**Warnings/Alerts:**
- "Remember to check your work."
- "Be careful with that step."
- "Don't forget the units."

## Implementation Modules

### 1. TTS Service (`src/oait/audio/tts.py`)

```python
import hashlib
import os
from pathlib import Path
import replicate
from typing import Optional

class TTSService:
    def __init__(self, cache_dir: str = "cache/tts"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.voice = "Abigail"
        self.reference_audio = "https://replicate.delivery/pbxt/OEt67TSAP4l1Aq36bC3DSaRR1oQ5VT5prVkVh0yioOWJBTiO/voice.wav"
    
    def _get_cache_key(self, text: str) -> str:
        """Generate cache key from normalized text."""
        normalized = text.strip().lower()
        return hashlib.sha256(normalized.encode()).hexdigest()[:16]
    
    def _get_cache_path(self, text: str) -> Path:
        """Get path for cached audio file."""
        key = self._get_cache_key(text)
        return self.cache_dir / f"{key}.wav"
    
    def get_cached(self, text: str) -> Optional[Path]:
        """Return cached audio path if exists."""
        path = self._get_cache_path(text)
        if path.exists():
            return path
        return None
    
    async def synthesize(self, text: str, use_cache: bool = True) -> Path:
        """Generate or retrieve TTS audio."""
        # Check cache first
        if use_cache:
            cached = self.get_cached(text)
            if cached:
                return cached
        
        # Generate via Replicate
        output = replicate.run(
            "resemble-ai/chatterbox-turbo",
            input={
                "text": text,
                "voice": self.voice,
                "reference_audio": self.reference_audio
            }
        )
        
        # Save to cache
        cache_path = self._get_cache_path(text)
        with open(cache_path, "wb") as f:
            f.write(output.read())
        
        return cache_path
    
    def precache_phrases(self, phrases: list[str]):
        """Pre-generate common phrases for cache."""
        for phrase in phrases:
            if not self.get_cached(phrase):
                self.synthesize(phrase, use_cache=False)
```

### 2. Cache Warming Script

```python
# scripts/warm_tts_cache.py
COMMON_PHRASES = [
    # Encouragements
    "Great job!",
    "That's correct!",
    "Excellent work!",
    "You're doing well!",
    "Perfect!",
    # Corrections
    "Not quite, let's try again.",
    "Close! Think about it a bit more.",
    # Prompts
    "What do you think?",
    "Can you explain your reasoning?",
    "Show me your work on the whiteboard.",
    # Transitions
    "Let's move on to the next problem.",
    "Ready for the next one?",
]

if __name__ == "__main__":
    from oait.audio.tts import TTSService
    tts = TTSService()
    tts.precache_phrases(COMMON_PHRASES)
```

## Integration Points

1. **OODA Loop**: After `Decision` is made with `response_text`, pass to TTS
2. **WebSocket Server**: Stream or send audio URL to client
3. **Client**: Play audio via `<audio>` element or Web Audio API

## Cost Considerations

- Replicate charges per inference
- Caching common phrases reduces costs significantly
- Consider batch processing during off-peak times

## Future Enhancements

1. **Voice cloning**: Custom tutor voice with reference audio
2. **Emotion control**: Adjust tone based on context (encouraging vs. serious)
3. **SSML support**: Fine-grained control over pronunciation
4. **Local fallback**: Use local TTS (e.g., pyttsx3) if API unavailable
5. **Streaming**: Stream audio chunks for faster perceived response

## Dependencies

Add to `pyproject.toml`:
```toml
[project.dependencies]
replicate = "^0.25.0"
```

## Environment Variables

```bash
# .env
REPLICATE_API_TOKEN=r8_xxxxxxxxxxxx
```



# What type of voice:

Limited direct studies exist on specific voice types like parent, teacher, or celebrity for educational chatbots, but research on related aspects like voice modality, anthropomorphism, and embodiment provides insights into engagement, trust, and learning.
​

Key Findings
Voice-based interactions outperform text-based ones in boosting emotional and cognitive engagement with educational robots. Physical embodiment of AI tutors, often paired with humanistic voices, increases initial on-task enjoyment but shows mixed effects on sustained performance and may fade due to novelty. Anthropomorphic traits like high sociability correlate negatively with task performance, while disturbance reduces enjoyment; balanced humanoid designs foster trust without uncanny valley issues.
​

Voice vs. Other Personas
No studies directly compare parent, teacher, famous person, or admired figure voices to robotic or humanistic ones in chatbots. However, humanistic and anthropomorphic voices (e.g., natural speech in robots) enhance perceived agency and reduce anxiety compared to purely robotic tones, improving willingness to communicate and self-perceived competence in language learning. Voice-enabled AI generally heightens motivation over text, suggesting humanistic over robotic for better student interaction.
​

Implications for Design
Educational chatbots benefit from voice over text for engagement, with physically embodied humanistic voices aiding initial trust and enjoyment. Avoid overly sociable personas that might distract from tasks; prioritize low-disturbance, natural voices to support learning without hindering performance. Future research should test specific personas like teacher-like voices against baselines for targeted outcomes in student trust and retention.
​