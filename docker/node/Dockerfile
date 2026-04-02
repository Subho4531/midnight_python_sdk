FROM python:3.11-slim

WORKDIR /app

# Install dependencies
RUN pip install --no-cache-dir aiohttp

# Copy server script
COPY server.py /app/
COPY blockchain.py /app/

# Expose port
EXPOSE 9944

# Run server
CMD ["python", "server.py"]
