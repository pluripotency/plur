FROM jupyter/minimal-notebook
# should be Ubuntu 20.04 by cat /etc/issue

USER root
RUN apt-get update && apt-get install -y git tzdata \
    &&  ln -sf /usr/share/zoneinfo/Asia/Tokyo /etc/localtime \
    &&  apt-get clean \
    &&  rm -rf /var/lib/apt/lists/*
ENV TZ=Asia/Tokyo

USER jovyan
RUN pip install uv
RUN rm -rf .cache/uv/git-v0
RUN uv venv && source .venv/bin/activate
RUN mkdir -p lib/plur
WORKDIR /home/jovyan/lib/plur
COPY pyproject.toml .
COPY plur/* ./plur/
RUN uv pip install .

WORKDIR /home/jovyan
ENV PATH=".venv/bin:$PATH"
ENV LOG_PARAMS=only_stdout
