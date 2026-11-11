# MediClaim AI

AI-powered health insurance claim fraud detection and adjudication platform.

Built for **Startup Expo 2027, IIT Guwahati (UDGAM)**.

## Stack
- Backend: FastAPI (Python), PostgreSQL, SQLAlchemy, Alembic
- Frontend: Next.js 15, React, TypeScript, Tailwind
- OCR: Tesseract (hin+eng) with PaddleOCR option
- LLM: OpenAI GPT-4o-mini (abstracted; mock fallback for demo)
- Hosting: Render (backend) + Vercel (frontend)

## Quick start (backend)
```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # edit DATABASE_URL, JWT_SECRET
# start postgres on :5433 (or set DATABASE_URL)
alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

## Quick start (frontend)
```bash
cd frontend
npm install
NEXT_PUBLIC_API_URL=http://localhost:8000 npm run dev
```

## Demo credentials
- admin@demo.med / AdminPass123!
- officer@demo.med / DemoPass123!
- manager@demo.med / DemoPass123!

## Architecture
See `docs/architecture/` and `docs/adr/`.

## License
MIT (pending)