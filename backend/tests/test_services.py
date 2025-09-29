from backend.services import Services, get_openai_client, build_review_prompt, ReviewResult

import io
import json
import os
import sys
import types
import pytest


# -----------------------------
# Helpers: Fake OpenAI SDK
# -----------------------------
class FakeTranscriptions:
    def __init__(self):
        self.to_return = None
        self.calls = []

    def create(self, **kwargs):
        self.calls.append(kwargs)
        return self.to_return


class FakeAudio:
    def __init__(self):
        self.transcriptions = FakeTranscriptions()


class FakeResponses:
    def __init__(self):
        self.to_return = None
        self.calls = []

    def create(self, **kwargs):
        self.calls.append(kwargs)
        return self.to_return


class FakeOpenAI:
    def __init__(self, api_key=None):
        self.api_key = api_key
        self.audio = FakeAudio()
        self.responses = FakeResponses()


# Response shapes for transcript_to_chatgpt
class _FakeContent:
    def __init__(self, text):
        self.text = text


class _FakeOutput:
    def __init__(self, content):
        self.content = content


class FakeRespNested:
    """Shape: resp.output[0].content[0].text"""
    def __init__(self, text):
        self.output = [_FakeOutput([_FakeContent(text)])]


class FakeRespOutputText:
    """Shape: resp.output_text"""
    def __init__(self, text):
        self.output_text = text


class FakeTranscriptionObj:
    """SDK-like object with .text attribute (used to document current bug)."""
    def __init__(self, text):
        self.text = text
    def __repr__(self):
        return f"<FakeTranscriptionObj text={self.text!r}>"


# -----------------------------
# Fixtures
# -----------------------------
@pytest.fixture
def fake_client():
    return FakeOpenAI(api_key="TESTKEY")


@pytest.fixture
def sample_review_json():
    return json.dumps({
        "rating": 7.5,
        "feedback": "Good structure; add concrete metrics.",
        "slightly_optimized_version": "Slightly expanded as requested.",
        "how_to_make_it_stronger": "Add tech, metrics, and outcomes.",
        "opt_with_placeholders": "Optimized with [PLACEHOLDER] for names.",
        "summary": "Solid answer; can be sharper."
    })


# -----------------------------
# get_openai_client tests
# -----------------------------
def test_get_openai_client_raises_when_key_missing(monkeypatch):
    # Make sure env var is absent
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    import backend.services as mod
    monkeypatch.setattr(mod, "OpenAI", FakeOpenAI)

    with pytest.raises(RuntimeError, match="OPENAI_API_KEY is not set"):
        get_openai_client()


def test_get_openai_client_uses_env_and_returns_client(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "ENVKEY")

    import backend.services as mod
    monkeypatch.setattr(mod, "OpenAI", FakeOpenAI)

    client = get_openai_client()
    assert isinstance(client, FakeOpenAI)
    assert client.api_key == "ENVKEY"


# -----------------------------
# build_review_prompt tests
# -----------------------------
def test_build_review_prompt_contains_question_and_transcript():
    q = "Tell me about a time you led a project."
    t = "I led a team of 4 and shipped X."
    prompt = build_review_prompt(q, t)

    # sanity checks
    assert isinstance(prompt, str)
    assert "Question:" in prompt and q in prompt
    assert "Transcript:" in prompt and t in prompt

    # ensure required JSON keys are present in instructions
    must_have = [
        "rating", "feedback", "slightly_optimized_version",
        "how_to_make_it_stronger", "opt_with_placeholders", "summary",
        "No answer provided."
    ]
    for token in must_have:
        assert token in prompt


# -----------------------------
# Services.speech_to_text tests
# -----------------------------
def test_speech_to_text_raises_on_missing_audio(fake_client):
    svc = Services(client=fake_client, audio_source=None)
    with pytest.raises(ValueError, match="No audio file provided"):
        svc.speech_to_text()


def test_speech_to_text_with_path_success(tmp_path, fake_client):
    # Make a fake audio file
    audio_path = tmp_path / "audio.wav"
    audio_path.write_bytes(b"FAKEAUDIO")

    # Fake SDK returns plain text
    fake_client.audio.transcriptions.to_return = "TRANSCRIBED TEXT"

    svc = Services(client=fake_client, audio_source=str(audio_path))
    text = svc.speech_to_text()

    # Check text retained
    assert text == "TRANSCRIBED TEXT"
    assert svc.transcription == "TRANSCRIBED TEXT"

    # Ensure create() called with expected model/defaults
    kwargs = fake_client.audio.transcriptions.calls[-1]
    assert kwargs["model"] == "gpt-4o-transcribe"
    assert kwargs["response_format"] == "text"
    assert hasattr(kwargs["file"], "read")  # file-like


