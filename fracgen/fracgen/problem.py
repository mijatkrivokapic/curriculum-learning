"""Reprezentacija zadataka oduzimanja razlomaka.

Broj se zapisuje kao (ceo deo, brojilac, imenilac):
    3       -> Num(3, 0, 0)     ceo broj
    3/4     -> Num(0, 3, 4)     razlomak
    2 3/2   -> Num(2, 3, 2)     mešoviti broj (razlomljeni deo može biti nepravi)
Zadatak je uvek a - b.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from math import gcd


@dataclass(frozen=True)
class Num:
    whole: int
    num: int = 0
    den: int = 0

    @property
    def has_frac(self) -> bool:
        return self.den > 0

    @property
    def frac(self) -> Fraction:
        return Fraction(self.num, self.den) if self.has_frac else Fraction(0)

    @property
    def value(self) -> Fraction:
        return self.whole + self.frac

    def form(self) -> str:
        """W = ceo, F = pravi razlomak, I = nepravi razlomak,
        M = mešoviti (pravi deo), MI = mešoviti sa nepravim delom."""
        if not self.has_frac:
            return "W"
        improper = self.num >= self.den
        if self.whole == 0:
            return "I" if improper else "F"
        return "MI" if improper else "M"

    def text(self) -> str:
        """Zapis u formatu ulaza mreže: '3', '3/4', '2_3/2'."""
        if not self.has_frac:
            return str(self.whole)
        if self.whole == 0:
            return f"{self.num}/{self.den}"
        return f"{self.whole}_{self.num}/{self.den}"


@dataclass(frozen=True)
class Problem:
    a: Num
    b: Num

    @property
    def result(self) -> Fraction:
        return self.a.value - self.b.value

    def input_text(self) -> str:
        return f"{self.a.text()}-{self.b.text()}="

    def answer_text(self) -> str:
        return canonical(self.result)

    def features(self) -> tuple:
        return features(self)


def canonical(x: Fraction) -> str:
    """Kanonski oblik odgovora: ceo broj, pravi razlomak ili mešoviti broj,
    uvek potpuno skraćeno. Fraction se automatski skraćuje."""
    if x < 0:
        raise ValueError("Negativan rezultat nije dozvoljen")
    whole, rest = divmod(x.numerator, x.denominator)
    if rest == 0:
        return str(whole)
    frac = f"{rest}/{x.denominator}"
    return frac if whole == 0 else f"{whole}_{frac}"


def den_relation(d1: int, d2: int) -> str:
    """Odnos imenilaca: eq, mult (jedan deli drugi), coprime, common."""
    if d1 == 0 or d2 == 0:
        return "-"
    if d1 == d2:
        return "eq"
    if max(d1, d2) % min(d1, d2) == 0:
        return "mult"
    return "coprime" if gcd(d1, d2) == 1 else "common"


def features(p: Problem) -> tuple:
    """Strukturna svojstva zadatka koja određuju potrebne veštine.

    Vraća torku:
      form_a, form_b        oblik umanjenika i umanjioca
      den_rel               odnos imenilaca
      borrow                da li treba pozajmiti od celog dela umanjenika
      reducible_input       da li je neki razlomak u ulazu neskraćen
      needs_reduce          da li rezultat dobijen preko NZS imenilaca treba skratiti
      result_form           oblik rezultata: zero, W, F, M
    """
    a, b = p.a, p.b
    borrow = a.whole > 0 and a.frac < b.frac
    reducible_input = any(
        x.has_frac and x.num > 0 and gcd(x.num, x.den) > 1 for x in (a, b)
    )

    r = p.result
    if r == 0:
        result_form = "zero"
    elif r.denominator == 1:
        result_form = "W"
    elif r < 1:
        result_form = "F"
    else:
        result_form = "M"

    # Imenilac koji bi se dobio bez skraćivanja: NZS imenilaca u zadatku
    dens = [x.den for x in (a, b) if x.has_frac]
    if not dens:
        lcd = 1
    elif len(dens) == 1:
        lcd = dens[0]
    else:
        lcd = dens[0] * dens[1] // gcd(*dens)
    needs_reduce = result_form in ("F", "M") and r.denominator < lcd

    return (a.form(), b.form(), den_relation(a.den, b.den), borrow,
            reducible_input, needs_reduce, result_form)


FEATURE_NAMES = ("form_a", "form_b", "den_rel", "borrow",
                 "reducible_input", "needs_reduce", "result_form")


# ---- tokenizacija (ulaz i izlaz kao niz karaktera) ----

PAD, BOS, EOS = "<pad>", "<bos>", "<eos>"
VOCAB = [PAD, BOS, EOS] + list("0123456789") + ["_", "/", "-", "="]
STOI = {t: i for i, t in enumerate(VOCAB)}


def encode(text: str) -> list[int]:
    return [STOI[c] for c in text]


def decode(ids: list[int]) -> str:
    return "".join(VOCAB[i] for i in ids if VOCAB[i] not in (PAD, BOS, EOS))


def parse_num(s: str) -> Num:
    """Parsira '3', '3/4' ili '2_3/2' u Num."""
    if "/" not in s:
        return Num(int(s))
    whole = 0
    if "_" in s:
        w, s = s.split("_")
        whole = int(w)
    n, d = s.split("/")
    return Num(whole, int(n), int(d))


def parse_problem(text: str) -> Problem:
    left = text.rstrip("=")
    a, b = left.split("-")
    return Problem(parse_num(a), parse_num(b))
