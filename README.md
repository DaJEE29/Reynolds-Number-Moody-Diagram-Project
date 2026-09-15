# Pipe Flow / Moody Chart Calculator

Compute Reynolds number, flow regime, Darcy friction factor, and pressure
drop for flow in a circular pipe, and plot the result on a Moody-style
chart.

## Features

- Reynolds number and laminar / transitional / turbulent classification
- Darcy friction factor via the Hagen-Poiseuille relation (laminar) or the
  Colebrook equation solved by fixed-point iteration (turbulent)
- Darcy-Weisbach pressure drop
- Moody chart plotting with several relative-roughness curves and a
  "complete turbulence" boundary line
- Interactive or fully flag-driven CLI

## Install

```bash
pip install -r requirements.txt
```

## Usage

Interactive (prompts for each value):

```bash
python cli.py
```

Non-interactive, via flags:

```bash
python cli.py --rho 1000 --v 2 --D 0.05 --mu 0.001 --L 10 --epsilon 0.00015 --no-plot
```

| Flag         | Meaning                        |
|--------------|---------------------------------|
| `--rho`      | Fluid density (kg/m^3)          |
| `--v`        | Velocity (m/s)                  |
| `--D`        | Pipe diameter (m)                |
| `--mu`       | Dynamic viscosity (Pa*s)         |
| `--L`        | Pipe length (m)                  |
| `--epsilon`  | Pipe roughness (m)               |
| `--no-plot`  | Skip showing the Moody chart     |

## Tests

```bash
pytest
```

## Project layout

- `pipe_flow.py` - core fluid-mechanics calculations
- `moody_chart.py` - Moody chart data generation and plotting
- `cli.py` - command-line interface
- `test_pipe_flow.py` - unit tests
