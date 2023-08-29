#!/bin/sh

version="$1"
if [ $version ]
then
  versions=("$version")
else
  versions=(1.23.1 1.23.0 1.22.1 1.22.0 1.21.3)
fi

for version in ${versions[*]}
do
  echo "Starting uptime kuma $version..."
  docker run -d -it --rm -p 3001:3001 --name uptimekuma "louislam/uptime-kuma:$version" > /dev/null

  while [[ "$(curl -s -L -o /dev/null -w ''%{http_code}'' 127.0.0.1:3001)" != "200" ]]
  do
    sleep 0.5
  done

  echo "Running tests..."
  python -m unittest discover -s tests

  echo "Stopping uptime kuma..."
  docker stop uptimekuma > /dev/null
  sleep 1

  echo ''
done
