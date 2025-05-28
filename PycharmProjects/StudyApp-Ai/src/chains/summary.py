from langchain_core.prompts import PromptTemplate
from src.llm_config import llm
from langchain_core.tools import tool
from langchain.chains import LLMChain

# Summarize prompt
_summary_prompt = PromptTemplate.from_template("""
You are an expert academic summarizer.

Summarize the following notes in a clear, concise, and accurate way for students.
Use simple understandable language and maintain key points. 

Notes:
{notes}

Summary:
""")

summary_chain = LLMChain(prompt=_summary_prompt, llm=llm)

@tool
def summarize_text(notes: str) -> str:
    """Summarizes a block of study notes clearly and simply."""
    return summary_chain.run({"notes": notes}).strip()
