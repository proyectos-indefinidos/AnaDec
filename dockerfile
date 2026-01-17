FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY src ./src
EXPOSE 8080
ENV FLET_SERVER_PORT=8080
ENV FLET_FORCE_WEB_SERVER=1
CMD ["python", "-m", "src.main"]