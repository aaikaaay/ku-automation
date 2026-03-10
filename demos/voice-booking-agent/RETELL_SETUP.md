# Retell AI Voice Booking Agent - Setup Guide

## Overview
This guide walks you through setting up the Voice Booking Agent in Retell AI.

---

## Step 1: Start the Webhook Server

```bash
cd demos/voice-booking-agent
pip install -r requirements.txt
python server.py
```

In another terminal, expose it publicly:
```bash
ngrok http 8890
```

Copy the ngrok URL (e.g., `https://abc123.ngrok.io`)

---

## Step 2: Create Agent in Retell Dashboard

1. Go to [Retell Dashboard](https://dashboard.retellai.com)
2. Click **Create Agent**
3. Select **Start from scratch** or use a template

---

## Step 3: Configure the Agent

### Basic Settings
- **Agent Name:** Appointment Booking Assistant
- **Voice:** Choose a professional voice (recommend: `Cimo` or `Emma`)
- **Language:** English (US)

### Agent Prompt (System Prompt)

Copy this into the agent's system prompt:

```
You are a friendly and professional appointment booking assistant for [BUSINESS NAME]. Your role is to help callers schedule, check, or cancel appointments.

## Your Personality
- Warm, helpful, and efficient
- Professional but not robotic
- Patient with callers who need clarification

## Key Information
- Business: [BUSINESS NAME]
- Services: General consultations, follow-ups, and new client meetings
- Appointment duration: 30 minutes
- Business hours: Monday-Friday 9 AM to 5 PM, Saturday 10 AM to 2 PM, Closed Sundays

## Conversation Flow

1. **Greeting:** Start with a warm greeting and ask how you can help
2. **Identify Intent:** Determine if they want to:
   - Book a new appointment
   - Check availability
   - Cancel/reschedule an appointment
   - Ask about business hours

3. **For Booking:**
   - Ask what date works for them
   - Use check_availability to find open slots
   - Offer available times
   - Get their name (required)
   - Get their phone number (optional but recommended)
   - Confirm the booking with book_appointment
   - Provide confirmation number

4. **For Cancellation:**
   - Ask for their confirmation number (starts with APT-)
   - Use cancel_appointment to process
   - Offer to reschedule

## Important Rules
- Always confirm details before booking
- If a time isn't available, suggest alternatives
- Keep responses concise for voice (2-3 sentences max)
- Always end by asking "Is there anything else I can help you with?"

## Example Phrases
- "I'd be happy to help you schedule an appointment!"
- "Let me check what we have available..."
- "Perfect, I have you down for [time] on [date]."
- "Your confirmation number is [number]. We'll see you then!"
```

---

## Step 4: Configure Custom Functions

In the Retell dashboard, add these custom functions:

### Function 1: check_availability
```json
{
  "name": "check_availability",
  "description": "Check available appointment slots for a specific date",
  "parameters": {
    "type": "object",
    "properties": {
      "date": {
        "type": "string",
        "description": "The date to check availability for (e.g., 'tomorrow', 'Monday', 'March 15')"
      }
    },
    "required": ["date"]
  }
}
```

### Function 2: book_appointment
```json
{
  "name": "book_appointment",
  "description": "Book an appointment for the customer",
  "parameters": {
    "type": "object",
    "properties": {
      "date": {
        "type": "string",
        "description": "The appointment date"
      },
      "time": {
        "type": "string",
        "description": "The appointment time (e.g., '10:00 AM', '2:30 PM')"
      },
      "customer_name": {
        "type": "string",
        "description": "The customer's name"
      },
      "customer_phone": {
        "type": "string",
        "description": "The customer's phone number"
      },
      "service_type": {
        "type": "string",
        "description": "Type of appointment or service"
      }
    },
    "required": ["date", "time", "customer_name"]
  }
}
```

### Function 3: cancel_appointment
```json
{
  "name": "cancel_appointment",
  "description": "Cancel an existing appointment",
  "parameters": {
    "type": "object",
    "properties": {
      "appointment_id": {
        "type": "string",
        "description": "The appointment confirmation number (e.g., APT-1001)"
      },
      "customer_phone": {
        "type": "string",
        "description": "Customer phone for verification"
      }
    },
    "required": ["appointment_id"]
  }
}
```

### Function 4: get_business_hours
```json
{
  "name": "get_business_hours",
  "description": "Get business hours information",
  "parameters": {
    "type": "object",
    "properties": {
      "day": {
        "type": "string",
        "description": "Specific day to check (optional)"
      }
    },
    "required": []
  }
}
```

---

## Step 5: Set Webhook URL

In Agent Settings → Webhook:
- **Webhook URL:** `https://YOUR_NGROK_URL/retell/webhook`
- Enable webhooks for function calls

---

## Step 6: Test the Agent

1. Click **Test** in the Retell dashboard
2. Try these conversations:
   - "I'd like to book an appointment for tomorrow"
   - "What times do you have available on Monday?"
   - "I need to cancel my appointment, the number is APT-1001"
   - "What are your business hours?"

---

## Step 7: Deploy to Phone Number

1. Go to **Phone Numbers** in Retell
2. Buy a new number or connect existing
3. Assign the Booking Agent to the number
4. Test by calling the number!

---

## Customization

### Change Business Hours
Edit `server.py` → `BUSINESS_HOURS` dict

### Change Slot Duration
Edit `server.py` → `SLOT_DURATION_MINUTES`

### Add Services
Modify the prompt and add a `service_type` parameter

### Integration with Real Calendar
Replace mock functions with:
- Google Calendar API
- Cal.com API
- Calendly API
- Your CRM's calendar

---

## Production Deployment

For production, deploy the webhook server to:
- **Railway** (easiest)
- **Render**
- **AWS Lambda + API Gateway**
- **Google Cloud Run**

Example Railway deployment:
```bash
railway login
railway init
railway up
```

Use the Railway URL as your webhook.
