# Application verification — 2026-11-11

Tested on Windows with CPython 3.12.13 and an editable checkout of Robotics Toolbox 1.5.0 using `RTB_PURE_WHEEL=1`. The native C++ extension was not built. Exact dependency versions are recorded in `examples/limb_analyzer/requirements.lock`.

| Check | Result |
|---|---|
| `python -m examples.limb_analyzer.analyze` | Completed; JSON, CSV and PNG outputs generated |
| `python -m pytest examples/limb_analyzer/test_analysis.py -q` | 2 passed |
| `ruff check examples/limb_analyzer` | Passed |
| Application-only mypy check | Passed with silent imported-library checking |
| Torque recovery | Maximum acceleration discrepancy approximately 4.98e-14 rad/s² |
| Thermal energy balance | Zero-loss equilibrium and constant-power analytical response passed |

The reported torsional natural frequency, approximately 6.89 Hz, comes from the specified idealised stiffness and inertia. It is not a physical vibration measurement. The illustrative gearbox temperature is not a demonstrated 9-degree reduction.

## Broader upstream checks

The required upstream command was attempted:

```bash
python -m pytest tests/ --ignore=tests/test_blocks.py --timeout=50 --timeout_method=thread -q
```

It reported failures and terminated on the 50-second timeout in `tests/test_dynamics_defaults.py::test_fdyn_without_optional_arguments`, inside the unmodified pure-Python forward-dynamics path. Therefore the full upstream suite did not pass and has no complete final test count for this environment.

The upstream `python -m mypy` check reported six Windows-specific errors involving `SIGALRM`, `setitimer` and `ITIMER_REAL` in the unmodified `symbolic_ik.py`. No library source or upstream test files were edited for this adaptation.

Original automation is preserved in `.github/upstream-workflows/`; the new application workflow runs the added smoke/physics checks without upstream releases or deployments. Passing that workflow is not a claim that the upstream toolbox's complete test matrix passes.
