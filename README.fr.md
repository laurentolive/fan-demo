# fan-demo

[English](README.md) | **Français**

Un ventilateur sur batterie à deux cartes, qui sert de **test d'intégration et de démonstration de tous les
outils eSquareSoft** : [Polenta](https://github.com/laurentolive/polenta) (exigences),
[e2Unit](https://github.com/laurentolive/e2Unit) (tests unitaires), [e2Sim](https://github.com/laurentolive/e2Sim)
(simulation PC), [eScope](https://github.com/laurentolive/eScope) (observation),
[e2HIL](https://github.com/laurentolive/e2HIL) (banc réel).

- **Carte IHM** `fan_hmi` sur Renesas **FPB-RA4E1** (Cortex-M33, J-Link) : boutons, écran, capteur de
  température SPI, batterie, réglages en NVM, watchdog.
- **Carte moteur** `fan_motor` sur **Arduino Nano Every** (AVR 8 bits, série) : ventilateur PC 4 fils,
  régulation PI sur le tachymètre, protections, eScope embarqué.
- Les deux cartes dialoguent par UART (trames à CRC). Le code applicatif est le même en simulation et sur cible.

| Documents | |
|---|---|
| [Plan du projet](docs/PLAN.md) | matériel, organisation, fil rouge de la démo, gestion de configuration, CI, phasage |
| [Matrice de couverture](docs/MATRIX.md) | chaque fonctionnalité de chaque outil → où, test, démo |
| [Guide de la démo e2Sim](demo/DEMO.md) | texte et manipulations, chapitre par chapitre |
| [Issues](https://github.com/laurentolive/fan-demo/issues) | travail en cours |

État : la partie simulation (e2Sim) est complète ; les ports sur cartes réelles, les suites e2Unit, le projet
Polenta et le banc arrivent (voir le plan).

## Démarrage

Prérequis : ceux d'e2Sim (Windows, Python 3.10+ avec `pyyaml` et `pytest`, GNU make, MSYS2 mingw32 / ucrt64 avec
gcc et gdb, un `e2sim_toolchains.yaml`) ; voir le README d'e2Sim.

```
python tools/fetch.py   # outils aux versions de tools.lock.yaml, dans .tools/
make                    # firmwares simulés (toolchain par défaut)
make test-all           # campagne e2Sim en host32 et host64
make demo               # démonstration dans la GUI web, chapitre par chapitre
make demo-check         # la démo en test
make coverage           # couverture des firmwares : out/coverage/index.html
make E2SIM_ROOT=../e2Sim test   # avec une copie de travail d'e2Sim
```

## Versions des outils

[`tools.lock.yaml`](tools.lock.yaml) fixe les versions des outils validées ensemble ; un tag `suite-<version>`
de ce dépôt certifie une combinaison. La CI rejoue aussi le projet contre la branche principale de chaque outil
et propose la mise à jour du fichier. Détails : [plan §6](docs/PLAN.md#6-gestion-de-configuration-entre-dépôts).

| Suite | e2Sim | e2Unit | eScope | Polenta | e2HIL |
|---|---|---|---|---|---|
| 0.1.0 (en cours) | `aa7a9e5` | `e168926` | v1.2.0 | v0.1.2 | `df32c8a` |

## Arborescence

```
fan_hmi/  fan_motor/  common/   applications et protocole (passent sous app/ avec les ports réels)
hal/            en-têtes HAL
port/e2sim/     HAL sur e2sim.h (simulation)  ← modèle de portage
escope/         code cible eScope V3
sim/            board.yaml, system.yaml, modèles Python
tests/          tests système e2Sim, images de référence, matrice
demo/           démonstration
tools/          fetch.py
docs/           plan, matrice de couverture
```

## Licence

MIT ([LICENSE.md](LICENSE.md)) : copiez, adaptez, livrez. Les outils ont leur propre licence.
