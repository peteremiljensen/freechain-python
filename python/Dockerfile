FROM alpine:3.5

# Update
RUN apk add --no-cache python3 && \
    python3 -m ensurepip && \
    rm -r /usr/lib/python*/ensurepip && \
    pip3 install --upgrade pip setuptools && \
    rm -r /root/.cache


# Bundle app source
COPY requirements.txt ./requirements.txt
COPY blockchain /src/blockchain
COPY main.py /src/main.py

RUN pip3 install -r requirements.txt

EXPOSE  9000
