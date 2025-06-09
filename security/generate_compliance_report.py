#!/usr/bin/env python3
"""Generate a simple compliance report from log files."""
import datetime
from pathlib import Path

def collect_logs(log_dir: Path) -> dict:
    logs = {}
    for log_file in log_dir.glob('*.log'):
        logs[log_file.name] = log_file.read_text(encoding='utf-8')
    return logs

def main() -> None:
    log_dir = Path('/var/log/mcp')
    report = log_dir / 'compliance-report.txt'
    log_dir.mkdir(parents=True, exist_ok=True)
    logs = collect_logs(log_dir)
    lines = [f'Compliance Report - {datetime.datetime.utcnow().isoformat()}']
    for name, content in logs.items():
        lines.append(f'\n## {name}')
        lines.append(content[:1000])
    report.write_text('\n'.join(lines), encoding='utf-8')

if __name__ == '__main__':
    main()
