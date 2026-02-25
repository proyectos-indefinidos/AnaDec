@echo off
echo anadec start.

start "AnaDec API (Python)" cmd /k "cd apps\api && uvicorn src.main:app --reload --port 8000"
start "AnaDec Web (Next.js)" cmd /k "cd apps\web && npm run dev"

echo server start.