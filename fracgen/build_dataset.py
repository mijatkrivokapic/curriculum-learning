"""Pravi skupove podataka i izveštaj o tipovima zadataka.

Pokretanje:  python build_dataset.py
Izlaz u data/: originals.csv, train.csv, probe.csv, type_report.csv
"""
import csv
from pathlib import Path

from fracgen.generator import (Ranges, adapt_ranges, build_pools,
                               derived_skills, item_types, make_splits)
from fracgen.problem import FEATURE_NAMES
from fracgen.tatsuoka import ITEMS

OUT = Path("data")
SEED = 0
MIN_POOL = 300      # najmanji broj različitih zadataka po tipu
N_PROBE = 200       # najviše zadataka po tipu u probnom skupu


def read_q():
    with open(OUT / "tatsuoka_qmatrix.csv") as f:
        return {r["item"]: {k: int(v) for k, v in r.items() if k != "item"}
                for r in csv.DictReader(f)}


def read_p():
    with open(OUT / "tatsuoka_responses.csv") as f:
        rows = list(csv.DictReader(f))
    return {k: sum(int(r[k]) for r in rows) / len(rows) for k in rows[0]}


def write(path, header, rows):
    with open(path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(rows)


def main():
    types = item_types()                       # Item01 -> tip
    assert len(set(types.values())) == 20, "Dva originala imaju isti tip"
    pools = build_pools(Ranges(max_whole=9, max_den=20), set(types.values()))
    pools, caps = adapt_ranges(pools, min_pool=MIN_POOL, base_den=12)
    train, probe = make_splits(pools, n_probe=N_PROBE, seed=SEED)

    write(OUT / "originals.csv", ["item", "input", "answer"],
          [[k, p.input_text(), p.answer_text()] for k, p in ITEMS.items()])
    write(OUT / "train.csv", ["item", "input", "answer"],
          [[k, p.input_text(), p.answer_text()]
           for k, t in types.items() for p in train[t]])
    write(OUT / "probe.csv", ["item", "input", "answer"],
          [[k, p.input_text(), p.answer_text()]
           for k, t in types.items() for p in probe[t]])

    q, pval = read_q(), read_p()
    rows, mismatches = [], []
    for k, t in types.items():
        d = derived_skills(t)
        q_str = "".join(str(q[k][s]) for s in d)
        d_str = "".join("?" if v is None else str(v) for v in d.values())
        for s, v in d.items():
            if v is not None and v != q[k][s]:
                mismatches.append(f"{k} {s}: Q={q[k][s]}, svojstva={v}")
        rows.append([k, ITEMS[k].input_text() + ITEMS[k].answer_text(),
                     *t, q_str, d_str, round(pval[k], 2), caps[t],
                     len(pools[t]), len(train[t]), len(probe[t])])
    write(OUT / "type_report.csv",
          ["item", "original", *FEATURE_NAMES, "q_matrix", "derived",
           "p_ljudi", "max_den", "n_pool", "n_train", "n_probe"], rows)

    print(f"{'item':7} {'original':22} {'Q':9} {'izved.':9} {'max_den':>7} "
          f"{'pool':>6} {'train':>6} {'probe':>6}")
    for r in rows:
        print(f"{r[0]:7} {r[1]:22} {r[9]:9} {r[10]:9} {r[12]:>7} "
              f"{r[13]:>6} {r[14]:>6} {r[15]:>6}")
    print("\nNeslaganja izvedenih veština sa Q-maticom:")
    print("\n".join(mismatches) or "nema")


if __name__ == "__main__":
    main()
