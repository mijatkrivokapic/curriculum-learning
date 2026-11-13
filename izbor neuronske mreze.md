
# Izveštaj: izbor neuronske mreže za oduzimanje razlomaka

## Sažetak

Cilj ove faze bio je da se pronađe neuronska mreža koja, kada se istrenira do kraja, pouzdano rešava zadatke oduzimanja razlomaka istog tipa kao 20 Tatsuokinih zadataka. Izabrana mreža je višeslojni perceptron (MLP) sa embedinzima za ulazne brojeve i tri izlazne glave. Posle 12.000 koraka treninga postiže **99,7% tačnosti** na neviđenim zadacima, najslabiji tip zadatka rešava sa 95%, a svih 20 originalnih zadataka rešava tačno.

Dva nalaza su presudila. Prvo, mreža mora da vežba na svim zadacima oduzimanja u opsegu, a ne samo na 20 Tatsuokinih tipova: inače pamti primere i ne generalizuje. Drugo, brojevi moraju ulaziti kroz embedinge, a ne kao skalarne vrednosti.

## 1. Zadatak i reprezentacija

Svaki zadatak je oblika a − b, gde su a i b celi brojevi, razlomci ili mešoviti brojevi. Svaki broj se predstavlja kao trojka (ceo deo, brojilac, imenilac), pri čemu nula znači da taj deo ne postoji:

| Broj | Trojka |
|---|---|
| 3 1/4 | (3, 1, 4) |
| 3/4 | (0, 3, 4) |
| 2 | (2, 0, 0) |

Ulaz mreže je šest celih brojeva (w₁, n₁, d₁, w₂, n₂, d₂). Izlaz je kanonski odgovor u istom obliku (W, N, D): ceo broj, pravi razlomak ili mešoviti broj, uvek potpuno skraćen. Na primer, za 3 1/4 − 1 3/4 ulaz je (3, 1, 4, 1, 3, 4), a tačan izlaz (1, 1, 2).

## 2. Arhitektura mreže

| Deo | Opis | Parametri |
|---|---|---|
| Ulazni embedinzi | Šest odvojenih tabela, po jedna za svaku poziciju. Svaka vrednost 0–39 dobija vektor dužine 16. Vektori se spajaju u jedan vektor dužine 96 | 3.840 |
| Skriveni sloj 1 | Potpuno povezan, 96 → 256, ReLU | 24.832 |
| Skriveni slojevi 2 i 3 | Potpuno povezani, 256 → 256, ReLU | 131.584 |
| Izlazna glava W | 256 → 11 klasa (ceo deo 0–10) | 2.827 |
| Izlazna glava N | 256 → 132 klase (brojilac 0–131) | 33.924 |
| Izlazna glava D | 256 → 133 klase (imenilac 0–132) | 34.181 |
| **Ukupno** | | **231.188** |

**Zašto embedinzi.** Embedding znači da svaka vrednost (npr. imenilac 6) ima svoj naučeni vektor. Mreža tako može da nauči svojstva brojeva koja nisu vidljiva iz same veličine, kao što su deljivost i zajednički činioci. Kada se brojevi daju kao skalari, mreža vidi samo da je 6 "malo veće" od 5, pa ne uspeva da nauči nalaženje zajedničkog imenioca (eksperiment 4).

**Zašto odvojene tabele po poziciji.** Isti broj ima različitu ulogu na različitim mestima: 4 kao imenilac znači nešto drugo nego 4 kao ceo deo. Odvojene tabele dozvoljavaju mreži da to razlikuje.

**Zašto tri glave.** Svaka glava bira jednu vrednost iz skupa mogućih (klasifikacija), umesto da predviđa broj (regresija). Tako je odgovor uvek ceo broj, a greška je jasno merljiva.

## 3. Trening

| Podešavanje | Vrednost |
|---|---|
| Funkcija gubitka | Zbir unakrsne entropije za tri glave |
| Optimizator | AdamW, weight decay 0,01 |
| Stopa učenja | Linearno zagrevanje do 0,003 tokom 500 koraka, zatim kosinusni pad do 5% |
| Veličina grupe | 256 zadataka |
| Broj koraka | 12.000 |
| Uzorkovanje | Uravnoteženo po tipu: prvo se nasumično bira tip zadatka, pa zadatak tog tipa |
| Inicijalizacija | Embedinzi N(0; 0,1²), skriveni slojevi He, izlazne glave N(0; 1/256) |

**Podaci.** Trening skup sadrži sve zadatke oduzimanja u opsegu (celi delovi do 9, imenioci do 12): ukupno oko 883.000 zadataka, svrstanih u 460 tipova po strukturnim svojstvima. Uravnoteženo uzorkovanje po tipu sprečava da mreža uči neke tipove ranije samo zato što ih ima više.

**Trajanje.** Oko jednog minuta na jednom CPU jezgru, što omogućava treniranje stotina mreža za glavni eksperiment.

## 4. Mere ocenjivanja

**Tačnost odgovora (tačno poklapanje).** Odgovor je tačan samo ako su sve tri glave tačne. Delimično tačan odgovor, npr. tačan imenilac a pogrešan brojilac, računa se kao netačan, isto kao kod učenika na testu. Neskraćen odgovor je takođe netačan, jer je skraćivanje rezultata jedna od veština iz Q-matice.

