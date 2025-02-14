from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from datetime import datetime, date
from typing import List, Optional
import mysql.connector

# Database Connection
def get_db():
    connection = mysql.connector.connect(
        host='127.0.0.120',
        user='root',
        password='SHA12had34',
        database='batoot'
    )
    return connection

# FastAPI Application
app = FastAPI()

# Pydantic Schemas
class ChildProfileCreate(BaseModel):
    Nickname: str
    DateOfBirth: date
    password: str
    ParentNumber: str  

class ChildProfileUpdate(BaseModel):
    ParentNumber: Optional[str] = None
    password: Optional[str] = None

class ChildProfileResponse(BaseModel):
    Nickname: str
    DateOfBirth: date
    ParentNumber: int

class ProgressUpdate(BaseModel):
    progress_id: int
    completion_status: bool
    current_prog: int

class ProgressHistoryCreate(BaseModel):
    child_nickname: str
    activity_id: int
    completion_date: datetime
    writing_image: Optional[str]

class ActivityCreate(BaseModel):
    letter: str
    letter_sound: str
    is_completed: bool
    image: str
    audio: str

class ActivityResponse(BaseModel):
    activity_id: int
    letter: str
    letter_sound: str
    is_completed: bool
    image: str
    audio: str

# API Endpoints
@app.get("/")
def hello_page():
    return {"message": "Welcome to Batoot DB!"}

@app.post("/child/signup", response_model=ChildProfileResponse)
def create_child_profile(profile: ChildProfileCreate):
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO ChildProfile (Nickname, DateOfBirth, password, ParentNumber) VALUES (%s, %s, %s, %s)",
        (profile.Nickname, profile.DateOfBirth, profile.password, profile.ParentNumber),
    )
    db.commit()
    cursor.close()
    db.close()
    return profile

@app.get("/child/{Nickname}", response_model=ChildProfileResponse)
def get_child_profile(Nickname: str):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT Nickname, DateOfBirth, ParentNumber FROM ChildProfile WHERE Nickname = %s", (Nickname,))
    profile = cursor.fetchone()
    cursor.close()
    db.close()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found.")
    return profile

@app.put("/child/{Nickname}", response_model=ChildProfileResponse)
def update_child_profile(Nickname: str, updates: ChildProfileUpdate):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT Nickname FROM ChildProfile WHERE Nickname = %s", (Nickname,))
    if not cursor.fetchone():
        cursor.close()
        db.close()
        raise HTTPException(status_code=404, detail="Profile not found.")
    if updates.ParentNumber:
        cursor.execute("UPDATE ChildProfile SET ParentNumber = %s WHERE Nickname = %s", (updates.ParentNumber, Nickname))
    if updates.password:
        cursor.execute("UPDATE ChildProfile SET password = %s WHERE Nickname = %s", (updates.password, Nickname))
    db.commit()
    cursor.close()
    db.close()
    return get_child_profile(Nickname)

@app.put("/progress/update", response_model=ProgressUpdate)
def update_progress(progress: ProgressUpdate):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT progress_id FROM progress WHERE progress_id = %s", (progress.progress_id,))
    if not cursor.fetchone():
        cursor.close()
        db.close()
        raise HTTPException(status_code=404, detail="Progress not found.")
    cursor.execute("UPDATE progress SET completion_status = %s, current_prog = %s WHERE progress_id = %s",
                   (progress.completion_status, progress.current_prog, progress.progress_id))
    db.commit()
    cursor.close()
    db.close()
    return progress

@app.post("/progress/history", response_model=ProgressHistoryCreate)
def save_ProgressHistory(progress: ProgressHistoryCreate):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("INSERT INTO ProgressHistory (child_nickname, activity_id, completion_date, writing_image) VALUES (%s, %s, %s, %s)",
                   (progress.child_nickname, progress.activity_id, progress.completion_date, progress.writing_image))
    db.commit()
    cursor.close()
    db.close()
    return progress

@app.get("/progress/history/{Nickname}", response_model=List[ProgressHistoryCreate])
def get_ProgressHistory(Nickname: str):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT child_nickname, activity_id, completion_date, writing_image FROM ProgressHistory WHERE child_nickname = %s", (Nickname,))
    history = cursor.fetchall()
    cursor.close()
    db.close()
    if not history:
        raise HTTPException(status_code=404, detail="No progress history found.")
    return history

@app.post("/activity/add", response_model=ActivityResponse)
def add_activity(activity: ActivityCreate):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("INSERT INTO activities (letter, letter_sound, is_completed, image, audio) VALUES (%s, %s, %s, %s, %s)",
                   (activity.letter, activity.letter_sound, activity.is_completed, activity.image, activity.audio))
    db.commit()
    cursor.execute("SELECT activity_id, letter, letter_sound, is_completed, image, audio FROM activities ORDER BY activity_id DESC LIMIT 1")
    new_activity = cursor.fetchone()
    cursor.close()
    db.close()
    return dict(zip(["activity_id", "letter", "letter_sound", "is_completed", "image", "audio"], new_activity))

@app.get("/activity/{activity_id}", response_model=ActivityResponse)
def get_activity(activity_id: int):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT activity_id, letter, letter_sound, is_completed, image, audio FROM activities WHERE activity_id = %s", (activity_id,))
    activity = cursor.fetchone()
    cursor.close()
    db.close()
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found.")
    return activity
