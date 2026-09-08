FROM python:3.11-slim-bookworm
RUN useradd -m -u 1000 appuser
WORKDIR /app
COPY hf_space/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt
RUN pip install --no-cache-dir torch==2.6.0 torchvision==0.21.0 --index-url https://download.pytorch.org/whl/cpu
COPY --chown=appuser:appuser . /app
ENV PYTHONPATH=/app/src:/app GRADIO_ANALYTICS_ENABLED=False PYTHONUNBUFFERED=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
USER appuser
EXPOSE 7860
CMD ["python", "hf_space/app.py"]
