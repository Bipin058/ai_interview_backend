# summarizer.py
import os
from dotenv import load_dotenv

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate

load_dotenv(".env.local")


def summarize_resume(resume_text: str) -> str:
    """
    Summarize the resume into a concise but detailed format
    suitable for your AI interview agent. Returns plain string.
    """

    if not resume_text:
        raise ValueError("Resume text is required.")

    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY missing in .env.local")

    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash-lite",
        temperature=0.3,
    )

    prompt_template = PromptTemplate(
        input_variables=["resume_text"],
        template="""
You are an AI assistant that summarizes resumes for an interview system.  
Your output will be used directly by another AI agent to generate interview questions.

Given a detailed resume, generate ONLY a **concise, structured summary** containing the following sections:

1. **Personal Details** – Extract name, email, phone, location, portfolio/GitHub if available.
2. **Role and Summary** – 2–3 sentences describing the candidate’s role, expertise, and primary technical domains.
3. **Key Strengths** – Bullet points summarizing core competencies.
4. **Projects** – Bullet points of major projects, highlighting impact, technologies, and domain.
5. **Notable Achievements** – Bullet points, include metrics or outcomes when available.
6. **Tools & Frameworks** – Bullet points listing languages, frameworks, cloud tools, platforms.
7. **Soft Skills** – Bullet points.

**STRICT REQUIREMENTS:**
- Output ONLY the summary in the structured format above.
- Do NOT include statements like “Here’s the summary” or any commentary.
- Keep content concise, relevant, and focused on what is useful for an interview agent.
- Avoid unnecessary personal details (DOB, nationality, marital status, etc.).
- Replace missing personal info with “Not provided”.

Here is the resume to summarize:
{resume_text}

"""
    )

    safe_text = resume_text.replace("{", "{{").replace("}", "}}")

    formatted_prompt = prompt_template.format(resume_text=safe_text)

    response = llm.invoke([
        {"role": "user", "content": formatted_prompt}
    ])

    # Handle Gemini output (string or list)
    if isinstance(response.content, str):
        summary = response.content.strip()

    elif isinstance(response.content, list):
        text_parts = []
        for block in response.content:
            if isinstance(block, dict) and block.get("type") == "text":
                text_parts.append(block.get("text", ""))
        summary = "\n".join(text_parts).strip()

    else:
        summary = str(response.content).strip()

    return summary
