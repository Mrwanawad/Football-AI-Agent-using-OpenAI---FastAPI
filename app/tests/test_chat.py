import pytest
from unittest.mock import AsyncMock, patch


class TestSessions:
    def test_create_session(self, client, auth_headers, sample_agent):
        resp = client.post(
            f"/api/v1/agents/{sample_agent['id']}/sessions",
            json={"title": "My Chat"},
            headers=auth_headers,
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["title"] == "My Chat"
        assert data["agent_id"] == sample_agent["id"]

    def test_create_session_default_title(self, client, auth_headers, sample_agent):
        resp = client.post(
            f"/api/v1/agents/{sample_agent['id']}/sessions",
            json={},
            headers=auth_headers,
        )
        assert resp.status_code == 201
        assert resp.json()["title"] == "New Session"

    def test_list_sessions(self, client, auth_headers, sample_agent):
        for i in range(3):
            client.post(
                f"/api/v1/agents/{sample_agent['id']}/sessions",
                json={"title": f"Session {i}"},
                headers=auth_headers,
            )
        resp = client.get(
            f"/api/v1/agents/{sample_agent['id']}/sessions",
            headers=auth_headers,
        )
        assert resp.status_code == 200
        assert len(resp.json()) == 3

    def test_get_session_with_messages(self, client, auth_headers, sample_session):
        agent_id = sample_session["agent_id"]
        session_id = sample_session["id"]
        resp = client.get(
            f"/api/v1/agents/{agent_id}/sessions/{session_id}",
            headers=auth_headers,
        )
        assert resp.status_code == 200
        assert "messages" in resp.json()
        assert isinstance(resp.json()["messages"], list)

    def test_delete_session(self, client, auth_headers, sample_session):
        agent_id = sample_session["agent_id"]
        session_id = sample_session["id"]
        resp = client.delete(
            f"/api/v1/agents/{agent_id}/sessions/{session_id}",
            headers=auth_headers,
        )
        assert resp.status_code == 204

    def test_session_not_found(self, client, auth_headers, sample_agent):
        resp = client.get(
            f"/api/v1/agents/{sample_agent['id']}/sessions/9999",
            headers=auth_headers,
        )
        assert resp.status_code == 404


class TestMessaging:
    @patch(
        "app.services.openai_service.chat_completion",
        new_callable=AsyncMock,
        return_value="Hello! How can I help you?",
    )
    def test_send_text_message(self, mock_chat, client, auth_headers, sample_session):
        agent_id = sample_session["agent_id"]
        session_id = sample_session["id"]
        resp = client.post(
            f"/api/v1/agents/{agent_id}/sessions/{session_id}/messages",
            json={"content": "Hello"},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["user_message"]["role"] == "user"
        assert data["user_message"]["content"] == "Hello"
        assert data["agent_message"]["role"] == "assistant"
        assert data["agent_message"]["content"] == "Hello! How can I help you?"
        mock_chat.assert_awaited_once()

    @patch(
        "app.services.openai_service.chat_completion",
        new_callable=AsyncMock,
        return_value="Reply 1",
    )
    def test_messages_persisted_in_history(self, mock_chat, client, auth_headers, sample_session):
        agent_id = sample_session["agent_id"]
        session_id = sample_session["id"]

        client.post(
            f"/api/v1/agents/{agent_id}/sessions/{session_id}/messages",
            json={"content": "First message"},
            headers=auth_headers,
        )

        resp = client.get(
            f"/api/v1/agents/{agent_id}/sessions/{session_id}",
            headers=auth_headers,
        )
        messages = resp.json()["messages"]
        assert len(messages) == 2
        assert messages[0]["role"] == "user"
        assert messages[1]["role"] == "assistant"

    @patch(
        "app.services.openai_service.chat_completion",
        new_callable=AsyncMock,
        return_value="Second reply",
    )
    def test_multi_turn_conversation(self, mock_chat, client, auth_headers, sample_session):
        agent_id = sample_session["agent_id"]
        session_id = sample_session["id"]

        for msg in ["Turn 1", "Turn 2"]:
            client.post(
                f"/api/v1/agents/{agent_id}/sessions/{session_id}/messages",
                json={"content": msg},
                headers=auth_headers,
            )

        resp = client.get(
            f"/api/v1/agents/{agent_id}/sessions/{session_id}",
            headers=auth_headers,
        )
        assert len(resp.json()["messages"]) == 4  # 2 user + 2 assistant

    def test_send_empty_message(self, client, auth_headers, sample_session):
        agent_id = sample_session["agent_id"]
        session_id = sample_session["id"]
        resp = client.post(
            f"/api/v1/agents/{agent_id}/sessions/{session_id}/messages",
            json={"content": ""},
            headers=auth_headers,
        )
        assert resp.status_code == 422


class TestVoiceInteraction:
    @patch("app.services.openai_service.speech_to_text", new_callable=AsyncMock, return_value="What is the weather?")
    @patch("app.services.openai_service.chat_completion", new_callable=AsyncMock, return_value="I don't know the weather.")
    @patch("app.services.openai_service.text_to_speech", new_callable=AsyncMock, return_value=b"fake-audio-bytes")
    def test_voice_message_returns_audio(
        self, mock_tts, mock_chat, mock_stt, client, auth_headers, sample_session
    ):
        agent_id = sample_session["agent_id"]
        session_id = sample_session["id"]

        resp = client.post(
            f"/api/v1/agents/{agent_id}/sessions/{session_id}/voice",
            files={"audio": ("test.webm", b"fake-audio-data", "audio/webm")},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        assert resp.headers["content-type"] == "audio/mpeg"
        assert resp.content == b"fake-audio-bytes"

        mock_stt.assert_awaited_once()
        mock_chat.assert_awaited_once()
        mock_tts.assert_awaited_once_with("I don't know the weather.")

    @patch("app.services.openai_service.speech_to_text", new_callable=AsyncMock, return_value="Hello agent")
    @patch("app.services.openai_service.chat_completion", new_callable=AsyncMock, return_value="Hi there!")
    @patch("app.services.openai_service.text_to_speech", new_callable=AsyncMock, return_value=b"audio")
    def test_voice_saves_messages_to_db(
        self, mock_tts, mock_chat, mock_stt, client, auth_headers, sample_session
    ):
        agent_id = sample_session["agent_id"]
        session_id = sample_session["id"]

        client.post(
            f"/api/v1/agents/{agent_id}/sessions/{session_id}/voice",
            files={"audio": ("voice.webm", b"data", "audio/webm")},
            headers=auth_headers,
        )

        # Messages should be persisted
        resp = client.get(
            f"/api/v1/agents/{agent_id}/sessions/{session_id}",
            headers=auth_headers,
        )
        messages = resp.json()["messages"]
        assert len(messages) == 2
        assert messages[0]["content"] == "Hello agent"
        assert messages[1]["content"] == "Hi there!"
