FROM python:3.10 as builder

RUN mkdir -p /app
WORKDIR /app

COPY kadenze_dl kadenze_dl
COPY requirements-dev.in requirements-dev.in
COPY setup.py setup.py
COPY Makefile Makefile

RUN make install-dev && \
    pyinstaller --onefile kadenze_dl/kadenze-dl.py

FROM mcr.microsoft.com/playwright/python:v1.22.0-focal

RUN mkdir -p /app
WORKDIR /app

COPY --from=builder /app/dist .

CMD ["./kadenze-dl"]