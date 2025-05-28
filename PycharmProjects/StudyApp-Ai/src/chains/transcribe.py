import os
os.environ["PATH"] += os.pathsep + r"D:\voice_upload\ffmpeg-7.1.1-full_build\ffmpeg-7.1.1-full_build\bin"

import whisper
from langchain.chains.llm import LLMChain
from langchain_core.prompts import PromptTemplate
from src.llm_config import llm

# to Make sure temp_files exists
UPLOAD_DIR = "temp_files"
os.makedirs(UPLOAD_DIR, exist_ok=True)
model = whisper.load_model("tiny")

def transcribe_audio(file_path: str) -> str:
    """Transcribes an audio file to text."""
    result = model.transcribe(file_path)
    return result["text"]


_enhanced_notes_prompt = PromptTemplate.from_template("""
You are an academic assistant helping students deeply understand complex material.

Take the following transcription and generate detailed, structured study notes with added context:

Instructions:
- Expand on each major topic in the transcript.
- Add related information, definitions, examples where helpful.
- Structure the notes logically into Topics → Subtopics → Detailed Points.
- If needed, elaborate based on common academic knowledge.
- Use clear, simple, academic language.
- Avoid hallucinating unknown facts — only expand reasonably based on standard knowledge.

Here is the transcription:
{transcript}

Now create expanded, full study notes:
""")


enhanced_notes_chain = LLMChain(prompt=_enhanced_notes_prompt, llm=llm)

def generate_detailed_notes_from_transcript(transcript: str) -> str:
    """Generates detailed study notes from a transcript."""
    return enhanced_notes_chain.run({"transcript": transcript}).strip()

