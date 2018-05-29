###############################################################################
# BUILDER
###############################################################################
FROM python:3.6.5-alpine3.7 as builder

RUN apk update \
&& apk add gcc libffi-dev musl-dev openssl-dev python3-dev

WORKDIR /usr/src/requirements

COPY requirements.txt ../

RUN pip install --install-option="--prefix=/usr/src/requirements" --no-cache-dir -r ../requirements.txt







###############################################################################
# FINAL
###############################################################################
FROM python:3.6.5-alpine3.7

WORKDIR /usr/src/dry-dock

RUN apk update \
&& apk add openssl-dev \
&& rm -rf /var/cache/apk/*

COPY --from=builder /usr/src/requirements /usr/local
COPY dry-dock ./

ENV PYTHONPATH /usr/src/dry-dock/lib