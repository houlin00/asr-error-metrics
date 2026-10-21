# asr-error-metrics

Word and character error rate (WER / CER) that keeps the alignment, so you can see *which*
words or characters went wrong instead of getting a single number.

I wrote it while evaluating a multilingual ASR model on low-resource languages, where the
aggregate error rate hid several different failure types (repetition loops, output in the
wrong script, systematic vowel confusions). The score was the same whether a word was
slightly misspelled or completely wrong, and I needed to separate those.

## Use

```python
from asr_error_metrics import wer, cer, align, corpus_rate, top_substitutions

wer("the cat sat", "the cat sit")        # 0.333...
cer("cat", "cut")                        # 0.333...

align(list("kitten"), list("sitting"))   # [('S','k','s'), ('C','i','i'), ..., ('I', None, 'g')]
```

Command line, one utterance per line in each file:

```
python -m asr_error_metrics refs.txt hyps.txt            # word error rate
python -m asr_error_metrics refs.txt hyps.txt --unit char
```

It prints the corpus-level rate, the counts of substitutions/deletions/insertions, and the
most frequent substitutions (e.g. `a -> ɑ`), which is the part that tells you where to look.

## Things the number can hide

- **Pooled vs averaged.** `corpus_rate` adds up errors and reference length over all
  utterances. Averaging per-utterance rates gives short utterances the same weight as long
  ones. They can differ a lot.
- **WER above 1.0.** Insertions count as errors but don't lengthen the reference, so a model
  that loops and repeats a phrase can score well over 100%.
- **Every error costs the same.** A one-letter spelling difference and a completely wrong
  word are both one substitution. If your task cares about the difference, look at the
  substitution list or score at the phoneme level.
- **Spelling and Unicode.** The same-looking text can be different code points (combining
  marks in Devanagari, Odia, IPA). `normalize` applies NFC first; it can also lowercase and
  drop punctuation. Decide those choices once and report them.
- **Words in languages without spaces.** WER needs a segmentation. For Mandarin, CER is the
  usual choice.

## Limitations

- The alignment uses the standard minimum edit distance. When several alignments tie, it
  picks one, so the exact list of substitutions can vary between equally good alignments.
- Memory is O(reference length x hypothesis length). Fine for utterances, not for hours of
  audio as one string.
- Plain Python, no dependencies, not optimized. For large benchmarks use a library built for
  speed; this is for looking at errors.

## Tests

```
python -m unittest discover -s tests -v
```

## License

MIT. See `LICENSE`.
