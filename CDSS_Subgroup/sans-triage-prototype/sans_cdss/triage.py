# Rule-based SANS triage. Tiers = NASA categories (Brunstetter 2023; Gew 2026).
# Actions are my drafts -> need clinician review.
from dataclasses import dataclass, field
from .parameters import TRIAGE_THRESHOLDS

TIER_NAMES = {0: "No SANS signs", 1: "Earliest indication", 2: "Clinically concerning", 3: "Acute functional impact"}

DRAFT_ACTIONS = {
    0: "Continue routine schedule (FD30, FD90, R-30).",
    1: "Increase surveillance: add interim OCT; review trend at next exam; notify flight surgeon at routine conference.",
    2: "Flight surgeon + ground ophthalmology review (timing TBD by clinicians); consider countermeasures per flight surgeon; "
       "flag for post-flight lumbar puncture (NASA: within 7-14 days of return).",
    3: "Urgent escalation to flight surgeon; functional vision testing; mission-impact assessment.",
}


def thresholds(**overrides):
    # copy of the cut-offs, e.g. thresholds(dtrt_concerning_um=45); defaults never change
    thr = {k: v[0] for k, v in TRIAGE_THRESHOLDS.items()}
    bad = set(overrides) - set(thr)
    if bad:
        raise KeyError(f"Unknown threshold(s): {sorted(bad)}")
    return {**thr, **overrides}


@dataclass
class TriageResult:
    tier: int
    tier_name: str
    reasons: list = field(default_factory=list)
    flags: list = field(default_factory=list)
    action: str = ""


def triage(obs, fd30_dtrt=None, thr=None):
    # check every rule, record why it fired; final tier = highest tier with a reason
    T = (thr or thresholds()).__getitem__
    R = {1: [], 2: [], 3: []}
    dtrt, shift = obs["dtrt_obs"], obs["refr_shift_D"]

    # tier 3
    if obs["visual_field_loss"]:
        R[3].append("Visual field loss (e.g., enlarged blind spot)")
    if obs["distorted_central_vision"]:
        R[3].append("Distorted central vision")
    if shift >= T("beyond_correction_D"):
        R[3].append(f"Refractive shift {shift:+.2f} D beyond available correction "
                    f"(>= {T('beyond_correction_D'):+.2f} D, ASSUMED limit)")
    # tier 2
    if dtrt >= T("dtrt_concerning_um"):
        R[2].append(f"dTRT {dtrt:.0f} um >= {T('dtrt_concerning_um')} um")
    if obs["frisen_ge1"]:
        R[2].append("Frisen grade >= 1 on fundus imaging")
    if obs["macular_folds"]:
        R[2].append("Chorioretinal folds near the macula")
    if obs["gf_moderate"]:
        R[2].append("Moderate globe flattening")
    # tier 1
    if dtrt >= T("dtrt_earliest_um"):
        R[1].append(f"dTRT {dtrt:.0f} um >= {T('dtrt_earliest_um')} um")
    if obs["folds_present"]:
        R[1].append("Chorioretinal folds present")
    if obs["globe_flattening"]:
        R[1].append("Globe flattening present")
    if shift >= T("hyperopic_shift_D"):
        R[1].append(f"Hyperopic shift {shift:+.2f} D >= {T('hyperopic_shift_D'):+.2f} D")

    tier = max([t for t in (3, 2, 1) if R[t]], default=0)

    # flags: warnings only, never change tier (Carter 2026)
    flags = []
    lo, hi = T("fd30_window_days")
    if fd30_dtrt is None and lo <= obs["flight_day"] <= hi:
        fd30_dtrt = dtrt
    if fd30_dtrt is not None and tier < 2:
        if fd30_dtrt > T("fd30_progression_um"):
            flags.append(f"Progression risk: FD30 dTRT {fd30_dtrt:.0f} um > {T('fd30_progression_um')} um "
                         "(Carter 2026: ~58% reach >= 55 um by FD150)")
        elif fd30_dtrt < T("dtrt_earliest_um"):
            flags.append(f"Low progression risk: FD30 dTRT < {T('dtrt_earliest_um')} um (Carter 2026: ~2% reach >= 55 um)")
    if obs.get("reports_blurred_vision") and tier == 0:
        flags.append("Astronaut reports blurred vision without objective SANS signs: check refraction / other causes")

    return TriageResult(tier, TIER_NAMES[tier], R.get(tier, []), flags, DRAFT_ACTIONS[tier])


def triage_sessions(sessions, thr=None):
    # triage every exam; carries each astronaut's FD30 dTRT forward for the flag
    import pandas as pd
    thr = thr or thresholds()
    out = sessions.sort_values(["astronaut_id", "flight_day"]).copy()
    lo, hi = thr["fd30_window_days"]
    fd30 = out[out.flight_day.between(lo, hi)].groupby("astronaut_id")["dtrt_obs"].first()
    res = []
    for _, row in out.iterrows():
        r = triage(row, fd30.get(row["astronaut_id"]) if row["flight_day"] > hi else None, thr)
        res.append((r.tier, r.tier_name, "; ".join(r.reasons), "; ".join(r.flags)))
    out[["tier", "tier_name", "reasons", "flags"]] = pd.DataFrame(res, index=out.index)
    return out


def explain(obs, fd30_dtrt=None, thr=None):
    r = triage(obs, fd30_dtrt, thr)
    return "\n".join([f"Tier {r.tier}: {r.tier_name}"]
                     + [f"  because: {x}" for x in r.reasons]
                     + [f"  flag:    {x}" for x in r.flags]
                     + [f"  draft action: {r.action}"])
