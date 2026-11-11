"""Analyse a two-joint limb, idealised harmonic-drive compliance and heating."""

import argparse
import json
from pathlib import Path
from time import perf_counter_ns

import matplotlib
import numpy as np
from scipy.integrate import solve_ivp

import roboticstoolbox as rtb
from roboticstoolbox.tools.types import NDArray

matplotlib.use("Agg")
import matplotlib.pyplot as plt


def make_limb() -> rtb.DHRobot:
    """Create a two-link planar limb with finite link inertias."""
    links = []
    for length, mass in [(0.4, 2.0), (0.35, 1.3)]:
        inertia = mass * length**2 / 12
        links.append(
            rtb.RevoluteDH(
                a=length,
                m=mass,
                r=[-length / 2, 0, 0],
                I=[0.001, inertia, inertia],
                G=1,
                B=0.01,
            )
        )
    return rtb.DHRobot(links, name="Robotic Limb", gravity=[0, -9.81, 0])


def thermal_response(
    time: NDArray,
    loss: NDArray,
    resistance: float = 2.0,
    capacity: float = 50.0,
    ambient: float = 25.0,
) -> NDArray:
    """Integrate an illustrative lumped RC temperature model with exact ZOH steps.

    :param time: Sample times in seconds.
    :param loss: Nonnegative dissipated power samples in watts.
    :returns: Temperature samples in degrees Celsius.
    """
    temperature = np.full(len(time), ambient)
    for k, dt in enumerate(np.diff(time), start=1):
        equilibrium = ambient + resistance * loss[k - 1]
        temperature[k] = equilibrium + (temperature[k - 1] - equilibrium) * np.exp(
            -dt / (resistance * capacity)
        )
    return temperature


def run_analysis() -> tuple[dict, NDArray, NDArray, NDArray]:
    """Measure inverse dynamics, torque recovery and elastic transmission response."""
    limb = make_limb()
    t = np.linspace(0, 2, 401)
    trajectory = rtb.jtraj([0.2, -0.5], [0.8, -0.8], t)
    tau = limb.rne(trajectory.q, trajectory.qd, trajectory.qdd)
    recovered = np.array(
        [
            limb.accel(q, v, torque)
            for q, v, torque in zip(trajectory.q, trajectory.qd, tau)
        ]
    )
    limb.rne(trajectory.q, trajectory.qd, trajectory.qdd)
    timings = []
    for _ in range(7):
        start = perf_counter_ns()
        limb.rne(trajectory.q, trajectory.qd, trajectory.qdd)
        timings.append((perf_counter_ns() - start) / 1e6)
    ratio, stiffness, damping, inertia = 100.0, 150.0, 1.5, 0.08
    natural_hz = np.sqrt(stiffness / inertia) / (2 * np.pi)

    def rhs(now: float, state: NDArray) -> list[float]:
        motor_angle = ratio * 0.2 * np.sin(2 * np.pi * 0.5 * now)
        elastic_torque = stiffness * (motor_angle / ratio - state[0])
        return [state[1], (elastic_torque - damping * state[1]) / inertia]

    response = solve_ivp(rhs, (t[0], t[-1]), [0, 0], t_eval=t, rtol=1e-8, atol=1e-10)
    if not response.success:
        raise RuntimeError(response.message)
    efficiency = 0.8
    output_power = np.abs(tau * trajectory.qd).sum(axis=1)
    loss = output_power * (1 / efficiency - 1)
    temperature = thermal_response(t, loss)
    metrics = {
        "model": "two-link planar limb; idealised harmonic-drive torsional compliance",
        "dynamics_samples": len(t),
        "inverse_forward_max_error_rad_s2": float(
            np.max(np.abs(recovered - trajectory.qdd))
        ),
        "rne_trajectory_median_ms": float(np.median(timings)),
        "peak_joint_torque_Nm": np.max(np.abs(tau), axis=0).tolist(),
        "gear_ratio": ratio,
        "torsional_natural_frequency_Hz": float(natural_hz),
        "illustrative_peak_gearbox_temperature_C": float(temperature.max()),
        "thermal_assumptions": {
            "ambient_C": 25,
            "Rth_K_W": 2,
            "Cth_J_K": 50,
            "transmission_efficiency": efficiency,
        },
        "hardware_validation": False,
    }
    rows = np.column_stack((t, trajectory.q, tau, response.y[0], temperature))
    return metrics, rows, trajectory.q, trajectory.qd


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output", type=Path, default=Path("examples/limb_analyzer/results")
    )
    args = parser.parse_args()
    metrics, rows, _, _ = run_analysis()
    args.output.mkdir(parents=True, exist_ok=True)
    (args.output / "metrics.json").write_text(json.dumps(metrics, indent=2) + "\n")
    np.savetxt(
        args.output / "limb.csv",
        rows,
        delimiter=",",
        comments="",
        header="time_s,shoulder_rad,elbow_rad,shoulder_Nm,elbow_Nm,gear_output_rad,temperature_C",
    )
    fig, axes = plt.subplots(1, 3, figsize=(13, 4))
    axes[0].plot(rows[:, 0], rows[:, 3], label="Shoulder", color="#0072B2")
    axes[0].plot(rows[:, 0], rows[:, 4], label="Elbow", color="#D55E00")
    axes[0].set(xlabel="Time (s)", ylabel="Torque (Nm)", title="Joint dynamics")
    axes[0].legend()
    axes[1].plot(rows[:, 0], rows[:, 5], color="#0072B2")
    axes[1].set(
        xlabel="Time (s)", ylabel="Output angle (rad)", title="Elastic drive response"
    )
    axes[2].plot(rows[:, 0], rows[:, 6], color="#0072B2")
    axes[2].set(
        xlabel="Time (s)",
        ylabel="Temperature (C)",
        title="Illustrative RC thermal model",
    )
    fig.tight_layout()
    fig.savefig(args.output / "overview.png", dpi=160)
    plt.close(fig)
    print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    main()
