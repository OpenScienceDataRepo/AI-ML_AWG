# Blinded case vignettes for clinicians to grade. Answer key kept separate.
import pandas as pd


def _text(row, astro):
    f = [f"Change in peripapillary total retinal thickness (dTRT) from preflight: {row.dtrt_obs:+.0f} um.",
         f"Refraction change from preflight: {row.refr_shift_D:+.2f} D (spherical equivalent).",
         "Fundus: " + ("Frisen grade >= 1 disc edema." if row.frisen_ge1 else "no Frisen-gradable disc edema.")]
    if row.macular_folds:
        f.append("OCT: chorioretinal folds extending toward the macula.")
    elif row.folds_present:
        f.append("OCT: peripapillary chorioretinal folds.")
    else:
        f.append("OCT: no chorioretinal folds.")
    f.append(("Ultrasound: " + ("moderate" if row.gf_moderate else "mild") + " posterior globe flattening.")
             if row.globe_flattening else "Ultrasound: no globe flattening.")
    sx = [s for s, on in (("reports blurred near vision", row.reports_blurred_vision),
                          ("reports distorted central vision", row.distorted_central_vision),
                          ("visual field testing shows an enlarged blind spot", row.visual_field_loss)) if on]
    f.append("Symptoms/function: " + ("; ".join(sx) + "." if sx else "no complaints; visual field not tested."))
    f.append(f"IOP {row.iop_mmhg:.0f} mmHg.")
    head = (f"{int(astro.age)}-year-old {'male' if astro.sex == 'M' else 'female'} astronaut "
            f"({'prior spaceflight' if astro.prior_flight else 'no prior spaceflight'}), "
            f"flight day {row.flight_day} of {astro.mission_days}.")
    return head + " " + " ".join(f)


def build_packet(triaged, astronauts, per_tier=10, seed=7):
    # each astronaut's worst exam, up to per_tier per tier, shuffled
    a = astronauts.set_index("astronaut_id")
    worst = triaged.loc[triaged.groupby("astronaut_id")["tier"].idxmax()]
    picks = pd.concat([g.sample(min(per_tier, len(g)), random_state=seed) for _, g in worst.groupby("tier")])
    picks = picks.sample(frac=1, random_state=seed).reset_index(drop=True)
    picks["case_id"] = [f"V{i+1:02d}" for i in range(len(picks))]
    packet = pd.DataFrame(dict(case_id=picks.case_id,
                               vignette=[_text(r, a.loc[r.astronaut_id]) for r in picks.itertuples()],
                               clinician_tier="", clinician_comment=""))
    key = picks[["case_id", "astronaut_id", "flight_day", "tier", "reasons"]].rename(columns={"tier": "engine_tier"})
    return packet, key
