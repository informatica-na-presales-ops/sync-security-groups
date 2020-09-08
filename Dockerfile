FROM python:3.8.5-alpine3.12

COPY requirements.txt /sync-security-groups/requirements.txt

RUN /usr/local/bin/pip install --no-cache-dir --requirement /sync-security-groups/requirements.txt

ENV APP_VERSION="2019.1" \
    AWS_ACCESS_KEY_ID="" \
    AWS_SECRET_ACCESS_KEY="" \
    DRY_RUN="True" \
    IP_LIST_FORMAT="plain" \
    IP_LIST_SOURCE="" \
    LOG_FORMAT="%(levelname)s [%(name)s] %(message)s" \
    LOG_LEVEL="INFO" \
    OTHER_LOG_LEVELS="" \
    PYTHONUNBUFFERED="1" \
    SECURITY_GROUP_IDS="" \
    SYNC_INTERVAL="6" \
    SYNC_ON_START="True" \
    TZ="Etc/UTC"

COPY sync-security-groups.py /sync-security-groups/sync-security-groups.py

LABEL org.opencontainers.image.authors="William Jackson <wjackson@informatica.com>" \
      org.opencontainers.image.version="${APP_VERSION}"

ENTRYPOINT ["/usr/local/bin/python"]
CMD ["/sync-security-groups/sync-security-groups.py"]

USER nobody
