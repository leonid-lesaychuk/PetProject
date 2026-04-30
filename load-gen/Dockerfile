FROM python:3.11-slim
RUN useradd -m loader
USER loader
WORKDIR /home/loader
RUN pip install --no-cache-dir -r requirements.txt
COPY load_gen.py
CMD ["python", "load_gen.py"]