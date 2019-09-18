FROM python:3.7.4-alpine3.10

COPY requirements.txt /sync-security-groups/requirements.txt

RUN /usr/local/bin/pip install --no-cache-dir --requirement /sync-security-groups/requirements.txt

ENV APP_VERSION="0.0.1" \
    AWS_ACCESS_KEY_ID="" \
    AWS_SECRET_ACCESS_KEY="" \
    DRY_RUN="True" \
    IP_LIST_SOURCE="" \
    LOG_FORMAT="%(levelname)s [%(name)s] %(message)s" \
    LOG_LEVEL="INFO" \
    OTHER_LOG_LEVELS="" \
    PYTHONUNBUFFERED="1" \
    SECURITY_GROUP_IDS=""

ENTRYPOINT ["/usr/local/bin/python"]
CMD ["/sync-security-groups/sync-security-groups.py"]

LABEL org.opencontainers.image.authors="William Jackson <wjackson@informatica.com>" \
      org.opencontainers.image.version=${APP_VERSION}

COPY sync-security-groups.py /sync-security-groups/sync-security-groups.py
