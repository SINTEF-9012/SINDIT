FROM python:3.10-slim-bullseye

# Set labels 
LABEL vendor=SINTEF_Digital \
      SINDIT.is-beta=True\
      SINDIT.version="0.0.1-beta" \
      SINDIT.release-date="2022-07-12"

RUN mkdir /opt/sindit
WORKDIR /opt/sindit
ENV PYTHONPATH /opt/sindit

COPY . .

RUN pip install --no-cache-dir -r requirements.txt
RUN apt-get update && apt-get install -y curl && apt-get clean

EXPOSE 8050
EXPOSE 8000

# ENTRYPOINT ["python", "/opt/sindit/main.sh" ]







