FROM python:3.11-slim

# System deps for MoviePy + Pillow
RUN apt-get update && apt-get install -y \
    ffmpeg imagemagick fonts-dejavu \
    && rm -rf /var/lib/apt/lists/*

# Fix ImageMagick policy for MoviePy TextClip
RUN sed -i 's/rights="none" pattern="@\*"/rights="read|write" pattern="@*"/' /etc/ImageMagick-6/policy.xml 2>/dev/null || true

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN mkdir -p data output logs

CMD ["python", "scheduler.py"]
