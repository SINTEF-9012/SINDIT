FROM python:3.8-slim-buster

# Set labels 
LABEL vendor=SINTEF_Digital \
      SINDIT.is-beta=True\
      SINDIT.version="0.0.1-beta" \
      SINDIT.release-date="2021-05-06"

RUN mkdir /opt/sindit
WORKDIR /opt/sindit
ENV PYTHONPATH /opt/sindit
	  
COPY . .

RUN pip install --no-cache-dir -r requirements.txt
RUN apt-get update && apt-get install -y curl && apt-get clean

EXPOSE 8050
EXPOSE 8000

ENTRYPOINT ["/bin/bash", "/opt/sindit/main.sh" ]







