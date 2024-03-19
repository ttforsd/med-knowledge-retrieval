FROM python:3.10-slim-bullseye

# Path: WORKDIR
WORKDIR /app

# Path: COPY
COPY requirement.txt .

# Path: RUN
RUN pip install -r requirement.txt

# Path: COPY
COPY . .

# Path: CMD streamlit 
CMD ["streamlit", "run", "app.py", "--server.port", "8001"]
