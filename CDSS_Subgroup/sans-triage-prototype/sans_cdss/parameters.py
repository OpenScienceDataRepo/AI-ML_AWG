# All numbers used. Format: name: (value, kind, source, note)
# kind = reported (from paper) | derived (calculated from paper) | assumption (my choice, needs review)

PARAMS = {
    # cohort
    "age_mean":          (46.9, "reported", "Pardon 2022", "n=31"),
    "age_sd":            (6.0, "reported", "Pardon 2022", ""),
    "p_male":            (0.81, "reported", "Pardon 2022; Carter 2026", "25/31, 35/43"),
    "mission_days_mean": (190, "derived", "Carter 2026; Pardon 2022", "198±55, 214±72 d"),
    "mission_days_sd":   (45, "derived", "Carter 2026", "clipped 120-365"),
    "p_prior_flight":    (0.55, "reported", "Pardon 2022", "17/31"),

    # optic cup (smaller cup -> more swelling)
    "cup_volume_mean":   (0.167, "reported", "Pardon 2022", "mm^3, range 0-0.841"),
    "cup_volume_sd":     (0.184, "derived", "Pardon 2022", "SE 0.033 x sqrt(31)"),
    "rho_cup_ode":       (-0.45, "assumption", "Pardon 2022", "direction from paper, strength mine"),

    # genetics
    "p_mtrr66_risk_allele":     (0.50, "assumption", "population estimate", "approx; verify in gnomAD"),
    "p_shmt1_1420_risk_allele": (0.65, "assumption", "population estimate", "approx; verify in gnomAD"),
    "rho_genetic_ode":          (0.20, "assumption", "Zwart 2019; Brunstetter 2024", "flight effect size unknown, kept small"),

    # disc edema: peak dTRT = shift + LogNormal(mu, sigma), solved for P(>=20)=0.64, P(>=55)=0.18
    "dtrt_lognorm_mu":    (3.618, "derived", "Brunstetter 2023; Macias 2020", ""),
    "dtrt_lognorm_sigma": (0.607, "derived", "Brunstetter 2023; Macias 2020", ""),
    "dtrt_shift":         (-10.0, "assumption", "modelling choice", "allows ~0 change"),
    "dtrt_tau_days":      (25.0, "assumption", "Macias 2020; Carter 2026", "rise time constant"),
    "dtrt_tau_logsd":     (0.30, "assumption", "modelling choice", "person-to-person spread"),
    "oct_noise_sd_um":    (7.0, "derived", "Pardon 2022", "19.4 = 1.96*sqrt(2)*SD"),

    # published prevalences (for checking only, not used to generate)
    "target_prev_ode20":     (0.64, "reported", "Brunstetter 2023", "dTRT >= 20"),
    "target_prev_folds":     (0.15, "reported", "Brunstetter 2023", ""),
    "target_prev_gf":        (0.26, "reported", "Brunstetter 2023", ""),
    "target_prev_hyperopic": (0.14, "reported", "Brunstetter 2023", ">= +0.75 D"),
    "target_prev_ode55":     (0.18, "derived", "Macias 2020; Valencia 2023", "16-19% clinically relevant"),

    # Frisen >= 1, by true dTRT
    "p_frisen_given_dtrt55": (0.60, "assumption", "Valencia 2023", "tuned to ~17% overall"),
    "p_frisen_given_dtrt20": (0.15, "assumption", "Valencia 2023", ""),
    "p_frisen_given_low":    (0.02, "assumption", "Valencia 2023", ""),

    # folds
    "p_folds_if_ode":             (0.24, "reported", "Ferguson 2023", "10/42 eyes"),
    "p_folds_if_no_ode":          (0.05, "derived", "Ferguson 2023", "2/~30 eyes"),
    "p_macular_given_folds":      (0.67, "reported", "Ferguson 2023", "4/6 crew"),
    "p_distortion_given_macular": (0.15, "assumption", "none", "not reported; placeholder"),

    # globe flattening
    "p_gf_if_ode":    (0.34, "assumption", "Brunstetter 2023", "tuned to 26%"),
    "p_gf_if_no_ode": (0.12, "assumption", "Brunstetter 2023", "tuned to 26%"),
    "p_gf_moderate":  (0.30, "assumption", "none", "not reported; placeholder"),

    # refraction (D)
    "refr_shift_base_mean": (0.10, "derived", "Pardon 2022", "-0.41 -> -0.21 D"),
    "refr_shift_base_sd":   (0.26, "assumption", "Brunstetter 2023", "tuned to 14%"),
    "refr_shift_gf_mean":   (0.55, "assumption", "Mader 2011", "extra shift with GF"),
    "refr_shift_gf_sd":     (0.35, "assumption", "Mader 2011", "range +0.5 to +1.75"),

    # function
    "p_vf_loss_if_dtrt100": (0.25, "assumption", "none", "not reported; placeholder"),

    # symptoms
    "p_symptom_base":     (0.45, "assumption", "Mader 2011", "~60% report blur"),
    "p_symptom_if_shift": (0.85, "assumption", "Mader 2011", "if shift >= +0.5 D"),
    "p_report":           (0.80, "assumption", "CDSS meeting 25 Sep", "under-reporting"),

    # context only (not used by triage)
    "iop_pre_mean":       (14.4, "reported", "Greenwald 2021", "mmHg"),
    "iop_pre_sd":         (2.5, "assumption", "general population", ""),
    "iop_inflight_delta": (1.3, "reported", "Greenwald 2021", "mmHg"),
    "choroid_pre_mean":   (213.3, "reported", "Pardon 2022", "um"),
    "choroid_pre_sd":     (61.8, "derived", "Pardon 2022", "SE 11.1 x sqrt(31)"),
    "choroid_delta_mean": (35.0, "reported", "Greenwald 2021; Macias 2020", "um"),
    "co2_mmhg_mean":      (2.8, "reported", "Macias 2020", ""),
}

# triage cut-offs (NASA categories: Brunstetter 2023, Gew 2026)
TRIAGE_THRESHOLDS = {
    "dtrt_earliest_um":    (20, "reported", "Brunstetter 2023; Gew 2026", "Tier 1"),
    "dtrt_concerning_um":  (55, "reported", "Brunstetter 2023; Gew 2026", "Tier 2"),
    "hyperopic_shift_D":   (0.75, "reported", "Brunstetter 2023", "Tier 1"),
    "beyond_correction_D": (1.75, "assumption", "Mader 2011", "placeholder for 'beyond correction'"),
    "fd30_progression_um": (29, "reported", "Carter 2026", "FD30 flag"),
    "fd30_window_days":    ((20, 40), "derived", "Macias 2020", "FD30 ±10 d"),
    "routine_exam_days":   ((30, 90, "R-30"), "reported", "Gew 2026", ""),
}


def value(name):
    return (PARAMS.get(name) or TRIAGE_THRESHOLDS[name])[0]


def provenance_table():
    import pandas as pd
    rows = [dict(group=g, parameter=k, value=v[0], kind=v[1], source=v[2], note=v[3])
            for g, d in (("simulator", PARAMS), ("triage", TRIAGE_THRESHOLDS)) for k, v in d.items()]
    return pd.DataFrame(rows)
