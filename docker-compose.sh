#!/bin/bash
if docker-compose build web; then
  docker-compose up -d
else
  echo "Build failed, exiting..."
  exit 1
fi
