ARG DOCKER_CLI_VERSION=29

FROM docker:${DOCKER_CLI_VERSION}-cli AS dockercli

FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update \
 && apt-get install -y --no-install-recommends git \
 && rm -rf /var/lib/apt/lists/*

COPY --from=dockercli /usr/local/bin/docker /usr/local/bin/docker
COPY --from=dockercli /usr/local/libexec/docker/cli-plugins/docker-buildx \
     /usr/local/libexec/docker/cli-plugins/docker-buildx

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN useradd --create-home --uid 10001 idp \
 && mkdir /workspace \
 && chown idp:idp /workspace

COPY common/ common/
COPY api/ api/
COPY worker/ worker/

USER idp

EXPOSE 8000

CMD ["python3", "-m", "uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]