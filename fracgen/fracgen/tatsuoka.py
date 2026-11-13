"""Originalnih 20 zadataka iz Tatsuokinog dataseta.

Izvor teksta zadataka: dokumentacija R paketa edmdata (items_fractions,
qmatrix_fractions), koja navodi Tatsuoka (1984, 2002).
"""
from .problem import Num, Problem

ITEMS: dict[str, Problem] = {
    "Item01": Problem(Num(0, 5, 3), Num(0, 3, 4)),     # 5/3 - 3/4
    "Item02": Problem(Num(0, 3, 4), Num(0, 3, 8)),     # 3/4 - 3/8
    "Item03": Problem(Num(0, 5, 6), Num(0, 1, 9)),     # 5/6 - 1/9
    "Item04": Problem(Num(3, 1, 2), Num(2, 3, 2)),     # 3 1/2 - 2 3/2
    "Item05": Problem(Num(4, 3, 5), Num(3, 4, 10)),    # 4 3/5 - 3 4/10
    "Item06": Problem(Num(0, 6, 7), Num(0, 4, 7)),     # 6/7 - 4/7
    "Item07": Problem(Num(3), Num(2, 1, 5)),           # 3 - 2 1/5
    "Item08": Problem(Num(0, 2, 3), Num(0, 2, 3)),     # 2/3 - 2/3
    "Item09": Problem(Num(3, 7, 8), Num(2)),           # 3 7/8 - 2
    "Item10": Problem(Num(4, 4, 12), Num(2, 7, 12)),   # 4 4/12 - 2 7/12
    "Item11": Problem(Num(4, 1, 3), Num(2, 4, 3)),     # 4 1/3 - 2 4/3
    "Item12": Problem(Num(0, 11, 8), Num(0, 1, 8)),    # 11/8 - 1/8
    "Item13": Problem(Num(3, 3, 8), Num(2, 5, 6)),     # 3 3/8 - 2 5/6
    "Item14": Problem(Num(3, 4, 5), Num(3, 2, 5)),     # 3 4/5 - 3 2/5
    "Item15": Problem(Num(2), Num(0, 1, 3)),           # 2 - 1/3
    "Item16": Problem(Num(4, 5, 7), Num(1, 4, 7)),     # 4 5/7 - 1 4/7
    "Item17": Problem(Num(7, 3, 5), Num(2, 4, 5)),     # 7 3/5 - 2 4/5
    "Item18": Problem(Num(4, 1, 10), Num(2, 8, 10)),   # 4 1/10 - 2 8/10
    "Item19": Problem(Num(4), Num(1, 4, 3)),           # 4 - 1 4/3
    "Item20": Problem(Num(4, 1, 3), Num(1, 5, 3)),     # 4 1/3 - 1 5/3
}

SKILLS = {
    "a1": "pretvaranje celog broja u razlomak",
    "a2": "odvajanje celog dela od razlomka",
    "a3": "skraćivanje pre oduzimanja",
    "a4": "nalaženje zajedničkog imenioca",
    "a5": "pozajmljivanje od celog dela",
    "a6": "pozajmljivanje u koloni",
    "a7": "oduzimanje brojilaca",
    "a8": "skraćivanje rezultata",
}
