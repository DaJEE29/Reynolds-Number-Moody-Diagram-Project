"""Command-line interface for the pipe-flow / Moody chart calculator.

Run interactively:
    python cli.py

Or non-interactively with flags (skips prompts for any value supplied):
    python cli.py --rho 1000 --v 2 --D 0.05 --mu 0.001 --L 10 --epsilon 0.00015 --no-plot
"""

from __future__ import annotations

import argparse

from moody_chart import MoodyChart
from pipe_flow import full_pipe_calc


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Compute pipe flow friction factor and pressure drop.")
    parser.add_argument("--rho", type=float, default=None, help="Fluid density (kg/m^3)")
    parser.add_argument("--v", type=float, default=None, help="Velocity (m/s)")
    parser.add_argument("--D", type=float, default=None, help="Pipe diameter (m)")
    parser.add_argument("--mu", type=float, default=None, help="Dynamic viscosity (Pa*s)")
    parser.add_argument("--L", type=float, default=None, help="Pipe length (m)")
    parser.add_argument("--epsilon", type=float, default=None, help="Pipe roughness (m)")
    parser.add_argument("--no-plot", action="store_true", help="Skip showing the Moody chart")
    return parser.parse_args(argv)


def prompt_for_missing(args: argparse.Namespace) -> None:
    """Fill in any argument left as None by prompting the user for it."""
    prompts = {
        "rho": "Enter fluid density (kg/m^3): ",
        "v": "Enter velocity (m/s): ",
        "D": "Enter pipe diameter (m): ",
        "mu": "Enter dynamic viscosity (Pa*s): ",
        "L": "Enter pipe length (m): ",
        "epsilon": "Enter pipe roughness (m): ",
    }
    for name, prompt in prompts.items():
        if getattr(args, name) is None:
            setattr(args, name, float(input(prompt)))


def run_once(args: argparse.Namespace) -> None:
    result = full_pipe_calc(args.rho, args.v, args.D, args.mu, args.L, args.epsilon)
    print(result)

    if not args.no_plot:
        chart = MoodyChart(D=args.D)
        chart.plot(user_Re=result.Re, user_f=result.f)


def main(argv: list[str] | None = None) -> None:
    first_args = parse_args(argv)
    # If every value was already supplied on the command line, run once and exit
    # instead of dropping into the interactive "run again?" loop.
    interactive = any(
        getattr(first_args, name) is None
        for name in ("rho", "v", "D", "mu", "L", "epsilon")
    )
    first_pass = True

    while True:
        args = first_args if first_pass else parse_args(None)
        first_pass = False

        try:
            prompt_for_missing(args)
        except ValueError:
            print("Invalid input - please enter numbers only.")
            continue

        try:
            run_once(args)
        except ValueError as exc:
            print(f"Invalid input - {exc}")
            continue
        except RuntimeError as exc:
            print(f"Calculation warning - {exc}")

        if not interactive:
            break

        again = input("Run again? (y/n): ")
        if again.lower() != "y":
            break


if __name__ == "__main__":
    main()
