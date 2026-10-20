"""ATS (Applicant Tracking System) Resume Checker module for SkillMatch AI.

Evaluates resume text for parseability, contact completeness, standard headings,
formatting hygiene, strong action verbs, quantifiable impact, and keyword density.
"""

from __future__ import annotations

import re
import unicodedata
from collections import Counter

from analyzer import (
    CATEGORY_OF,
    QUANTIFIED_PATTERN,
    SKILL_CATALOG,
    detect_sections,
    find_skills,
    normalize,
    split_resume_items,
)

# --------------------------------------------------------------------------- #
# Constants & Dictionaries
# --------------------------------------------------------------------------- #

STRONG_ACTION_VERBS = {
    # Engineering & Building
    "architected", "built", "designed", "developed", "engineered", "implemented",
    "programmed", "constructed", "created", "coded", "deployed", "refactored",
    "configured", "automated", "migrated", "integrated", "modeled", "trained",
    # Optimization & Impact
    "optimized", "accelerated", "boosted", "maximized", "minimized", "reduced",
    "increased", "improved", "scaled", "streamlined", "enhanced", "resolved",
    "eliminated", "consolidated", "upgraded", "transformed", "outperformed",
    # Leadership & Delivery
    "led", "directed", "managed", "spearheaded", "orchestrated", "supervised",
    "guided", "mentored", "delivered", "launched", "executed", "championed",
    # Research, Analysis & Testing
    "analyzed", "audited", "benchmarked", "diagnosed", "discovered", "evaluated",
    "formulated", "identified", "investigated", "tested", "validated", "verified",
}

WEAK_PASSIVE_PHRASES = [
    "responsible for",
    "duties included",
    "worked on",
    "helped with",
    "assisted in",
    "tasked with",
    "handled",
    "participated in",
    "involved in",
    "served as",
]

BUZZWORDS_CLICHES = [
    "hard worker",
    "team player",
    "fast learner",
    "quick learner",
    "results-driven",
    "results driven",
    "detail-oriented",
    "detail oriented",
    "self-motivated",
    "self motivated",
    "go-getter",
    "out of the box",
    "outside the box",
    "synergy",
    "strategic thinker",
    "work ethic",
    "dynamic",
    "thought leader",
]

STANDARD_REQUIRED_SECTIONS = [
    ("experience", "Work Experience / Experience", 8),
    ("skills", "Skills / Technical Skills", 7),
    ("education", "Education", 6),
    ("projects", "Projects", 4),
]

OPTIONAL_VALUABLE_SECTIONS = [
    ("summary", "Summary / Objective"),
    ("certifications", "Certifications / Awards"),
]


# --------------------------------------------------------------------------- #
# Contact & Header Parsing
# --------------------------------------------------------------------------- #

EMAIL_REGEX = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
PHONE_REGEX = re.compile(
    r"(?:\+?\d{1,3}[-.\s]?)?\(?\d{2,4}\)?[-.\s]?\d{3,4}[-.\s]?\d{3,4}"
)
LINKEDIN_REGEX = re.compile(r"linkedin\.com/(?:in|profile)/[\w-]+", re.I)
GITHUB_REGEX = re.compile(r"github\.com/[\w-]+", re.I)
PORTFOLIO_REGEX = re.compile(r"https?://(?:www\.)?[\w-]+\.(?:dev|io|me|com|tech|app|org)", re.I)


def extract_contact_info(text: str) -> dict[str, str | None]:
    """Finds contact information details in the resume."""
    lowered = normalize(text)
    
    # Email
    email_match = EMAIL_REGEX.search(text)
    email = email_match.group(0) if email_match else None

    # Phone
    phone = None
    for match in PHONE_REGEX.finditer(text):
        candidate = match.group(0).strip()
        # Filter out common false positives (like dates 2020-2024 or commit IDs)
        digits = re.sub(r"\D", "", candidate)
        if 8 <= len(digits) <= 15 and not (len(digits) == 8 and digits.startswith("20")):
            phone = candidate
            break

    # Profiles
    linkedin_match = LINKEDIN_REGEX.search(text)
    linkedin = linkedin_match.group(0) if linkedin_match else None

    github_match = GITHUB_REGEX.search(text)
    github = github_match.group(0) if github_match else None

    portfolio = None
    if not github:
        portfolio_match = PORTFOLIO_REGEX.search(text)
        if portfolio_match:
            portfolio = portfolio_match.group(0)

    # Location cues
    location = None
    loc_match = re.search(r"\b([A-Z][a-zA-Z\s]+,\s*[A-Z]{2}\b|[A-Z][a-zA-Z\s]+,\s*[A-Z][a-zA-Z]+)", text)
    if loc_match and len(loc_match.group(0).strip()) < 35:
        location = loc_match.group(0).strip()

    return {
        "email": email,
        "phone": phone,
        "linkedin": linkedin,
        "github": github or portfolio,
        "location": location,
    }


