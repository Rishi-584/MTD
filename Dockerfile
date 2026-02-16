FROM python:3.8-slim

RUN apt-get update && apt-get install -y \
    gcc \
    libffi-dev \
    libssl-dev \
    net-tools \
    iputils-ping \
    && rm -rf /var/lib/apt/lists/*

# Pin compatible Python tooling
RUN pip install --upgrade pip
RUN pip install setuptools==57.5.0 wheel

# Pin eventlet FIRST (very important)
RUN pip install eventlet==0.30.2

# Install Ryu
RUN pip install ryu==4.34

WORKDIR /app
COPY requirements.txt /app
RUN pip install -r requirements.txt

COPY . /app
ENV PYTHONPATH=/app

CMD ["ryu-manager", "--ofp-tcp-listen-port", "6653", "--wsapi-host", "0.0.0.0", "mtd_controller.py"]

