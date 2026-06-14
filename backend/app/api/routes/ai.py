import os
from typing import Any
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from google import genai
from google.genai import types

from app.api import deps
from app.models.core import User
from app.core.config import settings

router = APIRouter()

class LessonPlanRequest(BaseModel):
    subject: str
    grade_level: int
    topic: str
    language: str = "en"

class LessonPlanResponse(BaseModel):
    lesson_plan: str

@router.post("/lesson-plan", response_model=LessonPlanResponse)
async def generate_lesson_plan(
    request: LessonPlanRequest,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """Generate an AI-powered lesson plan."""
    
    api_key = settings.GEMINI_API_KEY
    if not api_key:
        raise HTTPException(status_code=500, detail="Gemini API Key not configured")
        
    client = genai.Client(api_key=api_key)
    
    prompt = f"""
    You are an expert CBSE school teacher. Create a detailed 45-minute lesson plan for:
    Subject: {request.subject}
    Grade Level: Class {request.grade_level}
    Topic: {request.topic}
    
    The lesson plan MUST be written entirely in: {"English" if request.language == "en" else "Hindi"}
    
    Include:
    1. Learning Objectives
    2. Required Materials
    3. Introduction (10 mins)
    4. Main Activity/Lecture (25 mins)
    5. Conclusion & Assessment (10 mins)
    6. Homework Assignment
    """
    
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        return {"lesson_plan": response.text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class NotificationRequest(BaseModel):
    student_name: str
    topic: str # e.g. "Low Attendance", "Excellent Exam Results"
    language: str = "en"

class NotificationResponse(BaseModel):
    message: str

@router.post("/generate-notification", response_model=NotificationResponse)
async def generate_notification(
    request: NotificationRequest,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """Generate an AI-powered parent communication message."""
    api_key = settings.GEMINI_API_KEY
    if not api_key:
        raise HTTPException(status_code=500, detail="Gemini API Key not configured")
        
    client = genai.Client(api_key=api_key)
    
    prompt = f"""
    You are an expert school administrator. Draft a polite, professional text message to a parent regarding their child, {request.student_name}.
    Topic: {request.topic}
    
    The message MUST be written entirely in: {"English" if request.language == "en" else "Hindi"}
    
    Keep it under 3 sentences, professional, and encouraging.
    """
    
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        return {"message": response.text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
