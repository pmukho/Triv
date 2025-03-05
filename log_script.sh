#!/bin/bash

mkdir -p logs

TIMESTAMP=$(date +%Y%m%d-%H%M)
LOG_FILE="logs/all-services-$TIMESTAMP.log"

docker-compose logs -t | awk '{
    # Find the timestamp pattern in the line
    for (i=1; i<=NF; i++) {
        if ($i ~ /[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}/) {
            timestamp = $i
            gsub("Z", "", timestamp)
            split(timestamp, parts, "T")
            date = parts[1]
            time = parts[2]
            sub(/\.[0-9]+$/, "", time)
            
            $i = ""
            
            printf "[%s %s]%s\n", date, time, $0
            next
        }
    }
    print
}' > "$LOG_FILE"

echo "Logs collected to $LOG_FILE with reformatted timestamps"