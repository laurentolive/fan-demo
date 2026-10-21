# fan-demo

**English** | [Français](README.fr.md)

A two-board battery fan that is the **integration test and the demonstration of every eSquareSoft tool**:
[Polenta](https://github.com/laurentolive/polenta) (requirements), [e2Unit](https://github.com/laurentolive/e2Unit)
(unit tests), [e2Sim](https://github.com/laurentolive/e2Sim) (PC simulation),
[eScope](https://github.com/laurentolive/eScope) (observation), [e2HIL](https://github.com/laurentolive/e2HIL)
(real bench).

- **HMI board** `fan_hmi` on a Renesas **FPB-RA4E1** (Cortex-M33, J-Link): buttons, display, SPI temperature
  sensor, battery, settings in NVM, watchdog.
- **Motor board** `fan_motor` on an **Arduino Nano Every** (8-bit AVR, serial): 4-wire PC fan, PI speed control
  on the tachometer, protections, embedded eScope.
- The boards talk over a UART (frames with CRC). The application code is the same in simulation and on target.

| Documents | |
|---|---|
| [Project plan](docs/PLAN.md) (French) | hardware, layout, demo storyline, configuration management, CI, phases |
| [Coverage matrix](docs/MATRIX.md) (French) | every feature of every tool → where, test, demo |
| [e2Sim demo guide](demo/DEMO.md) | chapter by chapter |
| [Issues](https://github.com/laurentolive/fan-demo/issues) | work in progress |

Status: the simulation part (e2Sim) is complete; the real-board ports, the e2Unit suites, the Polenta project
and the bench are coming (see the plan).

## Quick start

Requirements: those of e2Sim (Windows, Python 3.10+ with `pyyaml` and `pytest`, GNU make, MSYS2 mingw32 / ucrt64
gcc and gdb, an `e2sim_toolchains.yaml`); see the e2Sim README.

```
python tools/fetch.py   # tools at the versions of tools.lock.yaml, into .tools/
make test-all           # e2Sim campaign on host32 and host64
make demo               # demonstration in the web GUI
make demo-check         # the demonstration as a test
make E2SIM_ROOT=../e2Sim test   # against a working copy of e2Sim
```

## Tool versions

[`tools.lock.yaml`](tools.lock.yaml) pins the tool versions validated together; a `suite-<version>` tag of this
repository certifies a combination. The CI also runs the project against the main branch of every tool and
proposes the update of the file by a pull request.

## License

MIT ([LICENSE.md](LICENSE.md)). The tools have their own licenses.