def test_speech_to_text_with_bytes_success(fake_client):
    # Provide raw bytes; current implementation passes bytes directly
    audio_bytes = b"FAKEAUDIOBYTES"
    fake_client.audio.transcriptions.to_return = "OK TEXT"

    svc = Services(client=fake_client, audio_source=audio_bytes)
    text = svc.speech_to_text()

    assert text == "OK TEXT"
    assert svc.transcription == "OK TEXT"

    kwargs = fake_client.audio.transcriptions.calls[-1]
    assert kwargs["file"] == audio_bytes  # current code passes bytes


def test_speech_to_text_raises_on_empty_response(fake_client, tmp_path):
    audio_path = tmp_path / "audio.wav"
    audio_path.write_bytes(b"X")

    # Simulate falsy responses
    for bad in (None, ""):
        fake_client.audio.transcriptions.to_return = bad
        svc = Services(client=fake_client, audio_source=str(audio_path))
        with pytest.raises(RuntimeError, match="Empty transcription response"):
            svc.speech_to_text()


@pytest.mark.xfail(reason="Current implementation stringifies the object, losing .text")
def test_speech_to_text_should_extract_text_attr_when_sdk_returns_object(fake_client, tmp_path):
    """Documented fragility: when SDK returns an object with .text, the code uses str(obj)."""
    audio_path = tmp_path / "audio.wav"
    audio_path.write_bytes(b"X")

    fake_client.audio.transcriptions.to_return = FakeTranscriptionObj("REAL TEXT")
    svc = Services(client=fake_client, audio_source=str(audio_path))
    text = svc.speech_to_text()

    # Desired behavior (will fail until implementation is fixed):
    assert text == "REAL TEXT"
    assert svc.transcription == "REAL TEXT"


# -----------------------------
# Services.transcript_to_chatgpt tests
# -----------------------------
def _make_service_with_transcript(fake_client, transcript="Some transcript"):
    svc = Services(client=fake_client, audio_source=None, transcription=transcript)
    return svc


def test_transcript_to_chatgpt_raises_without_transcription(fake_client):
    svc = Services(client=fake_client, audio_source=None, transcription=None)
    with pytest.raises(ValueError, match="No transcription available"):
        svc.transcript_to_chatgpt("Q")


def test_transcript_to_chatgpt_parses_nested_output_shape(fake_client, sample_review_json):
    svc = _make_service_with_transcript(fake_client, "T1")
    fake_client.responses.to_return = FakeRespNested(sample_review_json)

    result = svc.transcript_to_chatgpt("What did you build?")
    assert isinstance(result, ReviewResult)
    assert result.rating == 7.5
    assert result.slight_opt == "Slightly expanded as requested."  # alias resolved
    assert result.improve_points == "Add tech, metrics, and outcomes."

    # Assert call captured prompt and params
    kwargs = fake_client.responses.calls[-1]
    assert kwargs["model"] == "gpt-4.1"
    assert kwargs["temperature"] == 0.2
    assert kwargs["response_format"] == {"type": "json_object"}

    prompt_sent = kwargs["input"]
    assert "Question:" in prompt_sent and "What did you build?" in prompt_sent
    assert "Transcript:" in prompt_sent and "T1" in prompt_sent


def test_transcript_to_chatgpt_parses_output_text_shape(fake_client, sample_review_json):
    svc = _make_service_with_transcript(fake_client, "T2")
    fake_client.responses.to_return = FakeRespOutputText(sample_review_json)

    result = svc.transcript_to_chatgpt("Q2")
    assert isinstance(result, ReviewResult)
    assert result.summary == "Solid answer; can be sharper."


def test_transcript_to_chatgpt_raises_on_invalid_json(fake_client):
    svc = _make_service_with_transcript(fake_client, "T")
    fake_client.responses.to_return = FakeRespOutputText("{not json}")

    with pytest.raises(ValueError, match="Failed to parse model JSON"):
        svc.transcript_to_chatgpt("Q")


def test_transcript_to_chatgpt_raises_when_content_missing(fake_client):
    class EmptyResp:
        pass

    svc = _make_service_with_transcript(fake_client, "T")
    fake_client.responses.to_return = EmptyResp()

    with pytest.raises(RuntimeError, match="No content returned"):
        svc.transcript_to_chatgpt("Q")


def test_transcript_to_chatgpt_raises_on_validation_error_from_model(fake_client):
    """rating out of range should fail Pydantic validation and be surfaced as ValueError."""
    bad_json = json.dumps({
        "rating": 11,  # invalid (>10)
        "feedback": "x",
        "slightly_optimized_version": "x",
        "how_to_make_it_stronger": "x",
        "opt_with_placeholders": "x",
        "summary": "x",
    })
    svc = _make_service_with_transcript(fake_client, "T")
    fake_client.responses.to_return = FakeRespOutputText(bad_json)

    with pytest.raises(ValueError, match="Failed to parse model JSON"):
        svc.transcript_to_chatgpt("Q")