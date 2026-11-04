# Synthetic astronauts -> in-flight exams.
# Astronaut table = hidden truth. Exam table = what you'd measure (truth + noise).
# One "worst eye" per astronaut. Synthetic only.
import numpy as np
import pandas as pd
from scipy import stats

from .parameters import value as P

DENSE_SCHEDULE = (10, 30, 60, 90, 120, 150)   # Macias 2020 exam windows


def _gamma(mean, sd):
    return stats.gamma(a=(mean / sd) ** 2, scale=sd ** 2 / mean)


def make_astronauts(n=1000, seed=0):
    rng = np.random.default_rng(seed)

    age = np.clip(rng.normal(P("age_mean"), P("age_sd"), n), 30, 62).round()
    sex = np.where(rng.random(n) < P("p_male"), "M", "F")
    mission_days = np.clip(rng.normal(P("mission_days_mean"), P("mission_days_sd"), n), 120, 365).round().astype(int)
    prior_flight = rng.random(n) < P("p_prior_flight")

    # risk factors -> z-scores
    cup_dist = _gamma(P("cup_volume_mean"), P("cup_volume_sd"))
    cup_volume = np.clip(cup_dist.rvs(size=n, random_state=rng), 0, 0.85)
    z_cup = stats.norm.ppf(np.clip(cup_dist.cdf(cup_volume), 1e-6, 1 - 1e-6))
    risk_alleles = rng.binomial(2, P("p_mtrr66_risk_allele"), n) + rng.binomial(2, P("p_shmt1_1420_risk_allele"), n)
    z_gen = (risk_alleles - risk_alleles.mean()) / risk_alleles.std()

    # hidden ODE susceptibility = cup + genes + noise (variance kept at 1)
    rc, rg = P("rho_cup_ode"), P("rho_genetic_ode")
    z_ode = rc * z_cup + rg * z_gen + np.sqrt(1 - rc**2 - rg**2) * rng.standard_normal(n)

    # plateau dTRT (um) and how fast it gets there
    dtrt_peak = P("dtrt_shift") + np.exp(P("dtrt_lognorm_mu") + P("dtrt_lognorm_sigma") * z_ode)
    tau = P("dtrt_tau_days") * np.exp(rng.normal(0, P("dtrt_tau_logsd"), n))
    has_ode = dtrt_peak >= 20

    # folds (more likely with ODE)
    folds = rng.random(n) < np.where(has_ode, P("p_folds_if_ode"), P("p_folds_if_no_ode"))
    folds_onset = np.where(folds, rng.uniform(30, 150, n), np.inf)
    macular = folds & (rng.random(n) < P("p_macular_given_folds"))
    macular_onset = np.where(macular, folds_onset + rng.uniform(0, 60, n), np.inf)
    distortion = macular & (rng.random(n) < P("p_distortion_given_macular"))

    # globe flattening (more likely with ODE)
    gf = rng.random(n) < np.where(has_ode, P("p_gf_if_ode"), P("p_gf_if_no_ode"))
    gf_onset = np.where(gf, rng.uniform(30, 120, n), np.inf)
    gf_moderate = gf & (rng.random(n) < P("p_gf_moderate"))

    # final hyperopic shift (D), bigger with GF
    refr_final = rng.normal(P("refr_shift_base_mean"), P("refr_shift_base_sd"), n)
    refr_final += np.where(gf, rng.normal(P("refr_shift_gf_mean"), P("refr_shift_gf_sd"), n), 0)

    # fixed per-person dice so findings don't flicker between exams
    u_frisen, u_vf, u_symptom, u_report = (rng.random(n) for _ in range(4))

    # context only
    iop_pre = np.clip(rng.normal(P("iop_pre_mean"), P("iop_pre_sd"), n), 8, 30)
    choroid_pre = np.clip(rng.normal(P("choroid_pre_mean"), P("choroid_pre_sd"), n), 100, 450)

    return pd.DataFrame(dict(
        astronaut_id=[f"SYN-{i:04d}" for i in range(n)],
        age=age, sex=sex, mission_days=mission_days, prior_flight=prior_flight,
        cup_volume_mm3=cup_volume.round(3), risk_alleles=risk_alleles,
        dtrt_peak_true=dtrt_peak, tau_days=tau,
        folds=folds, folds_onset=folds_onset, macular_folds=macular, macular_onset=macular_onset,
        distortion=distortion, globe_flattening=gf, gf_onset=gf_onset, gf_moderate=gf_moderate,
        refr_shift_final=refr_final,
        u_frisen=u_frisen, u_vf=u_vf, u_symptom=u_symptom, u_report=u_report,
        iop_pre=iop_pre, choroid_pre=choroid_pre,
    ))


