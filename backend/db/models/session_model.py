from sqlalchemy import Column, String, Text, JSON
from sqlalchemy.dialects.postgresql import UUID
import uuid
from db.base import Base

class ChatSession(Base):
    __tablename__ = "chat_sessions"

    session_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    todo = Column(JSON, nullable=True)
    diagnosis_paper = Column(JSON)
    note = Column(Text, default="")
    reasoning = Column(Text, default="")
    history = Column(Text, default="")
    decision = Column(String, default="CONVERSATION")
    medical_record = Column(JSON)
    diagnosis_response = Column(JSON)
    additional_info = Column(Text, default="")
    follow_up_questions = Column(JSON, nullable=True)
    previous_state = Column(String, default="CONVERSATION")
