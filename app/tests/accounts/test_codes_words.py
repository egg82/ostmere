"""Transfer codes and recovery words without a database: their shapes, what a player may type for them, their hashes,
and the cap on words hashed at once."""
import hashlib
import hmac
import threading

import pytest
from fastapi.testclient import TestClient
from hypothesis import given, settings
from hypothesis import strategies as st

from ashfall_app.accounts import codes, words
from ashfall_app.main import create_app

KEY = b"j" * 32
FAST = settings(max_examples=60, derandomize=True, deadline=None)

code_st = st.text(alphabet=codes.ALPHABET, min_size=codes.LENGTH, max_size=codes.LENGTH)
words_st = st.lists(st.sampled_from(words.WORDS), min_size=words.COUNT, max_size=words.COUNT)
gap_st = st.text(alphabet=" -\t", max_size=3)


def test_the_word_list_is_bip39_english():
    raw = (words.Path(words.__file__).parent / "words.txt").read_bytes()
    assert hashlib.sha256(raw).hexdigest() == "2f5eed53a4727b4bf8880d8f3f199efc90e58503646d9ff8eff3a2ed3b24dbda"
    assert len(words.WORDS) == 2048 == len(words.WORD_SET)


def test_a_made_code_and_words_have_their_shapes():
    for _ in range(50):
        code = codes.make()
        assert len(code) == 8 and set(code) <= set(codes.ALPHABET) and codes.normal(code) == code
        shown = codes.shown(code)
        assert shown[4] == "-" and codes.normal(shown) == code
        said = words.make()
        assert said.count("-") == 3 and words.normal(said) == said


@FAST
@given(code_st, st.lists(gap_st, min_size=9, max_size=9), st.booleans(), st.booleans())
def test_a_code_reads_back_from_any_case_spacing_or_its_link(code: str, gaps: list[str], lower: bool, link: bool):
    typed = "".join(g + c for g, c in zip(gaps, code)) + gaps[-1]
    typed = typed.lower() if lower else typed
    if link:
        typed = "https://ostmere.yggdrasil.pub/#join=" + typed.strip()
    assert codes.normal(typed) == code
    assert words.normal(typed) is None   # one box, told apart by shape


@FAST
@given(words_st, st.lists(st.text(alphabet=" -.,_\t", min_size=1, max_size=3), min_size=3, max_size=3),
       st.sampled_from([str.lower, str.upper, str.title]))
def test_words_read_back_from_any_case_and_separators(said: list[str], seps: list[str], case: object):
    assert callable(case)
    typed = str(case(said[0] + seps[0] + said[1] + seps[1] + said[2] + seps[2] + said[3]))
    assert words.normal("  " + typed + " ") == "-".join(said)
    assert codes.normal(typed) is None


@pytest.mark.parametrize("typed", ["", "ABCD-EFG", "ABCD-EFGHJ", "ABCD-EFG1", "ABCD-EFGO", "abandon ability able",
                                   "abandon ability able zzzz", "abandon ability able about above", "#join="])
def test_anything_else_is_neither(typed: str):
    assert codes.normal(typed) is None and words.normal(typed) is None


def test_the_hashes_are_keyed_and_tagged():
    code = "ABCDEFGH"
    assert codes.digest(KEY, code) == b"h1$" + hmac.new(KEY, b"ABCDEFGH", hashlib.sha256).digest()
    assert codes.digest(KEY, code) != codes.digest(b"k" * 32, code)
    said = "abandon-ability-able-about"
    h = words.Hashing().digest(KEY, said)
    expected = hashlib.scrypt(said.encode(), salt=KEY + b"ashfall-words-v1", n=2 ** 14, r=8, p=1, dklen=32)
    assert h == b"s1$" + expected and said.encode() not in h
    assert words.Hashing().digest(b"k" * 32, said) != h


def test_no_turn_free_within_the_wait_is_busy():
    hashing = words.Hashing(turns=1, wait=0.05)
    entered, release = threading.Event(), threading.Event()
    original = hashlib.scrypt

    def slow(*args: object, **kw: object) -> bytes:
        entered.set()
        release.wait(5)
        return original(b"x", salt=b"y", n=2, r=1, p=1)

    holder = threading.Thread(target=lambda: hashing.digest(KEY, "a-b-c-d"))
    with pytest.MonkeyPatch.context() as mp:
        mp.setattr(words.hashlib, "scrypt", slow)
        holder.start()
        assert entered.wait(5)
        with pytest.raises(words.Busy):
            hashing.digest(KEY, "a-b-c-d")
        release.set()
        holder.join(5)
    assert hashing.digest(KEY, "abandon-ability-able-about").startswith(b"s1$")   # the turn came back


def test_the_content_says_how_long_a_code_works(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    content = TestClient(create_app()).get("/api/content").json()
    assert content["transfer_code_s"] == codes.LIFETIME.total_seconds() == 600
    texts = {e["key"]: e["text"] for e in content["text_entries"]}
    assert "{minutes} minutes" in texts["ui.devices.join_none"]   # the number comes from the field, not the text
