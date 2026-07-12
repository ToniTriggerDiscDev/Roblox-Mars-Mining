# Pacing-Simulator für Mars Miner 2D.
# Simuliert einen typischen Spieler über Stunden (Trips, Käufe, Funde) und
# druckt eine Meilenstein-Timeline. Werte MÜSSEN mit GameConfig synchron
# gehalten werden (Quelle: Motherload-Referenz-Port).
#
# Usage: python sim_progression.py [stunden]
import sys

# === Spiegel von GameConfig (bei Änderungen dort: hier nachziehen!) ===
HEIGHT = 600
DIG_BASE = 0.4
BS = 8

ORES = {  # code: (value, weight) — gestauchte Kurve (2026-07-12, Option B)
    6: (30, 1), 7: (60, 1), 8: (100, 1), 9: (250, 2), 10: (700, 3),
    11: (1500, 4), 12: (3200, 6), 13: (6000, 8), 14: (25000, 10), 15: (120000, 12),
}
UPGRADES = {
    # (Kosten pro Tier ab Tier2, Effekte pro Tier ab Tier1)
    "Drill":  ([750, 2000, 5000, 20000, 100000, 500000], [2, 2.8, 4, 5, 7, 9.5, 12]),
    "Cargo":  ([750, 2000, 5000, 20000, 100000], [7, 15, 25, 40, 70, 120]),
    "Fuel":   ([750, 2000, 5000, 20000, 100000, 500000], [10, 15, 25, 40, 60, 100, 150]),
    "Engine": ([750, 2000, 5000, 20000, 100000, 500000], [6, 6.4, 6.8, 7.2, 7.6, 8, 8.4]),
}
FUEL_FLY = 0.33
FUEL_IDLE = 0.08
FUEL_PRICE = 1  # $/L
BIOMES = [("REGOLITH", 0), ("SEDIMENT BASIN", 121), ("CRYSTAL CAVERNS", 251),
          ("SCORCHED DEPTHS", 381), ("THE ANOMALY", 501)]
ARTIFACT_P = 0.2 * 0.2 * 0.2 * 0.25   # Treasure-Zweig der Gen (nur y>80)
ARTIFACT_AVG_VALUE = 12000            # grobe Mischung der 4 Typen (identifiziert)


def depth_mod(row):
    return 0.1 + 0.9 * (1 - row / HEIGHT)


def dig_time(row, drill):
    speed = DIG_BASE * drill * depth_mod(row) * BS  # studs/s
    return BS / speed


def ore_ev(row):
    """Erwartungswert (value, weight) PRO GEGRABENEM Block (inkl. Nicht-Erz)."""
    rng = row // 65 + 2
    def pool(base):
        vals = [ORES.get(min(r + base, 15), (0, 0)) for r in range(rng)]
        v = sum(x[0] for x in vals) / rng
        w = sum(x[1] for x in vals) / rng
        return v, w
    v6, w6 = pool(6)
    v7, w7 = pool(7)
    v8, w8 = pool(8)
    # Gen-Verzweigung: 20% Erz; davon 4/5 Basis-Pool, 1/5*4/5 Mittel, Rest Top
    p = 0.2
    v = p * (0.8 * v6 + 0.16 * v7 + 0.04 * v8)
    w = p * (0.8 * w6 + 0.16 * w7 + 0.04 * w8)
    return v, w


