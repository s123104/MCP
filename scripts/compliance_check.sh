#!/bin/bash
# MCP security compliance automation
set -e

run_cis_benchmark() {
    docker run --rm -v /var/run/docker.sock:/var/run/docker.sock:ro \
        -v /var/lib/docker:/var/lib/docker:ro \
        -v /etc/docker:/etc/docker:ro \
        docker/docker-bench-security:latest \
        > /var/log/mcp/cis-benchmark-$(date +%Y%m%d).log
}

scan_containers() {
    for c in $(docker ps --format '{{.Names}}'); do
        if [[ $c =~ mcp-.* ]]; then
            docker run --rm -v /var/run/docker.sock:/var/run/docker.sock:ro \
                aquasec/trivy image "$c" \
                > /var/log/mcp/vuln-scan-$c-$(date +%Y%m%d).log
        fi
    done
}

check_configurations() {
    if command -v conftest >/dev/null 2>&1; then
        conftest verify --policy ./policies/docker-daemon.rego /etc/docker/daemon.json
        for f in docker-compose*.yml; do
            conftest verify --policy ./policies/docker-compose.rego "$f"
        done
    fi
}

main() {
    mkdir -p /var/log/mcp
    run_cis_benchmark
    scan_containers
    check_configurations
    python3 security/generate_compliance_report.py
    echo "Security compliance check completed."
}

main "$@"
