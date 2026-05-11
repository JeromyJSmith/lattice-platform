"""service.ids.uuidv7 — sortable, unique, valid UUID strings."""

from __future__ import annotations

import time
import uuid

from service.ids import uuidv7


def test_returns_valid_uuid_string():
    s = uuidv7()
    u = uuid.UUID(s)
    # Our generator sets version nibble to 7.
    assert u.version == 7


def test_unique_within_burst():
    seq = [uuidv7() for _ in range(200)]
    assert len(set(seq)) == 200


def test_sortable_across_time():
    a = uuidv7()
    time.sleep(0.005)
    b = uuidv7()
    # uuidv7 prefixes with timestamp ms; lexicographic sort matches time order.
    assert a < b