def simulate(hours=10.0, verbose=True):
    t = 0.0  # Sekunden
    money = 20
    tiers = {k: 1 for k in UPGRADES}
    timeline = []
    biome_seen = {"REGOLITH"}
    artifacts = 0
    blocks_total = 0
    next_report = 0

    def eff(cat):
        return UPGRADES[cat][1][tiers[cat] - 1]

    def log(evt):
        timeline.append((t, evt))

    while t < hours * 3600:
        drill = eff("Drill")
        cargo_cap = eff("Cargo")
        tank = eff("Fuel")
        engine = eff("Engine")

        # Ziel-Tiefe: tiefste Row, deren Rundreise ins Fuel passt (85% Puffer)
        best_row = 10
        for row in range(20, HEIGHT - 12, 10):
            travel = 2 * (row / engine)              # s (rauf+runter, tiles/s)
            v, w = ore_ev(row)
            blocks_for_cargo = cargo_cap / max(w, 1e-9)
            digt = blocks_for_cargo * dig_time(row, drill)
            fuel_need = travel * FUEL_FLY + digt * FUEL_IDLE
            if fuel_need <= tank * 0.85:
                best_row = row
            else:
                break

        row = best_row
        v, w = ore_ev(row)
        blocks = cargo_cap / max(w, 1e-9)
        digt = blocks * dig_time(row, drill)
        travel = 2 * (row / engine)
        trip_time = digt + travel + 20  # +20s Verkauf/Tanken/Umschauen
        trip_income = v * blocks
        fuel_cost = (travel * FUEL_FLY + digt * FUEL_IDLE) * FUEL_PRICE

        # Artefakte (nur unter Row 80)
        if row > 80:
            exp_art = blocks * ARTIFACT_P
            artifacts += exp_art
            if int(artifacts) > int(artifacts - exp_art):
                log(f"ARTEFAKT #{int(artifacts)} gefunden (Row ~{row})")
                money += ARTIFACT_AVG_VALUE

        t += trip_time
        money += trip_income - fuel_cost
        blocks_total += blocks

        # Biom-Meilensteine
        for name, frm in BIOMES:
            if row >= frm and name not in biome_seen:
                biome_seen.add(name)
                log(f"NEUE ZONE: {name} (Row {row})")

        # Kauf-Strategie: billigstes verfügbares Next-Tier
        bought = True
        while bought:
            bought = False
            options = []
            for cat, (costs, _) in UPGRADES.items():
                nxt = tiers[cat] + 1
                if nxt <= len(costs) + 1:
                    cost = costs[nxt - 2]
                    options.append((cost, cat))
            options.sort()
            for cost, cat in options:
                if money >= cost:
                    money -= cost
                    tiers[cat] += 1
                    log(f"UPGRADE {cat} -> Tier {tiers[cat]} (${cost})")
                    bought = True
                    break

        if all(tiers[c] == len(UPGRADES[c][1]) for c in UPGRADES):
            log("ALLE UPGRADES MAX -> Endgame-Wand (Prestige-Punkt)")
            break

    if verbose:
        print(f"{'Zeit':>8}  Ereignis")
        print("-" * 60)
        last = 0
        for tt, evt in timeline:
            gap = (tt - last) / 60
            mark = "  <<< LÜCKE" if gap > 7 and tt < 2 * 3600 else ""
            print(f"{tt/60:7.1f}m  {evt}{mark}")
            last = tt
        print("-" * 60)
        print(f"Gesamt: {t/3600:.1f}h | Blöcke: {blocks_total:.0f} | Artefakte: {artifacts:.1f}")
    return timeline


def trip_stats(tiers):
    """(income/min, best_row) für einen gegebenen Tier-Stand."""
    drill = UPGRADES["Drill"][1][tiers["Drill"] - 1]
    cargo_cap = UPGRADES["Cargo"][1][min(tiers["Cargo"], len(UPGRADES["Cargo"][1])) - 1]
    tank = UPGRADES["Fuel"][1][tiers["Fuel"] - 1]
    engine = UPGRADES["Engine"][1][tiers["Engine"] - 1]
    best_row = 10
    for row in range(20, HEIGHT - 12, 10):
        travel = 2 * (row / engine)
        v, w = ore_ev(row)
        blocks = cargo_cap / max(w, 1e-9)
        digt = blocks * dig_time(row, drill)
        if travel * FUEL_FLY + digt * FUEL_IDLE <= tank * 0.85:
            best_row = row
        else:
            break
    v, w = ore_ev(best_row)
    blocks = cargo_cap / max(w, 1e-9)
    digt = blocks * dig_time(best_row, drill)
    travel = 2 * (best_row / engine)
    trip_time = digt + travel + 20
    income = v * blocks - (travel * FUEL_FLY + digt * FUEL_IDLE) * FUEL_PRICE
    return income / (trip_time / 60), best_row


def nice(x):
    """auf 2 signifikante Stellen runden (kaufmännisch hübsch)."""
    import math
    if x <= 0:
        return 0
    mag = 10 ** (math.floor(math.log10(x)) - 1)
    return int(round(x / mag) * mag)


def calibrate():
    """Ring-Zeit-Ziele -> Kostentabelle. Ring L = alle 4 Kategorien auf Tier L
    kaufen. Sim spielt ~2.5x schneller als echte Spieler (perfektes Spiel)."""
    RING_MINUTES = {2: 8, 3: 15, 4: 30, 5: 50, 6: 80, 7: 110}  # Sim-Minuten
    cats = 4
    proposed = {c: [] for c in UPGRADES}
    print(f"{'Ring':>4} {'Row':>5} {'$/min':>9}  Kosten/Kategorie")
    for L in range(2, 8):
        tiers = {c: min(L - 1, len(UPGRADES[c][1])) for c in UPGRADES}
        ipm, row = trip_stats(tiers)
        cost = nice(RING_MINUTES[L] / cats * ipm)
        print(f"{L:>4} {row:>5} {ipm:>9.0f}  ${cost}")
        for c in UPGRADES:
            if L <= len(UPGRADES[c][1]):
                proposed[c].append(cost)
    print("\nVorgeschlagene Kostenleiter (alle Kategorien):")
    print("  " + " / ".join(f"${c}" for c in proposed["Drill"]))
    # Verifikation: Sim mit neuen Kosten
    for c in UPGRADES:
        costs, effects = UPGRADES[c]
        UPGRADES[c] = (proposed[c][:len(costs)], effects)
    print("\n=== Verifikations-Lauf mit kalibrierten Kosten ===")
    simulate(24)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "calibrate":
        calibrate()
    else:
        hours = float(sys.argv[1]) if len(sys.argv) > 1 else 12
        simulate(hours)
