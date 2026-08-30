import numpy as np
import pandas as pd

TIMEPOINTS = ["L-30", "L+30", "L+60", "L+90", "L+120"]
DELTAS = {"L-30":[0,0,0,0], "L+30":[8,15,1.5,0.25], "L+60":[20,28,2.0,0.5], "L+90":[35,38,2.2,0.75], "L+120":[45,45,2.5,1.0]}

def generate_cohort(n=20, sans_ratio=0.5):
    records = []
    for i in range(n):
        aid = f"AST_{i+1:02d}"
        sans = (i % 2 == 0)
        grp = "SANS" if sans else "Control"
        b_rnfl, b_cho, b_iop, b_ref = np.random.normal(95, 8), np.random.normal(270, 40), np.random.normal(15, 2.5), np.random.normal(-0.25, 0.75)
        for t in TIMEPOINTS:
            d = DELTAS[t] if sans else [0, 0, 0, 0]
            records.append({"astronaut_id": aid, "cohort": grp, "timepoint": t, "rnfl_um": round(b_rnfl + d[0] + float(np.random.normal(0, 2)), 2), "choroid_um": round(b_cho + d[1] + float(np.random.normal(0, 5)), 2), "iop_mmhg": round(b_iop + d[2] + float(np.random.normal(0, 1)), 2), "refraction_diopters": round(b_ref + d[3] + float(np.random.normal(0, 0.1)), 2)})
    return pd.DataFrame(records)

def audit_cohort(df):
    p = df.pivot(index=["astronaut_id", "cohort"], columns="timepoint", values="rnfl_um")
    deltas = p["L+120"] - p["L-30"]
    sans_err = deltas[(p.index.get_level_values("cohort") == "SANS") & (deltas < 15.0)]
    ctrl_err = deltas[(p.index.get_level_values("cohort") == "Control") & (deltas > 10.0)]
    return len(sans_err) == 0 and len(ctrl_err) == 0

if __name__ == "__main__":
    cohort = generate_cohort(20)
    cohort.to_csv("synthetic_sans_cohort.csv", index=False)
    passed = audit_cohort(cohort)
    print(f"vmed_sans_generator: OK (Audit Passed: {passed})")
