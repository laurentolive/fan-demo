# Matrice de couverture des outils

fan-demo est le **test d'intégration de tous les outils eSquareSoft** et leur démonstration. Règle commune :
**toute fonctionnalité d'un outil a une ligne ici**, avec au moins un test automatique ; une fonctionnalité visible
a aussi un chapitre de démo. Une fonctionnalité non couverte par fan-demo n'est pas considérée comme livrée.
Une nouvelle fonctionnalité ajoute sa ligne dans la section de son outil.

La section e2Sim est vérifiée par [tests/test_matrix.py](../tests/test_matrix.py) : chaque test et chaque chapitre
cités existent (les selftests sont lus dans `E2SIM_ROOT/selftest`), chaque test porte une exigence. Les autres
sections seront vérifiées de la même façon quand leur partie du projet existera
([#11](https://github.com/laurentolive/fan-demo/issues/11)).

Colonnes : fonctionnalité, où dans le projet, test, chapitre de la démo e2Sim ([demo/DEMO.md](../demo/DEMO.md)).

## e2Sim

| Fonctionnalité e2Sim | Où dans l'exemple | Test | Démo |
|---|---|---|---|
| Superloop `main()` inchangée, yield sur HAL, `e2sim_idle()` | les deux firmwares | tous | 1 |
| Timer périodique + ISR, sections critiques | tick 1 ms, file d'événements boutons | T01 | 2 |
| Port `bit` in / out, verrou d'alimentation | boutons, LED, `SELF_HOLD` | T01, T04 | 1, 10 |
| Bloc framebuffer + PNG, comparaison à une référence | écran 128×64 | T02 | 2 |
| Attente active sur compteur HAL | délai d'init de l'écran | T02 | — |
| Port `stream` + modèle Python | `fan_hmi` seul, carte moteur = modèle `MotorBoard` | T03 | — |
| Bloc NVM persistant | dernière vitesse, compteur de minutes, CRC | T04 | 9, 10 |
| Port `xfer` synchrone | capteur de température SPI | T05 | 5 |
| Port `value` in (ADC brut) | batterie | T05 | 6 |
| Reset dans le process (watchdog) | capteur bloqué → reset WDT | T06 | 8 |
| Reset par nouveau process (`reset: process`) | reset WDT, NVM conservée, replay identique | T17 | — |
| Port `value` out (PWM) | duty lu par le modèle moteur | T07 | 4 |
| Port `event` (EXTI) | comparateur de courant → coupure immédiate | T08 | 7 |
| Multi-firmware (`system.yaml`) | `fan_hmi` ↔ `fan_motor`, le firmware remplace le modèle | T09 | 2 à 10 |
| Runs longs, temps accéléré | 10 min en quelques secondes | T00, T10 | 9 |
| Injection de fautes | trames corrompues, rotor bloqué, NVM corrompue, capteur absent | T03 à T08 | 5 à 8 |
| Forçage d'une entrée pilotée par un modèle (`force` / `release`) | `VBAT_ADC` forcé à 0 | T16 | 6 |
| Débit d'une ligne série (`baud:`) | `UART_DEBUG` à 9600, liaison moteur saturée à 300 | T18 | — |
| Index de `board.yaml` par enum ou `#define` (DWARF, `-g3`) | `UART_DEBUG` = `HAL_UART_TERMINAL` | T19 | — |
| Extraction des sources du build cible (`e2sim extract`) | makefile ARM factice, compile_commands.json | selftest (test_extract_from_make) | — |
| Fuzzing des parseurs de trames (`e2sim.fuzz`) | protocole IHM ↔ moteur, des deux côtés | T20 | — |
| Couverture de code gcov des tests système | `make coverage` : 93 % des lignes des deux firmwares | selftest (test_coverage_report) | — |
| Diagnostic « boucle sans yield point » avec la pile | firmware de selftest (`hang_here`) : bug volontaire hors de l'exemple | selftest (test_hang_report_sim) | — |
| Record / replay, sur l'autre architecture | enregistrement d'un scénario, rejoué | T12 | 11 |
| `sim.var()` / `set_var()` | variables des deux firmwares | tous | 3, 9 |
| Endpoint eScope intégré au host | `fan_hmi` sans code eScope | T14 | 3 |
| eScope embarqué + relais TCP d'un stream | `fan_motor` sur `UART_SCOPE` ; `UART_DEBUG` en terminal TCP | T15 | 3 |
| GUI web générée, API JSON, image du produit (`gui: skin`) | `system.yaml`, face avant de l'IHM | GUI | toute la démo |
| Rapport Excel exigences → tests | `pytest --e2sim-xlsx` | selftest (test_report_statuses) | — |
| Double architecture | campagne en `host32` et `host64` | CI (test-all) | — |
| Debug VS Code | `launch` sur un firmware, breakpoint conservé après reset | manuel | annexe du guide |
| Licence | dialogues, bandeau de la GUI, propriété JUnit | selftest (test_license_demonstration) | toute la démo |

## e2Unit

À construire (P1). Cibles : PC, FPB-RA4E1 (Cortex-M33, J-Link), Arduino Nano Every (AVR 8 bits, série).

| Fonctionnalité e2Unit | Où dans le projet | Test | Démo |
|---|---|---|---|
| Suite YAML, adapters générés depuis le prototype | `unit/` : crc16, fanProto | à faire | — |
| Adapter manuel (contexte, sorties multiples) | régulateur PI de la carte moteur | à faire | — |
| Stimuli (plage, aléatoire, segments) et tolérances | conversions tachymètre, VBAT, température | à faire | — |
| Runner `host` et `sim` (mailbox) | toutes les suites, CI hébergée | à faire | — |
| Runner `emu` (Cortex-M) | firmware ARM de l'IHM, CI hébergée | à faire | — |
| Runner `jlink`, cycles CPU, `--compare-host` | FPB-RA4E1 sur le banc | à faire | — |
| Runner série AVR (Arduino) | Arduino Nano Every ([e2Unit#1](https://github.com/laurentolive/e2Unit/issues/1)) | à faire | — |
| Rapports JUnit, Excel exigences, graphes | CI, import Polenta | à faire | — |

## eScope

| Fonctionnalité eScope | Où dans le projet | Test | Démo |
|---|---|---|---|
| Endpoint V3 du host e2Sim (TCP) | `fan_hmi` simulé, sans code eScope | e2Sim T14 | 3 |
| eScope embarqué, relais TCP d'e2Sim | `fan_motor` simulé, `UART_SCOPE` | e2Sim T15 | 3 |
| Transport RTT par J-Link | IHM sur FPB-RA4E1 | à faire | — |
| Transport série, Arduino (DebugScope) | moteur sur Nano Every ([eScope#4](https://github.com/laurentolive/eScope/issues/4)) | à faire | — |
| Plusieurs appareils simultanés | les deux cartes réelles | à faire | — |
| Symboles ELF par GDB, écriture de variables | consigne de vitesse, gains du PI | à faire | — |
| Automation REST en CI, analyse (dépassement, fréquence) | réponse indicielle de la régulation ([eScope#2](https://github.com/laurentolive/eScope/issues/2)) | à faire | — |

## Polenta

| Fonctionnalité Polenta | Où dans le projet | Test | Démo |
|---|---|---|---|
| Exigences SYS / SW / HW, paramètres | `polenta/` | à faire | — |
| Cas de test avec `automationId` = identifiant des tests | `polenta/` ↔ `@requirement` des tests | à faire | — |
| Import des résultats en CI | JUnit e2Unit / e2Sim / e2HIL ([polenta#129](https://github.com/laurentolive/polenta/issues/129)) | à faire | — |
| Contrôle de traçabilité en CI | [polenta#130](https://github.com/laurentolive/polenta/issues/130) | à faire | — |
| Baseline par version de suite | tag `suite-*` | à faire | — |

## e2HIL

| Fonctionnalité e2HIL | Où dans le projet | Test | Démo |
|---|---|---|---|
| `bench.yaml`, flash J-Link et Arduino, alimentation | banc de référence ([e2HIL#12](https://github.com/laurentolive/e2HIL/issues/12)) | à faire | — |
| Scénarios e2Sim rejoués sur banc | `tests/` (mêmes noms de signaux) | à faire | — |
| Mesures externes (latence de coupure sur faute courant) | `FAULT_IN` → `PWM_MOTOR` | à faire | — |
