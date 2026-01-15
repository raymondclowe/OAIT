"""Storage repository for student models."""

import logging
import json
import aiosqlite
from pathlib import Path
from typing import Optional, List
from datetime import datetime
from .data_models import StudentModel, SessionHistoryEntry

logger = logging.getLogger(__name__)


class StudentModelRepository:
    """Repository for storing and retrieving student models."""

    def __init__(self, db_path: str = "./memory/oait.db"):
        """Initialize student model repository.

        Args:
            db_path: Path to SQLite database
        """
        self.db_path = db_path
        self._ensure_db_dir()

    def _ensure_db_dir(self) -> None:
        """Ensure database directory exists."""
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)

    async def initialize(self) -> None:
        """Initialize database schema."""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS student_models (
                    student_id TEXT PRIMARY KEY,
                    data TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """)
            await db.commit()
            logger.info("Student model database initialized")

    async def save(self, model: StudentModel) -> None:
        """Save a student model.

        Args:
            model: Student model to save
        """
        async with aiosqlite.connect(self.db_path) as db:
            model_json = model.model_dump_json()
            await db.execute(
                """
                INSERT OR REPLACE INTO student_models 
                (student_id, data, created_at, updated_at)
                VALUES (?, ?, ?, ?)
                """,
                (
                    model.student_id,
                    model_json,
                    model.created_at.isoformat(),
                    model.updated_at.isoformat(),
                ),
            )
            await db.commit()
            logger.info(f"Saved student model: {model.student_id}")

    async def load(self, student_id: str) -> Optional[StudentModel]:
        """Load a student model.

        Args:
            student_id: Student ID to load

        Returns:
            Student model or None if not found
        """
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                "SELECT data FROM student_models WHERE student_id = ?",
                (student_id,),
            ) as cursor:
                row = await cursor.fetchone()
                if row:
                    model_data = json.loads(row[0])
                    return StudentModel(**model_data)
                return None

    async def list_all(self) -> List[str]:
        """List all student IDs.

        Returns:
            List of student IDs
        """
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("SELECT student_id FROM student_models") as cursor:
                rows = await cursor.fetchall()
                return [row[0] for row in rows]

    async def delete(self, student_id: str) -> bool:
        """Delete a student model.

        Args:
            student_id: Student ID to delete

        Returns:
            True if deleted, False if not found
        """
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                "DELETE FROM student_models WHERE student_id = ?",
                (student_id,),
            )
            await db.commit()
            deleted = cursor.rowcount > 0
            if deleted:
                logger.info(f"Deleted student model: {student_id}")
            return deleted

    async def create_default_model(self, student_id: str) -> StudentModel:
        """Create a default student model.

        Args:
            student_id: Student ID

        Returns:
            New student model
        """
        model = StudentModel(student_id=student_id)
        await self.save(model)
        return model
