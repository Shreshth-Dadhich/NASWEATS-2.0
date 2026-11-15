FROM python:3.12-slim
WORKDIR /app
# Build with the repository root as the Docker context.
COPY analysis/requirements.txt /app/analysis/requirements.txt
RUN pip install --no-cache-dir -r /app/analysis/requirements.txt
COPY analysis /app/analysis
COPY website/__init__.py /app/website/__init__.py
COPY website/api /app/website/api
ENV EARTHSIGNAL_CACHE=/data/cache
EXPOSE 8000
CMD ["uvicorn", "website.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
