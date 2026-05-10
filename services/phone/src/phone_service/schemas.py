from typing import Optional
from pydantic import BaseModel, Field
from enum import Enum


class NumberType(str, Enum):
    MOBILE = "mobile"
    FIXED_LINE = "fixed_line"
    FIXED_LINE_OR_MOBILE = "fixed_line_or_mobile"
    TOLL_FREE = "toll_free"
    PREMIUM_RATE = "premium_rate"
    SHARED_COST = "shared_cost"
    VOIP = "voip"
    PERSONAL_NUMBER = "personal_number"
    PAGER = "pager"
    UAN = "uan"
    VOICEMAIL = "voicemail"
    UNKNOWN = "unknown"


class SpamScore(BaseModel):
    score: float = Field(ge=0.0, le=100.0)
    risk_level: str
    indicators: list[str] = []


class WhatsAppStatus(BaseModel):
    registered: bool
    confidence: float


class TelegramStatus(BaseModel):
    possible_username: Optional[str] = None
    checked: bool


class PhoneLookupResponse(BaseModel):
    number: str
    country_code: int
    country: str
    national_format: str
    carrier: Optional[str] = None
    number_type: NumberType
    is_valid: bool
    is_possible: bool
    spam_score: SpamScore
    whatsapp: WhatsAppStatus
    telegram: TelegramStatus
    business_link: Optional[str] = None