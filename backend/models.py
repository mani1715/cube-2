from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional
from datetime import datetime
import uuid


# Session Booking Models
class SessionBookingCreate(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    phone: str = Field(..., min_length=10, max_length=15)
    age: str
    gender: str
    therapy_type: str  # individual or group
    concerns: List[str]
    current_feelings: str = Field(..., min_length=10, max_length=1000)
    previous_therapy: str
    preferred_time: str
    additional_info: Optional[str] = Field(None, max_length=500)
    consent: bool


class SessionBooking(SessionBookingCreate):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = Field(default_factory=datetime.utcnow)
    status: str = "pending"  # pending, confirmed, completed, cancelled


# Event Models
class EventCreate(BaseModel):
    title: str = Field(..., min_length=5, max_length=200)
    description: str = Field(..., max_length=2000)
    event_type: str  # panel, meetup, seminar, circle, writing, gaming
    date: str
    time: str
    price: str
    is_paid: bool
    schedule: str  # Monthly, Weekly, etc
    features: List[str]


class Event(EventCreate):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = True


class EventRegistration(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    event_id: str
    full_name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    phone: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


# Blog Models
class BlogCreate(BaseModel):
    title: str = Field(..., min_length=10, max_length=200)
    excerpt: str = Field(..., max_length=500)
    content: str = Field(..., min_length=100)
    author: str = Field(..., max_length=100)
    category: str
    read_time: str
    featured: bool = False


class Blog(BlogCreate):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    date: datetime = Field(default_factory=datetime.utcnow)
    is_published: bool = True


# Career Models
class CareerCreate(BaseModel):
    title: str = Field(..., max_length=200)
    department: str
    location: str
    employment_type: str  # full-time, part-time, contract
    description: str
    responsibilities: List[str]
    qualifications: List[str]
    benefits: Optional[List[str]] = None


class Career(CareerCreate):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    posted_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = True


class CareerApplication(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    job_id: str
    full_name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    phone: str
    resume_url: Optional[str] = None
    cover_letter: str = Field(..., max_length=2000)
    created_at: datetime = Field(default_factory=datetime.utcnow)


# Volunteer Models
class VolunteerCreate(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    phone: str
    interest_area: str
    availability: str
    experience: str = Field(..., max_length=1000)
    motivation: str = Field(..., max_length=1000)


class Volunteer(VolunteerCreate):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = Field(default_factory=datetime.utcnow)
    status: str = "pending"  # pending, approved, active, inactive


# Psychologist Models
class PsychologistCreate(BaseModel):
    full_name: str = Field(..., max_length=100)
    email: EmailStr
    phone: str
    license_number: str
    specializations: List[str]
    years_of_experience: int
    education: List[str]
    bio: str = Field(..., max_length=1000)
    session_rate: float


class Psychologist(PsychologistCreate):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = True
    rating: float = 0.0
    total_sessions: int = 0


# Contact Form Models
class ContactFormCreate(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    subject: str = Field(..., max_length=200)
    message: str = Field(..., min_length=10, max_length=2000)


class ContactForm(ContactFormCreate):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = Field(default_factory=datetime.utcnow)
    status: str = "new"  # new, read, responded


# Payment Models (for mock payments)
class PaymentCreate(BaseModel):
    event_id: Optional[str] = None
    session_id: Optional[str] = None
    amount: float
    payment_method: str  # card, bank, upi
    user_email: EmailStr


class Payment(PaymentCreate):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    transaction_id: str = Field(default_factory=lambda: f"TXN{uuid.uuid4().hex[:12].upper()}")
    status: str = "completed"  # pending, completed, failed
    created_at: datetime = Field(default_factory=datetime.utcnow)
