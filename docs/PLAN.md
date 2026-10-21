# fan-demo — Plan du projet

Version 0.1 (2026-10-21). Le travail restant est suivi dans les
[issues](https://github.com/laurentolive/fan-demo/issues).

## 1. Objectifs

Un seul projet, simple, qui sert à deux choses :

1. **Le test d'intégration de tous les outils eSquareSoft** (Polenta, e2Unit, e2Sim, eScope, e2HIL) : chaque
   fonctionnalité de chaque outil a une ligne dans la [matrice de couverture](MATRIX.md) et au moins un test.
   Une fonctionnalité non couverte ici n'est pas livrée.
2. **La démonstration de ces outils**, ensemble, sur un produit crédible : du cahier des charges aux cartes
   réelles.

Tout ce qui concerne le projet vit dans ce dépôt (code, exigences, tests, banc, démo). Les dépôts des outils
n'en ont pas de copie.

## 2. Produit : un ventilateur sur batterie à deux cartes

```
 ┌──────────── fan_hmi ────────────┐   UART_LINK    ┌────────── fan_motor ──────────┐
 │ FPB-RA4E1 (Cortex-M33 + FPU)    │◄──────────────►│ Arduino Nano Every (AVR 8 bits)│
 │ BTN_POWER, BTN_PLUS, BTN_MINUS  │  consigne,     │ PWM_MOTOR 25 kHz → ventilateur │
 │ LED, SELF_HOLD, MOTOR_EN        │  état, défauts │ TACHO (capture) ← ventilateur  │
 │ VBAT_ADC (pont diviseur)        │  (trames CRC)  │ CURRENT_ADC ← shunt            │
 │ TEMP_SPI capteur de température │                │ FAULT_IN ← comparateur (IRQ)   │
 │ LCD TFT SPI, NVM (data flash)   │                │ ENABLE ← MOTOR_EN, WDT         │
 │ UART_DEBUG ; eScope en RTT      │                │ UART_SCOPE : eScope (USB)      │
 └──────── J-Link OB (SWD) ────────┘                └──────── USB série ────────────┘
```

Le comportement est celui de la simulation : marche / arrêt, vitesses 1 à 5, régulation PI sur le tachymètre,
protections (surintensité matérielle et logicielle, rotor bloqué, surchauffe, batterie basse), réglages
sauvegardés, watchdog.

## 3. Matériel

| | Carte IHM | Carte moteur |
|---|---|---|
| Carte | **Renesas FPB-RA4E1** | **Arduino Nano Every** |
| Cœur | Cortex-M33 avec FPU, 32 bits | ATmega4809, AVR 8 bits (`int` sur 16 bits) |
| Interface outil | **J-Link** (OB intégré, SWD) : flash, e2Unit `jlink`, eScope RTT | **série** (USB) : flash, e2Unit série, eScope |
| Pourquoi | déjà supportée par e2Unit (`boards/ra4e1`) et eScope ; RAM suffisante pour le framebuffer | Arduino est une cible clé des outils ; plusieurs USART (liaison IHM + eScope), ce que la Nano classique n'a pas |

Deux cœurs très différents (32 bits avec FPU contre 8 bits) : les écarts de compilation, de taille de type et
de performance que les outils doivent révéler apparaissent naturellement.

Périphériques (nomenclature indicative, choix définitif dans une issue) :
- ventilateur PC **4 fils 12 V** : entrée PWM 25 kHz et sortie tachymètre intégrées, pas de pont en H ;
- MOSFET d'alimentation du ventilateur (`ENABLE`), shunt + comparateur (LM393) vers une broche d'interruption
  (`FAULT_IN`), la mesure de courant sur l'ADC ;
- écran TFT SPI (ST7735), la taille de l'écran simulé est alignée sur celle de l'écran retenu ;
- capteur de température SPI, 3 boutons, LED, pont diviseur sur `VBAT_ADC` ;
- alimentation 12 V de laboratoire (la « batterie »).

## 4. Organisation du dépôt

```
app/ (à venir)  fan_hmi/, fan_motor/, common/ : code applicatif identique sur PC et sur cible
hal/            en-têtes HAL génériques (halGpio, halAdc, halPwm, ...)
port/e2sim/     HAL sur e2sim.h (simulation PC)
port/ra4e1/     HAL réelle de l'IHM (à venir)
port/arduino/   HAL réelle de la carte moteur, sur le cœur Arduino (à venir)
escope/         code cible eScope V3
sim/            board.yaml, system.yaml, modèles Python
tests/          tests système e2Sim (T00..T20), image de référence, matrice
unit/           suites e2Unit (à venir)
hil/            bench.yaml et scénarios e2HIL (à venir)
scope/          configurations et scripts eScope (à venir)
polenta/        projet Polenta : exigences, cas de test, campagnes (à venir)
demo/           démonstration
tools/          fetch.py : récupération des outils aux versions de tools.lock.yaml
```

Aujourd'hui `fan_hmi/`, `fan_motor/` et `common/` sont à la racine (reprise de l'exemple d'e2Sim). Ils passent
sous `app/` avec les premiers ports réels.

**Zéro impact sur l'application.** Seuls les `port/*` changent d'une cible à l'autre. Pour l'Arduino, le
`main()` de l'application est renommé à la compilation et appelé depuis `setup()`, comme e2Sim le fait avec
`e2sim_app_main`.

## 5. Le fil rouge de la démonstration

Une exigence suivie de bout en bout :

> SYS : « Si le courant moteur dépasse I_max, le moteur est coupé en moins de 1 ms. »

| Étape | Outil | Ce qu'on montre |
|---|---|---|
| Exigence, cas de test, campagne | **Polenta** (+ MCP) | rédaction assistée, liens, revue, baseline |
| Conversion du seuil, filtre du courant, PI, CRC | **e2Unit** | host, sim, emu, puis cible (J-Link avec cycles, série sur l'Arduino), comparaison bit à bit avec le PC |
| Rotor bloqué → comparateur → coupure | **e2Sim** | logique, injection de fautes, temps accéléré, deux firmwares reliés |
| Même scénario sur les vraies cartes | **e2HIL** | la faute injectée par le banc, latence mesurée par le banc |
| Vitesse, courant, PWM sur les deux cartes | **eScope** | RTT + série en même temps, analyse automatique |
| Retour des résultats | **Polenta** | import JUnit, matrice de couverture |

La démo e2Sim actuelle (`make demo`, 11 chapitres) est le chapitre « simulation » de cette démo globale.

## 6. Gestion de configuration entre dépôts

Les outils évoluent séparément ; ce dépôt dit **quelles versions fonctionnent ensemble**.

- [`tools.lock.yaml`](../tools.lock.yaml) fige la version de chaque outil (tag quand l'outil a des releases,
  sinon un commit) ; `python tools/fetch.py` les installe dans `.tools/` et écrit `.tools/resolved.yaml`
  (versions réellement testées, jointes aux résultats de la CI).
- **Tag `suite-<version>`** de fan-demo : certificat « ces versions des outils fonctionnent ensemble ».
  Le tableau de compatibilité (README, page téléchargements du site) est tiré des tags `suite-*`.
- **Deux voies de CI** :
  - *figée* : les versions du fichier. Elle doit toujours passer ;
  - *suivante* : la branche principale de chaque outil (`--next`). Chaque nuit, si elle passe, une pull request
    met à jour `tools.lock.yaml` ; si elle casse, on sait quel outil a cassé quoi, avant sa release.
- **Vérification des releases d'outils** : le workflow de release d'un outil envoie un `repository_dispatch`
  (`tool-release`, `{tool, ref}`) ; fan-demo rejoue la voie figée avec cet outil à ce tag
  (`fetch.py --set outil=tag`).
- **Versions d'interface** vérifiées à l'exécution par chaque outil (ABI de `e2sim.h`, mailbox d'e2Unit,
  protocole eScope V3, protocole du boîtier e2HIL) : un écart donne une erreur claire.
- En développement, une copie de travail remplace un outil : `make E2SIM_ROOT=../e2Sim`.

## 7. Intégration continue (GitHub Actions)

Gratuite pour un dépôt public (runners hébergés, Windows compris).

| Niveau | Où | Quand | Contenu |
|---|---|---|---|
| Outils | dépôt de chaque outil, runners hébergés | push | selftests de l'outil |
| fan-demo sans matériel | runners hébergés | push, PR, nuit, release d'un outil | campagne e2Sim host32 + host64, démo testée, couverture ; build ARM et AVR, e2Unit host / sim / emu, contrôle Polenta (à venir) |
| fan-demo sur banc | runner auto-hébergé `hil` (e2HIL) | push sur `main`, tags, manuel, nuit | flash, e2Unit sur cible, scénarios e2HIL, eScope en automation (plus tard) |

Dépôt public : **aucun job de banc sur une PR venant d'un fork** (exécution de code sur la machine du banc).
Les jobs de banc ne se déclenchent que sur `main`, les tags, à la main ou la nuit, dans un *environment*
protégé.

## 8. Phasage

| Phase | Contenu |
|---|---|
| P0 (fait) | dépôt, reprise de l'exemple d'e2Sim avec son historique, `tools.lock.yaml` + `fetch.py`, CI voies figée et suivante, matrice de couverture |
| P1 | choix du matériel, ports RA4E1 et Arduino, build ARM / AVR en CI, suites e2Unit, projet Polenta, configurations eScope |
| P2 | démo globale, import des résultats dans Polenta, réception des releases d'outils, tableau de compatibilité |
| P3 | banc e2HIL : flash, scénarios sur cartes réelles, eScope en CI |
