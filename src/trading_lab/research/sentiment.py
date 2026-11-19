"""Headline scorers for study C: FinBERT (primary) and Loughran–McDonald (descriptive).

FinBERT needs the optional `news` extra (`uv sync --extra news`: torch CPU build,
transformers); it only ever runs on GitHub Actions.
"""

from __future__ import annotations

import csv
import importlib.util
import os
import re
import time
from pathlib import Path

import numpy as np

FINBERT = "ProsusAI/finbert"
_WORD = re.compile(r"[A-Za-z]+")


def n_words(text: str) -> int:
    return len(_WORD.findall(text))


def lm_lexicon(path: Path | None = None) -> tuple[frozenset[str], frozenset[str]]:
    """(positive, negative) word sets from the Loughran–McDonald master dictionary
    bundled with pysentiment2 (a word belongs to a list when its column holds the
    year it was added, i.e. > 0)."""
    if path is None:
        spec = importlib.util.find_spec("pysentiment2")
        if spec is None or not spec.submodule_search_locations:
            raise SystemExit("pysentiment2 missing — install the extra: uv sync --extra news")
        path = Path(spec.submodule_search_locations[0]) / "static" / "LM.csv"
    pos, neg = set(), set()
    with open(path, encoding="utf-8", errors="replace", newline="") as fh:
        for row in csv.DictReader(fh):
            if float(row["Positive"] or 0) > 0:
                pos.add(row["Word"].upper())
            if float(row["Negative"] or 0) > 0:
                neg.add(row["Word"].upper())
    return frozenset(pos), frozenset(neg)


def lm_scores(texts: list[str], lexicon: tuple[frozenset[str], frozenset[str]]) -> np.ndarray:
    """(positive − negative word count) ÷ word count; 0 for a headline with no words."""
    pos, neg = lexicon
    out = np.zeros(len(texts))
    for i, text in enumerate(texts):
        words = [w.upper() for w in _WORD.findall(text)]
        if words:
            out[i] = (sum(w in pos for w in words) - sum(w in neg for w in words)) / len(words)
    return out


class FinBert:
    """P(positive) − P(negative) from ProsusAI/finbert on CPU."""

    def __init__(self, model: str = FINBERT):
        import torch
        from transformers import AutoModelForSequenceClassification, AutoTokenizer

        torch.set_num_threads(os.cpu_count() or 4)
        self.torch = torch
        self.tok = AutoTokenizer.from_pretrained(model)
        self.model = AutoModelForSequenceClassification.from_pretrained(model).eval()
        labels = {str(v).lower(): int(k) for k, v in self.model.config.id2label.items()}
        self.pos, self.neg = labels["positive"], labels["negative"]

    def score(self, texts: list[str], batch: int = 64, log_every: int = 50_000) -> np.ndarray:
        # Similar lengths per batch → little padding → much faster on CPU.
        order = np.argsort([len(t) for t in texts], kind="stable")
        out = np.empty(len(texts))
        t0, logged = time.monotonic(), 0
        with self.torch.inference_mode():
            for s in range(0, len(texts), batch):
                idx = order[s : s + batch]
                enc = self.tok(
                    [texts[i] for i in idx],
                    padding=True,
                    truncation=True,
                    max_length=64,
                    return_tensors="pt",
                )
                p = self.model(**enc).logits.softmax(-1)
                out[idx] = (p[:, self.pos] - p[:, self.neg]).numpy()
                done = s + len(idx)
                if done - logged >= log_every or done == len(texts):
                    rate = done / max(time.monotonic() - t0, 1e-9)
                    print(f"finbert: {done:,}/{len(texts):,} headlines, {rate:,.0f}/s", flush=True)
                    logged = done
        return out
