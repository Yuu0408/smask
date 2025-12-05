"""reset ai_state to new shared state schema

Revision ID: 9b2e4f3dd7af
Revises: 28a10d997686
Create Date: 2025-05-06 19:45:00.000000

"""
from typing import Sequence, Union
import json

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "9b2e4f3dd7af"
down_revision: Union[str, None] = "28a10d997686"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _build_shared_state(basic_form: dict) -> dict:
    return {
        "basic_form": basic_form or {},
        "clarified_form": {},
        "symptom_notes": [],
        "red_flags": [],
        "info_gaps_basic": [],
        "info_gaps_symptom": [],
        "reasoning_snapshot": None,
        "pending_questions": [],
        "last_question": None,
        "conversation_tail": [],
    }


def upgrade() -> None:
    conn = op.get_bind()
    try:
        med_rows = conn.execute(sa.text("SELECT record_id, data FROM medical_records")).fetchall()
        med_map = {row.record_id: row.data or {} for row in med_rows}
    except Exception:
        # If medical_records table is absent, skip silently
        med_map = {}
    try:
        state_rows = conn.execute(sa.text("SELECT record_id, user_id FROM ai_state")).fetchall()
    except Exception:
        return

    for row in state_rows:
        basic_form = med_map.get(row.record_id, {})
        payload = {
            "shared_state": _build_shared_state(basic_form),
            "stage": "FORM_CLARIFICATION",
        }
        conn.execute(
            sa.text(
                "UPDATE ai_state SET data = :data WHERE record_id = :record_id AND user_id = :user_id"
            ),
            {"data": json.dumps(payload), "record_id": row.record_id, "user_id": row.user_id},
        )


def downgrade() -> None:
    conn = op.get_bind()
    try:
        conn.execute(sa.text("UPDATE ai_state SET data = '{}'"))
    except Exception:
        return
