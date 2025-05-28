import os


os.environ["PATH"] += os.pathsep + r"D:\voice_upload\ffmpeg-7.1.1-full_build\ffmpeg-7.1.1-full_build\bin"

from langchain_core.tools import Tool
from src.chains.quiz import generate_quiz
from src.chains.summary import summarize_text
from src.llm_config import llm
from fastapi import FastAPI, UploadFile, File
from src.chains.qa import get_qa_chain
from src.chains.notes import compose_notes
from src.models import ChatRequest, QARequest, SummaryRequest, NotesRequest, NotesUploadRequest, QuizRequest
from src.chains.transcribe import transcribe_audio, generate_detailed_notes_from_transcript
from src.vector import  add_notes_to_vectorstore
from langchain.agents import initialize_agent, AgentType
import sys

sys.stdout = sys.__stdout__


app = FastAPI()


sys.stdout.reconfigure(line_buffering=True)


# registering the tools
tools = [
    Tool(
        name="Summarizer",
        func=summarize_text,
        description="Use this tool to summarize a full block of study notes provided as a single string."
    ),
    Tool(
        name="Notes_maker",
        func=compose_notes,
        description="Use this tool to generate note about the topic given."
    ),
    Tool(
        name="QA",
        func=get_qa_chain,
        description="Use this tool to answer questions asked by the user."
    ),
    Tool(
        name="Quiz",
        func=generate_quiz,
        description="Use this tool to generate quiz questions based on topic input"
    )


]

chat_agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True,
    handle_parsing_errors=True
)


UPLOAD_DIR = "temp_files"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post("/ai/chat")
def chat_router(request: ChatRequest):
    try:
        response = chat_agent.run(request.message)
        return {"response": response}
    except Exception as e:

        return {"error": str(e)}

@app.post("/ai/transcribe_detailed_notes")
async def transcribe_audio_to_mindmap(audio: UploadFile = File(...)):
    """Uploads audio, transcribes it, and generates detailed academic study notes."""
    try:
        filename = audio.filename.replace(" ", "_")  # Replace spaces with underscores
        file_location = os.path.join(UPLOAD_DIR, filename)

        # Save uploaded file
        file_content = await audio.read()
        with open(file_location, "wb") as f:
            f.write(file_content)

        # Check if file is really saved
        if not os.path.exists(file_location):
            return {"error": "Upload failed: File not saved."}

        file_size = os.path.getsize(file_location)
        if file_size == 0:
            return {"error": "Upload failed: File saved but is empty."}

        print(f"File saved at {file_location}, size: {file_size} bytes")

        # Now call your transcription logic
        transcript = transcribe_audio(file_location)
        print(f"Transcription complete, length: {len(transcript)} characters")

        detailed_notes = generate_detailed_notes_from_transcript(transcript)

        return {"detailed_notes": detailed_notes}

    except Exception as e:
        print(f"Error during processing: {e}")
        return {"error": str(e)}


@app.post("/ai/summary")
def summarize_topic(request: SummaryRequest):
    summary = summarize_text(request.notes)
    return {"summary": summary}


@app.post("/ai/notes")
def notes_endpoint(request: NotesRequest):
    try:
        print("🔥 REQUEST RECEIVED!")

        print("📥 Topic:", request.topic)

        result = compose_notes(request.topic)

        print("✅ Notes result:", result)

        return {"notes": result}

    except Exception as e:
        import traceback
        print(" SOMETHING BROKE:")
        traceback.print_exc()
        return {"error": str(e)}


def preprocess_user_input(raw_msg: str):
    if raw_msg.lower().startswith("summarize") and ":" not in raw_msg:
        return raw_msg + ":"  # Helps it treat the next line as content
    return raw_msg

@app.post("/ai/upload_notes")
def upload_notes(request: NotesUploadRequest):
    try:
        if not request.notes.strip():
            return {"error": "No notes provided."}

        add_notes_to_vectorstore(request.notes)
        return {"message": "Notes uploaded and saved successfully."}

    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"error": str(e)}


@app.post("/ai/generate_quiz")
def generate_quiz_endpoint(request: QuizRequest):
    quiz_data = generate_quiz(request.subject, request.num_questions)
    return quiz_data



@app.post("/ai/qa")
def ask_question(request: QARequest):
    try:
        chain = get_qa_chain()
        # pass it as a kwarg instead of a bare string
        response = chain.run(query=request.query)
        return {"answer": response, "status": "success"}
    except Exception as e:
        print(f"Error in API endpoint: {e}")
        return {"answer": f"An error occurred: {e}", "status": "error"}





if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.Sa_main:app", host="127.0.0.1", port=8005, reload=True)


