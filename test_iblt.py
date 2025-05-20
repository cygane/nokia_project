# command to run tests: pytest test_iblt.py
import pytest
from iblt import IBLT

@pytest.fixture
def basic_iblt():
    return IBLT(size=20)

def test_insert_and_retrieve_single_entry(basic_iblt):
    basic_iblt.insert("x", "val")
    entries, deletions = basic_iblt.list_entries()
    assert ("x", "val") in entries
    assert deletions == []

def test_delete_entry(basic_iblt):
    basic_iblt.insert("x", "val")
    basic_iblt.delete("x", "val")
    entries, deletions = basic_iblt.list_entries()
    assert entries == []
    assert deletions == []

def test_symmetric_difference():
    iblt_A = IBLT(size=20)
    iblt_B = IBLT(size=20)

    # A = {"a", "b", "c"}
    iblt_A.insert("a", "val")
    iblt_A.insert("b", "val")
    iblt_A.insert("c", "val")

    # B = {"b", "c", "d"}
    iblt_B.insert("b", "val")
    iblt_B.insert("c", "val")
    iblt_B.insert("d", "val")

    iblt_A.known_keys.update(iblt_B.known_keys)
    iblt_A.known_values.update(iblt_B.known_values)

    # B - A
    for i in range(iblt_A.size):
        iblt_A.table[i].key_sum ^= iblt_B.table[i].key_sum
        iblt_A.table[i].value_sum ^= iblt_B.table[i].value_sum
        iblt_A.table[i].count -= iblt_B.table[i].count

    inserted, deleted = iblt_A.list_entries()
    assert ("a", "val") in inserted
    assert ("d", "val") in deleted
    assert len(inserted) == 1
    assert len(deleted) == 1
