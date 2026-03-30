from datetime import datetime, timezone
from sqlalchemy import String, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False, default="New Session")
    agent_id: Mapped[int] = mapped_column(ForeignKey("agents.id"), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    agent: Mapped["Agent"] = relationship("Agent", back_populates="sessions")  # noqa: F821
    messages: Mapped[list["Message"]] = relationship(  # noqa: F821
        "Message", back_populates="session", cascade="all, delete-orphan",
        order_by="Message.created_at"
    )