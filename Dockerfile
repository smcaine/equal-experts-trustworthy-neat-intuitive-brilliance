FROM python:3.11-slim

WORKDIR /opt/project

# Install system dependencies (if any) and pip
RUN apt-get update \
	&& apt-get install -y --no-install-recommends gcc libpq-dev \
	&& rm -rf /var/lib/apt/lists/*

# Copy only requirements first for better layer caching
COPY src/requirements.txt ./requirements.txt

# Install Python dependencies
RUN python -m pip install --upgrade pip \
	&& pip install --no-cache-dir -r requirements.txt

# Copy only the app folder into the image (keeps image minimal)
COPY src/app ./app

# Create a non-root user and set permissions
RUN groupadd -r app && useradd -r -g app -s /bin/false app \
	&& chown -R app:app /opt/project /opt/project/app

# Ensure package root is on PYTHONPATH so `import app` works
ENV PYTHONPATH=/opt/project

# Switch to non-root user
USER app

EXPOSE 8080

CMD ["python", "-m", "app.main"]
