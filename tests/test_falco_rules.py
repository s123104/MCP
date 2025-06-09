import yaml
from pathlib import Path


def test_falco_rules_valid():
    path = Path('security/falco_rules.local.yaml')
    with open(path, 'r', encoding='utf-8') as fh:
        data = yaml.safe_load(fh)
    assert isinstance(data, list)
    assert any('rule' in item for item in data)
