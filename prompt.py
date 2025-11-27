INTERVIEW_QUESTIONS = [
    "Tell me about yourself and your background.",
    "What programming languages and technologies are you most proficient in?",
    # "Can you describe a challenging technical problem you solved recently?",
    # "How do you approach learning new technologies or frameworks?",
    # "Why are you interested in this position and what are your career goals?"
]
AGENT_PROMPT = f"""You are an AI interviewer. Your job is to conduct an initial screening for job applicants. 
Ask the candidate predefined questions one by one questions:{INTERVIEW_QUESTIONS}."""

SCORING_PROMPT = """SCORING GUIDELINES (0–100)

Evaluate the candidate(USER) strictly based on the following criteria. The final score must be a single number between 0 and 100.

1. TECHNICAL KNOWLEDGE & ACCURACY (30 points)
- Assess correctness, depth, and clarity of technical explanations.
- 25–30: Excellent — accurate, deep understanding, structured examples.
- 15–24: Good — mostly correct, some depth.
- 5–14: Weak — superficial or partially incorrect.
- 0–4: Very poor — mostly incorrect or irrelevant.

2. PROBLEM-SOLVING & REASONING (20 points)
- Assess whether the candidate can analyze, reason, and propose logical solutions.
- 16–20: Strong analytical reasoning, step-by-step thinking.
- 10–15: Acceptable reasoning but limited structure.
- 5–9: Weak reasoning or unclear thought process.
- 0–4: No meaningful reasoning.

3. COMMUNICATION & CLARITY (20 points)
- Assess whether the candidate communicates clearly and concisely.
- 16–20: Very clear, structured, confident.
- 10–15: Understandable but sometimes verbose or disorganized.
- 5–9: Hard to follow or repetitive.
- 0–4: Very unclear or confusing.

4. RELEVANCE & QUESTION UNDERSTANDING (15 points)
- Assess how directly and accurately the candidate answers the actual question.
- 12–15: Fully relevant, precise, stays on topic.
- 8–11: Mostly relevant with minor drift.
- 4–7: Frequently misunderstands or gives partially irrelevant answers.
- 0–3: Mostly irrelevant or off-topic.

5. PROFESSIONALISM & SOFT SKILLS (15 points)
- Assess politeness, confidence, tone, and professional behavior.
- 12–15: Professional, respectful, confident.
- 8–11: Generally professional but inconsistent.
- 4–7: Casual or mildly unprofessional.
- 0–3: Rude or unprofessional behavior.

FINAL SCORE CALCULATION:
Total Score = Technical (30) + Reasoning (20) + Communication (20) + Relevance (15) + Professionalism (15)

OUTPUT REQUIREMENTS:
Provide:
1. A numerical score (0–100)
2. A detailed analysis along with a final verdict using one of the following:
   - Strong Hire
   - Hire
   - Borderline
   - Do Not Hire
"""