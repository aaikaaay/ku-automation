#!/usr/bin/env python3
"""
Voice Booking Agent - Webhook Server
=====================================
Backend for Retell AI voice agent that handles appointment booking.

Features:
- Check availability for given dates/times
- Book appointments
- Cancel appointments
- Send confirmation (mock SMS)

Run: python server.py
Expose: ngrok http 8890
"""

import json
import os
from datetime import datetime, timedelta
from typing import Optional
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uvicorn

app = FastAPI(title="Voice Booking Agent API")

# CORS for demo page
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# MOCK DATABASE (In production, use real DB + calendar integration)
# ============================================================================

# Business hours config
BUSINESS_HOURS = {
    "monday": {"open": "09:00", "close": "17:00"},
    "tuesday": {"open": "09:00", "close": "17:00"},
    "wednesday": {"open": "09:00", "close": "17:00"},
    "thursday": {"open": "09:00", "close": "17:00"},
    "friday": {"open": "09:00", "close": "17:00"},
    "saturday": {"open": "10:00", "close": "14:00"},
    "sunday": None,  # Closed
}

# Appointment slots (30 min each)
SLOT_DURATION_MINUTES = 30

# Mock booked appointments (in production, query from DB/calendar)
BOOKED_APPOINTMENTS = {
    # Format: "YYYY-MM-DD": ["HH:MM", "HH:MM", ...]
    "2026-03-11": ["10:00", "10:30", "14:00"],
    "2026-03-12": ["09:00", "11:00", "15:30"],
}

# Mock appointment records
APPOINTMENTS = []

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_day_name(date_str: str) -> str:
    """Get day name from date string."""
    date = datetime.strptime(date_str, "%Y-%m-%d")
    return date.strftime("%A").lower()


def generate_time_slots(open_time: str, close_time: str) -> list:
    """Generate available time slots between open and close."""
    slots = []
    current = datetime.strptime(open_time, "%H:%M")
    end = datetime.strptime(close_time, "%H:%M")
    
    while current < end:
        slots.append(current.strftime("%H:%M"))
        current += timedelta(minutes=SLOT_DURATION_MINUTES)
    
    return slots


def get_available_slots(date_str: str) -> list:
    """Get available appointment slots for a given date."""
    day_name = get_day_name(date_str)
    hours = BUSINESS_HOURS.get(day_name)
    
    if not hours:
        return []  # Closed
    
    all_slots = generate_time_slots(hours["open"], hours["close"])
    booked = BOOKED_APPOINTMENTS.get(date_str, [])
    
    available = [slot for slot in all_slots if slot not in booked]
    return available


def format_time_12h(time_24h: str) -> str:
    """Convert 24h time to 12h format."""
    dt = datetime.strptime(time_24h, "%H:%M")
    return dt.strftime("%I:%M %p").lstrip("0")


def parse_date_natural(date_input: str) -> Optional[str]:
    """Parse natural language date to YYYY-MM-DD."""
    today = datetime.now()
    date_input_lower = date_input.lower().strip()
    
    if date_input_lower in ["today"]:
        return today.strftime("%Y-%m-%d")
    elif date_input_lower in ["tomorrow"]:
        return (today + timedelta(days=1)).strftime("%Y-%m-%d")
    elif date_input_lower in ["day after tomorrow"]:
        return (today + timedelta(days=2)).strftime("%Y-%m-%d")
    else:
        # Try parsing various formats
        for fmt in ["%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y", "%B %d", "%b %d", "%B %d, %Y"]:
            try:
                parsed = datetime.strptime(date_input, fmt)
                # If year not specified, use current year
                if parsed.year == 1900:
                    parsed = parsed.replace(year=today.year)
                return parsed.strftime("%Y-%m-%d")
            except ValueError:
                continue
        
        # Try weekday parsing
        weekdays = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
        for i, day in enumerate(weekdays):
            if day in date_input_lower:
                days_ahead = i - today.weekday()
                if days_ahead <= 0:
                    days_ahead += 7
                target = today + timedelta(days=days_ahead)
                return target.strftime("%Y-%m-%d")
    
    return None


# ============================================================================
# RETELL WEBHOOK HANDLERS
# ============================================================================

