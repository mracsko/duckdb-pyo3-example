FROM docker.io/rust:1.81.0-bookworm

RUN apt-get update && \
    apt-get install -qq -y --no-install-recommends --no-install-suggests \
            build-essential \
            python3 \
            python3-pip \
            python3-venv \
            python3-poetry \
            ca-certificates && \
    apt-get autoremove -y && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . .

RUN python3 -m venv .venv
RUN . .venv/bin/activate && poetry install --no-interaction --no-root
RUN . .venv/bin/activate && maturin develop --release

CMD ["./run.sh"]