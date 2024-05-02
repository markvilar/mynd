"""Unit test for registry."""

from benthoscan.containers import Registry, create_registry


def test_registry_manipulation():
    """Test creation of a registry."""
    registry = Registry[str, str]()

    registry["key"] = "value"
    assert len(registry) == 1

    registry["new_key"] = "new_value"
    assert len(registry) == 2

    # Retrieve and pop the same item from the registry
    first: str = registry["new_key"]
    second: str = registry.pop("new_key")
    assert first == second
    assert len(registry) == 1

    assert not registry is None
