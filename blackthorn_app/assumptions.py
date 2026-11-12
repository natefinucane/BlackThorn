"""
ALL the numbers the model uses live in this file.

When new data arrives (your dad's cases, Nostra, a broker), change the numbers here.
You should never need to touch model.py or app.py to update the data.

Each block says where the number comes from:
  REAL        = taken from a published source
  ASSUMPTION  = a stated judgement, backed by some evidence
  PLACEHOLDER = a guess, to be replaced with real data
"""

# ---------------------------------------------------------------------------
# Simulation settings
# ---------------------------------------------------------------------------
N_YEARS = 100_000   # simulated years (rare events need lots)
SEED = 42           # fixed so results are repeatable

# ---------------------------------------------------------------------------
# Exchange rates
# ---------------------------------------------------------------------------
GBP_TO_EUR = 1 / 0.836   # REAL: 11 Nov 2026, €1 = £0.836
USD_TO_EUR = 0.87        # ASSUMPTION: approximate, check current rate

# ---------------------------------------------------------------------------
# Firm size bands (staff numbers)
# ---------------------------------------------------------------------------
def size_band(staff):
    if staff < 10:
        return "micro"
    if staff < 50:
        return "small"
    if staff < 250:
        return "medium"
    return "large"

# ---------------------------------------------------------------------------
# SERIOUS incidents: how often
# REAL: Eurostat isoc_cisce_ic, Ireland 2024 (CSO survey, table ICA81).
# Serious = outside attack knocking out services + data destroyed by malware/intrusion
#           + data leaked through intrusion/phishing/deliberate staff action.
# Micro firms aren't surveyed: ASSUMPTION small x 42/46 (UK micro/small ratio).
# ---------------------------------------------------------------------------
SERIOUS_PCT_BY_SIZE = {
    "small": 1.21 + 0.62 + 0.34,
    "medium": 1.19 + 1.48 + 2.35,
    "large": 1.51 + 0.85 + 2.16,
}
SERIOUS_PCT_BY_SIZE["micro"] = SERIOUS_PCT_BY_SIZE["small"] * 42 / 46

# ASSUMPTION: survey under-counts because firms without monitoring don't notice.
# Evidence: ESRI 2024 back-calculation (about 2.4), Ireland vs EU gap (about 2.6). Set to 1.0 to switch off.
UNDER_REPORTING = 2.0

# REAL: Eurostat isoc_cisce_icn2, Ireland 2024, % of firms with ANY incident, by sector.
# ASSUMPTION: the sector pattern for malicious incidents is the same.
ANY_INCIDENT_PCT_ALL_SECTORS = 13.32
ANY_INCIDENT_PCT_BY_SECTOR = {
    "manufacturing": 17.23,
    "energy": 23.33,
    "water_waste": 9.46,
    "construction": 8.06,
    "wholesale_retail": 13.60,
    "transport": 13.11,
    "accommodation_food": 9.34,
    "information_communication": 19.86,
    "real_estate": 14.44,
    "professional_services": 19.83,
    "admin_support": 11.03,
}
SECTOR_LABELS = {
    "information_communication": "IT, software and telecoms",
    "professional_services": "Professional services (legal, accounting, consulting)",
    "manufacturing": "Manufacturing",
    "wholesale_retail": "Wholesale and retail",
    "construction": "Construction",
    "transport": "Transport and logistics",
    "accommodation_food": "Hospitality (accommodation and food)",
    "real_estate": "Property and real estate",
    "admin_support": "Admin and support services",
    "energy": "Energy",
    "water_waste": "Water and waste",
}

# ---------------------------------------------------------------------------
# SERIOUS incidents: how much
# REAL: NetDiligence Cyber Claims Study 2026, "Nano-Rev" band (under $50M revenue):
#       3,872 claims, average $141K, largest $10.4M. Median fitted from the largest claim.
# ---------------------------------------------------------------------------
ND_MEAN_USD = 141_000
ND_MAX_USD = 10_400_000
ND_CLAIMS = 3_872

# ASSUMPTION: scale costs to firm size, (turnover / reference) ** exponent
REFERENCE_TURNOVER_EUR = 9_000_000
SIZE_EXPONENT = 0.4

# ---------------------------------------------------------------------------
# MINOR incidents
# REAL: UK Cyber Security Breaches Survey 2025/26 (breach rates) and 2024/25 (costs).
# ---------------------------------------------------------------------------
UK_BREACH_RATE_BY_SIZE = {"micro": 0.42, "small": 0.46, "medium": 0.65, "large": 0.69}
SHARE_WITH_A_COST = 1_600 / 3_550     # mean cost all / mean cost excluding £0
MINOR_MEDIAN_GBP = 560
MINOR_MEAN_GBP = 3_550

