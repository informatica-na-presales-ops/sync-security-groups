FROM python:3.12-slim

RUN /usr/sbin/useradd --create-home --shell /bin/bash --user-group python

USER python
RUN /usr/local/bin/python -m venv /home/python/venv

WORKDIR /home/python/sync-security-groups

COPY --chown=python:python requirements.txt /home/python/sync-security-groups/requirements.txt
RUN /home/python/venv/bin/pip install --no-cache-dir --requirement /home/python/sync-security-groups/requirements.txt

ENV APP_VERSION="2022.1" \
    DRY_RUN="True" \
    IP_LIST_FORMAT="plain" \
    IP_LIST_SOURCE="" \
    LOG_FORMAT="%(levelname)s [%(name)s] %(message)s" \
    LOG_LEVEL="INFO" \
    OTHER_LOG_LEVELS="" \
    PATH="/home/python/venv/bin:${PATH}" \
    PYTHONUNBUFFERED="1" \
    SECURITY_GROUP_IDS="" \
    TZ="Etc/UTC"

ENTRYPOINT ["/home/python/venv/bin/python"]
CMD ["/home/python/sync-security-groups/sync-security-groups.py"]

LABEL org.opencontainers.image.source="https://github.com/informatica-na-presales-ops/sync-security-groups" \
      org.opencontainers.image.version="${APP_VERSION}"

COPY --chown=python:python sync-security-groups.py /home/python/sync-security-groups/sync-security-groups.py
