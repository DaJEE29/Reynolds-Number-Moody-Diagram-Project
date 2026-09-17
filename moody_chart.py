"""Moody chart generation and plotting for pipe friction factor vs Reynolds number."""

from __future__ import annotations

import math
from dataclasses import dataclass, field

import matplotlib.pyplot as plt
import numpy as np

from pipe_flow import (
    LAMINAR_LIMIT,
    TURBULENT_LIMIT,
    friction_factor_colebrook,
    friction_factor_laminar,
)

DEFAULT_EPSILON_VALUES: tuple[float, ...] = (0.05, 0.02, 0.01, 0.005, 0.001, 0.0001, 0.00001)


@dataclass
class MoodyChart:
    """Precomputed Moody chart data for a given pipe diameter and set of
    relative-roughness curves.
    """

    D: float
    epsilon_values: tuple[float, ...] = DEFAULT_EPSILON_VALUES
    re_min: float = TURBULENT_LIMIT
    re_max: float = 1e8
    n_points: int = 50

    Re_values: np.ndarray = field(init=False)
    Re_values_laminar: np.ndarray = field(init=False)
    f_values_laminar: list[float] = field(init=False)
    all_f_values: list[list[float]] = field(init=False)
    boundary_points: list[tuple[float, float]] = field(init=False)

    def __post_init__(self) -> None:
        self.Re_values = np.logspace(np.log10(self.re_min), np.log10(self.re_max), self.n_points)
        self.Re_values_laminar = np.logspace(np.log10(500), np.log10(LAMINAR_LIMIT), 30)
        self.f_values_laminar = [friction_factor_laminar(Re) for Re in self.Re_values_laminar]

        self.all_f_values = [
            [friction_factor_colebrook(Re, self.D, eps_rel * self.D) for Re in self.Re_values]
            for eps_rel in self.epsilon_values
        ]

        self.boundary_points = self._find_boundary_points()

    def _find_boundary_points(self, tolerance: float = 0.01) -> list[tuple[float, float]]:
        """Find the approximate Re at which each roughness curve flattens out
        into the complete-turbulence asymptote.
        """
        points = []
        for eps_rel, f_curve in zip(self.epsilon_values, self.all_f_values):
            eps_actual = eps_rel * self.D
            rhs = -2 * math.log10((eps_actual / self.D) / 3.7)
            f_infinity = 1 / (rhs ** 2)

            for Re, f in zip(self.Re_values, f_curve):
                if abs(f - f_infinity) / f_infinity < tolerance:
                    points.append((Re, f))
                    break
        return points

    def plot(self, user_Re: float | None = None, user_f: float | None = None, show: bool = True):
        """Render the Moody chart. Returns the (fig, ax) pair for further customization."""
        fig, ax = plt.subplots(figsize=(12, 7))

        ax.plot(self.Re_values_laminar, self.f_values_laminar, label="Laminar (f=64/Re)", color="green")

        for eps_rel, f_curve in zip(self.epsilon_values, self.all_f_values):
            ax.plot(self.Re_values, f_curve, label=f"ε/D={eps_rel}")

        ax.axvspan(LAMINAR_LIMIT, TURBULENT_LIMIT, color="gray", alpha=0.2, label="Transitional zone (undefined)")

        if self.boundary_points:
            boundary_Re, boundary_f = zip(*self.boundary_points)
            ax.plot(
                boundary_Re, boundary_f, color="black", linestyle="--", alpha=0.7,
                label="Complete turbulence boundary",
            )

        if user_Re is not None and user_f is not None:
            ax.scatter(user_Re, user_f, color="red", s=100, zorder=5, label="Your input")

        ax.set_xscale("log")
        ax.set_yscale("log")
        ax.set_xlabel("Reynolds Number (Re)")
        ax.set_ylabel("Friction Factor (f)")
        ax.set_title("Moody-style Chart: Friction Factor vs Reynolds Number")
        ax.legend(bbox_to_anchor=(1.15, 1), loc="upper left")
        ax.grid(True, which="both", ls="--", alpha=0.5)

        ax2 = ax.twinx()
        ax2.set_yscale("log")
        ax2.set_ylim(ax.get_ylim())
        end_f_values = [f_curve[-1] for f_curve in self.all_f_values]
        ax2.set_yticks(end_f_values)
        ax2.set_yticklabels(["" for _ in self.epsilon_values])
        ax2.set_ylabel("Relative Pipe Roughness (ε/D)")

        fig.tight_layout()
        if show:
            plt.show()
        return fig, ax
