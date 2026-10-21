# Démo e2Sim : le ventilateur à deux cartes

Durée : 15 à 20 minutes. Prérequis : `make` (les deux firmwares), un navigateur, et eScope pour le chapitre 3.

```
python tools/fetch.py           # outils aux versions de tools.lock.yaml
make demo                       # interactif : Entrée avant chaque chapitre, temps réel
make demo DEMO_OPTS="--auto"    # chapitres enchaînés (stand, boucle)
make demo-check                 # la même démo en test, accélérée, sans navigateur
```

La page `http://127.0.0.1:8080/` s'ouvre : une colonne par firmware (écran, touches, LEDs, sorties, terminaux,
paramètres des modèles). Le bandeau bleu affiche le chapitre en cours. On peut aussi agir à la main dans la
page entre deux chapitres.

## Message d'introduction

« Ce sont deux vrais firmwares, compilés depuis leurs sources sans aucune modification, qui tournent sur le PC.
Seule la couche basse de la HAL est remplacée. Autour d'eux, l'environnement (moteur, batterie, capteur) est
simulé en Python, au niveau des données de la HAL. Le temps est virtuel : tout est reproductible au bit près. »

## Chapitres

| # | Montrer | Dire |
|---|---|---|
| 1 | Bouton POWER, LED, terminal `UART_DEBUG` | Le `main()` du firmware démarre tel quel ; le verrou d'alimentation tient quand on relâche la touche. |
| 2 | Écran de l'IHM, `PWM_MOTOR`, vitesses | L'IHM envoie la consigne par UART, la carte moteur régule (PI) et renvoie la vitesse mesurée : deux firmwares reliés, comme sur le produit. |
| 3 | eScope connecté aux ports affichés dans la console | Chaque firmware a un endpoint eScope sans une ligne de code ajoutée ; la carte moteur embarque aussi eScope sur une UART, relayée en TCP. Tracer `motor.rpmMeas` et `motor.duty`. |
| 4 | Paramètre `load` du modèle moteur | Le modèle change la charge : le régulateur du firmware compense (le rapport cyclique monte). |
| 5 | Paramètre `temp_C` du capteur | Le capteur SPI répond de façon synchrone ; à 70 °C : OVER TEMP, moteur arrêté. |
| 6 | Paramètre `voltage_V` de la batterie, puis Force sur `VBAT_ADC` | Points ADC bruts : BAT LOW à 9,2 V. Injection de faute : l'entrée est forcée à 0 par-dessus le modèle (pont diviseur coupé), puis rendue au modèle. |
| 7 | Paramètre `blocked` du moteur | Le comparateur de courant déclenche une interruption externe : la coupure arrive dans la milliseconde, sans attendre la boucle de régulation. |
| 8 | Paramètre `stuck_busy` du capteur | Le firmware attend le capteur sans timeout : le watchdog le remet à zéro, dans le même process (le debugger resterait attaché). Défaut trouvé en simulation, sans banc. |
| 9 | Vitesse « max » | Le temps accéléré : le compteur de minutes de fonctionnement défile et se sauve en NVM. Une endurance de plusieurs heures se joue en minutes. |
| 10 | Appui long POWER | Sauvegarde, coupure, rallumage : les réglages sont relus de la NVM (fichier persistant). |
| 11 | Console | Toute la démo a été enregistrée ; elle est rejouée sans modèle ni script : mêmes sorties au bit près (et sur l'autre architecture). |

## eScope (chapitre 3)

Workspaces prêts : ouvrir `demo/fan-host32.escope` (ou `fan-host64.escope` pour `make TOOLCHAIN=host64`) dans
eScope, ou `eScope.exe demo\fan-host32.escope`. Ils contiennent trois devices, sur les ports fixes des `board.yaml` :

| Device | Port | Rôle |
|---|---|---|
| `Hmi` | 47710 | endpoint eScope du host pour `fan_hmi` |
| `Motor` | 47720 | endpoint eScope du host pour `fan_motor` |
| `MotorEmbedded` | 47721 | eScope embarqué dans `fan_motor`, sur son UART relayée en TCP |

Un seul tracé `Fan` réunit tout, pour suivre la chaîne consigne → régulation → mesure : `app.rpmTarget`,
`app.rpmMeasured` (HMI), `motor.rpmMeas`, `motor.duty` (Motor), les mêmes vus par l'eScope embarqué
(`embedded.motor.…`), `app.batPercent`, `app.temp_dC`. Protocole V3, symboles GDB sur la DLL de la toolchain
(`build/host32/…`), adresses 32 bits (64 bits pour `host64`), sampling 1 ms. Si un port est déjà pris, e2Sim en
prend un autre et l'affiche dans la console : corriger alors le device. L'axe de temps est juste même en vitesse « max » : les
trames arrivent simplement plus vite.

Le terminal `UART_DEBUG` de l'IHM est aussi sur un port fixe : 47711.

## Annexe : debugger

Dans VS Code (dossier racine de fan-demo) : tâche **e2sim connect**, puis configuration **fan_hmi (host32)**.
Poser un breakpoint dans `sensor_Process()`, déclencher le chapitre 8 depuis la page : le reset watchdog
recharge le firmware et le breakpoint est toujours là.
