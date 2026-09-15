"""Unit tests for pipe_flow.py. Run with: pytest"""

import pytest

from pipe_flow import (
    flow_regime,
    friction_factor_colebrook,
    friction_factor_laminar,
    full_pipe_calc,
    pressure_drop,
    reynolds_number,
)


def test_reynolds_number():
    # Water at ~20C through a 5cm pipe at 2 m/s
    Re = reynolds_number(rho=1000, v=2, D=0.05, mu=0.001)
    assert Re == pytest.approx(100_000)


def test_flow_regime_boundaries():
    assert flow_regime(2299) == "Laminar"
    assert flow_regime(2300) == "Transitional"
    assert flow_regime(3999) == "Transitional"
    assert flow_regime(4000) == "Turbulent"


def test_friction_factor_laminar():
    assert friction_factor_laminar(1000) == pytest.approx(0.064)


def test_friction_factor_colebrook_matches_moody_chart_range():
    # Re=1e5, epsilon/D ~= 0.003 (commercial steel pipe): Moody chart gives f ~ 0.023-0.028
    f = friction_factor_colebrook(Re=100_000, D=0.05, epsilon=0.00015)
    assert 0.02 < f < 0.03


def test_friction_factor_colebrook_raises_on_nonconvergence():
    with pytest.raises(RuntimeError):
        friction_factor_colebrook(Re=100_000, D=0.05, epsilon=0.00015, max_iter=0)


def test_pressure_drop():
    dP = pressure_drop(f=0.02, L=10, rho=1000, v=2, D=0.05)
    assert dP == pytest.approx(0.02 * (10 / 0.05) * (1000 * 2 ** 2 / 2))


def test_full_pipe_calc_laminar():
    result = full_pipe_calc(rho=1000, v=0.01, D=0.05, mu=0.001, L=10, epsilon=0.0)
    assert result.regime == "Laminar"
    assert result.f == pytest.approx(64 / result.Re)


@pytest.mark.parametrize(
    "kwargs",
    [
        {"rho": -1, "v": 2, "D": 0.05, "mu": 0.001, "L": 10, "epsilon": 0.0},
        {"rho": 1000, "v": 2, "D": 0, "mu": 0.001, "L": 10, "epsilon": 0.0},
        {"rho": 1000, "v": 0, "D": 0.05, "mu": 0.001, "L": 10, "epsilon": 0.0},
        {"rho": 1000, "v": 2, "D": 0.05, "mu": 0.001, "L": 10, "epsilon": -0.001},
    ],
)
def test_full_pipe_calc_rejects_invalid_input(kwargs):
    with pytest.raises(ValueError):
        full_pipe_calc(**kwargs)
