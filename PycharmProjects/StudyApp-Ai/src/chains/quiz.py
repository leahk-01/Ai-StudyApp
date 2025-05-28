import json
from src.llm_config import llm
from src.vector import get_vectorstore


def generate_quiz(subject: str, num_questions: int = 5):
    retriever = get_vectorstore().as_retriever()
    docs = retriever.invoke(subject)
    notes_context = "\n\n".join([doc.page_content for doc in docs])

    if not notes_context.strip() or len(notes_context) < 50:
        # No good notes found → fallback when notes are tooo short wich is less then 50 characters

        notes_context = f"(No useful notes found. Generate {num_questions} questions using your knowledge about {subject}.)"

    prompt = f"""
You are an expert tutor specializing in generating quizzes.

TASK:
- Generate {num_questions} high-quality multiple-choice questions.
- Each question must have exactly 4 meaningful options.
- The correct answer must be one of the four options.
- Questions and options must be relevant to the topic.
- Use simple, clear, and accurate language.
- Format the output STRICTLY as valid JSON.

EXAMPLE FORMAT (do not copy literally!):

[
  {{
    "question": "What is photosynthesis?",
    "options": ["A process by which plants make food", "A type of animal behavior", "A method of soil erosion", "A seasonal migration pattern"],
    "answer": "A process by which plants make food"
  }}
]


Context:
{notes_context}

If the context is weak or missing, use your own expertise to create relevant questions.

IMPORTANT:
- DO NOT use placeholder text like "Option A" or "Option B".
- Write real questions and real answers.
- Keep the formatting strictly valid JSON.

"""

    raw_output = llm.invoke(prompt).strip()

    try:
        quiz = json.loads(raw_output)
        validated = []

        for q in quiz:
            if (
                isinstance(q.get("question"), str) and q["question"].strip() and
                isinstance(q.get("options"), list) and len(q["options"]) == 4 and
                q.get("answer") in q["options"]
            ):
                validated.append(q)

        return {
            "quiz": validated,
            "skipped": len(quiz) - len(validated),
            "total": len(quiz)
        }

    except json.JSONDecodeError:
        return {
            "quiz": [],
            "error": "Failed to parse quiz JSON from LLM output.",
            "raw": raw_output
        }
