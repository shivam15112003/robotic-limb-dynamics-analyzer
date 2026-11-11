# Project requirements

## Design targets

| Capability | Target | Acceptance evidence |
|---|---|---|
| Multibody limb dynamics | Increase movement calculation speed by 31 percent | Named baseline and repeated identical-workload timings |
| Harmonic-drive control | Improve position control precision by 16 percent | Defined error metric under identical loads and trajectories |
| Propulsion vibration reports | Decrease resonance anomalies by 25 percent | Defined anomaly statistic and comparable vibration recordings |
| Planetary gearbox thermal modelling | Lower peak operating temperatures by 9 degrees | Specified temperature scale, operating conditions and baseline |

Current code implements planar joint torque analysis, an idealised compliant transmission and RC thermal post-processing. It reports absolute values. Its thermal plot is not a validated planetary gearbox design or a demonstrated temperature reduction. The 9-degree target remains unchanged; the original temperature scale was unspecified. These targets are not claimed as achieved.

OpenCV processing, physical drive calibration, propulsion vibration tests and planetary gearbox validation remain extensions.
