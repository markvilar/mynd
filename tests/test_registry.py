"""Unit test for registry."""

from benthoscan.containers import Registry, create_registry

def test_registry_creation():
    """Test creation of a registry."""
    registry = Registry[str, str]()
    
    registry["key"] = "value"
    assert len(registry) == 1

    registry["new_key"] = "new_value"
    assert len(registry) == 2

    assert not registry is None
