import pytest
from collections import Counter
from restless_iblt import RatelessIBLT
from hypothesis import given, strategies as st

@pytest.fixture
def setup_iblt():
    def _setup(insert_A, insert_B):
        iblt_A = RatelessIBLT()
        iblt_B = RatelessIBLT()

        for k, v in insert_A:
            iblt_A.insert(k, v)
        for k, v in insert_B:
            iblt_B.insert(k, v)

        # common keys for decoding
        iblt_A.known_keys.update(iblt_B.known_keys)
        iblt_A.known_values.update(iblt_B.known_values)

        iblt_A.subtract(iblt_B, max_symbols=30)
        return iblt_A
    return _setup


@pytest.mark.parametrize("insert_A, insert_B, expected_inserted, expected_deleted", [
    (
        [("a", "val"), ("b", "val"), ("c", "val")],
        [("b", "val"), ("c", "val"), ("d", "val")],
        [("a", "val")],
        [("d", "val")]
    ),
    (
        [("x", "val")],
        [],
        [("x", "val")],
        []
    ),
    (
        [],
        [("y", "val")],
        [],
        [("y", "val")]
    ),
    (
        [("a", "val")],
        [("a", "val")],
        [],
        []
    ),
])

def test_rateless_iblt_diff(setup_iblt, insert_A, insert_B, expected_inserted, expected_deleted):
    iblt = setup_iblt(insert_A, insert_B)
    inserted, deleted = iblt.list_entries()

    assert Counter(inserted) == Counter(expected_inserted)
    assert Counter(deleted) == Counter(expected_deleted)


@given(
    st.lists(st.tuples(st.text(min_size=1, max_size=5), st.text(min_size=1, max_size=5)), max_size=10),
    st.lists(st.tuples(st.text(min_size=1, max_size=5), st.text(min_size=1, max_size=5)), max_size=10)
)
def test_diff_symmetric_behavior(insert_A, insert_B):
    iblt1 = RatelessIBLT()
    iblt2 = RatelessIBLT()

    for k, v in insert_A:
        iblt1.insert(k, v)
    for k, v in insert_B:
        iblt2.insert(k, v)

    iblt1.known_keys.update(iblt2.known_keys)
    iblt1.known_values.update(iblt2.known_values)

    iblt1.subtract(iblt2, max_symbols=40)
    inserted, deleted = iblt1.list_entries()

    assert not set(inserted).intersection(set(deleted))
