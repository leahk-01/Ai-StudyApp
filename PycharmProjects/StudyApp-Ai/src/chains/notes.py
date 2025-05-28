from langchain.chains.llm import LLMChain
from langchain_core.prompts import PromptTemplate
from langchain_core.tools import tool
from src.llm_config import llm

_notes_prompt = PromptTemplate.from_template("""
You are an expert academic tutor.

Your job is to generate clear, well-organized and detailed bullet-point study notes for the following topic:

Topic: {topic}

Format:
- Use bullet points
- Keep language simple and accurate
- Include key concepts and explanations
- If it's a complex topic, break it into sections

Start now:
""")


#  LLMChain for the notes generation
notes_chain = LLMChain(prompt=_notes_prompt, llm=llm)


@tool
def compose_notes(topic: str) -> str:
    """Use this tool to generate detailed information/notes based on the given text"""
    return notes_chain.run({"topic": topic}).strip()