#!/bin/bash
set -e

SERVICE_NAME="web"
LOG_LINES=50
SLEEP_TIME=10

show_color_logs() {
  docker-compose logs --tail=$LOG_LINES $SERVICE_NAME |
    awk '/ERROR/ {print "\033[31m" $0 "\033[0m"}
         /WARN/  {print "\033[33m" $0 "\033[0m"}
         /INFO/  {print "\033[36m" $0 "\033[0m"}
         !/ERROR|WARN|INFO/ {print}'
}


show_logs() {
  echo "📋 Displaying last $LOG_LINES log lines:"
  docker-compose logs --tail=$LOG_LINES $SERVICE_NAME
}

# Main execution flow
if show_color_logs; then
  echo "⏳ Waiting $SLEEP_TIME seconds for services to initialize..."
  sleep $SLEEP_TIME
  show_logs
fi

echo "🛑 Script completed"