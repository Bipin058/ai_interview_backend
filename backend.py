# backend.py
from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from db import User, get_db
import secrets
import string
from scoring import score_conversation as score_with_llm
import os
# Email imports
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from summary import summarize_resume
app = FastAPI()


# ---------------- EMAIL SENDER FUNCTION ---------------- #

def send_email(receiver_email: str, name: str, password: str):
    """
    Sends login credentials via SendGrid.
    Requires environment variables:
    - SENDER_EMAIL (from email)
    - SENDGRID_API_KEY
    """
    sender_email = os.environ.get("SENDER_EMAIL")
    sendgrid_api_key = os.environ.get("SENDGRID_API_KEY")

    # if not sender_email or not sendgrid_api_key:
    #     raise ValueError("SENDER_EMAIL or SENDGRID_API_KEY not set in environment variables")

    subject = "Your Login Credentials - AI Interview System"

    html_content = f"""
    <p>Hello {name},</p>
    <p>Your interview profile has been created successfully.</p>
    <p>
    Here are your login details:<br>
    Interview link: https://ai-interview-frontend-0ou3.onrender.com/<br>
    Email: {receiver_email}<br>
    Password: {password}
    </p>
    <p>Regards,<br>AI Interview System</p>
    """

    message = Mail(
        from_email=sender_email,
        to_emails=receiver_email,
        subject=subject,
        html_content=html_content
    )

    try:
        sg = SendGridAPIClient(sendgrid_api_key)
        response = sg.send(message)
        print(f"Email sent successfully! Status code: {response.status_code}")
    except Exception as e:
        print("Error sending email:", str(e))

# ---------------- REQUEST MODELS ---------------- #

class UserRequest(BaseModel):
    name: str
    email: str
    resume_extracted: str


class ScoreRequest(BaseModel):
    email: str


# ---------------- HELPERS ---------------- #

def generate_password(length=10):
    chars = string.ascii_letters + string.digits + "!@#$%&*?"
    return ''.join(secrets.choice(chars) for _ in range(length))


# ---------------- ROUTES ---------------- #

@app.post("/add_user")
def add_user(data: UserRequest, db: Session = Depends(get_db)):
    
     # Check for existing user
    existing_user = db.query(User).filter(User.email == data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="A user with this email already exists."
        )
    
    
    generated_password = generate_password()
    summarized_resume = summarize_resume(data.resume_extracted)
    user = User(
        name=data.name,
        email=data.email,
        resume_extracted=summarized_resume,
        password=generated_password,
        full_resume=data.resume_extracted
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    # Send welcome email with password
    send_email(user.email, user.name, generated_password)

    return {
        "message": "User saved and email sent!",
        "user_id": user.user_id,
        "generated_password": generated_password
    }


@app.get("/users")
def get_users(db: Session = Depends(get_db)):
    return db.query(User).all()


@app.post("/score_conversation")
def score_conversation(data: ScoreRequest, db: Session = Depends(get_db)):
    """Score a candidate's conversation using Gemini."""
    
    user = db.query(User).filter(User.email == data.email).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if not user.conversation_text:
        raise HTTPException(status_code=400, detail="No conversation found to score")

    try:
        result = score_with_llm(user.conversation_text)

        user.score = result["score"]
        user.analysis = result["analysis"]
        db.commit()

        return {
            "success": True,
            "score": result["score"],
            "analysis": result["analysis"]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error scoring: {str(e)}")
