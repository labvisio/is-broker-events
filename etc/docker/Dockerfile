FROM ubuntu:22.04 as build

ENV DEBIAN_FRONTEND=noninteractive
ENV VIRTUAL_ENV=/opt/is-broker-events/.venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

RUN apt-get update; \
    apt-get install -y --no-install-recommends \
        gcc \
        build-essential \
        git \
        python3 \
        python3-pip \
        python3-venv

COPY . /opt/is-broker-events/

WORKDIR /opt/is-broker-events
RUN python3 -m venv .venv; \
    pip3 install wheel; \
    pip3 install .

FROM ubuntu:22.04 as final

RUN set -eux; \ 
    apt-get update; \
    apt-get install -y --no-install-recommends python3; \
    rm -rf /var/lib/apt/lists/* ; rm -rf /tmp/* /var/tmp/*;

WORKDIR /opt/is-broker-events
COPY --from=build /opt/is-broker-events/.venv /opt/is-broker-events/.venv
COPY --from=build /opt/is-broker-events/etc/conf/options.json /etc/is-broker-events/options.json

ENV VIRTUAL_ENV=/opt/is-broker-events/.venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

CMD [ "is-broker-events", "/etc/is-broker-events/options.json" ]