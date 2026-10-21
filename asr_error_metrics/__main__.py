"""python -m asr_error_metrics ref.txt hyp.txt [--unit char]

ref.txt and hyp.txt have one utterance per line, in the same order.
"""
import argparse

from .metrics import corpus_rate, top_substitutions


def main():
    p = argparse.ArgumentParser(description="Corpus-level WER/CER with the most common substitutions.")
    p.add_argument("reference")
    p.add_argument("hypothesis")
    p.add_argument("--unit", choices=["word", "char"], default="word")
    p.add_argument("--top", type=int, default=10, help="how many substitutions to list")
    args = p.parse_args()

    with open(args.reference, encoding="utf-8") as f:
        refs = f.read().splitlines()
    with open(args.hypothesis, encoding="utf-8") as f:
        hyps = f.read().splitlines()
    if len(refs) != len(hyps):
        raise SystemExit(f"{len(refs)} reference lines but {len(hyps)} hypothesis lines")

    pairs = list(zip(refs, hyps))
    rate, c = corpus_rate(pairs, args.unit)
    label = "WER" if args.unit == "word" else "CER"
    print(f"{label}: {rate:.3f}   ({c.subs} substitutions, {c.dels} deletions, {c.ins} insertions, {c.ref_len} reference units)")
    for (a, b), k in top_substitutions(pairs, args.unit, args.top):
        print(f"  {a} -> {b}: {k}")


if __name__ == "__main__":
    main()
