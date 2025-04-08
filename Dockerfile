FROM rust:1.86-bookworm AS wheelbuilder

WORKDIR /
RUN apt-get update
RUN DEBIAN_FRONTEND=noninteractive apt-get install -y \
    make \
    build-essential \
    libssl-dev \
    zlib1g-dev \
    libbz2-dev \
    libreadline-dev \
    libsqlite3-dev \
    wget \
    curl \
    llvm \
    libncurses5-dev \
    libncursesw5-dev \
    xz-utils \
    tk-dev \
    libffi-dev \
    liblzma-dev \
    git

RUN git clone https://github.com/pyenv/pyenv.git /pyenv
ENV PYENV_ROOT=/pyenv
RUN /pyenv/bin/pyenv install 3.13.2
RUN eval "$(/pyenv/bin/pyenv init -)" && /pyenv/bin/pyenv local 3.13.2 && pip install wheel maturin

# Build the wheels
WORKDIR /mitmproxy-adblock
COPY ./src/ ./src/
COPY ./Cargo.toml ./Cargo.toml
COPY ./Cargo.lock ./Cargo.lock
COPY ./pyproject.toml ./pyproject.toml


RUN mkdir -p .venv
RUN eval "$(/pyenv/bin/pyenv init -)" && /pyenv/bin/pyenv local 3.13.2 && maturin build --release

# Build the final image
# Use the official mitmproxy image as the base
FROM mitmproxy/mitmproxy
COPY --from=wheelbuilder /mitmproxy-adblock/target/wheels/*.whl /wheels/
RUN pip install /wheels/mitmproxy_adblock-*.whl
