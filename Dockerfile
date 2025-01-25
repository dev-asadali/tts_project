# Base image with NVIDIA CUDA
ARG BASE=nvidia/cuda:11.8.0-base-ubuntu22.04
FROM ${BASE}

# Set the working directory
WORKDIR /app

# Update and install required system packages
RUN apt-get update && apt-get upgrade -y && \
    apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    make \
    python3 \
    python3-dev \
    python3-pip \
    python3-venv \
    python3-wheel \
    espeak-ng \
    libsndfile1-dev && \
    apt-get clean && rm -rf /var/lib/apt/lists/*
RUN apt-get update && apt-get install -y tzdata

# Install Python dependencies individually
RUN pip3 install --no-cache-dir --default-timeout=2000 llvmlite --ignore-installed
RUN pip3 install --no-cache-dir --default-timeout=2000 torch torchaudio --extra-index-url https://download.pytorch.org/whl/cu118
RUN pip3 install --no-cache-dir --default-timeout=2000 django
RUN pip3 install --no-cache-dir --default-timeout=2000 TTS
RUN pip3 install --no-cache-dir --default-timeout=2000 pillow
RUN pip3 install --no-cache-dir --default-timeout=2000 numpy
# Add other Python dependencies here (one per line)

# Copy application code into the container
COPY . .

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Collect static files, apply migrations, and run the Django server
EXPOSE 5000
CMD ["sh", "-c", "python3 manage.py collectstatic --noinput && python3 manage.py migrate && python3 manage.py runserver 0.0.0.0:5000"]
