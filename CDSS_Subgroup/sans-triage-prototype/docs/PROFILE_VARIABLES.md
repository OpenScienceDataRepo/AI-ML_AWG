# Profile variables

Sources for every number: `sans_cdss/parameters.py` / `outputs/parameter_provenance.csv`.
ΔTRT = change in peripapillary total retinal thickness from preflight (µm). Onset `inf` = never.

## Astronaut (hidden truth)

| Variable | Unit | Generated as | Used by triage |
|---|---|---|---|
| `astronaut_id` | – | SYN-0000… | – |
| `age` | y | N(46.9, 6) | no |
| `sex` | M/F | 81% M | no |
| `mission_days` | d | N(190, 45), 120–365 | sets exam days |
| `prior_flight` | bool | 55% | no |
| `cup_volume_mm3` | mm³ | gamma, mean 0.167 | indirectly (smaller → more swelling) |
| `risk_alleles` | 0–4 | MTRR 66 + SHMT1 1420 | indirectly (small effect) |
| `dtrt_peak_true` | µm | −10 + lognormal(susceptibility) | drives ΔTRT |
| `tau_days` | d | ~25, varies by person | drives ΔTRT timing |
| `folds` | bool | 24% if ODE, else 5% | via exams |
| `folds_onset` | FD | U(30, 150) | via exams |
| `macular_folds` | bool | 67% of folds | via exams |
| `macular_onset` | FD | folds onset + U(0, 60) | via exams |
| `distortion` | bool | 15% of macular folds (assumed) | via exams |
| `globe_flattening` | bool | 34% if ODE, else 12% | via exams |
| `gf_onset` | FD | U(30, 120) | via exams |
| `gf_moderate` | bool | 30% of GF (assumed) | via exams |
| `refr_shift_final` | D | N(0.10, 0.26) + extra if GF | via exams |
| `iop_pre` | mmHg | N(14.4, 2.5), 8–30 | no |
| `choroid_pre` | µm | N(213, 62) | no |

Susceptibility: `z_ode = −0.45·z_cup + 0.20·z_genes + noise`.

## Exam (what's measured)

| Variable | Unit | Generated as | Triage rule |
|---|---|---|---|
| `astronaut_id`, `flight_day` | – | FD10, 30, 60, 90, 120, 150, R−30 | FD30 flag |
| `dtrt_true` | µm | peak × (1 − e^(−day/τ)) | – (truth) |
| `dtrt_obs` | µm | true + N(0, 7) | ≥20 T1, ≥55 T2 |
| `frisen_ge1` | bool | 60% / 15% / 2% by ΔTRT band | T2 |
| `folds_present` | bool | after onset | T1 |
| `macular_folds` | bool | after onset | T2 |
| `distorted_central_vision` | bool | after macular onset | T3 |
| `globe_flattening` | bool | after onset | T1 |
| `gf_moderate` | bool | after onset | T2 |
| `refr_shift_D` | D | final × min(1, day/90) + noise | ≥+0.75 T1, ≥+1.75 T3 |
| `visual_field_loss` | bool | 25% once ΔTRT ≥ 100 (assumed) | T3 |
| `reports_blurred_vision` | bool | symptom × 80% reported | flag |
| `iop_mmhg`, `choroid_um` | – | context | – |
| `tier`, `tier_name`, `reasons`, `flags` | – | triage output | – |

Not yet modelled: pre/post-flight, laterality, MRI, history, missing/poor-quality data, rate of change.