# --------------------------------------------------------------------------- #
# ATS Content & Formatting Audit
# --------------------------------------------------------------------------- #

def audit_action_verbs(text: str) -> dict:
    """Analyze the prevalence of strong action verbs vs weak/passive phrases."""
    items = split_resume_items(text)
    bullet_texts = [item[1] for item in items if item[0] in ("experience", "projects", "other")]
    
    found_strong = set()
    first_word_strong_count = 0
    total_bullets = len(bullet_texts)
    
    for b in bullet_texts:
        words = re.findall(r"\b[a-zA-Z]+(?:-[a-zA-Z]+)?\b", b.lower())
        if not words:
            continue
        first_word = words[0]
        if first_word in STRONG_ACTION_VERBS:
            first_word_strong_count += 1
            found_strong.add(first_word)
        for w in words:
            if w in STRONG_ACTION_VERBS:
                found_strong.add(w)

    # Check weak phrases
    lowered = normalize(text)
    found_weak = [p for p in WEAK_PASSIVE_PHRASES if p in lowered]
    found_buzzwords = [b for b in BUZZWORDS_CLICHES if b in lowered]

    return {
        "total_bullets": total_bullets,
        "strong_lead_count": first_word_strong_count,
        "strong_verbs_unique": sorted(found_strong),
        "weak_phrases_found": found_weak,
        "buzzwords_found": found_buzzwords,
        "action_density": (first_word_strong_count / max(total_bullets, 1)),
    }


def audit_formatting(text: str) -> dict:
    """Check word count, bullet lengths, and special characters that choke ATS parsers."""
    words = text.split()
    word_count = len(words)
    lines = [line.strip() for line in text.splitlines() if line.strip()]

    # Non-standard or special characters check
    # Many older ATS systems break on weird symbols or graphics
    problematic_chars = []
    for ch in text:
        category = unicodedata.category(ch)
        # So = Symbol, other (emojis, complex symbols)
        if category == "So" and ch not in "•●▪◦‣∙·*-–—►▶■□✓➢%#$&+=":
            if ch not in problematic_chars:
                problematic_chars.append(ch)

    items = split_resume_items(text)
    exp_project_bullets = [i[1] for i in items if i[0] in ("experience", "projects")]
    
    bullet_word_lengths = [len(b.split()) for b in exp_project_bullets]
    avg_bullet_len = round(sum(bullet_word_lengths) / max(len(bullet_word_lengths), 1), 1)
    
    # Quantified bullet check
    quantified_count = sum(
        1 for b in exp_project_bullets if QUANTIFIED_PATTERN.search(normalize(b))
    )

    return {
        "word_count": word_count,
        "line_count": len(lines),
        "bullet_count": len(exp_project_bullets),
        "avg_bullet_words": avg_bullet_len,
        "quantified_bullets": quantified_count,
        "quantified_ratio": (quantified_count / max(len(exp_project_bullets), 1)),
        "problematic_chars": problematic_chars,
    }


# --------------------------------------------------------------------------- #
# Full ATS Audit & Scoring Engine
# --------------------------------------------------------------------------- #

