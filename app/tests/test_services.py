import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import HTTPException

from app.services.user_service import create_user, authenticate_user
from app.services.agent_service import create_agent, get_agent_or_404
from app.schemas.user import UserCreate
from app.schemas.agent import AgentCreate


class TestUserService:
    def test_create_user_success(self, db):
        data = UserCreate(username="alice", email="alice@test.com", password="password123")
        user = create_user(db, data)
        assert user.id is not None
        assert user.username == "alice"
        assert user.hashed_password != "password123"

    def test_create_user_duplicate_username(self, db):
        data = UserCreate(username="alice", email="a@test.com", password="password123")
        create_user(db, data)
        with pytest.raises(HTTPException) as exc:
            create_user(db, UserCreate(username="alice", email="b@test.com", password="password123"))
        assert exc.value.status_code == 400

    def test_authenticate_user_success(self, db):
        create_user(db, UserCreate(username="bob", email="bob@test.com", password="mypassword"))
        user = authenticate_user(db, "bob", "mypassword")
        assert user.username == "bob"

    def test_authenticate_user_wrong_password(self, db):
        create_user(db, UserCreate(username="carol", email="carol@test.com", password="rightpass"))
        with pytest.raises(HTTPException) as exc:
            authenticate_user(db, "carol", "wrongpass")
        assert exc.value.status_code == 401


class TestAgentService:
    def _make_user(self, db):
        from app.models.user import User
        from app.core.security import hash_password
        user = User(username="owner", email="owner@test.com", hashed_password=hash_password("pass"))
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    def test_create_agent(self, db):
        user = self._make_user(db)
        agent = create_agent(db, AgentCreate(name="Bot", prompt="Be helpful."), owner_id=user.id)
        assert agent.id is not None
        assert agent.owner_id == user.id

    def test_get_agent_not_found_raises_404(self, db):
        with pytest.raises(HTTPException) as exc:
            get_agent_or_404(db, agent_id=999, owner_id=1)
        assert exc.value.status_code == 404

    def test_get_agent_wrong_owner_raises_404(self, db):
        user = self._make_user(db)
        agent = create_agent(db, AgentCreate(name="Bot", prompt="Hi"), owner_id=user.id)
        with pytest.raises(HTTPException) as exc:
            get_agent_or_404(db, agent_id=agent.id, owner_id=999)
        assert exc.value.status_code == 404


class TestOpenAIService:
    @pytest.mark.asyncio
    async def test_chat_completion_called_with_system_prompt(self):
        with patch("app.services.openai_service.get_openai_client") as mock_get_client:
            mock_client = MagicMock()
            mock_client.chat.completions.create = AsyncMock(
                return_value=MagicMock(
                    choices=[MagicMock(message=MagicMock(content="Test response"))]
                )
            )
            mock_get_client.return_value = mock_client

            from app.services.openai_service import chat_completion
            result = await chat_completion("You are a bot.", [{"role": "user", "content": "Hi"}])

            assert result == "Test response"
            call_args = mock_client.chat.completions.create.call_args
            messages = call_args.kwargs["messages"]
            assert messages[0]["role"] == "system"
            assert messages[0]["content"] == "You are a bot."

    @pytest.mark.asyncio
    async def test_speech_to_text(self):
        with patch("app.services.openai_service.get_openai_client") as mock_get_client:
            mock_client = MagicMock()
            mock_client.audio.transcriptions.create = AsyncMock(
                return_value=MagicMock(text="transcribed text")
            )
            mock_get_client.return_value = mock_client

            from app.services.openai_service import speech_to_text
            result = await speech_to_text(b"audio bytes", "audio.webm")
            assert result == "transcribed text"

    @pytest.mark.asyncio
    async def test_text_to_speech(self):
        with patch("app.services.openai_service.get_openai_client") as mock_get_client:
            mock_client = MagicMock()
            mock_client.audio.speech.create = AsyncMock(
                return_value=MagicMock(content=b"audio output")
            )
            mock_get_client.return_value = mock_client

            from app.services.openai_service import text_to_speech
            result = await text_to_speech("Hello world")
            assert result == b"audio output"
