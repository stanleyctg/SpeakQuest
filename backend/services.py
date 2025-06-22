from openai import OpenAI
import os
from backend.config import load_config_from_env

class Services:
    def __init__(self, audio_file):
        load_config_from_env()
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.audio_file = audio_file
        self.transcription = None

    def speech_to_text(self):
        load_config_from_env()
        if not self.audio_file:
            raise ValueError("No audio file provided")
        transcription = self.client.audio.transcriptions.create(
            model="gpt-4o-transcribe", 
            file=self.audio_file,
            response_format="text"
        )
        if transcription:
            self.transcription = transcription
        return transcription
    
    def transcript_to_chatgpt(self, question):
        if not self.transcription:
            raise ValueError("No transcription available")

        message = f"""Imagine you are a recruiter for top companies, hiring software engineering graduates to join your software engineering graduate schemes.
        Your company are looking for the best candidates so their interview answer must be crisp, to the point, detailed, and have done their research.
        Be very strict in your marking and give comprehensive feedback (no fluff straight to the point) Call out on bullshit or things that make no sense Dont be afraid to use some cuss words to get ur points across cause this is how I learn.
        Given the quesiton {question} and the transcript {self.transcription}
        
        rate this answer out of 10 then give feedback then an optimised version of the answer
        forget any memories u had in the past for this, new candidate, optimised answer should not change the meaning of things or include things that were not said. Just expand on things.

        But one thing to note is to tell candidate what they couldve add, like maybe more technologies, explain more on things or talk about others.
        So with that aid give another optimised version where if the candidate do so, and add placeholder if there are some personal names

        If there is no answer, just say "No answer provided".

        Here how you should format your response:
        1) Rating: [rating out of 10]
        2) Feedback: [detailed feedback on the answer]
        3) Slightly Optimised Version (only expanding existing info, no added facts):
        4) How to Make it Stronger (What you should’ve added):
        5) Optimised Version With Placeholders (if you had added those points)
        6) Summary
        """

        response = self.client.responses.create(
            model="gpt-4.1",
            input=message
        )

        return response.output_text
