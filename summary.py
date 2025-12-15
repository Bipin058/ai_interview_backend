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

2. **Role and Summary** – 3–4 sentences describing the candidate's current/target role, years of experience, primary expertise areas, and key technical domains.

3. **Professional Experience** – For each major role (limit to 3–4 most recent/relevant):
   - Company name and role title
   - Duration (if available)
   - 2–3 bullet points highlighting key responsibilities and impact

4. **Key Strengths** – 5–7 bullet points summarizing core technical and professional competencies.

5. **Projects** – 4–6 bullet points of major projects, including:
   - Project name/context
   - Technologies used
   - Measurable impact or outcome (if available)

6. **Notable Achievements** – 4–6 bullet points with specific metrics, awards, publications, or recognition.

7. **Education** – Degree(s), institution(s), specialization, and graduation year (if provided).

8. **Skills & Tools** – Categorize based on the field:
   - For technical roles: Programming languages, frameworks, cloud tools, databases
   - For non-technical roles: Software proficiency, industry-specific tools, methodologies
   - Include any relevant certifications or specialized training

9. **Soft Skills** – 4–6 bullet points covering leadership, communication, collaboration, and other interpersonal skills.

**STRICT REQUIREMENTS:**
- Output ONLY the summary in the structured format above.
- Do NOT include introductory statements like "Here's the summary" or any commentary.
- Target length: **1500–1800 tokens** – be detailed but concise.
- Focus on information useful for generating technical and behavioral interview questions.
- Avoid unnecessary personal details (DOB, nationality, marital status, etc.).
- Replace missing personal info with "Not provided".
- Use bullet points for readability and structure.

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
