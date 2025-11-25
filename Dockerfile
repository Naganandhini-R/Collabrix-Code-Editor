# ---- Base image ----
FROM python:3.9-slim

# ---- Install compilers for C, C++, and Java ----
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    default-jdk \
    nodejs \
    npm \
    build-essential \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# ---- Working directory ----
WORKDIR /CollaBrix

# ---- Copy all files ----
COPY . .

# ---- Install Python dependencies ----
RUN pip install --no-cache-dir -r requirements.txt

# ---- Environment variables ----
ENV PORT=5000

# ---- Expose port ----
EXPOSE 5000

# ---- Default command ----
CMD ["python", "app.py"]
