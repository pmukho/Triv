#!/bin/bash

set -e

echo "🔧 Starting mock frontend..."
docker-compose up -d frontend

echo "⏳ Waiting for frontend to be ready..."
sleep 10  

echo "✅ Pinging frontend..."
curl -sSf http://localhost:3000 > /dev/null

echo "Success."

docker-compose down
