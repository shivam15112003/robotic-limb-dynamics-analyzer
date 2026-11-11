import numpy as np

from examples.limb_analyzer.analyze import make_limb, run_analysis, thermal_response


def test_torque_recovery_and_positive_inertia():
    limb = make_limb()
    assert np.linalg.eigvalsh(limb.inertia([0.2, -0.5])).min() > 0
    metrics, rows, _, _ = run_analysis()
    assert np.isfinite(rows).all()
    assert metrics["inverse_forward_max_error_rad_s2"] < 1e-8
    assert np.max(np.abs(rows[:, 3:5])) > 1


def test_thermal_energy_balance():
    time = np.linspace(0, 100, 501)
    assert np.allclose(thermal_response(time, np.zeros(len(time))), 25)
    heated = thermal_response(time, np.full(len(time), 5.0))
    assert np.all(np.diff(heated) > 0)
    assert np.isclose(heated[-1], 25 + 10 * (1 - np.exp(-1)))
