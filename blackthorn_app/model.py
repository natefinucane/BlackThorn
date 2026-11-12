"""
The calculations. All numbers come from assumptions.py.
"""
import copy
import numpy as np
from scipy.stats import norm

import assumptions as A


# ---------- serious-incident cost distribution (fitted once) ----------
def _fit_serious():
    z_max = norm.ppf(1 - 1 / (A.ND_CLAIMS + 1))
    gap = np.log(A.ND_MAX_USD) - np.log(A.ND_MEAN_USD)
    sigma = z_max - np.sqrt(z_max ** 2 - 2 * gap)
    mu = np.log(A.ND_MEAN_USD) - sigma ** 2 / 2 + np.log(A.USD_TO_EUR)
    return mu, sigma

SERIOUS_MU, SERIOUS_SIGMA = _fit_serious()


# ---------- controls ----------
def freq_effect(control):
    return (1 / A.MARSH_SIGNAL[control]) ** A.DAMPING


def control_adjustment(biz, kind):
    """Multiplier vs the average Irish firm of the same size. kind = 'freq' or 'sev'."""
    band = A.size_band(biz["staff"])
    m = 1.0
    for c, has_it in biz["controls"].items():
        effect = freq_effect(c) if kind == "freq" else A.SEVERITY_EFFECT[c]
        a = A.ADOPTION_BY_SIZE[c][band]
        m *= (effect if has_it else 1.0) / (a * effect + (1 - a))
    return m


def control_cost(control, staff):
    fixed, per_staff = A.YEARLY_COST[control]
    return fixed + per_staff * staff


# ---------- frequency and severity ----------
def rates(biz):
    band = A.size_band(biz["staff"])
    sector = A.ANY_INCIDENT_PCT_BY_SECTOR[biz["sector"]] / A.ANY_INCIDENT_PCT_ALL_SECTORS
    adj = sector * control_adjustment(biz, "freq")
    p_minor = min(A.UK_BREACH_RATE_BY_SIZE[band] * A.SHARE_WITH_A_COST, 0.99)
    p_serious = A.SERIOUS_PCT_BY_SIZE[band] / 100
    minor_rate = -np.log(1 - p_minor) * adj
    serious_rate = -np.log(1 - p_serious) * A.UNDER_REPORTING * adj
    return minor_rate, serious_rate


def size_scale(biz):
    return (biz["turnover"] / A.REFERENCE_TURNOVER_EUR) ** A.SIZE_EXPONENT


def severity(biz):
    sev_adj = control_adjustment(biz, "sev")
    m_median = A.MINOR_MEDIAN_GBP * A.GBP_TO_EUR
    m_mean = A.MINOR_MEAN_GBP * A.GBP_TO_EUR
    m_sigma = np.sqrt(2 * np.log(m_mean / m_median))
    m_mu = np.log(m_median * sev_adj)
    s_mu = SERIOUS_MU + np.log(sev_adj) + np.log(size_scale(biz))
    return (m_mu, m_sigma), (s_mu, SERIOUS_SIGMA)


# ---------- simulation ----------
def _tier(rng, rate, mu, sigma, n):
    counts = rng.poisson(rate, n)
    costs = rng.lognormal(mu, sigma, counts.sum())
    total = np.zeros(n)
    np.add.at(total, np.repeat(np.arange(n), counts), costs)
    return total


def simulate(biz, n_years=A.N_YEARS, seed=A.SEED):
    rng = np.random.default_rng(seed)
    minor_rate, serious_rate = rates(biz)
    (m_mu, m_sig), (s_mu, s_sig) = severity(biz)
    minor = _tier(rng, minor_rate, m_mu, m_sig, n_years)
    serious = _tier(rng, serious_rate, s_mu, s_sig, n_years)
    return minor, serious


def grade(p99_loss, turnover):
    r = p99_loss / turnover
    for g, limit in A.GRADE_THRESHOLDS:
        if r < limit:
            return g
    return "E"


# ---------- the full rating ----------
def rate_business(biz):
    minor, serious = simulate(biz)
    losses = minor + serious
    expected = losses.mean()
    p95 = np.percentile(losses, 95)
    p99 = np.percentile(losses, 99)
    _, serious_rate = rates(biz)
    p_serious = 1 - np.exp(-serious_rate)

    fixes = []
    for c, has_it in biz["controls"].items():
        if has_it:
            continue
        test = copy.deepcopy(biz)
        test["controls"][c] = True
        m2, s2 = simulate(test)
        new = m2 + s2
        cost = control_cost(c, biz["staff"])
        saving = expected - new.mean()
        fixes.append({
            "control": c,
            "saving": saving,
            "p99_cut": p99 - np.percentile(new, 99),
            "cost": cost,
            "return": saving / cost if cost else float("inf"),
            "new_grade": grade(np.percentile(new, 99), biz["turnover"]),
        })
    fixes.sort(key=lambda f: f["p99_cut"], reverse=True)

    # What if they did every fix?
    all_on = copy.deepcopy(biz)
    all_on["controls"] = {c: True for c in biz["controls"]}
    m3, s3 = simulate(all_on)
    all_losses = m3 + s3
    all_fixed = {
        "expected": all_losses.mean(),
        "p99": np.percentile(all_losses, 99),
        "grade": grade(np.percentile(all_losses, 99), biz["turnover"]),
        "cost": sum(f["cost"] for f in fixes),
    }

    # Step-down: worst-case year as each fix is added, in ranked order
    stepdown = [{"label": "Today", "control": None, "p99": p99, "grade": grade(p99, biz["turnover"])}]
    running = copy.deepcopy(biz)
    for f in fixes:
        running["controls"][f["control"]] = True
        m4, s4 = simulate(running)
        q = np.percentile(m4 + s4, 99)
        stepdown.append({"label": f["control"], "control": f["control"], "p99": q,
                         "grade": grade(q, biz["turnover"])})

    band = A.size_band(biz["staff"])
    return {
        "stepdown": stepdown,
        "losses": losses,
        "expected": expected,
        "expected_minor": minor.mean(),
        "expected_serious": serious.mean(),
        "p95": p95,
        "p99": p99,
        "p99_share": p99 / biz["turnover"],
        "no_loss_share": (losses == 0).mean(),
        "grade": grade(p99, biz["turnover"]),
        "p_serious": p_serious,
        "p_long_outage": p_serious * (1 - A.DOWNTIME_PROFILE[0][1]),
        "freq_vs_avg": control_adjustment(biz, "freq"),
        "sev_vs_avg": control_adjustment(biz, "sev"),
        "fixes": fixes,
        "all_fixed": all_fixed,
        "adoption": {c: A.ADOPTION_BY_SIZE[c][band] for c in A.CONTROLS},
        "band": band,
    }