class RetellRequest(BaseModel):
    """Retell webhook request model."""
    call_id: Optional[str] = None
    agent_id: Optional[str] = None
    call_type: Optional[str] = None
    from_number: Optional[str] = None
    to_number: Optional[str] = None
    direction: Optional[str] = None
    
    # For function calls
    name: Optional[str] = None
    args: Optional[dict] = None


@app.post("/retell/webhook")
async def retell_webhook(request: Request):
    """
    Main webhook endpoint for Retell AI.
    Handles custom function calls from the voice agent.
    """
    try:
        body = await request.json()
        print(f"[Retell Webhook] Received: {json.dumps(body, indent=2)}")
        
        # Handle function calls
        function_name = body.get("name") or body.get("function_name")
        args = body.get("args") or body.get("arguments") or {}
        
        if isinstance(args, str):
            args = json.loads(args)
        
        if function_name == "check_availability":
            return await handle_check_availability(args)
        elif function_name == "book_appointment":
            return await handle_book_appointment(args)
        elif function_name == "cancel_appointment":
            return await handle_cancel_appointment(args)
        elif function_name == "get_business_hours":
            return await handle_get_business_hours(args)
        else:
            return JSONResponse({
                "result": f"Unknown function: {function_name}"
            })
            
    except Exception as e:
        print(f"[Retell Webhook] Error: {e}")
        return JSONResponse({
            "result": f"Error processing request: {str(e)}"
        })


async def handle_check_availability(args: dict):
    """Check available appointment slots."""
    date_input = args.get("date", "tomorrow")
    
    # Parse the date
    date_str = parse_date_natural(date_input)
    if not date_str:
        return JSONResponse({
            "result": f"I couldn't understand the date '{date_input}'. Could you please specify a date like 'tomorrow', 'Monday', or 'March 15th'?"
        })
    
    # Check if date is in the past
    if datetime.strptime(date_str, "%Y-%m-%d").date() < datetime.now().date():
        return JSONResponse({
            "result": "That date is in the past. Would you like to check availability for a future date?"
        })
    
    # Get available slots
    available = get_available_slots(date_str)
    
    if not available:
        day_name = get_day_name(date_str)
        if not BUSINESS_HOURS.get(day_name):
            return JSONResponse({
                "result": f"We're closed on {day_name.title()}s. Would you like to check another day?"
            })
        return JSONResponse({
            "result": f"Unfortunately, we're fully booked on {date_input}. Would you like to check another day?"
        })
    
    # Format response
    formatted_slots = [format_time_12h(s) for s in available[:6]]  # Show first 6 slots
    slots_text = ", ".join(formatted_slots[:-1]) + f", and {formatted_slots[-1]}" if len(formatted_slots) > 1 else formatted_slots[0]
    
    date_display = datetime.strptime(date_str, "%Y-%m-%d").strftime("%A, %B %d")
    
    return JSONResponse({
        "result": f"For {date_display}, I have the following times available: {slots_text}. Which time works best for you?",
        "data": {
            "date": date_str,
            "available_slots": available,
            "formatted_slots": formatted_slots
        }
    })


