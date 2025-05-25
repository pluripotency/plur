FROM ghcr.io/astral-sh/uv:python3.11-alpine

# REMOVE ANY $TZ to enable /etc/localtime
RUN apk add --no-cache git openssh-client bash tzdata \
    && cp /usr/share/zoneinfo/Asia/Tokyo /etc/localtime && apk del tzdata

WORKDIR /usr/src/app
RUN rm -rf /root/.cache/uv/git-v0
COPY pyproject.toml .
COPY plur/* ./plur/
RUN uv venv && source .venv/bin/activate
RUN uv pip install .
