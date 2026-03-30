import io
from openai import AsyncOpenAI
from app.core.config import settings
 
_client: AsyncOpenAI | None = None
 
 
def get_openai_client() -> AsyncOpenAI:
    global _client
    if _client is None:
        _client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
    return _client
 
 
async def chat_completion(system_prompt: str, messages: list[dict]) -> str:
    """Call OpenAI chat completion with a system prompt and message history."""
    client = get_openai_client()
    full_messages = [{"role": "system", "content": system_prompt}] + messages
    response = await client.chat.completions.create(
        model=settings.OPENAI_CHAT_MODEL,
        messages=full_messages,
    )
    return response.choices[0].message.content
 
 
async def speech_to_text(audio_bytes: bytes, filename: str = "audio.webm") -> str:
    """Transcribe audio bytes to text using OpenAI Whisper."""
    client = get_openai_client()
    audio_file = io.BytesIO(audio_bytes)
    audio_file.name = filename
    transcript = await client.audio.transcriptions.create(
        model=settings.OPENAI_STT_MODEL,
        file=audio_file,
    )
    return transcript.text
 
 
async def text_to_speech(text: str) -> bytes:
    """Convert text to speech audio bytes using OpenAI TTS."""
    client = get_openai_client()
    response = await client.audio.speech.create(
        model=settings.OPENAI_TTS_MODEL,
        voice=settings.OPENAI_TTS_VOICE,
        input=text,
    )
    return response.content