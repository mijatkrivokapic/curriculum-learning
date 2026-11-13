from fractions import Fraction

from fracgen.generator import Ranges, build_pools, item_types
from fracgen.problem import (Num, Problem, canonical, decode, encode,
                             features, parse_problem)
from fracgen.tatsuoka import ITEMS


def test_canonical():
    assert canonical(Fraction(0)) == "0"
    assert canonical(Fraction(3)) == "3"
    assert canonical(Fraction(2, 4)) == "1/2"
    assert canonical(Fraction(10, 8)) == "1_1/4"


def test_original_answers():
    expected = {"Item01": "11/12", "Item04": "0", "Item05": "1_1/5",
                "Item10": "1_3/4", "Item11": "1", "Item13": "13/24",
                "Item19": "1_2/3"}
    for k, ans in expected.items():
        assert ITEMS[k].answer_text() == ans


def test_original_types_unique():
    assert len(set(item_types().values())) == 20


def test_roundtrip():
    for p in ITEMS.values():
        text = p.input_text()
        assert parse_problem(text) == p
        assert decode(encode(text)) == text


def test_pools_match_type_and_exclude_originals():
    types = item_types()
    pools = build_pools(Ranges(max_whole=4, max_den=8), set(types.values()))
    originals = set(ITEMS.values())
    for t, plist in pools.items():
        for p in plist:
            assert features(p) == t
            assert p not in originals
            assert p.result >= 0
