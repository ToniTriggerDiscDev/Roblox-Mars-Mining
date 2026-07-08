# Mars Miner 2D — Economy Design

## Ist-Zustand (aktuelle Zahlen)

### Erz-Werte & Gewicht
| Erz | Wert | Gewicht | $/Gewicht | Tiefe ab (Row) |
|-----|------|---------|-----------|----------------|
| Dirt | $0 | — | — | 6 |
| Ironium | $30 | 1 | 30 | 6 |
| Bronzium | $60 | 1 | 60 | 6 |
| Silverium | $100 | 1 | 100 | ~65 |
| Goldium | $250 | 2 | 125 | ~130 |
| Platinium | $750 | 3 | 250 | ~195 |
| Einsteinium | $2,000 | 4 | 500 | ~260 |
| Emerald | $5,000 | 6 | 833 | ~325 |
| Ruby | $20,000 | 8 | 2,500 | ~390 |
| Diamond | $100,000 | 10 | 10,000 | ~455 |
| Amazonite | $500,000 | 12 | 41,667 | ~520 |

**Wertsprünge:** 2x, 1.7x, 2.5x, 3x, 2.7x, 2.5x, **4x**, **5x**, **5x**
→ Die letzten drei Sprünge (Ruby→Diamond→Amazonite) sind steiler als der Rest.

### Upgrade-Preise (alle Kategorien gleich)
| Tier | Preis | Kumuliert |
|------|-------|-----------|
| 2 | $750 | $750 |
| 3 | $2,000 | $2,750 |
| 4 | $5,000 | $7,750 |
| 5 | $20,000 | $27,750 |
| 6 | $100,000 | $127,750 |
| 7 | $500,000 | $627,750 |

6 Kategorien × gleiche Preise → Tier 2 komplett: $4,500. Tier 7 komplett: ~$3.77M.

### Erz-Verteilung (Generierung)
- 80% Dirt, 20% Erz-Branche
- Von Erz: ~80% häufig, ~4% selten, ~1% sehr selten/Schatz
- 25% Luftlöcher (über alles drüber)
- Effektive Erz-Rate: ~15% aller Blöcke
- Schätze erst ab Row 80 (~Depth 75)

### Fuel-Ökonomie
| Tank | Kapazität | Flugzeit (fly) | Kosten Volltanken |
|------|-----------|----------------|-------------------|
| Micro (Start) | 10L | 30s | $10 |
| Medium | 15L | 45s | $15 |
| Huge | 25L | 76s | $25 |
| Gigantic | 40L | 121s | $40 |
| Titanic | 60L | 182s | $60 |
| Leviathan | 100L | 303s | $100 |
| Liquid Comp. | 150L | 455s | $150 |

Fuel-Kosten sind vernachlässigbar ($1/L). Selbst max Tank = $150 bei Trips die $100K+ einbringen.

### Items
| Item | Preis | Zweck |
|------|-------|-------|
| Hull Repair | $7,500 | 30 HP reparieren |
| DD-4 Blast | $2,000 | Kleiner Radius |
| DD-X Breach | $5,000 | Großer Radius |
| Matter Transmitter | $10,000 | Sicherer Rücktransport |
| ID Kit | $1,500 | Artefakt identifizieren |

---

## Analyse: Was funktioniert gut

1. **Tiefenbasierte Progression** — Wertvollere Erze tauchen erst in tieferen Schichten auf. Spieler muss Upgrades kaufen um tiefer zu kommen → natürliche Progression.

2. **Cargo-als-Risiko** — Pod-Tod = Cargo-Verlust. Gierig tief graben vs. sicher zurückkommen = Kernspannung. Das ist der wichtigste Mechanismus.

3. **Gewicht-System** — Wertvolle Erze wiegen mehr. Zwingt zu Entscheidungen: 1 Diamond (10kg) oder 10 Ironium (10kg, $300)?

4. **Upgrade-Preise passen zu Erz-Tiers** — Tier 2 ($750) ≈ Platinium-Wert. Tier 5 ($20,000) ≈ Ruby-Wert. Spieler kauft Upgrades mit Erzen der entsprechenden Tiefe.

---

## Analyse: Potenzielle Probleme

### 1. Frühes Spiel fühlt sich leer an
- Dirt = $0. Erste Minuten nur wertloses Bohren bis man Ironium ($30) findet.
- Erstes Upgrade (Tier 2) = $750 → braucht 25 Ironium-Trips oder 12 Bronzium.
- Bei Cargo 7kg und Ironium 1kg = 7 Erze pro Trip × $30 = $210/Trip → 3-4 Trips für erstes Upgrade.
- **Bewertung:** OK, aber Dirt-Bohren fühlt sich unrewarding an. Das neue "DIRT" Popup hilft.

### 2. Mittleres Spiel ist gut gepacat
- Mit Drill Tier 2-3 und Fuel Tier 2-3 erreicht man Goldium/Platinium.
- Trips bringen $1,000-$3,000, Upgrades kosten $2,000-$5,000 → 1-3 Trips pro Upgrade.
- **Bewertung:** Goldene Zone. Hier funktioniert der Loop am besten.

