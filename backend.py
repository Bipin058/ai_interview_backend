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

app = FastAPI()


# ---------------- EMAIL SENDER FUNCTION ---------------- #

def send_email(receiver_email: str, name: str, password: str):
    sender_email = os.environ.get("SENDER_EMAIL")
    sender_password = os.environ.get("SENDER_PASSWORD")         # CHANGE THIS (Use Gmail App Password)

    subject = "Your Login Credentials - AI Interview System"

    body = f"""
Hello {name},

Your interview profile has been created successfully.

Here are your login details:
Interview link: https://192.168.1.196:3000
Email: {receiver_email}
Password: {password}

You will use these credentials to log in and take your AI interview.

Regards,
AI Interview System
"""

    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = receiver_email
    msg["Subject"] = subject

    msg.attach(MIMEText(body, "plain"))

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)

        print("Email sent successfully!")
    except Exception as e:
        print("Error sending email:", e)


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

    user = User(
        name=data.name,
        email=data.email,
        resume_extracted=data.resume_extracted,
        password=generated_password
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
