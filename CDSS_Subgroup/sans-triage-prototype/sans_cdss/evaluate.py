# Checks: realism vs literature, tier summaries, noise robustness, threshold what-ifs, kappa.
import numpy as np
import pandas as pd

from .parameters import value as P
from . import triage as tri


def validate_generator(astronauts, sessions):
    # 1) prevalence (tuned -> confirms calibration only)
    mx = sessions.groupby("astronaut_id").agg(
        dtrt=("dtrt_true", "max"), folds=("folds_present", "any"), gf=("globe_flattening", "any"),
        refr=("refr_shift_D", "max"), frisen=("frisen_ge1", "any"))
    prev = pd.DataFrame([
        ("dTRT >= 20 um (earliest-indication ODE)", (mx.dtrt >= 20).mean(), P("target_prev_ode20"), "Brunstetter 2023"),
        ("dTRT >= 55 um (clinically concerning ODE)", (mx.dtrt >= 55).mean(), P("target_prev_ode55"), "Macias 2020 intro: 16-19%"),
        ("Chorioretinal folds", mx.folds.mean(), P("target_prev_folds"), "Brunstetter 2023; Ferguson 2023: 17%"),
        ("Globe flattening", mx.gf.mean(), P("target_prev_gf"), "Brunstetter 2023"),
        ("Hyperopic shift >= +0.75 D", (mx.refr >= 0.75).mean(), P("target_prev_hyperopic"), "Brunstetter 2023"),
        ("Frisen grade >= 1", mx.frisen.mean(), 0.17, "Valencia 2023: 17% of images"),
    ], columns=["finding", "synthetic", "published", "source"])

    # 2) time course (Carter rows NOT tuned -> independent check)
    piv = sessions.pivot_table(index="astronaut_id", columns="flight_day", values="dtrt_obs")
    x, y = piv.get(30), piv.get(150)
    ok = x.notna() & y.notna()
    x, y = x[ok], y[ok]
    mean_at = lambda d: sessions.loc[sessions.flight_day == d, "dtrt_obs"].mean()
    traj = pd.DataFrame([
        ("Mean dTRT, FD10 (um)", mean_at(10), "11.9 (95% CI 6.6-17.3)", "Macias 2020"),
        ("Mean dTRT, FD150 (um)", mean_at(150), "27.6 (Macias, n=11); 38.2 (Pardon, n=31)", "Macias 2020; Pardon 2022"),
        ("Correlation dTRT FD30 vs FD150", np.corrcoef(x, y)[0, 1], "0.89 (0.80-0.94)", "Carter 2026"),
        ("P(FD150 >= 55 | FD30 < 20)", (y[x < 20] >= 55).mean(), "2% (1-15%)", "Carter 2026"),
        ("P(FD150 >= 55 | FD30 20-55)", (y[(x >= 20) & (x < 55)] >= 55).mean(), "34% (19-60%)", "Carter 2026"),
        ("P(FD150 >= 55 | FD30 29-55)", (y[(x > 29) & (x < 55)] >= 55).mean(), "58% (37-90%)", "Carter 2026"),
    ], columns=["check", "synthetic", "published", "source"])

    # 3) cup volume effect (Pardon 2022)
    a = astronauts.set_index("astronaut_id")
    big = a.cup_volume_mm3 >= 0.3
    cup = pd.DataFrame([
        ("P(peak dTRT > 19.4 | cup >= 0.3 mm3)", (a.dtrt_peak_true[big] > 19.4).mean(), "0% (none of ~31 crew)"),
        ("P(peak dTRT > 19.4 | cup < 0.3 mm3)", (a.dtrt_peak_true[~big] > 19.4).mean(), "most"),
    ], columns=["check", "synthetic", "published (Pardon 2022)"])
    return prev, traj, cup


def tier_summary(triaged):
    # worst tier per astronaut
    final = triaged.groupby("astronaut_id")["tier"].max()
    out = final.value_counts().sort_index().rename("n").to_frame()
    out["share"] = out["n"] / out["n"].sum()
    out.index = [f"{i} - {tri.TIER_NAMES[i]}" for i in out.index]
    return out


def tier_by_day(triaged, days=(10, 30, 60, 90, 120, 150)):
    t = triaged[triaged.flight_day.isin(days)]
    return pd.crosstab(t.flight_day, t.tier, normalize="index").rename(columns=tri.TIER_NAMES)


def criterion_drivers(triaged):
    # which rules put people in each tier (at their worst exam)
    worst = triaged.loc[triaged.groupby("astronaut_id")["tier"].idxmax()]
    rows = []
    for tier, grp in worst[worst.tier > 0].groupby("tier"):
        reasons = grp["reasons"].str.split("; ").explode()
        reasons = reasons.str.replace(r"[-+]?\d+(\.\d+)? (um|D)", r"# \2", regex=True)
        rows += [dict(tier=tier, reason=r, share_of_tier=c / len(grp)) for r, c in reasons.value_counts().items()]
    return pd.DataFrame(rows)


def test_retest(triaged, astronauts, remeasure_fn):
    # same eyes, new noise -> how often does tier change? (alarm-fatigue proxy)
    re = tri.triage_sessions(remeasure_fn(astronauts, triaged.drop(columns=["tier", "tier_name", "reasons", "flags"])))
    m = triaged[["astronaut_id", "flight_day", "tier"]].merge(
        re[["astronaut_id", "flight_day", "tier"]], on=["astronaut_id", "flight_day"], suffixes=("_a", "_b"))
    return dict(
        exam_level_agreement=(m.tier_a == m.tier_b).mean(),
        exam_level_kappa=cohen_kappa(m.tier_a, m.tier_b, weights="quadratic"),
        crosstab=pd.crosstab(m.tier_a, m.tier_b, rownames=["measurement A"], colnames=["measurement B"]),
    )


def threshold_sensitivity(sessions, earliest=(10, 15, 20, 25, 30), concerning=(45, 50, 55, 60, 65)):
    # move the dTRT cut-offs, count astronauts whose final tier changes
    base = tri.triage_sessions(sessions).groupby("astronaut_id").tier.max()
    rows = []
    for e in earliest:
        for c in concerning:
            thr = tri.thresholds(dtrt_earliest_um=e, dtrt_concerning_um=c)
            final = tri.triage_sessions(sessions, thr=thr).groupby("astronaut_id").tier.max()
            rows.append(dict(earliest_um=e, concerning_um=c, pct_reclassified=100 * (final != base).mean(),
                             pct_tier2plus=100 * (final >= 2).mean()))
    return pd.DataFrame(rows)


def cohen_kappa(a, b, weights=None, categories=(0, 1, 2, 3)):
    # agreement beyond chance; weights="quadratic" gives partial credit for near-misses
    k = len(categories)
    idx = {c: i for i, c in enumerate(categories)}
    obs = np.zeros((k, k))
    for x, y in zip(np.asarray(a), np.asarray(b)):
        obs[idx[x], idx[y]] += 1
    obs /= obs.sum()
    exp = np.outer(obs.sum(1), obs.sum(0))
    i, j = np.indices((k, k))
    w = (i != j).astype(float) if weights is None else ((i - j) ** 2) / (k - 1) ** 2
    return 1 - (w * obs).sum() / (w * exp).sum()
