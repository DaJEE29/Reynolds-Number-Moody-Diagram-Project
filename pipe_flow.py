"""Core fluid-mechanics calculations for pipe flow: Reynolds number,
flow regime classification, Darcy friction factor (Colebrook equation),
and Darcy-Weisbach pressure drop.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

LAMINAR_LIMIT = 2300
TURBULENT_LIMIT = 4000


def reynolds_number(rho: float, v: float, D: float, mu: float) -> float:
    """Compute the Reynolds number for flow in a circular pipe."""
    return (rho * v * D) / mu


def flow_regime(Re: float) -> str:
    """Classify flow as 'Laminar', 'Transitional', or 'Turbulent'."""
    if Re < LAMINAR_LIMIT:
        return "Laminar"
    if Re < TURBULENT_LIMIT:
        return "Transitional"
    return "Turbulent"


def friction_factor_laminar(Re: float) -> float:
    """Darcy friction factor for laminar flow (Hagen-Poiseuille)."""
    return 64 / Re


def friction_factor_colebrook(
    Re: float,
    D: float,
    epsilon: float,
    tol: float = 1e-6,
    max_iter: int = 100,
) -> float:
    """Solve the Colebrook equation for the Darcy friction factor by fixed-point iteration.

    Raises:
        RuntimeError: if the iteration fails to converge within max_iter steps.
    """
    f = 0.02  # initial guess

    for _ in range(max_iter):
        rhs = -2 * math.log10(epsilon / D / 3.7 + 2.51 / (Re * math.sqrt(f)))
        f_new = 1 / (rhs ** 2)

        if abs(f_new - f) < tol:
            return f_new

        f = f_new

    raise RuntimeError(
        f"Colebrook iteration did not converge after {max_iter} iterations "
        f"(Re={Re}, epsilon/D={epsilon / D})."
    )


def friction_factor(Re: float, D: float, epsilon: float) -> float:
    """Darcy friction factor for any regime.

    Laminar flow uses f = 64/Re. Transitional and turbulent flow use the
    Colebrook correlation, though the Colebrook equation is not physically
    validated in the transitional zone (2300 < Re < 4000) -- treat results
    there as a rough estimate only.
    """
    if flow_regime(Re) == "Laminar":
        return friction_factor_laminar(Re)
    return friction_factor_colebrook(Re, D, epsilon)


def pressure_drop(f: float, L: float, rho: float, v: float, D: float) -> float:
    """Darcy-Weisbach pressure drop over a pipe length L."""
    return f * (L / D) * (rho * v ** 2 / 2)


@dataclass
class PipeFlowResult:
    Re: float
    regime: str
    f: float
    dP: float


def full_pipe_calc(rho: float, v: float, D: float, mu: float, L: float, epsilon: float) -> PipeFlowResult:
    """Run the full pipe-flow calculation: Reynolds number, regime, friction factor, pressure drop.

    Raises:
        ValueError: if any input is physically invalid (non-positive rho/D/mu/L/v,
            or negative epsilon).
    """
    if rho <= 0 or D <= 0 or mu <= 0 or L <= 0:
        raise ValueError("Density, diameter, viscosity, and length must be positive.")
    if v <= 0:
        raise ValueError("Velocity must be positive.")
    if epsilon < 0:
        raise ValueError("Pipe roughness cannot be negative.")

    Re = reynolds_number(rho, v, D, mu)
    regime = flow_regime(Re)
    f = friction_factor(Re, D, epsilon)
    dP = pressure_drop(f, L, rho, v, D)

    return PipeFlowResult(Re=Re, regime=regime, f=f, dP=dP)
