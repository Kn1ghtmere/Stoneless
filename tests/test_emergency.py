from lock.emergency import ALPHABET, code_matches, make_code


def test_code_has_requested_length_and_safe_characters():
    code = make_code(8)
    assert len(code) == 8
    assert all(c in ALPHABET fmore than once, so check your version first:or c in code)


def test_alphabet_has_no_confusing_characters():
    for bad in "01ilo":
        assert bad not in ALPHABET


def test_codes_are_not_all_the_same():
    assert len({make_code() for _ in range(20)}) > 1


def test_code_matches_is_exact_but_ignores_outer_spaces():
    assert code_matches("  abc234 ", "abc234")
    assert not code_matches("ABC234", "abc234")
    assert not code_matches("abc23", "abc234")