# ---------------------------------------------------------------------------
# CONTROLS
# ---------------------------------------------------------------------------
CONTROLS = ["mfa", "offline_backups", "staff_training", "patching",
            "endpoint_protection", "incident_plan"]

CONTROL_LABELS = {
    "mfa": "Two-step login (MFA) on ALL email, remote access and admin accounts",
    "offline_backups": "Backups ransomware can't reach (offline or immutable), tested",
    "staff_training": "Security / phishing training for all staff at least yearly",
    "patching": "Serious security updates installed within 7 days",
    "endpoint_protection": "Monitoring that spots suspicious activity (beyond basic antivirus)",
    "incident_plan": "Written, tested plan for what to do if hit",
}
CONTROL_SHORT = {
    "mfa": "MFA everywhere",
    "offline_backups": "Offline backups",
    "staff_training": "Staff training",
    "patching": "Fast patching",
    "endpoint_protection": "Monitoring",
    "incident_plan": "Incident plan",
}
CONTROL_ACTION = {
    "mfa": "Turn on two-step login (MFA) for every account: email, remote access and admin",
    "offline_backups": "Set up backups that ransomware can't reach (offline or immutable) and test a restore",
    "staff_training": "Run phishing and security training for all staff, at least once a year",
    "patching": "Install serious security updates within 7 days (automatic updates where possible)",
    "endpoint_protection": "Add monitoring that alerts you to suspicious activity, not just antivirus",
    "incident_plan": "Write a one-page plan for what to do if you're hit, and rehearse it once",
}

# REAL: Marsh McLennan (2023) signal strength = claim rate without / with the control.
MARSH_SIGNAL = {"mfa": 1.44, "staff_training": 1.76, "patching": 2.19,
                "endpoint_protection": 1.67, "incident_plan": 1.15, "offline_backups": 1.0}
# ASSUMPTION: controls overlap, so effects are dampened. 1.0 = no dampening.
DAMPING = 0.5

# PLACEHOLDER: how much each control cuts COSTS when something happens.
SEVERITY_EFFECT = {"mfa": 1.00, "offline_backups": 0.50, "staff_training": 1.00,
                   "patching": 1.00, "endpoint_protection": 0.90, "incident_plan": 0.75}

# PLACEHOLDER: yearly cost (fixed €, € per staff member)
YEARLY_COST = {"mfa": (0, 40), "offline_backups": (1200, 0), "staff_training": (300, 40),
               "patching": (600, 15), "endpoint_protection": (0, 60), "incident_plan": (800, 0)}

# Share of Irish firms with each control.
# micro: REAL, MTU / NCSC SME Cyber Resilience 2025 (strict definitions; monitoring uses small)
# small-large: REAL, Eurostat isoc_cisce_ra Ireland 2024; patching ASSUMPTION (stricter 7-day definition)
ADOPTION_BY_SIZE = {
    "mfa":                 {"micro": 0.26,  "small": 0.381, "medium": 0.659, "large": 0.888},
    "offline_backups":     {"micro": 0.23,  "small": 0.574, "medium": 0.811, "large": 0.914},
    "staff_training":      {"micro": 0.26,  "small": 0.175, "medium": 0.484, "large": 0.818},
    "patching":            {"micro": 0.37,  "small": 0.45,  "medium": 0.65,  "large": 0.85},
    "endpoint_protection": {"micro": 0.311, "small": 0.311, "medium": 0.587, "large": 0.835},
    "incident_plan":       {"micro": 0.33,  "small": 0.410, "medium": 0.649, "large": 0.929},
}

# ---------------------------------------------------------------------------
# DOWNTIME if a serious incident happens
# REAL: Sophos State of Ransomware in the UK 2026 (firms of 100 to 5,000 staff)
# ---------------------------------------------------------------------------
DOWNTIME_PROFILE = [("Back within a week", 0.55),
                    ("One week to one month", 0.29),
                    ("One to six months", 0.16)]

# ---------------------------------------------------------------------------
# GRADES: 1-in-100 year loss as a share of turnover. PLACEHOLDER thresholds.
# ---------------------------------------------------------------------------
GRADE_THRESHOLDS = [("A", 0.02), ("B", 0.05), ("C", 0.10), ("D", 0.20)]   # else E
GRADE_MEANING = {
    "A": "Low risk. A disaster year would cost under 2% of turnover.",
    "B": "Moderate risk. A disaster year would cost 2 to 5% of turnover.",
    "C": "Elevated risk. A disaster year would cost 5 to 10% of turnover.",
    "D": "High risk. A disaster year would cost 10 to 20% of turnover.",
    "E": "Severe risk. A disaster year could cost over 20% of turnover.",
}
