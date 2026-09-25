# Isolated code runner. User code runs on this image's Python 3.12.
FROM python:3.12-slim
RUN apt-get update \
 && apt-get install -y --no-install-recommends libseccomp2 \
 && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY harness.py sandbox.py server.py /app/
# Code is root-owned and read-only; /sandbox is an empty, non-writable working dir for jobs.
RUN chmod 0755 /app && chmod 0644 /app/*.py && mkdir -p /sandbox && chmod 0555 /sandbox
ENV RUNNER_PYTHON=/usr/local/bin/python3 PYTHONDONTWRITEBYTECODE=1
EXPOSE 8080
CMD ["python3", "-u", "server.py"]
