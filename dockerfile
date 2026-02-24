FROM python:3.11-slim

WORKDIR /app

COPY apps/api/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY apps/api/src ./src
COPY src/financeCore ./src/financeCore
COPY src/dataAccess ./src/dataAccess

EXPOSE 8000

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
