FROM ghcr.io/astral-sh/uv:python3.11-alpine

RUN addgroup -S plur -g 1000 && adduser -S plur -G plur -u 1000

# REMOVE ANY $TZ to enable /etc/localtime
RUN apk add --no-cache git openssh-client bash tzdata busybox-extras iputils \
    && cp /usr/share/zoneinfo/Asia/Tokyo /etc/localtime && apk del tzdata

USER plur
WORKDIR /home/plur
RUN rm -rf .cache/uv/git-v0
COPY pyproject.toml .
COPY plur/* ./plur/
RUN uv venv && source .venv/bin/activate
RUN uv pip install .
ENV PS1='[\u@\h \w]\$ '
ENV PATH=".venv/bin:$PATH"

COPY docker/plur_bash_sample/recipes ./recipes/
COPY docker/plur_bash_sample/main.py .
CMD [".venv/bin/python", "main.py"]
