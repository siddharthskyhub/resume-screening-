"""Multi-job skill-gap analysis: which gaps matter most across ALL target jobs?"""

from __future__ import annotations

from analyzer import (
    CATEGORY_OF,
    extract_evidence,
    find_skills,
    job_profile,
    score_against,
)

# How much of a skill's demand still counts as a "gap" given its evidence level.
# Missing = full gap, listed-only = half a gap (claimed but unproven).
GAP_FACTOR = {"missing": 1.0, "listed": 0.5, "demonstrated": 0.0, "strong": 0.0}


def analyze_jobs(resume_text: str, jobs: dict[str, str]) -> dict:
    """Compare one resume against many jobs.

    Returns per-job scores, a skill table ranked by gap priority, and the gaps.
    """
    resume_found = find_skills(resume_text)
    evidence = extract_evidence(resume_text)
    profiles = {name: job_profile(text) for name, text in jobs.items()}
    n_jobs = len(profiles)

    per_job = {}
    for name, job in profiles.items():
        keyword, proven = score_against(job, resume_found, evidence)
        ordered = sorted(job, key=lambda s: (-job[s]["weight"], s))
        per_job[name] = {
            "score": keyword,
            "evidence_score": proven,
            "n_skills": len(job),
            "matched": [s for s in ordered if s in resume_found],
            "missing": [s for s in ordered if s not in resume_found],
        }

    rows = []
    for skill in sorted({s for p in profiles.values() for s in p}):
        present = {n: p[skill] for n, p in profiles.items() if skill in p}
        if skill in resume_found:
            status = evidence.get(skill, {}).get("level", "listed")
        else:
            status = "missing"

        weight = sum(info["weight"] for info in present.values())
        rows.append({
            "skill": skill,
            "category": CATEGORY_OF[skill],
            "status": status,
            "demand": len(present),
            "n_jobs": n_jobs,
            "required": sum(1 for i in present.values() if i["level"] == "required"),
            "priority": round(weight * GAP_FACTOR[status], 2),
            "per_job": {
                n: (profiles[n][skill]["level"] if skill in profiles[n] else None)
                for n in profiles
            },
        })

    rows.sort(key=lambda r: (-r["priority"], -r["demand"], r["skill"]))
    gaps = [r for r in rows if r["priority"] > 0]

    scores = [j["evidence_score"] for j in per_job.values() if j["evidence_score"] is not None]
    avg = round(sum(scores) / len(scores)) if scores else None

    return {
        "jobs": per_job,
        "skills": rows,
        "gaps": gaps,
        "avg_evidence_score": avg,
        "resume_skills": resume_found,
        "evidence": evidence,
    }
