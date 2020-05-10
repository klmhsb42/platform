from syncloudlib.json.convertible import to_json

from syncloud_platform.insider.config import Port


def test_port_mapping():
    expected = '{"external_port": "8080", "local_port": "80", "protocol": "TCP"}'
    actual = to_json(Port("80", "8080", "TCP"))
    assert str(expected) == str(actual)
