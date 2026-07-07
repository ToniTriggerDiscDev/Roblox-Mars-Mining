# Mars Miner 2D — Roadmap

2D-Mining-Game auf Roblox, inspiriert von Motherload. Die Referenz ist nur ein grober Leitfaden —
das Spiel soll Eigenwert und Originalität haben, kein Klon sein. Eigene Art (Pixel-Sprites),
eigene Systeme (Artefakt-Identifikation, Sammlungen), bewusste Abweichungen wo sie Mehrwert bringen.

## Status (erledigt)

- **Core**: Terrain-Generation (36×600 Grid), Grid-Mining (Server-Tween), Fuel/Hull/Cargo,
  Fallschaden, Tiefen-abhängige Bohrgeschwindigkeit, Tod + Respawn
- **Surface**: Fuel Station, Mineral Buyer, 6 Upgrade-Pedestals, Item Shop (Items + Repair)
- **Save-System**: DataStore (Money/Upgrades/Items/Collection), Auto-Save, BindToClose
  (echter DataStore-Test steht aus bis Publish)
- **Artefakt-Sammlungen**: 4 Sets × 5 Pieces, gewichtete Drops (seltene Pieces wertvoller,
  0.5–2.8× Basiswert, ±10% Jitter), Set-Bonus bei Komplettierung, Collection-UI (Taste C)
- **Visuals**: 95 eigene prozedurale Pixel-Texturen (Varianten-Pools + Deko-Overlays),
  texturierte Rückwand mit ~2100 Deko-Decals, Tiefen-Farbverlauf, Galaxy-Skybox,
  globale Beleuchtung (kein Sonnenlicht — Untergrund-Illusion)
- **Juice**: Dig-Partikel + physische Brocken pro Dig, Score-Popups mit Tiers
  (Funken, Shine-Sweep, Shockwave-Ring, Regenbogen-Text-Explosion)

## Als Nächstes

### 1. Artefakt-Identifikation (bewusste Abweichung von der Referenz)
- Ausgraben: kein Geld, kein Roll — Popup „ARTEFAKT ???", Spieler trägt unidentifizierte
  Artefakte (kein Cargo-Gewicht), **Verlust bei Pod-Tod** (Risk/Reward)
- An der Oberfläche: Identifikations-Station — erst hier Piece-Roll, Auszahlung, Set-Bonus
- Reveal-UI: rotierendes 3D-Modell im ViewportFrame (Bewunderungsmoment)
- Benötigt Verbrauchs-Item „Identification Kit" aus dem Item Shop
- Effekt: alles Geld kommt an der Oberfläche an (konsistent), Loot-Spannung beim Graben

### 2. Item-Shop ausmisten
- Redundante Referenz-Items streichen (zwei Teleporter → einer; Reserve Fuel Tank /
  Dynamite-vs-C4 Kandidaten), Identification Kit neu

### 3. Juice-Runde 3
- Arcade-Font für alle Popups
- Screen-Space-Slam-Popup (oben-mittig) für große Funde, Squash-Overshoot
- Kamera-Shake bei Riesenfunden (subtil, ~0.2s)
- Money-Tick: HUD-Counter pulsiert + zählt hoch bei jeder Geld-Erhöhung
  (Erz tickt beim Verkauf, Artefakte bei Identifikation)
- Afterimage-Trails an aufsteigenden Popups

### 4. Shops fertigstellen
- Alle Upgrades in Shops verfügbar machen
- Danach: Shop-Gebäude-Modelle → Pod/Player-Modell (Blender, low-poly flat-shaded
  passend zur Pixel-Ästhetik) → Shop UI/UX zuletzt

### 5. Journal-UI (wartet auf Material)
- Collection-UI als Expeditions-Journal mit analogen Scan-Assets
  (Papier/Tinte-Fotos → Cutout-Pipeline → Upload)

### 6. Ads & Brand-Deals vorbereiten
- Welt mit fiktiven Marken-Äquivalenten bauen (z.B. „Apex Drones"-Stil auf Equipment/Shops)
  als Proof-of-Concept für echte Brand-Integrationen
- Video-Screens/Billboards an der Mars-Basis für **Roblox Immersive Ads**
  (Ad Manager füllt automatisch, Bezahlung pro Impression)

## Backlog
- Sounds (Drill-Loop, Clink bei unbohrbaren Blöcken)
- Instanzierte Welten pro Spieler
- grass_top-Look an der Oberfläche überarbeiten; Farn-Deko liest sich als Tanne
- Echter DataStore-Test nach Publish
- 20 Platzhalter-Artefaktmodelle durch eigene ersetzen
