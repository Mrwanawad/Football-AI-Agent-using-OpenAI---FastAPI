from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.session import ChatSession
from app.models.message import Message, MessageRole
from app.schemas.session import SessionCreate
from app.services.agent_service import get_agent_or_404
from app.services import openai_service


def create_session(db: Session, agent_id: int, user_id: int, data: SessionCreate) -> ChatSession:
    # Verify agent belongs to user
    get_agent_or_404(db, agent_id, user_id)
    session = ChatSession(title=data.title, agent_id=agent_id, user_id=user_id)
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


def get_sessions(db: Session, agent_id: int, user_id: int) -> list[ChatSession]:
    get_agent_or_404(db, agent_id, user_id)
    return (
        db.query(ChatSession)
        .filter(ChatSession.agent_id == agent_id, ChatSession.user_id == user_id)
        .all()
    )


def get_session_or_404(db: Session, session_id: int, user_id: int) -> ChatSession:
    session = (
        db.query(ChatSession)
        .filter(ChatSession.id == session_id, ChatSession.user_id == user_id)
        .first()
    )
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    return session


def delete_session(db: Session, session_id: int, user_id: int) -> None:
    session = get_session_or_404(db, session_id, user_id)
    db.delete(session)
    db.commit()


def _build_message_history(session: ChatSession) -> list[dict]:
    return [
        {"role": msg.role.value, "content": msg.content}
        for msg in session.messages
    ]


async def send_message(
    db: Session, session_id: int, user_id: int, content: str
) -> tuple[Message, Message]:
    session = get_session_or_404(db, session_id, user_id)
    agent = session.agent

    # Persist user message
    user_msg = Message(session_id=session_id, role=MessageRole.user, content=content)
    db.add(user_msg)
    db.commit()
    db.refresh(user_msg)

    # Build history including the new user message
    history = _build_message_history(session)

    # Get AI response
    ai_text = await openai_service.chat_completion(agent.prompt, history)

    # Persist assistant message
    assistant_msg = Message(
        session_id=session_id, role=MessageRole.assistant, content=ai_text
    )
    db.add(assistant_msg)
    db.commit()
    db.refresh(assistant_msg)

    return user_msg, assistant_msg


async def send_voice_message(
    db: Session, session_id: int, user_id: int, audio_bytes: bytes, filename: str
) -> tuple[Message, Message, bytes]:
    # STT: audio → text
    user_text = await openai_service.speech_to_text(audio_bytes, filename)

    # Chat: text → AI response text
    user_msg, assistant_msg = await send_message(db, session_id, user_id, user_text)

    # TTS: AI response text → audio
    audio_response = await openai_service.text_to_speech(assistant_msg.content)

    return user_msg, assistant_msg, audio_response