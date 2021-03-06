from syncloudlib.json import convertible

from syncloud_platform.insider.config import Port
from test.insider.helpers import get_port_config


def test_add_update_remove():

    port_config = get_port_config([])

    port_config.add_or_update(Port(80, 10000, 'TCP'))
    port_config.add_or_update(Port(80, 10001, 'TCP'))
    port_config.add_or_update(Port(81, 10002, 'UDP'))
    port_config.add_or_update(Port(81, 10003, 'UDP'))
    port_config.add_or_update(Port(81, 10004, 'TCP'))

    assert len(port_config.load()) == 3
    assert port_config.get(80, 'TCP').external_port == 10001
    assert port_config.get(81, 'UDP').external_port == 10003
    assert port_config.get(81, 'TCP').external_port == 10004

    port_config.remove(81, 'UDP')

    assert len(port_config.load()) == 2
    assert port_config.get(80, 'TCP').external_port == 10001
    assert port_config.get(81, 'TCP').external_port == 10004

