import phonenumbers
from phonenumbers import carrier, geocoder, number_type, PhoneNumberUtil
from phonenumbers.phonenumber import PhoneNumber
import httpx
from typing import Optional

from .schemas import (
    NumberType,
    SpamScore,
    WhatsAppStatus,
    TelegramStatus,
    PhoneLookupResponse,
)


PHONE_NUMBER_UTIL = PhoneNumberUtil()


def parse_number(e164_number: str) -> Optional[PhoneNumber]:
    try:
        return phonenumbers.parse(e164_number, None)
    except phonenumbers.NumberParseException:
        return None


def get_country_code(number: PhoneNumber) -> int:
    return number.country_code


def get_country(number: PhoneNumber) -> str:
    return geocoder.description_for_number(number, "en") or "Unknown"


def get_national_format(number: PhoneNumber) -> str:
    return phonenumbers.format_number(number, phonenumbers.PhoneNumberFormat.NATIONAL)


def get_carrier(number: PhoneNumber) -> Optional[str]:
    carrier_name = carrier.name_for_number(number, "en")
    return carrier_name if carrier_name else None


def get_number_type(number: PhoneNumber) -> NumberType:
    type_enum = number_type(number)
    type_mapping = {
        phonenumbers.PhoneNumberType.MOBILE: NumberType.MOBILE,
        phonenumbers.PhoneNumberType.FIXED_LINE: NumberType.FIXED_LINE,
        phonenumbers.PhoneNumberType.FIXED_LINE_OR_MOBILE: NumberType.FIXED_LINE_OR_MOBILE,
        phonenumbers.PhoneNumberType.TOLL_FREE: NumberType.TOLL_FREE,
        phonenumbers.PhoneNumberType.PREMIUM_RATE: NumberType.PREMIUM_RATE,
        phonenumbers.PhoneNumberType.SHARED_COST: NumberType.SHARED_COST,
        phonenumbers.PhoneNumberType.VOIP: NumberType.VOIP,
        phonenumbers.PhoneNumberType.PERSONAL_NUMBER: NumberType.PERSONAL_NUMBER,
        phonenumbers.PhoneNumberType.PAGER: NumberType.PAGER,
        phonenumbers.PhoneNumberType.UAN: NumberType.UAN,
        phonenumbers.PhoneNumberType.VOICEMAIL: NumberType.VOICEMAIL,
    }
    return type_mapping.get(type_enum, NumberType.UNKNOWN)


def calculate_spam_score(number: str, carrier_name: Optional[str]) -> SpamScore:
    indicators = []
    score = 0.0

    if carrier_name:
        voip_indicators = ["voip", "virtual", "wifi", "google", "skype"]
        if any(ind.lower() in carrier_name.lower() for ind in voip_indicators):
            score += 30.0
            indicators.append("VOIP carrier detected")

    if len(number) < 10:
        score += 20.0
        indicators.append("Short number pattern")

    risk_level = "low"
    if score >= 70:
        risk_level = "high"
    elif score >= 40:
        risk_level = "medium"

    return SpamScore(score=min(score, 100.0), risk_level=risk_level, indicators=indicators)


async def check_whatsapp(number: str) -> WhatsAppStatus:
    e164_clean = number.replace("+", "").replace("-", "").replace(" ", "")
    url = f"https://wa.me/{e164_clean}"
    
    try:
        async with httpx.AsyncClient(timeout=5.0, follow_redirects=True) as client:
            response = await client.head(url)
            if response.status_code == 200:
                final_url = str(response.url)
                if "wa.me" in final_url and "error" not in final_url.lower():
                    return WhatsAppStatus(registered=True, confidence=0.8)
    except Exception:
        pass
    
    return WhatsAppStatus(registered=False, confidence=0.9)


async def check_telegram(number: str) -> TelegramStatus:
    patterns = [
        number.replace("+", ""),
        number.replace("+", "").replace("-", ""),
        number.replace("+", "").replace(" ", ""),
    ]
    
    for pattern in patterns:
        if pattern.startswith("1"):
            username = pattern
        else:
            username = pattern[-10:] if len(pattern) >= 10 else pattern
        
        url = f"https://t.me/{username}"
        try:
            async with httpx.AsyncClient(timeout=5.0, follow_redirects=True) as client:
                response = await client.head(url)
                if response.status_code == 200 and "t.me" in str(response.url):
                    return TelegramStatus(possible_username=username, checked=True)
        except Exception:
            continue
    
    return TelegramStatus(possible_username=None, checked=True)


def get_business_link(carrier_name: Optional[str], email: Optional[str] = None) -> Optional[str]:
    if email:
        domain = email.split("@")[-1] if "@" in email else None
        if domain:
            return f"https://www.{domain}"
    
    if carrier_name:
        known_businesses = {
            "AT&T": "https://www.att.com",
            "Verizon": "https://www.verizon.com",
            "T-Mobile": "https://www.t-mobile.com",
            "Vodafone": "https://www.vodafone.com",
            "Orange": "https://www.orange.com",
        }
        for key, url in known_businesses.items():
            if key.lower() in carrier_name.lower():
                return url
    
    return None


async def lookup_phone_number(number: str, email: Optional[str] = None) -> PhoneLookupResponse:
    parsed = parse_number(number)
    
    if not parsed:
        return PhoneLookupResponse(
            number=number,
            country_code=0,
            country="Unknown",
            national_format="Invalid",
            number_type=NumberType.UNKNOWN,
            is_valid=False,
            is_possible=False,
            spam_score=SpamScore(score=0.0, risk_level="unknown", indicators=["Invalid number"]),
            whatsapp=WhatsAppStatus(registered=False, confidence=0.0),
            telegram=TelegramStatus(possible_username=None, checked=False),
            business_link=None,
        )
    
    is_valid = phonenumbers.is_valid_number(parsed)
    is_possible = phonenumbers.is_possible_number(parsed)
    country_code = get_country_code(parsed)
    country = get_country(parsed)
    national_format = get_national_format(parsed)
    carrier_name = get_carrier(parsed)
    number_type_val = get_number_type(parsed)
    
    spam_score = calculate_spam_score(number, carrier_name)
    whatsapp = await check_whatsapp(number)
    telegram = await check_telegram(number)
    business_link = get_business_link(carrier_name, email)
    
    return PhoneLookupResponse(
        number=number,
        country_code=country_code,
        country=country,
        national_format=national_format,
        carrier=carrier_name,
        number_type=number_type_val,
        is_valid=is_valid,
        is_possible=is_possible,
        spam_score=spam_score,
        whatsapp=whatsapp,
        telegram=telegram,
        business_link=business_link,
    )