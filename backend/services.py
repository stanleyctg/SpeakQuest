from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional, Union

from openai import OpenAI
from pydantic import BaseModel, Field, ValidationError

# Configure OpenAI client here or via environment variables
def get_openai_client(api_key: Optional[str] = None) -> OpenAI:
    key = api_key or os.getenv("OPENAI_API_KEY")
    if not key:
        raise RuntimeError("OPENAI_API_KEY is not set.")
    return OpenAI(api_key=key)


# Data model for the review result
class ReviewResult(BaseModel):
    rating: float = Field(..., ge=0, le=10)
    feedback: str
    slight_opt: str = Field(alias="slightly_optimized_version")
    improve_points: str = Field(alias="how_to_make_it_stronger")
    opt_with_placeholders: str
    summary: str

# AI prompt
BASE_INSTRUCTIONS = (
    "You are a strict recruiter assessing software engineering interview answers. "
    "Be direct, concise, and specific. Point out inaccuracies plainly. Avoid profanity. "
    "Only expand on what was said; do not invent new facts unless asked to propose improvements."
)

# Prompt builder
def build_review_prompt(question: str, transcript: str) -> str:
    return f"""
            {BASE_INSTRUCTIONS}

            Question: {question}

            Transcript:
            {transcript}

            Return your analysis **as JSON** with these exact keys:
            - rating (0-10 number)
            - feedback (string)
            - slightly_optimized_version (string)  # expand only what's there; no new facts
            - how_to_make_it_stronger (string)     # what else to add (tech, metrics, names...)
            - opt_with_placeholders (string)       # a rewritten version including those additions with [PLACEHOLDER]s
            - summary (string)
            If there is no answer in the transcript, return:
            {{
            "rating": 0,
            "feedback": "No answer provided.",
            "slightly_optimized_version": "",
            "how_to_make_it_stronger": "",
            "opt_with_placeholders": "",
            "summary": "No answer provided."
            }}
        """.strip()


# Service wrapper
@dataclass
class Services:
    client: OpenAI
    audio_source: Optional[Union[str, bytes]] = None  # path or bytes
    transcription: Optional[str] = None

    def speech_to_text(
        self,
        model: str = "gpt-4o-transcribe",
        response_format: str = "text",
    ) -> str:
        if not self.audio_source:
            raise ValueError("No audio file provided.")

        # Handle file input
        if isinstance(self.audio_source, str):
            with open(self.audio_source, "rb") as f:
                transcription = self.client.audio.transcriptions.create(
                    model=model,
                    file=f,
                    response_format=response_format,
                )
        else:
            transcription = self.client.audio.transcriptions.create(
                model=model,
                file=self.audio_source,
                response_format=response_format,
            )

        if not transcription:
            raise RuntimeError("Empty transcription response from API.")

        # Store and return the transcription text
        self.transcription = str(transcription)
        return self.transcription

    def transcript_to_chatgpt(
        self,
        question: str,
        model: str = "gpt-4.1",
        temperature: float = 0.2,
    ) -> ReviewResult:

        if not self.transcription:
            raise ValueError("No transcription available. Run speech_to_text() first.")

        prompt = build_review_prompt(question=question, transcript=self.transcription)

        # Call OpenAI chat endpoint
        resp = self.client.responses.create(
            model=model,
            input=prompt,
            temperature=temperature,
            response_format={"type": "json_object"},
        )

        # Extract content from response
        try:
            content = resp.output[0].content[0].text
        except Exception:
            # Fallback for clients that expose .output_text
            content = getattr(resp, "output_text", None)

        if not content:
            raise RuntimeError("No content returned by the model.")

        try:
            return ReviewResult.model_validate_json(content)
        except ValidationError as ve:
            raise ValueError(f"Failed to parse model JSON: {ve}") from ve