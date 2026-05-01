FROM python:3.11-slim
WORKDIR /app
COPY app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app/index.html /app/templates/
COPY app/app.py /app
RUN mkdir -p /home/app
RUN useradd app && chown -R app:app /app /home/app
USER app
EXPOSE 5000
CMD ["gunicorn", "-w", "2", "-b", "0.0.0.0:5000", "app:app"]