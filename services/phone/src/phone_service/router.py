from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from typing import Optional

from .schemas import PhoneLookupResponse
from .service import lookup_phone_number


router = APIRouter()


class PhoneLookupRequest(BaseModel):
    number: str
    email: Optional[EmailStr] = None


@router.post("/phone/lookup", response_model=PhoneLookupResponse)
async def lookup_phone(request: PhoneLookupRequest):
    if not request.number:
        raise HTTPException(status_code=400, detail="Phone number is required")
    
    result = await lookup_phone_number(request.number, request.email)
    return result


@router.get("/health")
async def health_check():
    return {"status": "healthy", "service": "phone-service"}