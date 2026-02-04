# P&ID Parser Demo

AI-powered extraction of equipment, valves, instruments, and line data from P&ID diagrams.

## Features

- 📤 Upload P&ID images (JPG, PNG, WebP) or PDFs
- 🤖 AI extracts: Equipment, Valves, Instruments, Lines
- 📊 View results in organized tables
- 📥 Download as formatted Excel report

## Setup

1. **Install dependencies:**
   ```bash
   cd projects/pid-parser-demo
   pip install -r requirements.txt
   ```

2. **Set OpenAI API key:**
   ```bash
   export OPENAI_API_KEY="your-key-here"
   ```

3. **Run the server:**
   ```bash
   python app.py
   ```

4. **Open in browser:**
   ```
   http://localhost:8890
   ```

## Deployment

### Vercel (Frontend only)
The static frontend can be deployed to Vercel, but you'll need a separate backend.

### Railway / Render (Full stack)
1. Push to GitHub
2. Connect to Railway/Render
3. Set `OPENAI_API_KEY` environment variable
4. Deploy

### Client Server
1. Copy files to client server
2. Install Python 3.9+
3. Run with systemd or PM2

## Cost Estimate

- OpenAI GPT-4o Vision: ~$0.01-0.03 per P&ID analyzed
- Hosting: $0-20/month depending on platform

## API Endpoint

```
POST /api/analyze
Content-Type: multipart/form-data

file: <P&ID image or PDF>

Response:
{
  "success": true,
  "data": {
    "equipment": [...],
    "valves": [...],
    "instruments": [...],
    "lines": [...],
    "notes": [...],
    "summary": "..."
  },
  "excel": "<base64-encoded-xlsx>",
  "filename": "PID_Extract_20260203_120000.xlsx"
}
```

---

Built by [KU Automation](https://ai-automation-agency-gilt.vercel.app)