def check_ats(resume_text: str, job_text: str | None = None) -> dict:
    """Performs a comprehensive ATS compliance audit on the resume text."""
    contacts = extract_contact_info(resume_text)
    detected_secs = detect_sections(resume_text)
    verbs = audit_action_verbs(resume_text)
    format_info = audit_formatting(resume_text)
    skills_found = find_skills(resume_text)

    checks: list[dict] = []
    score = 0

    # 1. Contact Checks (Max 20 pts)
    # Email (8 pts)
    if contacts["email"]:
        score += 8
        checks.append({
            "category": "Contact Information",
            "name": "Professional Email Address",
            "status": "pass",
            "points": 8,
            "max_points": 8,
            "detail": f"Found valid contact email: {contacts['email']}",
        })
    else:
        checks.append({
            "category": "Contact Information",
            "name": "Professional Email Address",
            "status": "fail",
            "points": 0,
            "max_points": 8,
            "detail": "No contact email detected. ATS cannot create a candidate profile without an email.",
        })

    # Phone (6 pts)
    if contacts["phone"]:
        score += 6
        checks.append({
            "category": "Contact Information",
            "name": "Phone Number",
            "status": "pass",
            "points": 6,
            "max_points": 6,
            "detail": f"Found contact phone number: {contacts['phone']}",
        })
    else:
        checks.append({
            "category": "Contact Information",
            "name": "Phone Number",
            "status": "warning",
            "points": 0,
            "max_points": 6,
            "detail": "No phone number found. Recruiters frequently filter candidates by reachable phone number.",
        })

    # LinkedIn / Portfolio (6 pts)
    profile_found = contacts["linkedin"] or contacts["github"]
    if profile_found:
        score += 6
        detail_msg = []
        if contacts["linkedin"]:
            detail_msg.append(f"LinkedIn ({contacts['linkedin']})")
        if contacts["github"]:
            detail_msg.append(f"Portfolio/GitHub ({contacts['github']})")
        checks.append({
            "category": "Contact Information",
            "name": "Online Profile / Portfolio Link",
            "status": "pass",
            "points": 6,
            "max_points": 6,
            "detail": "Found: " + ", ".join(detail_msg),
        })
    else:
        checks.append({
            "category": "Contact Information",
            "name": "Online Profile / Portfolio Link",
            "status": "warning",
            "points": 2,
            "max_points": 6,
            "detail": "No LinkedIn or GitHub link found. Adding a profile URL boosts recruiter engagement by up to 70%.",
        })
        score += 2

    # 2. Standard Section Headers (Max 25 pts)
    for key, label, max_pts in STANDARD_REQUIRED_SECTIONS:
        if key in detected_secs:
            score += max_pts
            checks.append({
                "category": "Section Headers",
                "name": f"'{label}' Section",
                "status": "pass",
                "points": max_pts,
                "max_points": max_pts,
                "detail": f"Recognized standard ATS header for {label}.",
            })
        else:
            checks.append({
                "category": "Section Headers",
                "name": f"'{label}' Section",
                "status": "fail" if key in ("experience", "skills") else "warning",
                "points": 0,
                "max_points": max_pts,
                "detail": f"Missing standard '{label}' header. Non-standard titles (e.g. 'My Journey') confuse ATS parsers.",
            })

    # 3. Formatting & Length (Max 20 pts)
    wc = format_info["word_count"]
    if 350 <= wc <= 950:
        score += 8
        checks.append({
            "category": "Formatting & Length",
            "name": "Resume Length & Word Count",
            "status": "pass",
            "points": 8,
            "max_points": 8,
            "detail": f"Optimal length: {wc} words (ideal range: 350–900 words for 1–2 pages).",
        })
    elif 250 <= wc < 350 or 950 < wc <= 1250:
        score += 4
        checks.append({
            "category": "Formatting & Length",
            "name": "Resume Length & Word Count",
            "status": "warning",
            "points": 4,
            "max_points": 8,
            "detail": f"Length is {wc} words. Aim closer to 400–850 words to avoid looking sparse or overflowing pages.",
        })
    else:
        checks.append({
            "category": "Formatting & Length",
            "name": "Resume Length & Word Count",
            "status": "fail",
            "points": 1,
            "max_points": 8,
            "detail": f"Suboptimal length ({wc} words). Less than 250 words is too brief; over 1,250 words risks ATS truncation.",
        })
        score += 1

    # Bullet Count & Structure (6 pts)
    bc = format_info["bullet_count"]
    if bc >= 5:
        score += 6
        checks.append({
            "category": "Formatting & Length",
            "name": "Bullet Point Formatting",
            "status": "pass",
            "points": 6,
            "max_points": 6,
            "detail": f"Found {bc} bullet points across experience and projects. Parsers favor structured bullet points.",
        })
    else:
        checks.append({
            "category": "Formatting & Length",
            "name": "Bullet Point Formatting",
            "status": "warning",
            "points": 2,
            "max_points": 6,
            "detail": f"Only {bc} bullet items detected. Avoid dense narrative paragraphs; break duties into bullet points.",
        })
        score += 2

    # Clean character encoding & symbols (6 pts)
    bad_chars = format_info["problematic_chars"]
    if not bad_chars:
        score += 6
        checks.append({
            "category": "Formatting & Length",
            "name": "Character & Symbol Hygiene",
            "status": "pass",
            "points": 6,
            "max_points": 6,
            "detail": "Clean text encoding with no problematic emojis or proprietary graphic glyphs.",
        })
    else:
        checks.append({
            "category": "Formatting & Length",
            "name": "Character & Symbol Hygiene",
            "status": "warning",
            "points": 1,
            "max_points": 6,
            "detail": f"Found {len(bad_chars)} graphical emojis or non-standard symbols: {' '.join(bad_chars[:6])}. These can render as corrupt squares or question marks in ATS databases.",
        })
        score += 1

    # 4. Impact & Action Verbs (Max 25 pts)
    # Action verbs (13 pts)
    action_count = len(verbs["strong_verbs_unique"])
    if action_count >= 6 or verbs["action_density"] >= 0.4:
        score += 13
        checks.append({
            "category": "Impact & Action Verbs",
            "name": "Strong Action Verbs",
            "status": "pass",
            "points": 13,
            "max_points": 13,
            "detail": f"Found {action_count} distinct action verbs (e.g. {', '.join(verbs['strong_verbs_unique'][:5])}).",
        })
    elif action_count >= 3:
        score += 8
        checks.append({
            "category": "Impact & Action Verbs",
            "name": "Strong Action Verbs",
            "status": "warning",
            "points": 8,
            "max_points": 13,
            "detail": f"Found {action_count} action verbs. Start each bullet with strong verbs like 'Architected', 'Reduced', 'Deployed'.",
        })
    else:
        checks.append({
            "category": "Impact & Action Verbs",
            "name": "Strong Action Verbs",
            "status": "fail",
            "points": 3,
            "max_points": 13,
            "detail": "Few or no strong action verbs detected. Replace passive phrases with proactive action words.",
        })
        score += 3

    # Quantified results / numbers (12 pts)
    quant_count = format_info["quantified_bullets"]
    if quant_count >= 3 or format_info["quantified_ratio"] >= 0.35:
        score += 12
        checks.append({
            "category": "Impact & Action Verbs",
            "name": "Quantified Results & Metrics",
            "status": "pass",
            "points": 12,
            "max_points": 12,
            "detail": f"Found measurable metrics/numbers in {quant_count} bullets (percentages, performance stats, volume).",
        })
    elif quant_count >= 1:
        score += 6
        checks.append({
            "category": "Impact & Action Verbs",
            "name": "Quantified Results & Metrics",
            "status": "warning",
            "points": 6,
            "max_points": 12,
            "detail": f"Only {quant_count} bullet with metrics found. ATS and hiring managers prioritize measurable achievements (e.g. 'boosted throughput by 30%').",
        })
    else:
        checks.append({
            "category": "Impact & Action Verbs",
            "name": "Quantified Results & Metrics",
            "status": "fail",
            "points": 1,
            "max_points": 12,
            "detail": "No quantified impact detected. Add real metrics (%, $, user count, latency reduction) to validate claims.",
        })
        score += 1

    # 5. Tone & Passive Language Hygiene (Max 10 pts)
    weak_found = verbs["weak_phrases_found"]
    buzz_found = verbs["buzzwords_found"]
    
    deductions = (len(weak_found) * 2) + (len(buzz_found) * 2)
    tone_points = max(10 - deductions, 2)
    score += tone_points
    
    if not weak_found and not buzz_found:
        checks.append({
            "category": "Tone & Phrasing",
            "name": "Clean Proactive Tone",
            "status": "pass",
            "points": 10,
            "max_points": 10,
            "detail": "No passive phrases ('responsible for') or overused buzzwords detected.",
        })
    else:
        issues = []
        if weak_found:
            issues.append(f"Passive phrases to rephrase: {', '.join(weak_found[:3])}")
        if buzz_found:
            issues.append(f"Clichés/buzzwords to replace: {', '.join(buzz_found[:3])}")
        checks.append({
            "category": "Tone & Phrasing",
            "name": "Clean Proactive Tone",
            "status": "warning",
            "points": tone_points,
            "max_points": 10,
            "detail": " · ".join(issues),
        })

    # Final score normalization (ensure 0 <= score <= 100)
    score = max(0, min(100, score))

    if score >= 90:
        grade = "A"
        rating = "ATS Ready (Excellent)"
    elif score >= 80:
        grade = "B"
        rating = "ATS Compatible (Good)"
    elif score >= 65:
        grade = "C"
        rating = "Needs Optimization"
    else:
        grade = "D"
        rating = "High Risk of ATS Rejection"

    # Job match alignment (if job_text provided)
    job_alignment = None
    if job_text and job_text.strip():
        from analyzer import job_profile
        job = job_profile(job_text)
        total_weight = sum(info["weight"] for info in job.values())
        if total_weight > 0:
            hits = [s for s in job if s in skills_found]
            misses = [s for s in job if s not in skills_found]
            matched_weight = sum(job[s]["weight"] for s in hits)
            kw_match = round(100 * matched_weight / total_weight)
            job_alignment = {
                "match_rate": kw_match,
                "matched_keywords": hits,
                "missing_keywords": misses,
                "total_target_keywords": len(job),
            }

    return {
        "score": score,
        "grade": grade,
        "rating": rating,
        "checks": checks,
        "contacts": contacts,
        "detected_sections": sorted(detected_secs),
        "verbs": verbs,
        "format": format_info,
        "skills_detected": sorted(skills_found.keys()),
        "job_alignment": job_alignment,
    }


