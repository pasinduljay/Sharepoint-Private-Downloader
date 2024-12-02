FROM debian:bullseye-slim

# Set environment variables to prevent interactive prompts during installation
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies and fix shared library issues
RUN apt-get update && apt-get install -y \
    ffmpeg \
    curl \
    ca-certificates \
    libcurl4 \
    libssl1.1 \
    libgssapi-krb5-2 \
    --no-install-recommends && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Download and install yt-dlp
RUN curl -L https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp -o /usr/local/bin/yt-dlp && \
    chmod a+rx /usr/local/bin/yt-dlp

# Set up the application
WORKDIR /app
COPY app/ /app
RUN apt-get update && apt-get install -y python3-pip && pip3 install Flask

# Expose port 5000 and run the app
CMD ["python3", "main.py"]
