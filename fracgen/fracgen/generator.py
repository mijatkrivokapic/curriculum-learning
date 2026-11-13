"""Generator zadataka istog tipa kao originalni Tatsuokini zadaci.

Tip zadatka = torka strukturnih svojstava (problem.features). Generator
nabraja sve zadatke u zadatim opsezima brojeva, grupiše ih po tipu i za
svaki originalni zadatak vraća skup novih zadataka istog tipa.
"""
from __future__ import annotations

import random
from collections import defaultdict
from dataclasses import dataclass

from .problem import Num, Problem, features
from .tatsuoka import ITEMS


@dataclass(frozen=True)
class Ranges:
    max_whole: int = 9   # celi delovi 1..9 (originali idu do 7)
    min_den: int = 2
    max_den: int = 12    # originali idu do 12


def all_numbers(r: Ranges) -> list[Num]:
    """Svi brojevi u opsegu: celi, pravi i nepravi razlomci, mešoviti.
    Nepravi razlomljeni deo je između 1 i 2 (kao u originalima: 5/3, 3/2, 11/8)."""
    nums = [Num(w) for w in range(1, r.max_whole + 1)]
    for d in range(r.min_den, r.max_den + 1):
        fracs = list(range(1, d)) + list(range(d + 1, 2 * d))
        for n in fracs:
            for w in range(0, r.max_whole + 1):
                nums.append(Num(w, n, d))
    return nums


def build_pools(r: Ranges = Ranges(), types: set | None = None) -> dict[tuple, list[Problem]]:
    """Grupiše sve zadatke a - b sa rezultatom >= 0 po tipu.
    Ako je `types` zadat, čuva samo te tipove (štedi memoriju)."""
    nums = all_numbers(r)
    originals = set(ITEMS.values())
    pools: dict[tuple, list[Problem]] = defaultdict(list)
    for a in nums:
        va = a.value
        for b in nums:
            if b.value > va:
                continue
            p = Problem(a, b)
            if p in originals:
                continue
            f = features(p)
            if types is None or f in types:
                pools[f].append(p)
    return dict(pools)


def item_types() -> dict[str, tuple]:
    return {name: features(p) for name, p in ITEMS.items()}


def make_splits(pools: dict[tuple, list[Problem]], n_probe: int = 200,
                probe_frac_max: float = 0.2, seed: int = 0):
    """Za svaki tip deli zadatke na probni (evaluacioni) i trening skup.
    Probni skup ima najviše n_probe zadataka i najviše probe_frac_max pool-a."""
    rng = random.Random(seed)
    train, probe = {}, {}
    for t, plist in pools.items():
        plist = sorted(plist, key=lambda p: p.input_text())
        rng.shuffle(plist)
        k = min(n_probe, int(len(plist) * probe_frac_max))
        probe[t] = plist[:k]
        train[t] = plist[k:]
    return train, probe


def den_cap(p: Problem) -> int:
    return max(p.a.den, p.b.den)


def adapt_ranges(pools: dict[tuple, list[Problem]], min_pool: int = 300,
                 base_den: int = 12) -> tuple[dict, dict]:
    """Za svaki tip zadržava zadatke sa imeniocima <= base_den. Ako ih je
    manje od min_pool, postepeno povećava gornju granicu imenioca dok ne
    dobije dovoljno zadataka. Vraća (novi pools, granica imenioca po tipu)."""
    out, caps = {}, {}
    for t, plist in pools.items():
        top = max(den_cap(p) for p in plist)
        cap = base_den
        while cap < top and sum(den_cap(p) <= cap for p in plist) < min_pool:
            cap += 1
        out[t] = [p for p in plist if den_cap(p) <= cap]
        caps[t] = cap
    return out, caps


# ---- poređenje sa Q-maticom ----

def derived_skills(f: tuple) -> dict[str, int | None]:
    """Veštine izvedene iz svojstava zadatka (metod B: odvajanje celog dela).
    None znači da pravilo nije moguće jednoznačno izvesti iz svojstava."""
    form_a, form_b, den_rel, borrow, _red_in, needs_reduce, _res = f
    mixed = {"M", "MI"}
    return {
        "a1": int(form_a == "W" and form_b != "W"),
        "a2": int(form_a in mixed or form_b in mixed),
        "a3": int(form_b == "MI"),
        "a4": int(den_rel in ("mult", "coprime", "common")),
        "a5": int(borrow and form_a != "W"),
        "a6": None,
        "a7": int(form_b != "W"),
        "a8": int(needs_reduce),
    }