async def handle_book_appointment(args: dict):
    """Book an appointment."""
    date_input = args.get("date")
    time_input = args.get("time")
    customer_name = args.get("customer_name", "Guest")
    customer_phone = args.get("customer_phone", "")
    service_type = args.get("service_type", "General consultation")
    
    if not date_input or not time_input:
        return JSONResponse({
            "result": "I need both a date and time to book your appointment. What date and time would you prefer?"
        })
    
    # Parse date
    date_str = parse_date_natural(date_input)
    if not date_str:
        return JSONResponse({
            "result": f"I couldn't understand the date. Could you please specify it again?"
        })
    
    # Parse time (handle various formats)
    time_str = time_input.strip().upper()
    try:
        # Try parsing 12h format
        if "AM" in time_str or "PM" in time_str:
            parsed_time = datetime.strptime(time_str.replace(" ", ""), "%I:%M%p")
        else:
            parsed_time = datetime.strptime(time_str, "%H:%M")
        time_24h = parsed_time.strftime("%H:%M")
    except ValueError:
        # Try simpler format like "10" or "2"
        try:
            hour = int(time_input.split(":")[0].split()[0])
            if hour < 8:  # Assume PM for small numbers
                hour += 12
            time_24h = f"{hour:02d}:00"
        except:
            return JSONResponse({
                "result": "I couldn't understand the time. Could you please say it like '10 AM' or '2:30 PM'?"
            })
    
    # Check availability
    available = get_available_slots(date_str)
    if time_24h not in available:
        return JSONResponse({
            "result": f"Sorry, {format_time_12h(time_24h)} is not available on that day. Would you like me to suggest some available times?"
        })
    
    # Book the appointment
    appointment = {
        "id": f"APT-{len(APPOINTMENTS) + 1001}",
        "date": date_str,
        "time": time_24h,
        "customer_name": customer_name,
        "customer_phone": customer_phone,
        "service_type": service_type,
        "status": "confirmed",
        "created_at": datetime.now().isoformat()
    }
    APPOINTMENTS.append(appointment)
    
    # Mark slot as booked
    if date_str not in BOOKED_APPOINTMENTS:
        BOOKED_APPOINTMENTS[date_str] = []
    BOOKED_APPOINTMENTS[date_str].append(time_24h)
    
    date_display = datetime.strptime(date_str, "%Y-%m-%d").strftime("%A, %B %d")
    
    return JSONResponse({
        "result": f"Your appointment has been confirmed for {date_display} at {format_time_12h(time_24h)}. Your confirmation number is {appointment['id']}. Is there anything else I can help you with?",
        "data": appointment
    })


async def handle_cancel_appointment(args: dict):
    """Cancel an existing appointment."""
    appointment_id = args.get("appointment_id", "").upper()
    customer_phone = args.get("customer_phone", "")
    
    if not appointment_id:
        return JSONResponse({
            "result": "I need your confirmation number to cancel the appointment. It starts with APT followed by numbers."
        })
    
    # Find the appointment
    for apt in APPOINTMENTS:
        if apt["id"] == appointment_id:
            apt["status"] = "cancelled"
            # Remove from booked slots
            if apt["date"] in BOOKED_APPOINTMENTS and apt["time"] in BOOKED_APPOINTMENTS[apt["date"]]:
                BOOKED_APPOINTMENTS[apt["date"]].remove(apt["time"])
            
            return JSONResponse({
                "result": f"Your appointment {appointment_id} has been cancelled. Would you like to reschedule for another time?"
            })
    
    return JSONResponse({
        "result": f"I couldn't find an appointment with confirmation number {appointment_id}. Could you please verify the number?"
    })


async def handle_get_business_hours(args: dict):
    """Get business hours information."""
    day = args.get("day", "").lower()
    
    if day and day in BUSINESS_HOURS:
        hours = BUSINESS_HOURS[day]
        if hours:
            return JSONResponse({
                "result": f"On {day.title()}s, we're open from {format_time_12h(hours['open'])} to {format_time_12h(hours['close'])}."
            })
        else:
            return JSONResponse({
                "result": f"We're closed on {day.title()}s."
            })
    
    # Return all hours
    hours_text = []
    for day, hours in BUSINESS_HOURS.items():
        if hours:
            hours_text.append(f"{day.title()}: {format_time_12h(hours['open'])} to {format_time_12h(hours['close'])}")
        else:
            hours_text.append(f"{day.title()}: Closed")
    
    return JSONResponse({
        "result": "Our business hours are: " + ". ".join(hours_text[:5]) + ". We're closed on Sundays."
    })


# ============================================================================
# REST API FOR DEMO PAGE
# ============================================================================

@app.get("/api/availability/{date}")
async def api_get_availability(date: str):
    """REST endpoint to check availability (for demo page)."""
    available = get_available_slots(date)
    return {
        "date": date,
        "available_slots": available,
        "formatted_slots": [format_time_12h(s) for s in available]
    }


@app.get("/api/appointments")
async def api_list_appointments():
    """REST endpoint to list appointments (for demo page)."""
    return {"appointments": APPOINTMENTS}


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "voice-booking-agent"}


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    print("🎙️ Voice Booking Agent Server")
    print("=" * 50)
    print("Webhook URL: http://localhost:8890/retell/webhook")
    print("Health Check: http://localhost:8890/api/health")
    print("")
    print("To expose publicly, run:")
    print("  ngrok http 8890")
    print("=" * 50)
    
    uvicorn.run(app, host="0.0.0.0", port=8890)
