FROM python:3.11-slim

# Install system dependencies required for LibreOffice (Word to PDF) and OpenCV/rembg
RUN apt-get update && apt-get install -y \
    libreoffice \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Set up a non-root user (required by Hugging Face Spaces)
RUN useradd -m -u 1000 user
USER user
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH \
    U2NET_HOME=/home/user/.u2net

WORKDIR $HOME/app

# Copy requirements and install
COPY --chown=user requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Pre-download the rembg model during build so it doesn't download on first request
RUN python -c "from rembg import new_session; new_session()"

# Copy the rest of the application
COPY --chown=user . .

# Create temp directory
RUN mkdir -p temp

# Start the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]
