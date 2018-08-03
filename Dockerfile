FROM python:3-alpine3.8

WORKDIR /opt/is

COPY src/ src 
COPY setup.py . 

RUN pip install .

CMD ["is-broker-events"]
