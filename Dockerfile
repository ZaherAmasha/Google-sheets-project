# using the official playwright image to resolve dependency issues on Render.com
# where I can't install dependencies locally there because of user previleges in the free tier
FROM mcr.microsoft.com/playwright/python:v1.48.0-jammy

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000

# Donwloading and installing the chromium browser
RUN python -m playwright install chromium

# Start the fastapi app
CMD ["python", "main.py"]  