### 3. Spätes Spiel: Mauern und Inflation
- Ruby→Diamond Sprung: $20K → $100K (5x) aber Upgrade-Preis auch 5x ($20K → $100K).
- Ein einziger Diamond ($100K) bezahlt ein komplettes Tier-6-Upgrade.
- Amazonite ($500K × 1 Stück) = ganzes Tier 7.
- **Problem:** Ab Diamond-Tiefe wird Geld irrelevant. Ein Trip kann $500K+ bringen.
- **Bewertung:** Endgame braucht mehr Sinks oder der Spieler "gewinnt" zu schnell.

### 4. Fuel-Kosten sind ein Nicht-Faktor
- Max Fuel $150/Tanken bei Trips die $50K+ einbringen = 0.3% der Einnahmen.
- Fuel ist nur ein Timer (Tripzeitbegrenzung), kein wirtschaftlicher Faktor.
- **Bewertung:** OK als Timer-Mechanik, aber kein Economy-Sink.

### 5. Engine-Upgrades sind kaum spürbar
- Stock: 6.0, Max: 8.4 → nur 40% schneller über 7 Tiers.
- Vergleich: Drill geht von 2→12 (6x), Fuel von 10→150 (15x).
- **Bewertung:** Engine fühlt sich wie verschwendetes Geld an.

### 6. Alle Kategorien gleiche Preise
- Drill Tier 2 kostet gleich viel wie Cargo Tier 2 ($750).
- Aber Drill-Upgrade ist spielentscheidend, Cargo Tier 2 (7→15) ist auch stark.
- **Bewertung:** Funktioniert, weil es Spieler-Wahl erzwingt. Aber keine Differenzierung = weniger strategische Tiefe.

---

## Verbesserungsvorschläge

### Quick Wins (kleine Zahlen-Änderungen)
1. **Engine-Effekt verstärken** — von 6→8.4 auf z.B. 5→11. Muss sich lohnen.
2. **Späte Upgrade-Preise staffeln** — nicht alle $500K für Tier 7. Drill Tier 7 = $500K, Cargo Tier 6 = $300K, Engine Tier 7 = $200K. Gibt dem Spieler eine Reihenfolge.
3. **Fuel-Preis tiefenabhängig machen** — $1/L an der Oberfläche, aber $3/L wenn man eine tiefere Tankstelle einführt. Oder: Fuel-Drain steigt mit der Tiefe (Mars-Druck?).

### Mittlere Änderungen
4. **Dirt einen Minimalwert geben** — $1-2 pro Dirt. Frühes Spiel fühlt sich productive an. Oder: "Soil Samples" Cargo-Item das sich bei genug Stück verkaufen lässt.
5. **Reparaturkosten als Sink** — Wenn Hull unter 50% → automatische Reparatur beim Landen kostet $/HP. Zwingt dazu Hull-Upgrades ernst zu nehmen.
6. **Versicherung / "Bergungskosten"** — Bei Pod-Tod nicht nur Cargo weg, sondern auch $X Reparaturgebühr. Steigt mit Upgrade-Tier (teurerer Pod = teurere Reparatur).

### Größere Features (falls gewünscht)
7. **Prestige/Rebirth** — Nach Tier 7 komplett: Reset mit permanentem Bonus (z.B. 10% mehr Erz-Wert pro Rebirth). Gibt Endgame-Loop.
8. **Markt-Schwankungen** — Erz-Preise ändern sich alle 5 Minuten (±20%). Spieler lernt zu timen.
9. **Tiefe Shops** — Unterirdische Tankstelle/Reparatur bei Row 200+. Teurer als Oberfläche, aber spart den Rückweg. Eleganter Fuel-Sink.
10. **Auftragssystem** — "Bringe 3 Goldium" → Bonus-$. Gibt Richtung und Extra-Belohnung.

---

## Trip-Kalkulation (Ist-Zustand)

### Früher Trip (Tier 1-2, Depth ~50)
- Tank: 15L → ~45s Flugzeit
- Cargo: 15kg
- Funde: 10 Ironium ($300) + 3 Bronzium ($180) + 2 Silverium ($200)
- **Ertrag: ~$680/Trip** → ~1.1 Trips für Tier-3-Upgrade ($750)

### Mittlerer Trip (Tier 3-4, Depth ~200)
- Tank: 40L → ~120s Flugzeit
- Cargo: 40kg
- Funde: 5 Goldium ($1,250) + 3 Platinium ($2,250) + Kleinzeug ($500)
- **Ertrag: ~$4,000/Trip** → 1.25 Trips für Tier-4 ($5,000)

### Später Trip (Tier 5-6, Depth ~400)
- Tank: 100L → ~300s Flugzeit
- Cargo: 120kg
- Funde: 2 Ruby ($40K) + 1 Diamond ($100K) + Kleinzeug ($10K)
- **Ertrag: ~$150,000/Trip** → 0.67 Trips für Tier-6 ($100K) ⚠️

→ **Ab Tier 5 verdient der Spieler schneller als er ausgeben kann.** Endgame-Sinks fehlen.
