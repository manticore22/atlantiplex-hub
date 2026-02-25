FROM python:3.11-slim AS builder
WORKDIR /app
COPY requirements_enhanced.txt requirements_payments.txt ./
RUN python -m pip install --upgrade pip && \
    if [ -s requirements_enhanced.txt ]; then \
        pip install --no-cache-dir -r requirements_enhanced.txt; \
    fi && \
    if [ -s requirements_payments.txt ]; then \
        pip install --no-cache-dir -r requirements_payments.txt; \
    fi
COPY . .

FROM python:3.11-slim
WORKDIR /app
COPY --from=builder /usr/local/lib/python* /usr/local/lib/python*
COPY --from=builder /app .
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
EXPOSE 8000
CMD ["python", "server.py"]
