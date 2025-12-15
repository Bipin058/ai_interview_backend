# db.py
import os
import uuid
from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, String, Column, Integer, String, Float, TIMESTAMP, func, ARRAY,Text

from sqlalchemy.dialects.postgresql import UUID

from sqlalchemy.orm import declarative_base, sessionmaker

from sqlalchemy.sql import func

# Load environment variables
load_dotenv()

# DATABASE_URL = "postgresql://postgres:password@localhost:5432/AI-interviewer"
DATABASE_URL = os.environ.get("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set")
# SQLAlchemy engine
engine = create_engine(DATABASE_URL)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base model
Base = declarative_base()

# User table
class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True)
    user_uuid = Column(UUID(as_uuid=True), unique=True, nullable=False, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    resume_extracted = Column(Text, nullable=False)
    conversation_text = Column(Text, nullable=True)
    score = Column(Integer, nullable=True)
    analysis = Column(Text, nullable=True)
    full_resume= Column(Text, nullable=True)
# Dependency for FastAPI routes
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Create tables if they don't exist
Base.metadata.create_all(bind=engine)
