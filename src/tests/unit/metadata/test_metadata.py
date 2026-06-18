import pytest

from pn_ncbi_pkg.metadata import Metadata
from pn_ncbi_pkg.metadata.result_types import MetadataPatch


@pytest.fixture
def metadata_update_state():
    return {
        "meta": Metadata({"key": "value"}),
        "fv_update_only": MetadataPatch({"new_key": "new_value"}),
        "fv_update_only_existing": MetadataPatch({"key": "new_value"}),
        "fv_del_only": MetadataPatch({}, ("key",)),
        "fv_update_del": MetadataPatch({"new_key": "new_value"}, ("key",)),
        "fv_update_del_missing": MetadataPatch({"new_key": "new_value"}, ("fake_key",)),
    }

def test_metadata_creation_empty():
    meta = Metadata()

    assert meta == {}, "empty Metadata should be equal to empty dict"


def test_metadata_creation_from_dict():
    meta = Metadata({"key": "value"})

    assert meta == {"key": "value"}


def test_metadata_kv_addition():
    meta = Metadata()
    meta["key"] = "value"

    assert meta == {"key": "value"}


def test_metadata_key_removal_with_del(metadata_update_state):
    meta = metadata_update_state["meta"]

    del meta["key"]

    assert meta == {}


def test_metadata_update_with_dict(metadata_update_state):
    meta = metadata_update_state["meta"]

    with pytest.raises(AttributeError):
        meta.apply({"new_key": "new_value"})


def test_metadata_update_with_new_field_values(metadata_update_state):
    meta = metadata_update_state["meta"]

    meta.apply(metadata_update_state["fv_update_only"])

    assert meta == {"key": "value", "new_key": "new_value"}


def test_metadata_update_existing_key_with_field_values(metadata_update_state):
    meta = metadata_update_state["meta"]

    meta.apply(metadata_update_state["fv_update_only_existing"])

    assert meta == {"key": "new_value"}


def test_metadata_del_with_field_values(metadata_update_state):
    meta = metadata_update_state["meta"]

    meta.apply(metadata_update_state["fv_del_only"])

    assert meta == {}


def test_metadata_update_and_delete_with_field_values(metadata_update_state):
    meta = metadata_update_state["meta"]

    meta.apply(metadata_update_state["fv_update_del"])

    assert meta == {"new_key": "new_value"}


def test_metadata_update_and_delete_missing_with_field_values(metadata_update_state):
    meta = metadata_update_state["meta"]

    with pytest.raises(KeyError):
        meta.apply(metadata_update_state["fv_update_del_missing"])

