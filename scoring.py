# scoring.py
import json
import os
from dotenv import load_dotenv

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate

from prompt import SCORING_PROMPT

load_dotenv(".env.local")


def score_conversation(conversation_text: str) -> dict:
    """
    Score a conversation using Gemini and return a structured JSON output:
    {
        "score": int,
        "analysis": str
    }
    """
    if not conversation_text:
        raise ValueError("Conversation text is required.")

    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY missing in .env.local")

    llm = ChatGoogleGenerativeAI(
        model="gemini-flash-latest",
        temperature=0.3,
    )

    # JSON-enforced prompt
    prompt_template = PromptTemplate(
        input_variables=["conversation_text", "scoring_instructions"],
        template="""You are an AI evaluator. Read the conversation below between AI interviewer(ASSISTANT) and candidate(USER) :

conversation_text:
{conversation_text}

Instructions for scoring:
{scoring_instructions}

Return ONLY a valid JSON object in this exact format:

{{
  "score": <number between 0 and 100>,
  "analysis": "<detailed explanation>"
}}

NO extra text before or after.
NO markdown blocks.
NO commentary.
ONLY the JSON object.
        """
    )

    # Escape braces to avoid breaking .format()
    safe_text = conversation_text.replace("{", "{{").replace("}", "}}")

    formatted_prompt = prompt_template.format(
        conversation_text=safe_text,
        scoring_instructions=SCORING_PROMPT
    )

    # Invoke LLM
    response = llm.invoke([
        {"role": "user", "content": formatted_prompt}
    ])

    # --- FIX: Extract proper text from Gemini output ---
    if isinstance(response.content, str):
        # Direct string
        response_text = response.content.strip()

    elif isinstance(response.content, list):
        # Gemini sometimes returns [{"type":"text","text": "..."}]
        text_parts = []
        for block in response.content:
            if isinstance(block, dict) and block.get("type") == "text":
                text_parts.append(block.get("text", ""))
        response_text = "\n".join(text_parts).strip()

    else:
        # Fallback
        response_text = str(response.content).strip()

    # Clean markdown fences if model added them
    response_text = (
        response_text.replace("```json", "")
                     .replace("```", "")
                     .strip()
    )

    # Decode JSON
    try:
        result = json.loads(response_text)
    except json.JSONDecodeError:
        raise ValueError(f"Failed to decode JSON from model: {response_text}")

    # Validate structure
    if "score" not in result or "analysis" not in result:
        raise ValueError(f"JSON missing required fields: {result}")

    # Ensure correct types
    try:
        result["score"] = int(result["score"])
        result["analysis"] = str(result["analysis"])
    except Exception:
        raise ValueError(f"Invalid JSON value types: {result}")

    return result