**Tačnost na probnom skupu.** Glavna mera. Probni skup čini do 200 zadataka svakog od 20 Tatsuokinih tipova (najviše polovina tipa), koje mreža nikada nije videla tokom treninga. Meri da li je mreža naučila postupak, a ne zapamtila primere. Prijavljuje se ukupno i po tipu.

**Najslabiji tip.** Najniža tačnost po tipu na probnom skupu. Bitna je jer prosek može sakriti tip koji mreža uopšte ne zna. Za KST analizu svaki tip mora biti naučiv.

**Tačnost na originalnim zadacima.** Broj tačno rešenih od 20 originalnih Tatsuokinih zadataka. Ovi zadaci nisu ni u treningu ni u probnom skupu, a na njima se mreže direktno porede sa učenicima.

**Tačnost na treningu.** Koristi se samo kao kontrola: velika razlika između tačnosti na treningu i na probnom skupu znači da mreža pamti umesto da generalizuje.

**Korak savladavanja tipa.** Prvi korak treninga u kome tačnost tipa na probnom skupu dostiže 80%. Opisuje dinamiku učenja: kojim redom mreža savladava tipove. Ova mera je osnova za glavni eksperiment, jer pokazuje da li će mreže zaustavljene u različitim trenucima imati različita stanja znanja.

## 5. Rezultati

### Poređenje konfiguracija

Sve konfiguracije koriste istu arhitekturu i 10.000–12.000 koraka treninga.

| # | Trening skup | Ulaz | Trening | Probni skup | Najslabiji tip | Originali |
|---|---|---|---|---|---|---|
| 1 | Samo 20 Tatsuokinih tipova (~19.000 zadataka) | embedding | 100% | 89,1% | Item01: 4% | 16/20 |
| 2 | Isto, jača regularizacija (weight decay 0,3) | embedding | 100% | 89,9% | Item01: 10% | 16/20 |
| 3 | **Svi zadaci u opsegu (~883.000)** | **embedding** | **100%** | **99,7%** | **Item01: 95%** | **20/20** |
| 4 | Svi zadaci u opsegu | skalari | 49,6% | 57,1% | Item01: 6% | 13/20 |

**Eksperimenti 1 i 2.** Mreža savršeno rešava trening, ali na probnom skupu ne uspeva na zadacima koji sadrže samo razlomke sa različitim imeniocima: Item01 (4%), Item12 (4%), Item03 (14%) i Item02 (25%). Ovih tipova ima premalo (25–700 zadataka), pa mreža pamti primere umesto da nauči postupak. Jača regularizacija ne pomaže.

**Eksperiment 3.** Kada mreža vežba na svim zadacima, uči opšti postupak oduzimanja koji prenosi i na neviđene zadatke. Ovo odgovara i učenju kod ljudi: učenik vežba mnogo različitih zadataka, a test sadrži samo njih 20.

**Eksperiment 4.** Ista mreža sa brojevima kao skalarima ne uči ni trening skup (49,6%), što potvrđuje da su embedinzi neophodni.

### Dinamika učenja

Za konfiguraciju 3 praćena je tačnost po tipu svakih 200 koraka, za dva seeda. Tabela prikazuje korak savladavanja svakog tipa (prvi korak sa tačnošću od bar 80%):

| Tip | 01 | 02 | 03 | 04 | 05 | 06 | 07 | 08 | 09 | 10 | 11 | 12 | 13 | 14 | 15 | 16 | 17 | 18 | 19 | 20 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Seed 0 | >6000 | 1600 | 2400 | 1600 | 1800 | 2800 | 1800 | 600 | 2400 | 1800 | 2800 | 2000 | 2400 | 2800 | 2400 | 3400 | 3000 | 2200 | 2200 | 4600 |
| Seed 1 | >6000 | 1200 | 2400 | 1600 | 2200 | 3200 | 2000 | 800 | 2800 | 1800 | 2600 | 2200 | 2400 | 3000 | 2400 | 3600 | 3800 | 2400 | 2200 | 6000 |

Tipovi se savladavaju postepeno, od 600 koraka (Item08, 2/3 − 2/3) do više od 6.000 (Item01, 5/3 − 3/4). Redosled je sličan između seedova, ali nije identičan. To je poželjno za glavni eksperiment: mreže zaustavljene u nasumičnim trenucima imaće različita stanja znanja, a razlike među seedovima daju dodatnu raznovrsnost.

Neki tipovi se savladavaju redom koji se razlikuje od intuitivne težine za ljude. Na primer, Item16 (4 5/7 − 1 4/7), koji ne traži pozajmljivanje ni zajednički imenilac, mreža savladava među poslednjima. Ovo je prvi nagoveštaj da se mašinska i ljudska struktura mogu razlikovati.

## 6. Ograničenja

- **Reprezentacija razdvaja ceo deo od razlomka.** Pošto je ulaz već podeljen na trojke, veština "odvajanje celog dela od razlomka" (a2 u Q-matici) za mrežu je data unapred. Ovo treba uzeti u obzir pri poređenju sa ljudskom strukturom.
- **Dva seeda.** Dinamika učenja je proverena samo na dva seeda; glavni eksperiment će dati potpuniju sliku.
- **Implementacija.** Eksperimenti su rađeni u JAX-u (`reference_jax/`). Datoteka `train.py` je ista mreža u PyTorch-u i treba je jednom proveriti: očekivano je oko 99% na probnom skupu i 20/20 na originalima.