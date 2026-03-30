from fastapi import APIRouter, Depends, UploadFile, File
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.core.security import get_current_user_id
from app.schemas.session import (
    SessionCreate,
    SessionResponse,
    SessionWithMessages,
    MessageCreate,
    ChatResponse,
    MessageResponse,
)
from app.services import chat_service

router = APIRouter(prefix="/agents/{agent_id}/sessions", tags=["Sessions & Messaging"])


@router.post("", response_model=SessionResponse, status_code=201)
def create_session(
    agent_id: int,
    data: SessionCreate = SessionCreate(),
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """Start a new chat session for an agent."""
    return chat_service.create_session(db, agent_id=agent_id, user_id=user_id, data=data)


@router.get("", response_model=list[SessionResponse])
def list_sessions(
    agent_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """List all chat sessions for an agent."""
    return chat_service.get_sessions(db, agent_id=agent_id, user_id=user_id)


@router.get("/{session_id}", response_model=SessionWithMessages)
def get_session(
    agent_id: int,
    session_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """Retrieve a session with its full message history."""
    session = chat_service.get_session_or_404(db, session_id, user_id=user_id)
    return session


@router.delete("/{session_id}", status_code=204)
def delete_session(
    agent_id: int,
    session_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """Delete a chat session and all its messages."""
    chat_service.delete_session(db, session_id, user_id=user_id)


@router.post("/{session_id}/messages", response_model=ChatResponse)
async def send_message(
    agent_id: int,
    session_id: int,
    data: MessageCreate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """Send a text message and receive the agent's response."""
    user_msg, assistant_msg = await chat_service.send_message(
        db, session_id=session_id, user_id=user_id, content=data.content
    )
    return ChatResponse(
        user_message=MessageResponse.model_validate(user_msg),
        agent_message=MessageResponse.model_validate(assistant_msg),
    )


@router.post("/{session_id}/voice", response_class=Response)
async def send_voice_message(
    agent_id: int,
    session_id: int,
    audio: UploadFile = File(..., description="Audio file (webm, mp3, wav, ogg, m4a)"),
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """
    Send a voice message and receive an audio response.

    - Transcribes the uploaded audio (STT)
    - Sends the transcript to the agent for a response
    - Converts the response to speech (TTS)
    - Returns the audio file as `audio/mpeg`
    """
    audio_bytes = await audio.read()
    _, _, audio_response = await chat_service.send_voice_message(
        db,
        session_id=session_id,
        user_id=user_id,
        audio_bytes=audio_bytes,
        filename=audio.filename or "audio.webm",
    )
    return Response(content=audio_response, media_type="audio/m4a")