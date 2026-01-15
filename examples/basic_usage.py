"""Example usage of OAIT components."""

import asyncio
import os
from oait.config import get_settings, reset_settings
from oait.models import StudentModel, SessionState, StudentModelRepository
from oait.api.openrouter import OpenRouterClient


async def example_student_model() -> None:
    """Example: Create and save a student model."""
    print("\n=== Example: Student Model ===")
    
    # Create repository
    repo = StudentModelRepository("./memory/example.db")
    await repo.initialize()
    
    # Create a new student
    student = StudentModel(student_id="student_123")
    print(f"Created student: {student.student_id}")
    
    # Update competency
    from oait.models import CompetencyLevel
    student.update_competency("algebra", CompetencyLevel.MASTERED)
    print(f"Updated competency: algebra -> {student.competencies['algebra']}")
    
    # Save to database
    await repo.save(student)
    print("Saved to database")
    
    # Load back
    loaded = await repo.load("student_123")
    if loaded:
        print(f"Loaded student: {loaded.student_id}")
        print(f"Competencies: {loaded.competencies}")


async def example_session_state() -> None:
    """Example: Create and manage session state."""
    print("\n=== Example: Session State ===")
    
    # Create session state
    session = SessionState(
        session_id="session_001",
        student_id="student_123",
    )
    print(f"Created session: {session.session_id}")
    
    # Add transcript
    session.add_transcript("I'm working on quadratic equations", 1000.0)
    session.add_transcript("How do I factor this?", 1002.0)
    print(f"Added {len(session.student_speech_buffer)} transcripts")
    
    # Get recent transcripts
    recent = session.get_recent_transcripts(5.0)
    print(f"Recent transcripts: {[t.text for t in recent]}")


async def example_openrouter_chat() -> None:
    """Example: Chat with OpenRouter (requires API key)."""
    print("\n=== Example: OpenRouter Chat ===")
    
    # Check for API key
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        print("Skipping - no OPENROUTER_API_KEY found in environment")
        return
    
    # Create client
    client = OpenRouterClient(api_key=api_key)
    
    # Send a chat message
    messages = [
        {"role": "user", "content": "What is 2 + 2? Answer in one word."}
    ]
    
    try:
        response = await client.chat(messages=messages, temperature=0)
        content = response["choices"][0]["message"]["content"]
        print(f"Response: {content}")
    except Exception as e:
        print(f"Error: {e}")


async def main() -> None:
    """Run all examples."""
    print("OAIT Component Examples")
    print("=" * 50)
    
    await example_student_model()
    await example_session_state()
    await example_openrouter_chat()
    
    print("\n" + "=" * 50)
    print("Examples complete!")


if __name__ == "__main__":
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    # Run examples
    asyncio.run(main())
