# End-to-End Testing Guide for OAIT

This guide walks through testing the complete OAIT system from setup to a live tutoring session.

## Prerequisites

### Required
- Python 3.9+
- OpenRouter API key ([Get one here](https://openrouter.ai/))
- Microphone (for audio testing)
- Webcam or drawing tablet (optional, for whiteboard testing)

### Recommended
- GPU (for faster Whisper inference)
- Chrome or Edge browser (for best PWA support)
- Headphones (to avoid audio feedback)

## Setup

### 1. Install Dependencies

```bash
# Clone repository
git clone https://github.com/raymondclowe/OAIT.git
cd OAIT

# Run setup script (installs uv, creates venv, installs deps)
bash setup.sh
```

### 2. Configure Environment

```bash
# Copy example config
cp .env.example .env

# Edit .env and add your OpenRouter API key
nano .env  # or vim, code, etc.
```

Required settings in `.env`:
```bash
# REQUIRED: Get from https://openrouter.ai/
OPENROUTER_API_KEY=sk-or-v1-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Recommended: Use a model that supports vision + tools
OPENROUTER_MODEL=google/gemini-3-pro-preview

# Optional: Whisper model size (base, small, medium, large)
WHISPER_MODEL_SIZE=base

# Optional: Server configuration
SERVER_HOST=0.0.0.0
SERVER_PORT=7860
```

### 3. Verify Installation

```bash
# Activate virtual environment
source .venv/bin/activate

# Run all tests
pytest -v

# Should see: 46/46 tests passing
```

## Testing Components

### Unit Tests

Test individual components in isolation:

```bash
# Test configuration loading
pytest tests/unit/test_config.py -v

# Test data models
pytest tests/unit/test_models.py -v

# Test pedagogical tools
pytest tests/unit/test_pedagogical_tools.py -v
```

### Integration Tests

Test components working together:

```bash
# Test complete workflows
pytest tests/integration/test_component_integration.py -v -s

# Should show analysis outputs for scenarios
```

## Manual Testing

### 1. Start the Server

```bash
# From project root with venv activated
python start_server.py
```

You should see:
```
╔═══════════════════════════════════════════════════════════╗
║              OAIT - Observational AI Tutor                ║
║                    Starting Server                         ║
╚═══════════════════════════════════════════════════════════╝

✓ Configuration loaded
✓ OpenRouter API key found
✓ Whisper model: base
✓ Server starting on http://0.0.0.0:7860

Open your browser to:
  → http://localhost:7860
```

### 2. Test Web UI

Open browser to `http://localhost:7860`

**Check:**
- [ ] Page loads correctly
- [ ] No console errors (F12 → Console)
- [ ] UI displays student ID input
- [ ] Start Session button visible

### 3. Test Session Creation

1. Enter student ID: `test-student-001`
2. Click "Start Session"
3. Session ID should appear
4. UI should show "Session Active"

**Check:**
- [ ] Session starts successfully
- [ ] Session ID displayed
- [ ] WebSocket connection established
- [ ] No errors in console

### 4. Test Audio Pipeline

1. Click "Start Audio" button
2. Grant microphone permission
3. Speak clearly: "Hello, I need help with math"
4. Wait 2-3 seconds

**Check:**
- [ ] Microphone permission granted
- [ ] Audio indicator shows activity
- [ ] Transcript appears in UI
- [ ] No audio errors in console

**Expected Output:**
```
Transcript: Hello, I need help with math
```

### 5. Test Whiteboard

1. Use mouse/touch to draw on canvas
2. Draw simple shapes or equations
3. Wait 3-5 seconds for frame capture

**Check:**
- [ ] Canvas allows drawing
- [ ] Drawing tools work smoothly
- [ ] Canvas sends frames via WebSocket
- [ ] No canvas errors in console

### 6. Test AI Analysis

With audio and whiteboard active:

1. Say: "What is 2 plus 2?"
2. Wait for AI response (5-10 seconds)
3. Response should appear and be spoken

**Check:**
- [ ] Question detected by AI
- [ ] AI generates response
- [ ] Response displayed in UI
- [ ] TTS speaks response (Web Speech API)

**Expected Flow:**
1. Audio → Whisper STT → "What is 2 plus 2?"
2. Trigger detection → Explicit question detected
3. OODA loop → Analyze → Decide (SPEAK)
4. OpenRouter → Generate response
5. TTS → Speak response

### 7. Test Pedagogical Tools

Test each tool manually:

**Calculation Verification:**
```python
from oait.tools.pedagogical import PedagogicalTools

result = PedagogicalTools.verify_calculation("2 + 2", "4")
print(result)
# Should show: correct=True, correct_answer=4.0
```

**Confusion Detection:**
```python
transcript = "Um, I'm not sure how to solve this"
result = PedagogicalTools.assess_confusion_level(transcript)
print(result)
# Should show: confusion_level='medium' or 'high'
```

**Question Detection:**
```python
transcript = "How do I solve for x?"
result = PedagogicalTools.detect_question(transcript)
print(result)
# Should show: is_question=True
```

### 8. Test OODA Loop

Monitor server logs while student interacts:

```bash
# In server terminal, watch for:
[OODA] Starting cycle #1
[OODA] Observation: <audio + visual data>
[OODA] Analysis: <student state analysis>
[OODA] Decision: SPEAK / WAIT / UPDATE_DB
[OODA] Action: <action details>
```

**Test Scenarios:**

1. **Silent Student** (10+ seconds)
   - Expected: Trigger on silence
   - AI should check if help needed

2. **Explicit Question**
   - Say: "Can you help me?"
   - Expected: Immediate SPEAK decision

3. **Confused Student**
   - Say: "Um... I don't understand this at all"
   - Expected: High confusion detected, intervention

4. **Working Student**
   - Say: "I think I'll try this approach"
   - Expected: WAIT decision, no interruption

### 9. Test PWA Installation

**Android:**
1. Open `https://your-server:7860` in Chrome
2. Menu → "Install app"
3. Confirm installation
4. Launch from home screen

**Desktop:**
1. Open `https://your-server:7860` in Chrome/Edge
2. Click install icon (⊕) in address bar
3. Confirm installation
4. Launch as standalone app

**Check:**
- [ ] App installs successfully
- [ ] Icon appears on home/desktop
- [ ] App opens in standalone mode
- [ ] All features work in installed app

### 10. Test Offline Mode

1. Install PWA (see above)
2. Turn off network / close server
3. Launch app from home screen

**Check:**
- [ ] UI loads from cache
- [ ] Offline message shown for WebSocket
- [ ] Static content available
- [ ] Reconnects when network restored

## Performance Testing

### Latency Measurements

Measure key latencies:

```python
import time
import asyncio
from oait.audio.whisper_stt import WhisperSTT
from oait.api.openrouter import OpenRouterClient

# Test Whisper latency
whisper = WhisperSTT(model_size="base")
start = time.time()
transcript = await whisper.transcribe(audio_file)
whisper_latency = time.time() - start
print(f"Whisper latency: {whisper_latency:.2f}s")

# Test OpenRouter latency
client = OpenRouterClient(api_key="...", model="google/gemini-3-pro-preview")
start = time.time()
response = await client.chat(messages=[{"role": "user", "content": "Hello"}])
llm_latency = time.time() - start
print(f"LLM latency: {llm_latency:.2f}s")
```

**Target Latencies:**
- Whisper STT: < 1s (local inference)
- OpenRouter LLM: < 3s (network + cloud)
- Decision making: < 0.5s (local logic)
- End-to-end: < 5s (total from speech to response)

### Load Testing

Test with multiple concurrent sessions:

```bash
# Install load testing tool
pip install locust

# Create locustfile.py with WebSocket tests
# Run load test
locust -f locustfile.py --host=http://localhost:7860
```

## Troubleshooting

### Common Issues

**1. Whisper model not found**
```
Error: Model not found
Solution: Model downloads on first run. Wait 2-5 minutes.
Location: ~/.cache/huggingface/hub/
```

**2. OpenRouter API errors**
```
Error: 401 Unauthorized
Solution: Check OPENROUTER_API_KEY in .env
```

**3. Microphone not working**
```
Error: Permission denied
Solution: 
- Grant microphone permission in browser
- Check browser settings
- Use HTTPS (required for getUserMedia)
```

**4. WebSocket connection fails**
```
Error: WebSocket connection failed
Solution:
- Check server is running
- Verify port 7860 is accessible
- Check firewall settings
```

**5. Service Worker not registering**
```
Error: Service Worker registration failed
Solution:
- Use HTTPS or localhost
- Clear browser cache
- Check console for errors
```

## Success Criteria

A successful end-to-end test includes:

- [x] All 46 tests passing
- [x] Server starts without errors
- [x] WebSocket connection established
- [x] Audio captured and transcribed
- [x] Whiteboard captures frames
- [x] AI detects questions and confusion
- [x] OODA loop runs complete cycles
- [x] AI generates and speaks responses
- [x] PWA installs on mobile/desktop
- [x] Offline mode provides UI access
- [x] Latencies within targets
- [x] No memory leaks or crashes

## Next Steps

After successful testing:

1. **User Acceptance Testing**
   - Recruit 3-5 real students
   - Test with actual math problems
   - Collect feedback on intervention quality

2. **Performance Optimization**
   - Profile bottlenecks
   - Optimize heavy operations
   - Reduce API calls where possible

3. **Production Deployment**
   - Set up HTTPS
   - Configure production settings
   - Set up monitoring and logging

---

**Last Updated**: 2026-01-17
