import numpy as np
import pandas as pd
import uuid

# 1. Parametros del estandar CDSS
MISSION_TIMELINES = ["L-30", "L", "L+30", "L+90", "L+120"]

CLINICAL_RANGES = {
    "rnfl_thickness_um": {"normal": (85.0, 105.0), "edema_risk": 115.0},
    "choroidal_thickness_um": {"normal": (250.0, 320.0), "congestion_risk": 360.0},
    "intraocular_pressure_mmhg": {"normal": (12.0, 20.0), "high_risk": 22.0},
    "spherical_equivalent_diopters": {"normal": (-0.5, 0.5), "hyperopic_shift": 1.25}
}

class AstronautProfileGenerator:
    def __init__(self, seed: int = 42):
        np.random.seed(seed)

    def generate_patient(self, astronaut_id: str, trajectory_type: str = "normal") -> pd.DataFrame:
        age = np.random.randint(35, 56)
        sex = np.random.choice(["Male", "Female"], p=[0.7, 0.3])
        base_rnfl = np.random.normal(95.0, 4.0)
        base_choroid = np.random.normal(285.0, 15.0)
        base_iop = np.random.normal(15.0, 2.0)
        base_refraction = np.random.normal(0.0, 0.25)
        
        records = []
        for t_idx, timepoint in enumerate(MISSION_TIMELINES):
            flight_factor = 0.0 if timepoint == "L-30" else (t_idx * 1.5)
            if trajectory_type == "progressive_sans":
                rnfl = base_rnfl + (flight_factor * 4.2) + np.random.normal(0, 0.8)
                choroid = base_choroid + (flight_factor * 12.5) + np.random.normal(0, 2.0)
                iop = base_iop + (flight_factor * 1.1) + np.random.normal(0, 0.5)
                refraction = base_refraction + (flight_factor * 0.2) + np.random.normal(0, 0.05)
                clinical_flag = "At_Risk_SANS" if rnfl > CLINICAL_RANGES["rnfl_thickness_um"]["edema_risk"] else "Monitoring"
            else:
                rnfl = base_rnfl + np.random.normal(0, 0.9)
                choroid = base_choroid + np.random.normal(0, 3.0)
                iop = base_iop + np.random.normal(0, 0.6)
                refraction = base_refraction + np.random.normal(0, 0.05)
                clinical_flag = "Normal"

            records.append({
                "patient_id": astronaut_id,
                "age": age,
                "sex": sex,
                "timepoint": timepoint,
                "rnfl_thickness_um": round(float(rnfl), 2),
                "choroidal_thickness_um": round(float(choroid), 2),
                "iop_mmhg": round(float(iop), 2),
                "refraction_diopters": round(float(refraction), 2),
                "trajectory_profile": trajectory_type,
                "clinical_status": clinical_flag,
                "data_integrity_hash": str(uuid.uuid5(uuid.NAMESPACE_DNS, f"{astronaut_id}_{timepoint}"))[:8]
            })
        return pd.DataFrame(records)

def audit_cohort(df: pd.DataFrame) -> pd.DataFrame:
    audit_summary = []
    for patient_id, group in df.groupby("patient_id"):
        baseline = group[group["timepoint"] == "L-30"].iloc[0]
        final = group[group["timepoint"] == "L+120"].iloc[0]
        rnfl_delta = final["rnfl_thickness_um"] - baseline["rnfl_thickness_um"]
        choroid_delta = final["choroidal_thickness_um"] - baseline["choroidal_thickness_um"]
        status = "ALERT: Progressive SANS" if rnfl_delta > 15.0 or choroid_delta > 40.0 else "PASS: Stable"
        audit_summary.append({
            "patient_id": patient_id,
            "profile": baseline["trajectory_profile"],
            "rnfl_delta_um": round(rnfl_delta, 2),
            "choroid_delta_um": round(choroid_delta, 2),
            "audit_verdict": status
        })
    return pd.DataFrame(audit_summary)

if __name__ == "__main__":
    generator = AstronautProfileGenerator(seed=101)
    cohort = []
    for i in range(1, 6):
        cohort.append(generator.generate_patient(f"ASTRO-NORM-{i:02d}", "normal"))
        cohort.append(generator.generate_patient(f"ASTRO-SANS-{i:02d}", "progressive_sans"))
    dataset = pd.concat(cohort, ignore_index=True)
    dataset.to_csv("cdss_sans_synthetic_cohort.csv", index=False)
    report = audit_cohort(dataset)
    report.to_csv("cdss_audit_report.csv", index=False)
    print("Execution complete: Synthetic dataset and audit report generated.")
