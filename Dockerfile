FROM python:3.11-slim

# ตั้งค่า working directory
WORKDIR /app

# ติดตั้ง system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# คัดลอก requirements และติดตั้ง dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# คัดลอก application code
COPY . .

# Expose port
EXPOSE 8000

# คำสั่งสำหรับรัน application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
