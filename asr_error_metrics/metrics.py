"""Word and character error rate, with the alignment kept so you can look at the errors.

Most WER functions return one number. For error analysis I wanted to see *which*
words or characters were substituted, dropped or inserted, so `align` returns the
full alignment and everything else is built on it.
"""
from collections import Counter
from dataclasses import dataclass
import re
import unicodedata


@dataclass
class Counts:
    hits: int
    subs: int
    dels: int
    ins: int

    @property
    def ref_len(self):
        return self.hits + self.subs + self.dels

    @property
    def errors(self):
        return self.subs + self.dels + self.ins

    def rate(self):
        """(S + D + I) / reference length. Can be above 1.0 when there are many insertions."""
        if self.ref_len == 0:
            return 0.0 if self.ins == 0 else float("inf")
        return self.errors / self.ref_len


def normalize(text, lowercase=True, strip_punct=True):
    """NFC-normalize, optionally lowercase and drop punctuation, collapse spaces.

    Unicode normalization matters for scripts with combining marks (Devanagari, Odia,
    IPA diacritics): the same-looking string can be two different code point sequences.
    """
    text = unicodedata.normalize("NFC", text)
    if lowercase:
        text = text.lower()
    if strip_punct:
        text = "".join(c for c in text if not unicodedata.category(c).startswith("P"))
    return re.sub(r"\s+", " ", text).strip()


def tokenize(text, unit="word"):
    """Split into words (on whitespace) or characters (spaces dropped)."""
    if unit == "word":
        return text.split()
    if unit == "char":
        return [c for c in text if not c.isspace()]
    raise ValueError("unit must be 'word' or 'char'")


def align(ref, hyp):
    """Minimum edit-distance alignment of two sequences.

    Returns a list of (op, ref_item, hyp_item) where op is
    'C' (correct), 'S' (substitution), 'D' (deletion: in ref, missing from hyp)
    or 'I' (insertion: in hyp, not in ref). The missing side is None.
    """
    n, m = len(ref), len(hyp)
    d = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(n + 1):
        d[i][0] = i
    for j in range(m + 1):
        d[0][j] = j
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            if ref[i - 1] == hyp[j - 1]:
                d[i][j] = d[i - 1][j - 1]
            else:
                d[i][j] = 1 + min(d[i - 1][j - 1], d[i - 1][j], d[i][j - 1])

    ops = []
    i, j = n, m
    while i > 0 or j > 0:
        if i > 0 and j > 0 and ref[i - 1] == hyp[j - 1] and d[i][j] == d[i - 1][j - 1]:
            ops.append(("C", ref[i - 1], hyp[j - 1])); i -= 1; j -= 1
        elif i > 0 and j > 0 and d[i][j] == d[i - 1][j - 1] + 1:
            ops.append(("S", ref[i - 1], hyp[j - 1])); i -= 1; j -= 1
        elif i > 0 and d[i][j] == d[i - 1][j] + 1:
            ops.append(("D", ref[i - 1], None)); i -= 1
        else:
            ops.append(("I", None, hyp[j - 1])); j -= 1
    return ops[::-1]


def error_counts(ref, hyp):
    c = Counter(op for op, _, _ in align(ref, hyp))
    return Counts(hits=c["C"], subs=c["S"], dels=c["D"], ins=c["I"])


def wer(reference, hypothesis, **norm):
    return error_counts(tokenize(normalize(reference, **norm)), tokenize(normalize(hypothesis, **norm))).rate()


def cer(reference, hypothesis, **norm):
    r = tokenize(normalize(reference, **norm), "char")
    h = tokenize(normalize(hypothesis, **norm), "char")
    return error_counts(r, h).rate()


def corpus_rate(pairs, unit="word", **norm):
    """Total errors over total reference length across many utterances.

    This is not the same as averaging per-utterance rates: a long, well-recognized
    utterance should count for more than a two-word one. Returns (rate, Counts).
    """
    total = Counts(0, 0, 0, 0)
    for ref, hyp in pairs:
        c = error_counts(tokenize(normalize(ref, **norm), unit), tokenize(normalize(hyp, **norm), unit))
        total = Counts(total.hits + c.hits, total.subs + c.subs, total.dels + c.dels, total.ins + c.ins)
    return total.rate(), total


def top_substitutions(pairs, unit="word", n=10, **norm):
    """Most frequent (reference -> hypothesis) substitutions across a set of utterances."""
    seen = Counter()
    for ref, hyp in pairs:
        r = tokenize(normalize(ref, **norm), unit)
        h = tokenize(normalize(hyp, **norm), unit)
        for op, a, b in align(r, h):
            if op == "S":
                seen[(a, b)] += 1
    return seen.most_common(n)
