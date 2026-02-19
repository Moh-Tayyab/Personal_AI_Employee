#!/bin/bash
# Health Monitor - Monitor and restart AI Employee services
# Usage: ./health_monitor.sh

set -e

# Configuration
CHECK_INTERVAL=60
MAX_RESTART_ATTEMPTS=3
LOG_FILE="./logs/health.log"

# Services to monitor
SERVICES=("orchestrator" "gmail-watcher" "filesystem-watcher")

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

check_service() {
    local service=$1
    if pm2 describe "$service" &> /dev/null; then
        local status=$(pm2 describe "$service" | grep "status" | head -1 | awk '{print $4}')
        if [ "$status" = "online" ]; then
            return 0
        fi
    fi
    return 1
}

restart_service() {
    local service=$1
    local attempt=0

    while [ $attempt -lt $MAX_RESTART_ATTEMPTS ]; do
        log "Attempting to restart $service (attempt $((attempt+1))/$MAX_RESTART_ATTEMPTS)"

        pm2 restart "$service" 2>/dev/null && sleep 5

        if check_service "$service"; then
            log "$service restarted successfully"
            return 0
        fi

        attempt=$((attempt+1))
        sleep 10
    done

    log "ERROR: Failed to restart $service after $MAX_RESTART_ATTEMPTS attempts"
    return 1
}

check_disk_space() {
    local usage=$(df . | tail -1 | awk '{print $5}' | sed 's/%//')
    if [ $usage -gt 90 ]; then
        log "WARNING: Disk space critical at ${usage}%"
        return 1
    fi
    return 0
}

check_memory() {
    local available=$(free -m | grep Mem | awk '{print $7}')
    if [ $available -lt 256 ]; then
        log "WARNING: Low memory: ${available}MB available"
        return 1
    fi
    return 0
}

send_alert() {
    local message=$1
    # TODO: Implement email/Slack alert
    log "ALERT: $message"
}

# Main monitoring loop
main() {
    log "Starting health monitor..."

    while true; do
        local all_healthy=true

        # Check each service
        for service in "${SERVICES[@]}"; do
            if ! check_service "$service"; then
                log "Service $service is down, attempting restart..."
                if ! restart_service "$service"; then
                    all_healthy=false
                    send_alert "Service $service failed to restart"
                fi
            fi
        done

        # Check system resources
        if ! check_disk_space; then
            all_healthy=false
            send_alert "Disk space critical"
        fi

        if ! check_memory; then
            all_healthy=false
            send_alert "Memory low"
        fi

        if $all_healthy; then
            log "All services healthy"
        fi

        sleep $CHECK_INTERVAL
    done
}

# Run
if [ "$1" = "once" ]; then
    for service in "${SERVICES[@]}"; do
        if ! check_service "$service"; then
            log "Service $service is down"
            restart_service "$service" || true
        fi
    done
else
    main
fi
