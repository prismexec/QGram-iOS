FROM python:3.12-slim
RUN pip install --no-cache-dir telethon==1.36.0
WORKDIR /app
COPY prismgram_notify.py /app/
CMD ["python3", "-u", "/app/prismgram_notify.py"]
