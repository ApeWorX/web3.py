FROM python:3.13

# Set up code directory
WORKDIR /usr/src/app

# Install Linux dependencies
RUN apt-get update && apt-get install -y libssl-dev

COPY web3 ./web3/
COPY tests ./tests/
COPY ens ./ens/

COPY pyproject.toml .
COPY README.md .

RUN pip install -e .[dev]

WORKDIR /code
