# Robotic Limb Dynamics Analyzer

A two-link robotic limb analysis application built on Robotics Toolbox for Python. It covers rigid-body dynamics, an idealised harmonic-drive transmission, and lumped thermal post-processing, with measured reports in `examples/limb_analyzer/`.

![Limb torque, transmission and thermal analysis](examples/limb_analyzer/results/overview.png)

## What I built

- **Planar limb model** — two links with explicit lengths, masses, centres of mass, and finite rotational inertias.
- **Dynamics pipeline** — quintic joint trajectories, recursive Newton–Euler torque evaluation, and forward-dynamics recovery checked against the inverse result.
- **Harmonic-drive model** — gear ratio, torsional stiffness, damping, and load inertia, giving a computed torsional natural frequency.
- **Thermal post-processing** — lumped RC gearbox heating with explicit efficiency, resistance, and capacitance assumptions.
- **Measurement harness** — CSV samples, JSON timing and consistency metrics, a headless report plot, and pytest checks for torque recovery and thermal energy balance.

## Measured results

From `examples/limb_analyzer/results/metrics.json` (CPython 3.12.13, Robotics Toolbox 1.5.0 pure-Python mode, 401 dynamics samples):

| Metric | Measured |
|---|---|
| Inverse/forward acceleration error | 4.98 × 10⁻¹⁴ rad/s² |
| RNE trajectory evaluation, median | 215.06 ms |
| Peak joint torques | 11.33 Nm, 2.23 Nm |
| Gear ratio | 100:1 |
| Torsional natural frequency | 6.89 Hz |
| Illustrative peak gearbox temperature | 25.03 °C (25 °C ambient) |
| Hardware validation | none (`false`) |

## Resume targets vs. what this repo measures

The resume bullets are design targets from the project brief. This table maps each one to the evidence in this repository.

| Resume claim | Measured in this repo | Status |
|---|---|---|
| Increase movement calculation speed by 31% | RNE median 215.06 ms per trajectory | No before/after baseline; absolute timing only |
| Improve position control precision by 16% with harmonic-drive equations | Idealised compliance model, 6.89 Hz natural frequency | Model implemented; no position-control comparison |
| Decrease resonance anomalies by 25% for electric propulsion units | Natural-frequency estimate only | Not measured — no propulsion unit or vibration data |
| Lower planetary-gearbox peak temperatures by 9 °C | 25.03 °C peak against 25 °C ambient | Not demonstrated — lumped RC estimate, no planetary geometry or baseline |

## Scope

The transmission is an idealised model, not a calibrated commercial harmonic drive. Thermal results are illustrative post-processing. Planetary gear geometry, propulsion-unit modal analysis, OpenCV processing, and physical drive calibration are not implemented. The upstream toolbox has C++ extensions and a pure-Python fallback; the reported run used the fallback.

## Run

Python 3.12 is the tested environment. In Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
$env:RTB_PURE_WHEEL = "1"
python -m pip install -e .
python -m pip install pytest
python -m examples.limb_analyzer.analyze
python -m pytest examples/limb_analyzer/test_analysis.py -q
```

On Linux/macOS, activate with `source .venv/bin/activate`; use `RTB_PURE_WHEEL=1 python -m pip install -e .` if native build tools are unavailable. Exact versions are in `examples/limb_analyzer/requirements.lock`. Reports default to `examples/limb_analyzer/results/`; `--output` selects another directory.

## More detail

- [Verification report](docs/source/PROJECT_VERIFICATION.md)
- [Project requirements and design targets](docs/source/PROJECT_REQUIREMENTS.md)
- [Metrics JSON](examples/limb_analyzer/results/metrics.json) · [Limb CSV](examples/limb_analyzer/results/limb.csv)

## Attribution and license

Extends [Robotics Toolbox for Python](https://github.com/petercorke/robotics-toolbox-python) (`petercorke/robotics-toolbox-python`, MIT). Upstream copyright notices and the [LICENSE](LICENSE) text are retained; the application code in `examples/limb_analyzer/` is the work described above.
