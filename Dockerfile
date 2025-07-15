# Base Image
FROM python:3.12-slim

# Environment Variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 

RUN apt-get update && apt-get install -y curl build-essential \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory inside the container
WORKDIR /app

# Install uv
RUN curl -LsSf https://astral.sh/uv/install.sh | sh \
    && echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc

# Ensure uv is in the PATH for the current session
ENV PATH="/root/.local/bin:${PATH}"

# Copy requirements and install dependencies using uv
COPY requirements.txt ./
RUN uv pip install -r requirements.txt --system

# Copy your entire application code
COPY . .

# Expose the port Streamlit runs on (default is 8501)
EXPOSE 8501

# Command to run your Streamlit application
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]