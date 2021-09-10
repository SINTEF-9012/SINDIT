#!/bin/bash
# don't forget to set the env PYTHONPATH
# export PYTHONPATH=$PWD
# here we fill the factory graph into the DB
python ./random_factory.py &
# start kafka consumer
python ./dtwin/kafka_consumer.py &
# start the rest API
# kill $(pgrep -P $pid) # to kill uvicorn cleanly
uvicorn api:app --host 0.0.0.0 --port 8000 &
status=$?
if [ $status -ne 0 ]; then
  echo "Failed to start api: $status"
  exit $status
fi

echo "Waiting for api server up"
until $(curl --output /dev/null --silent --fail http://localhost:8000/get_factory_cytoscape_from_neo4j); do
  printf '.'
  sleep 1
done

# start dash app
uvicorn app:app --host 0.0.0.0 --port 8050
status=$?
if [ $status -ne 0 ]; then
  echo "Failed to start dash app: $status"
  exit $status
fi