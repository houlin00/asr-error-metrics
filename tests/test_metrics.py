import math
import unittest

from asr_error_metrics import align, cer, corpus_rate, error_counts, normalize, top_substitutions, wer


class TestRates(unittest.TestCase):
    def test_identical(self):
        self.assertEqual(wer("the cat sat", "the cat sat"), 0.0)

    def test_one_substitution(self):
        self.assertAlmostEqual(wer("the cat sat", "the cat sit"), 1 / 3)

    def test_one_deletion(self):
        self.assertAlmostEqual(wer("a b c", "a c"), 1 / 3)

    def test_one_insertion(self):
        self.assertAlmostEqual(wer("a b", "a x b"), 1 / 2)

    def test_can_exceed_one(self):
        self.assertEqual(wer("a", "a b c"), 2.0)

    def test_char_rate(self):
        self.assertAlmostEqual(cer("cat", "cut"), 1 / 3)

    def test_empty_reference(self):
        self.assertEqual(wer("", ""), 0.0)
        self.assertTrue(math.isinf(wer("", "hello")))

    def test_mandarin_characters(self):
        self.assertAlmostEqual(cer("今天天气好", "今天天汽好"), 1 / 5)


class TestAlignment(unittest.TestCase):
    def test_ops(self):
        ops = align(["a", "b", "c"], ["a", "x", "c", "d"])
        self.assertEqual([o for o, _, _ in ops], ["C", "S", "C", "I"])

    def test_counts_sum_to_reference_length(self):
        c = error_counts(list("kitten"), list("sitting"))
        self.assertEqual(c.ref_len, 6)
        self.assertEqual(c.errors, 3)


class TestNormalize(unittest.TestCase):
    def test_punctuation_and_case(self):
        self.assertEqual(normalize("Hello,  World!"), "hello world")

    def test_unicode_composition(self):
        # e + combining acute vs precomposed e-acute should compare equal
        self.assertEqual(normalize("é"), normalize("é"))


class TestCorpus(unittest.TestCase):
    def test_pooled_not_averaged(self):
        pairs = [("a b c d e f g h i j", "a b c d e f g h i j"), ("x y", "q z")]
        rate, c = corpus_rate(pairs)
        self.assertAlmostEqual(rate, 2 / 12)      # pooled
        self.assertNotAlmostEqual(rate, (0.0 + 1.0) / 2)

    def test_top_substitutions(self):
        pairs = [("the cat", "the bat"), ("a cat", "a bat"), ("a dog", "a log")]
        self.assertEqual(top_substitutions(pairs, n=1), [(("cat", "bat"), 2)])


if __name__ == "__main__":
    unittest.main()
