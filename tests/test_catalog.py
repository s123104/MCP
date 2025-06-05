import json
from mcp_docker_configurator import load_mcp_servers_from_catalog


def test_load_mcp_servers_from_catalog(tmp_path, monkeypatch):
    # copy catalog to temp dir
    catalog_path = tmp_path / "mcp_catalog.json"
    with open("mcp_catalog.json", "r", encoding="utf-8") as src:
        data = src.read()
    catalog_path.write_text(data, encoding="utf-8")

    monkeypatch.chdir(tmp_path)
    servers = load_mcp_servers_from_catalog()
    assert isinstance(servers, dict)
    assert "filesystem" in servers
