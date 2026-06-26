FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . .
RUN python generate_data.py

EXPOSE 10000

CMD ["gunicorn", "app:server", "--bind", "0.0.0.0:10000"]
