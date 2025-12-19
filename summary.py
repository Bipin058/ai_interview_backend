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

2. **Role and Summary** – 2–4 sentences describing the candidate's current/target role, years of experience, primary expertise areas, and key technical domains.

3. **Professional Experience** – For each major role (limit to 3–4 most recent/relevant):
   - Company name and role title
   - Duration (if available)
   - 1–3 bullet points highlighting key responsibilities and impact (only if details are provided in the resume)

4. **Key Strengths** – 3–7 bullet points summarizing core technical and professional competencies found in the resume.

5. **Projects** – ONLY if projects are explicitly mentioned in the resume:
   - 2–6 bullet points of projects with name/context, technologies, and outcomes
   - If no projects are listed, write "Not provided"

6. **Notable Achievements** – ONLY if achievements are explicitly mentioned:
   - 2–6 bullet points with specific metrics, awards, publications, or recognition
   - If no achievements are listed, write "Not provided"

7. **Education** – Degree(s), institution(s), specialization, and graduation year (if provided).

8. **Skills & Tools** – Categorize based on the field:
   - For technical roles: Programming languages, frameworks, cloud tools, databases
   - For non-technical roles: Software proficiency, industry-specific tools, methodologies
   - Include any relevant certifications or specialized training

9. **Soft Skills** – 2–6 bullet points covering leadership, communication, collaboration, and other interpersonal skills (only if evident from the resume).

**CRITICAL REQUIREMENTS:**
- Output ONLY the summary in the structured format above.
- Do NOT include introductory statements like "Here's the summary" or any commentary.
- **NEVER fabricate, infer, or add information not explicitly present in the resume.**
- **The summary MUST be shorter than or equal in length to the original resume.**
- For short resumes (under 800 tokens): Keep the summary proportionally brief and concise.
- For long resumes (over 3000 tokens): Target 1500–1800 tokens maximum.
- If a section has no information in the resume, use "Not provided" instead of making up content.
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