def build_ats_report(audit: dict) -> str:
    """Generates a downloadable plain text ATS audit report."""
    lines = [
        "SKILLMATCH AI - ATS RESUME AUDIT REPORT",
        "=" * 45,
        "",
        f"Overall ATS Score: {audit['score']}/100 (Grade: {audit['grade']})",
        f"Rating: {audit['rating']}",
        "",
        "SUMMARY METRICS",
        "-" * 20,
        f"Word Count: {audit['format']['word_count']} words",
        f"Bullet Points: {audit['format']['bullet_count']}",
        f"Quantified Bullets: {audit['format']['quantified_bullets']}",
        f"Action Verbs Detected: {len(audit['verbs']['strong_verbs_unique'])}",
        f"Technical Skills Detected: {len(audit['skills_detected'])}",
        "",
        "CONTACT DETAILS AUDIT",
        "-" * 20,
        f"Email: {audit['contacts']['email'] or 'MISSING'}",
        f"Phone: {audit['contacts']['phone'] or 'MISSING'}",
        f"LinkedIn: {audit['contacts']['linkedin'] or 'MISSING'}",
        f"Portfolio/GitHub: {audit['contacts']['github'] or 'MISSING'}",
        "",
        "SECTIONS FOUND",
        "-" * 20,
        ", ".join(audit['detected_sections']) or "None recognized",
        "",
        "DETAILED AUDIT CHECKS",
        "-" * 20,
    ]
    for check in audit["checks"]:
        tag = check["status"].upper()
        lines.append(f"[{tag}] {check['name']} ({check['points']}/{check['max_points']} pts)")
        lines.append(f"      {check['detail']}")
    
    if audit.get("job_alignment"):
        ja = audit["job_alignment"]
        lines += [
            "",
            "TARGET JOB KEYWORD ALIGNMENT",
            "-" * 30,
            f"ATS Keyword Match: {ja['match_rate']}%",
            f"Matched Keywords ({len(ja['matched_keywords'])}): {', '.join(ja['matched_keywords']) or 'None'}",
            f"Missing Critical Keywords ({len(ja['missing_keywords'])}): {', '.join(ja['missing_keywords']) or 'None'}",
        ]

    lines += [
        "",
        "RECOMMENDATIONS TO PASS ATS SCREENING:",
        "1. Ensure all 4 standard section headers (Experience, Skills, Education, Projects) are present.",
        "2. Begin every bullet point with a decisive action verb (e.g. Developed, Led, Architected).",
        "3. Include quantifiable outcomes (percentages, performance multipliers, user counts).",
        "4. Avoid complex multi-column tables, emojis, or unusual symbols that can cause parsing errors.",
    ]
    return "\n".join(lines)
