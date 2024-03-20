FROM python:3.11-slim-bullseye

# Path: WORKDIR
WORKDIR /app

# Path: COPY
COPY requirements.txt .

# Path: RUN
RUN pip install -r requirements.txt

# Path: COPY
COPY . .

# Path: CMD streamlit 
CMD ["streamlit", "run", "web.py", "--server.port", "8001"]
