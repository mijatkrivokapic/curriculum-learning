# Generator zadataka

Pravi nove zadatke oduzimanja razlomaka istog tipa kao 20 originalnih Tatsuokinih zadataka.

## Pokretanje

```bash
pip install pytest
python build_dataset.py     # pravi data/originals.csv, train.csv, probe.csv, type_report.csv
python -m pytest tests      # testovi
```

## Kako radi

1. Svaki zadatak `a - b` opisuje se torkom svojstava (`fracgen/problem.py`, funkcija `features`):
   oblik umanjenika i umanjioca (ceo, pravi/nepravi razlomak, mešoviti), odnos imenilaca,
   potreba za pozajmljivanjem, neskraćen ulaz, potreba za skraćivanjem rezultata i oblik rezultata.
2. Tip zadatka je ta torka. Svih 20 originala ima različit tip.
3. Generator nabraja sve zadatke u opsegu (celi delovi do 9, imenioci do 12) i grupiše ih po tipu.
   Originalni zadaci se izbacuju.
4. Ako tip ima manje od 300 različitih zadataka, gornja granica imenioca se povećava (najviše do 20).
5. Za svaki tip pravi se probni skup (najviše 200 zadataka, najviše 20% tipa), a ostatak je trening.

## Format

Ulaz: `3_1/4-1_3/4=`, izlaz: `1_1/2`. Znak `_` odvaja ceo deo od razlomka.
Odgovor je uvek kanonski: ceo broj, pravi razlomak ili mešoviti broj, potpuno skraćen.

## Izvori

Tekstovi zadataka i Q-matica: R paket edmdata (`items_fractions`, `qmatrix_fractions`).