def true_dtrt(a, day):
    # exponential rise to plateau
    return a["dtrt_peak_true"] * (1 - np.exp(-day / a["tau_days"]))


def session_days(mission_days, schedule="dense"):
    # dense = research schedule, routine = NASA FD30, FD90, R-30
    r30 = mission_days - 30
    base = (30, 90) if schedule == "routine" else DENSE_SCHEDULE
    return [d for d in base if d < r30 - 5] + [r30]


def _observe(a, day, rng):
    t = true_dtrt(a, day)
    p_fr = P("p_frisen_given_dtrt55") if t >= 55 else P("p_frisen_given_dtrt20") if t >= 20 else P("p_frisen_given_low")
    refr = a["refr_shift_final"] * min(1.0, day / 90)          # shift builds over ~90 d
    symptom = a["u_symptom"] < (P("p_symptom_if_shift") if refr >= 0.5 else P("p_symptom_base"))
    return dict(
        astronaut_id=a["astronaut_id"], flight_day=int(day),
        dtrt_true=round(t, 1),
        dtrt_obs=round(t + rng.normal(0, P("oct_noise_sd_um")), 1),   # OCT noise
        frisen_ge1=bool(a["u_frisen"] < p_fr),
        folds_present=bool(day >= a["folds_onset"]),
        macular_folds=bool(day >= a["macular_onset"]),
        distorted_central_vision=bool(a["distortion"] and day >= a["macular_onset"]),
        globe_flattening=bool(day >= a["gf_onset"]),
        gf_moderate=bool(a["gf_moderate"] and day >= a["gf_onset"]),
        refr_shift_D=round(refr + rng.normal(0, 0.125), 2),           # refraction noise
        visual_field_loss=bool(t >= 100 and a["u_vf"] < P("p_vf_loss_if_dtrt100")),
        reports_blurred_vision=bool(symptom and a["u_report"] < P("p_report")),
        iop_mmhg=round(a["iop_pre"] + P("iop_inflight_delta") + rng.normal(0, 1.0), 1),
        choroid_um=round(a["choroid_pre"] + P("choroid_delta_mean") * (1 - np.exp(-day / 30)) + rng.normal(0, 8), 1),
    )


def make_sessions(astronauts, schedule="dense", seed=1):
    rng = np.random.default_rng(seed)
    return pd.DataFrame([_observe(a, d, rng)
                         for _, a in astronauts.iterrows()
                         for d in session_days(a["mission_days"], schedule)])


def remeasure(astronauts, sessions, seed=99):
    # same eyes, fresh noise (test-retest)
    rng = np.random.default_rng(seed)
    a = astronauts.set_index("astronaut_id")
    out = sessions.copy()
    out["dtrt_obs"] = (out["dtrt_true"] + rng.normal(0, P("oct_noise_sd_um"), len(out))).round(1)
    out["refr_shift_D"] = [round(a.loc[i, "refr_shift_final"] * min(1.0, d / 90) + rng.normal(0, 0.125), 2)
                           for i, d in zip(out["astronaut_id"], out["flight_day"])]
    return out
