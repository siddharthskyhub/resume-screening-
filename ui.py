"""Shared Streamlit helpers: the visual system, small components, and the resume loader.

Design system: Modern, responsive, colorful SaaS UI with refined typography,
colorful pill badges, card accents, and responsive layouts across all devices.
"""

import html
import re

import streamlit as st

from analyzer import ResumeError, extract_text

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Bricolage+Grotesque:wght@600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

:root {
    --ink: #0f172a;
    --ink-light: #1e293b;
    --muted: #64748b;
    --subtle: #94a3b8;
    --line: #e2e8f0;
    --line-subtle: #f1f5f9;
    --card-bg: #ffffff;
    --canvas: #f8fafc;

    /* Vibrant Brand & Accents */
    --primary: #4f46e5;
    --primary-hover: #4338ca;
    --primary-light: #eef2ff;
    --primary-border: #c7d2fe;
    --primary-glow: rgba(79, 70, 229, 0.18);
    --primary-gradient: linear-gradient(135deg, #6366f1 0%, #4f46e5 50%, #3b82f6 100%);

    /* Colorful Status Palettes */
    --green-bg: #ecfdf5;
    --green-text: #047857;
    --green-border: #a7f3d0;
    --green-strong: #10b981;
    --green-gradient: linear-gradient(135deg, #10b981 0%, #059669 100%);

    --yellow-bg: #fffbeb;
    --yellow-text: #b45309;
    --yellow-border: #fde68a;
    --yellow-strong: #f59e0b;
    --yellow-gradient: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);

    --red-bg: #fff1f2;
    --red-text: #be123c;
    --red-border: #fecdd3;
    --red-strong: #f43f5e;
    --red-gradient: linear-gradient(135deg, #f43f5e 0%, #e11d48 100%);

    --blue-bg: #eff6ff;
    --blue-text: #1d4ed8;
    --blue-border: #bfdbfe;
    --blue-strong: #3b82f6;

    --purple-bg: #faf5ff;
    --purple-text: #7e22ce;
    --purple-border: #e9d5ff;
    --purple-strong: #a855f7;
    --purple-gradient: linear-gradient(135deg, #a855f7 0%, #7c3aed 100%);

    --cyan-bg: #ecfeff;
    --cyan-text: #0e7490;
    --cyan-border: #a5f3fc;
    --cyan-strong: #06b6d4;

    --display: 'Plus Jakarta Sans', 'Bricolage Grotesque', system-ui, sans-serif;
    --sans: 'Plus Jakarta Sans', system-ui, -apple-system, sans-serif;
    --mono: 'JetBrains Mono', monospace;

    --radius-sm: 8px;
    --radius-md: 12px;
    --radius-lg: 16px;
    --radius-full: 9999px;

    --shadow-xs: 0 1px 2px 0 rgba(15, 23, 42, 0.04);
    --shadow-sm: 0 1px 3px 0 rgba(15, 23, 42, 0.06), 0 1px 2px -1px rgba(15, 23, 42, 0.04);
    --shadow-md: 0 4px 6px -1px rgba(15, 23, 42, 0.08), 0 2px 4px -2px rgba(15, 23, 42, 0.05);
    --shadow-lg: 0 10px 15px -3px rgba(15, 23, 42, 0.08), 0 4px 6px -4px rgba(15, 23, 42, 0.04);
    --shadow-colored: 0 4px 14px rgba(79, 70, 229, 0.25);
}

/* ---------- Global Reset & Atmosphere ---------- */
html, body, .stApp {
    font-family: var(--sans);
    color: var(--ink);
    background: linear-gradient(180deg, #f8fafc 0%, #f1f5f9 100%);
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
}

.block-container {
    padding-top: 1.8rem !important;
    padding-bottom: 3.5rem !important;
    max-width: 1180px !important;
    margin: 0 auto;
}

header[data-testid="stHeader"] {
    background: transparent;
}
footer {
    visibility: hidden;
}

h1, h2, h3, h4 {
    font-family: var(--display) !important;
    color: var(--ink);
    letter-spacing: -0.025em;
    font-weight: 700;
}
h1 { font-size: 2.2rem !important; line-height: 1.2 !important; }
h2 { font-size: 1.55rem !important; margin-top: 1.2rem !important; }
h3 { font-size: 1.22rem !important; }

/* ---------- Buttons & Interactive Controls ---------- */
div.stButton > button {
    border-radius: var(--radius-sm);
    font-weight: 600;
    font-size: 0.92rem;
    letter-spacing: -0.01em;
    padding: 0.5rem 1.15rem;
    transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
    box-shadow: var(--shadow-xs);
    border: 1px solid var(--line);
    background: #ffffff;
    color: var(--ink);
}
div.stButton > button:hover {
    border-color: #cbd5e1;
    background: #f8fafc;
    transform: translateY(-1px);
    box-shadow: var(--shadow-sm);
}
div.stButton > button:active {
    transform: translateY(0);
}

div.stButton > button[kind="primary"] {
    background: var(--primary-gradient) !important;
    border: 1px solid rgba(255, 255, 255, 0.25) !important;
    color: #ffffff !important;
    box-shadow: var(--shadow-colored) !important;
}
div.stButton > button[kind="primary"]:hover {
    background: linear-gradient(135deg, #4f46e5 0%, #3730a3 100%) !important;
    box-shadow: 0 6px 18px rgba(79, 70, 229, 0.4) !important;
    transform: translateY(-1.5px);
}

div.stDownloadButton > button {
    border-radius: var(--radius-sm);
    font-weight: 600;
    background: #ffffff;
    border: 1px solid var(--primary-border);
    color: var(--primary);
    transition: all 0.2s ease;
}
div.stDownloadButton > button:hover {
    background: var(--primary-light);
    border-color: var(--primary);
    transform: translateY(-1px);
    box-shadow: var(--shadow-sm);
}

/* Expanders */
[data-testid="stExpander"] details {
    border: 1px solid var(--line) !important;
    border-radius: var(--radius-md) !important;
    background: #ffffff !important;
    box-shadow: var(--shadow-xs);
    transition: box-shadow 0.2s ease, border-color 0.2s ease;
}
[data-testid="stExpander"] details:hover {
    border-color: #cbd5e1;
    box-shadow: var(--shadow-sm);
}
[data-testid="stExpander"] summary {
    font-weight: 600;
    font-size: 0.95rem;
    color: var(--ink);
    padding: 12px 16px !important;
}

/* File Uploader Dropzone */
[data-testid="stFileUploaderDropzone"] {
    border: 2px dashed #cbd5e1 !important;
    border-radius: var(--radius-md) !important;
    background: #ffffff !important;
    padding: 22px 16px !important;
    transition: all 0.2s ease;
}
[data-testid="stFileUploaderDropzone"]:hover {
    border-color: var(--primary) !important;
    background: var(--primary-light) !important;
}

/* Colorful Tabs */
.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
    border-bottom: 2px solid var(--line);
    padding-bottom: 4px;
}
.stTabs [data-baseweb="tab"] {
    font-weight: 600;
    font-size: 0.94rem;
    color: var(--muted);
    border-radius: var(--radius-sm);
    padding: 8px 16px;
    border: none !important;
    transition: all 0.2s ease;
}
.stTabs [data-baseweb="tab"]:hover {
    color: var(--primary);
    background: rgba(238, 242, 255, 0.7);
}
.stTabs [aria-selected="true"] {
    color: var(--primary) !important;
    background: var(--primary-light) !important;
    border-bottom: 2px solid var(--primary) !important;
}

/* Vibrant Progress Bar */
.stProgress > div > div > div > div {
    background: linear-gradient(90deg, #6366f1 0%, #3b82f6 50%, #10b981 100%) !important;
    border-radius: var(--radius-full);
}

/* Form Inputs */
input[type="text"], textarea, [data-baseweb="select"] {
    border-radius: var(--radius-sm) !important;
    border-color: var(--line) !important;
    font-family: var(--sans) !important;
}
input[type="text"]:focus, textarea:focus {
    border-color: var(--primary) !important;
    box-shadow: 0 0 0 3px var(--primary-glow) !important;
}

/* ---------- Sidebar Branding & Live Indicator ---------- */
[data-testid="stSidebar"] {
    background: #ffffff;
    border-right: 1px solid var(--line);
}
.brand-container {
    padding: 6px 0 14px;
}
.brand-header {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 6px;
}
.brand-logo {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 42px;
    height: 42px;
    background: var(--primary-gradient);
    border-radius: 12px;
    color: white;
    font-size: 1.35rem;
    box-shadow: 0 4px 12px rgba(79, 70, 229, 0.35);
}
.brand-text {
    font-family: var(--display);
    font-weight: 800;
    font-size: 1.4rem;
    background: var(--primary-gradient);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    letter-spacing: -0.025em;
    line-height: 1.1;
}
.brand-sub {
    color: var(--muted);
    font-size: 0.85rem;
    line-height: 1.4;
    margin-top: 4px;
}
.sidebar-status-card {
    background: var(--canvas);
    border: 1px solid var(--line);
    border-radius: var(--radius-md);
    padding: 10px 14px;
    margin: 12px 0 10px;
    display: flex;
    align-items: center;
    gap: 10px;
    box-shadow: var(--shadow-xs);
}
.status-indicator {
    width: 10px;
    height: 10px;
    border-radius: 50%;
    flex-shrink: 0;
}
.status-indicator.active {
    background: var(--green-strong);
    box-shadow: 0 0 0 4px rgba(16, 185, 129, 0.25);
}
.status-indicator.idle {
    background: var(--subtle);
}
.sidebar-status-info {
    overflow: hidden;
    line-height: 1.3;
}
.sidebar-status-title {
    font-size: 0.84rem;
    font-weight: 700;
    color: var(--ink);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}
.sidebar-status-sub {
    font-size: 0.75rem;
    color: var(--muted);
}

/* ---------- Page Header (Hero) ---------- */
.page-head {
    padding: 6px 0 20px;
    border-bottom: 1px solid var(--line);
    margin-bottom: 24px;
}
.page-head-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 4px 12px;
    background: var(--primary-light);
    color: var(--primary);
    border: 1px solid var(--primary-border);
    border-radius: var(--radius-full);
    font-size: 0.8rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-bottom: 10px;
}
.page-head h1 {
    font-size: 2.15rem !important;
    line-height: 1.2 !important;
    font-weight: 800 !important;
    margin: 0 0 8px !important;
    color: var(--ink) !important;
    letter-spacing: -0.03em !important;
}
.page-head p {
    color: var(--muted);
    font-size: 1.05rem;
    margin: 0;
    max-width: 68ch;
    line-height: 1.55;
}

/* ---------- Colorful Stats Cards Grid ---------- */
.stats-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
    gap: 14px;
    margin-bottom: 16px;
}
.stat-card {
    background: #ffffff;
    border: 1px solid var(--line);
    border-radius: var(--radius-md);
    padding: 16px 20px;
    box-shadow: var(--shadow-xs);
    position: relative;
    overflow: hidden;
    transition: transform 0.2s cubic-bezier(0.16, 1, 0.3, 1), box-shadow 0.2s ease, border-color 0.2s ease;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
}
.stat-card::before {
    content: "";
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 3px;
    background: var(--stat-c, var(--primary));
}
.stat-card:nth-child(1) { --stat-c: #4f46e5; }
.stat-card:nth-child(2) { --stat-c: #06b6d4; }
.stat-card:nth-child(3) { --stat-c: #10b981; }
.stat-card:nth-child(4) { --stat-c: #f59e0b; }
.stat-card:nth-child(5) { --stat-c: #8b5cf6; }

.stat-card:hover {
    transform: translateY(-2px);
    box-shadow: var(--shadow-md);
    border-color: #cbd5e1;
}
.stat-label {
    color: var(--muted);
    font-size: 0.8rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-bottom: 6px;
}
.stat-value {
    font-family: var(--display);
    font-size: 1.85rem;
    font-weight: 800;
    color: var(--ink);
    line-height: 1.15;
    letter-spacing: -0.025em;
}

/* ---------- Panels / Cards ---------- */
.panel {
    background: #ffffff;
    border: 1px solid var(--line);
    border-radius: var(--radius-md);
    padding: 20px 22px;
    margin-bottom: 14px;
    box-shadow: var(--shadow-xs);
    transition: box-shadow 0.2s ease, border-color 0.2s ease;
}
.panel:hover {
    box-shadow: var(--shadow-sm);
    border-color: #cbd5e1;
}
.panel h3 {
    font-size: 1.15rem !important;
    margin: 0 0 3px !important;
    color: var(--ink);
    font-weight: 700;
}
.panel-sub {
    color: var(--muted);
    font-size: 0.88rem;
    margin: 0 0 14px;
    line-height: 1.4;
}
.empty {
    color: var(--muted);
    font-style: italic;
    font-size: 0.92rem;
}

/* ---------- Colorful Pill Badges ---------- */
.mk {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    margin: 3px 6px 5px 0;
    padding: 4px 11px;
    font-weight: 600;
    font-size: 0.86rem;
    border-radius: var(--radius-full);
    line-height: 1.4;
    transition: transform 0.15s ease, box-shadow 0.15s ease;
    white-space: nowrap;
}
.mk:hover {
    transform: translateY(-1px);
    box-shadow: var(--shadow-xs);
}

.mk.matched {
    background: var(--green-bg);
    color: var(--green-text);
    border: 1px solid var(--green-border);
}
.mk.matched::before {
    content: "✓";
    font-size: 0.8rem;
    font-weight: 800;
    color: var(--green-strong);
}

.mk.unproven {
    background: var(--yellow-bg);
    color: var(--yellow-text);
    border: 1px solid var(--yellow-border);
}
.mk.unproven::before {
    content: "●";
    font-size: 0.68rem;
    color: var(--yellow-strong);
}

.mk.missing {
    background: var(--red-bg);
    color: var(--red-text);
    border: 1px solid var(--red-border);
}
.mk.missing::before {
    content: "✕";
    font-size: 0.74rem;
    font-weight: 800;
    color: var(--red-strong);
}

.mk.preferred {
    background: var(--blue-bg);
    color: var(--blue-text);
    border: 1px dashed var(--blue-border);
    font-weight: 500;
}
.mk.preferred::before {
    content: "○";
    font-size: 0.72rem;
    color: var(--blue-strong);
}

.mk.extra {
    background: var(--purple-bg);
    color: var(--purple-text);
    border: 1px solid var(--purple-border);
}
.mk.extra::before {
    content: "★";
    font-size: 0.76rem;
    color: var(--purple-strong);
}

.legend {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 6px 10px;
    margin: 6px 0 16px;
    padding: 10px 14px;
    background: rgba(241, 245, 249, 0.8);
    border-radius: var(--radius-md);
    border: 1px solid var(--line);
}
.legend .mk {
    font-size: 0.82rem;
    margin: 0;
    padding: 3px 9px;
}

/* ---------- Evidence & Proof Bar Card ---------- */
.proof {
    background: #ffffff;
    border: 1px solid var(--line);
    border-radius: var(--radius-lg);
    padding: 24px 28px;
    margin-bottom: 16px;
    box-shadow: var(--shadow-sm);
    position: relative;
    overflow: hidden;
}
.proof-top {
    display: flex;
    align-items: baseline;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 12px;
}
.proof-score-group {
    display: flex;
    align-items: baseline;
    gap: 14px;
}
.proof-num {
    font-family: var(--display);
    font-size: 3.5rem;
    font-weight: 800;
    color: var(--ink);
    line-height: 1;
    letter-spacing: -0.04em;
}
.proof-label {
    color: var(--muted);
    font-size: 1.05rem;
    font-weight: 600;
}
.proof-badge {
    display: inline-flex;
    align-items: center;
    padding: 5px 14px;
    border-radius: var(--radius-full);
    font-size: 0.85rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.04em;
}
.proof-badge.fit-high {
    background: var(--green-bg);
    color: var(--green-text);
    border: 1px solid var(--green-border);
}
.proof-badge.fit-mid {
    background: var(--blue-bg);
    color: var(--blue-text);
    border: 1px solid var(--blue-border);
}
.proof-badge.fit-low {
    background: var(--yellow-bg);
    color: var(--yellow-text);
    border: 1px solid var(--yellow-border);
}

.proof-track {
    display: flex;
    height: 15px;
    border-radius: var(--radius-full);
    overflow: hidden;
    margin: 18px 0 14px;
    background: #f1f5f9;
    box-shadow: inset 0 1px 2px rgba(0, 0, 0, 0.06);
}
.proof-track i {
    display: block;
    height: 100%;
    transition: width 0.4s ease;
}
.p-ok {
    background: linear-gradient(90deg, #10b981 0%, #059669 100%);
}
.p-listed {
    background: linear-gradient(90deg, #f59e0b 0%, #d97706 100%);
}
.p-missing {
    background: repeating-linear-gradient(135deg, #fecdd3 0, #fecdd3 6px, #fee2e2 6px, #fee2e2 12px);
}

.proof-meta {
    display: flex;
    flex-wrap: wrap;
    gap: 8px 14px;
    font-size: 0.9rem;
    color: var(--muted);
}
.proof-meta-pill {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 4px 11px;
    background: #f8fafc;
    border: 1px solid var(--line);
    border-radius: var(--radius-sm);
}
.proof-meta-pill b {
    color: var(--ink);
}

/* ---------- Demand Rows (Skill Gaps) ---------- */
.demand {
    display: grid;
    grid-template-columns: minmax(140px, 220px) 1fr minmax(160px, auto);
    align-items: center;
    gap: 16px;
    padding: 12px 0;
    border-bottom: 1px solid var(--line-subtle);
}
.demand:last-child {
    border-bottom: 0;
}
.demand .mk {
    justify-self: start;
    margin: 0;
}
.demand-bar {
    height: 10px;
    background: #f1f5f9;
    border-radius: var(--radius-full);
    overflow: hidden;
    box-shadow: inset 0 1px 2px rgba(0, 0, 0, 0.05);
}
.demand-bar i {
    display: block;
    height: 100%;
    background: var(--primary-gradient);
    border-radius: var(--radius-full);
}
.demand-meta {
    color: var(--muted);
    font-size: 0.88rem;
    text-align: right;
    white-space: nowrap;
    font-weight: 500;
}

/* ---------- Heatmap Table (Responsive & Sticky) ---------- */
.hm-wrap {
    overflow-x: auto;
    margin-bottom: 12px;
    background: #ffffff;
    border: 1px solid var(--line);
    border-radius: var(--radius-md);
    box-shadow: var(--shadow-xs);
    -webkit-overflow-scrolling: touch;
}
.hm {
    border-collapse: collapse;
    width: 100%;
    font-size: 0.9rem;
    min-width: 580px;
}
.hm th, .hm td {
    border-bottom: 1px solid var(--line-subtle);
    padding: 10px 14px;
    text-align: center;
}
.hm tr:last-child td {
    border-bottom: 0;
}
.hm th {
    background: #f8fafc;
    color: var(--muted);
    font-weight: 700;
    font-size: 0.82rem;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    position: sticky;
    top: 0;
}
.hm td:first-child, .hm th:first-child {
    text-align: left;
    font-weight: 700;
    width: 160px;
    position: sticky;
    left: 0;
    background: #ffffff;
    z-index: 2;
    border-right: 1px solid var(--line);
    box-shadow: 2px 0 5px rgba(0, 0, 0, 0.02);
}
.hm th:first-child {
    background: #f8fafc;
}
.hm-cell-badge {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 26px;
    height: 26px;
    border-radius: 50%;
    font-weight: 700;
    font-size: 0.82rem;
}
.hm-ok      { background: var(--green-bg); color: var(--green-text); border: 1px solid var(--green-border); }
.hm-listed  { background: var(--yellow-bg); color: var(--yellow-text); border: 1px solid var(--yellow-border); }
.hm-missing { background: var(--red-bg); color: var(--red-text); border: 1px solid var(--red-border); }
.pref { opacity: 0.6; }

/* ---------- Tracker Board Columns & Responsive Cards ---------- */
.col-head {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 8px 12px;
    margin-bottom: 12px;
    font-weight: 700;
    color: var(--ink);
    background: #ffffff;
    border: 1px solid var(--line);
    border-top: 3px solid var(--c, var(--primary));
    border-radius: var(--radius-sm);
    box-shadow: var(--shadow-xs);
    font-size: 0.92rem;
}
.col-head-pill {
    background: var(--canvas);
    color: var(--muted);
    font-size: 0.78rem;
    font-weight: 700;
    padding: 2px 8px;
    border-radius: var(--radius-full);
    border: 1px solid var(--line);
}

/* ---------- Home Page Hero & Components ---------- */
.home-hero-badge {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 6px 14px;
    background: var(--primary-light);
    color: var(--primary);
    border: 1px solid var(--primary-border);
    border-radius: var(--radius-full);
    font-size: 0.84rem;
    font-weight: 700;
    margin-bottom: 14px;
}
.home-title {
    font-family: var(--display);
    font-weight: 800;
    font-size: 3.1rem;
    line-height: 1.1;
    letter-spacing: -0.035em;
    color: var(--ink);
    margin: 4px 0 16px;
}
.home-sub {
    color: var(--muted);
    font-size: 1.12rem;
    line-height: 1.6;
    max-width: 48ch;
    margin: 0 0 24px;
}

/* Resume Editor Sheet Preview */
.sheet {
    background: #ffffff;
    border: 1px solid var(--line);
    border-radius: var(--radius-lg);
    padding: 24px 26px;
    box-shadow: var(--shadow-lg);
    line-height: 1.8;
    font-size: 0.96rem;
    position: relative;
}
.sheet-doc-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding-bottom: 12px;
    margin-bottom: 12px;
    border-bottom: 1px solid var(--line);
}
.sheet-doc-title {
    font-weight: 800;
    font-size: 1.05rem;
    color: var(--ink);
    letter-spacing: -0.02em;
}
.sheet-doc-status {
    font-size: 0.78rem;
    font-weight: 700;
    color: var(--green-text);
    background: var(--green-bg);
    border: 1px solid var(--green-border);
    padding: 2px 8px;
    border-radius: var(--radius-full);
}
.sheet-h {
    font-weight: 700;
    color: var(--muted);
    font-size: 0.84rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-top: 10px;
    margin-bottom: 4px;
}
.sheet-ask {
    margin-top: 16px;
    padding-top: 14px;
    border-top: 1px dashed var(--line);
}
.sheet-ask-label {
    display: block;
    color: var(--muted);
    font-size: 0.85rem;
    font-weight: 600;
    margin-bottom: 6px;
}
.sheet .legend {
    margin-top: 14px;
    margin-bottom: 0;
}

/* Workflow Step Cards */
.flow {
    display: flex;
    gap: 16px;
    align-items: flex-start;
    padding: 14px 16px;
    background: #ffffff;
    border: 1px solid var(--line);
    border-radius: var(--radius-md);
    margin-bottom: 10px;
    box-shadow: var(--shadow-xs);
    transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
}
.flow:hover {
    border-color: #cbd5e1;
    transform: translateY(-1px);
    box-shadow: var(--shadow-sm);
}
.flow-num {
    flex: 0 0 34px;
    height: 34px;
    border-radius: 10px;
    background: var(--flow-c, var(--primary-gradient));
    color: #ffffff;
    font-weight: 800;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.95rem;
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.15);
}
.flow-opt {
    flex: 0 0 auto;
    padding: 4px 10px;
    border: 1px solid var(--purple-border);
    background: var(--purple-bg);
    border-radius: var(--radius-sm);
    color: var(--purple-text);
    font-size: 0.8rem;
    font-weight: 700;
}
.flow-title {
    font-weight: 700;
    color: var(--ink);
    font-size: 1.05rem;
    letter-spacing: -0.01em;
}
.flow-desc {
    color: var(--muted);
    font-size: 0.92rem;
    margin-top: 3px;
    line-height: 1.45;
}

/* Resume Loader Active Card */
.resume-active-card {
    background: #ffffff;
    border: 1px solid var(--green-border);
    border-radius: var(--radius-md);
    padding: 16px 20px;
    box-shadow: var(--shadow-xs);
    margin-bottom: 12px;
}
.resume-active-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 6px;
}
.resume-active-title {
    display: flex;
    align-items: center;
    gap: 8px;
    font-weight: 700;
    font-size: 1.02rem;
    color: var(--ink);
}
.resume-badge-ok {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    font-size: 0.78rem;
    font-weight: 700;
    background: var(--green-bg);
    color: var(--green-text);
    padding: 2px 8px;
    border-radius: var(--radius-full);
}
.resume-active-desc {
    color: var(--muted);
    font-size: 0.88rem;
    margin-bottom: 10px;
}

/* ---------- Responsive Media Queries ---------- */
@media (max-width: 900px) {
    .home-title { font-size: 2.5rem; }
    .proof-num { font-size: 3rem; }
    .stats-grid { grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); }
}

@media (max-width: 640px) {
    .block-container { padding: 1.2rem 0.8rem 2.5rem !important; }
    .home-title { font-size: 2.15rem; }
    .home-sub { font-size: 1.02rem; }
    .proof-num { font-size: 2.5rem; }
    .proof { padding: 18px; }
    .stats-grid { grid-template-columns: 1fr 1fr; gap: 10px; }
    .demand { grid-template-columns: 1fr; gap: 6px; }
    .demand-meta { text-align: left; }
    .flow { flex-direction: column; gap: 10px; }
}
</style>
"""

STATUS_COLORS = {
    "Saved": "#64748b",
    "Applied": "#3b82f6",
    "Interview": "#f59e0b",
    "Offer": "#10b981",
    "Rejected": "#f43f5e",
}
GAP_CHIP = {
    "missing": "missing",
    "listed": "unproven",
    "demonstrated": "matched",
    "strong": "matched",
}


def esc(value) -> str:
    return html.escape(str(value))


def inject_css() -> None:
    st.markdown(CSS, unsafe_allow_html=True)


def hero(title: str, subtitle: str, badge: str | None = None) -> None:
    """Modern, colorful page header with optional pill badge."""
    badge_html = f'<div class="page-head-badge">{esc(badge)}</div>' if badge else ""
    st.markdown(
        f'<div class="page-head">'
        f'{badge_html}'
        f'<h1>{esc(title)}</h1>'
        f'<p>{esc(subtitle)}</p>'
        f'</div>',
        unsafe_allow_html=True,
    )


def md_escape(text: str) -> str:
    """Escape characters Streamlit's markdown would otherwise interpret."""
    return re.sub(r"([\\`*_{}\[\]()#+\-.!|<>$~])", r"\\\1", text)


# ----------------------------- components ---------------------------------- #

def stat_row(items: list[tuple[str, object]]) -> str:
    """Responsive grid of modern, colorful stat cards with top accent highlights."""
    cards = "".join(
        f'<div class="stat-card">'
        f'<div class="stat-label">{esc(label)}</div>'
        f'<div class="stat-value">{esc(value)}</div>'
        f'</div>'
        for label, value in items
    )
    return f'<div class="stats-grid">{cards}</div>'


def metric_card(label: str, value: str) -> str:  # backwards compatible
    return stat_row([(label, value)])


def chip(name: str, css: str) -> str:
    return f'<span class="mk {css}">{esc(name)}</span>'


def legend() -> str:
    return (
        '<div class="legend">'
        + '<span style="font-size:0.8rem; font-weight:700; color:var(--muted); margin-right:4px;">KEY:</span>'
        + chip("proven in project/job", "matched")
        + chip("listed only", "unproven")
        + chip("missing", "missing")
        + chip("nice-to-have", "preferred")
        + chip("extra strength", "extra")
        + "</div>"
    )


def skill_card(title: str, subtitle: str, badges: list[tuple[str, str]]) -> str:
    """Heading and skill marks inside ONE sleek panel. badges = [(name, css_class)]."""
    body = "".join(chip(name, css) for name, css in badges) or '<span class="empty">None detected.</span>'
    return (
        f'<div class="panel"><h3>{esc(title)}</h3>'
        f'<p class="panel-sub">{esc(subtitle)}</p>'
        f'<div style="display:flex; flex-wrap:wrap; gap:2px 0;">{body}</div></div>'
    )


def proof_bar(result: dict) -> str:
    """Headline score plus a colorful bar showing evidence breakdown."""
    job = result["job"]
    total = sum(info["weight"] for info in job.values())
    if not total:
        return ""

    unproven = set(result["unproven"])
    proven_skills = [s for s in result["matched"] if s not in unproven]
    weight = lambda skills: sum(job[s]["weight"] for s in skills)
    ok, listed = weight(proven_skills), weight(result["unproven"])
    missing = max(total - ok - listed, 0)
    pct = lambda w: f"{100 * w / total:.1f}%"

    ev_score = result.get("evidence_score", 0)
    if ev_score >= 75:
        fit_badge = '<span class="proof-badge fit-high">Strong Fit</span>'
    elif ev_score >= 50:
        fit_badge = '<span class="proof-badge fit-mid">Moderate Fit</span>'
    else:
        fit_badge = '<span class="proof-badge fit-low">Developing Fit</span>'

    return (
        '<div class="proof">'
        '<div class="proof-top">'
        '<div class="proof-score-group">'
        f'<div class="proof-num">{ev_score}%</div>'
        '<div><div class="proof-label">Evidence-Backed Match</div>'
        f'<div style="font-size:0.85rem; color:var(--muted);">Keyword match: <b style="color:var(--ink);">{result["score"]}%</b></div></div>'
        '</div>'
        f'{fit_badge}'
        '</div>'
        '<div class="proof-track">'
        f'<i class="p-ok" style="width:{pct(ok)}" title="Proven: {pct(ok)}"></i>'
        f'<i class="p-listed" style="width:{pct(listed)}" title="Listed only: {pct(listed)}"></i>'
        f'<i class="p-missing" style="width:{pct(missing)}" title="Missing: {pct(missing)}"></i>'
        '</div>'
        '<div class="proof-meta">'
        f'<div class="proof-meta-pill"><span>✓</span> <b>{len(proven_skills)}</b> proven</div>'
        f'<div class="proof-meta-pill"><span>●</span> <b>{len(result["unproven"])}</b> listed only</div>'
        f'<div class="proof-meta-pill"><span>✕</span> <b>{len(result["missing"])}</b> missing</div>'
        '</div>'
        '</div>'
    )


def demand_rows(gaps: list[dict]) -> str:
    """How many of your target jobs ask for each gap, with responsive bars."""
    rows = "".join(
        '<div class="demand">'
        f'{chip(g["skill"], GAP_CHIP.get(g["status"], "missing"))}'
        f'<div class="demand-bar"><i style="width:{100 * g["demand"] / g["n_jobs"]:.0f}%"></i></div>'
        f'<div class="demand-meta">{g["demand"]} of {g["n_jobs"]} jobs ({g["required"]} required)</div>'
        "</div>"
        for g in gaps
    )
    return f'<div class="panel">{rows}</div>'


def column_head(status: str, count: int) -> str:
    color = STATUS_COLORS.get(status, "#4f46e5")
    return (
        f'<div class="col-head" style="--c:{color}">'
        f'<span>{esc(status)}</span>'
        f'<span class="col-head-pill">{count}</span>'
        f'</div>'
    )


# ------------------------- state that survives pages ------------------------ #

def persistent(widget, label, key, default, *args, **kwargs):
    """Draw a widget whose value survives navigating to another page."""
    store = f"_saved_{key}"
    if key not in st.session_state:
        st.session_state[key] = st.session_state.get(store, default)
    value = widget(label, *args, key=key, **kwargs)
    st.session_state[store] = value
    return value


SAMPLE_RESUME = """Alex Rivera
alex.rivera@example.com | (555) 349-2810 | San Francisco, CA
linkedin.com/in/alexrivera-dev | github.com/alexrivera-codes

Professional Summary
Full-Stack & Backend Software Engineer with 4+ years of experience building scalable distributed systems, RESTful APIs, and cloud services. Proven track record of improving system performance and architecting resilient microservices.

Work Experience
Apex Cloud Technologies - Software Engineer (2022 - Present)
• Architected and deployed a high-throughput FastAPI and Python microservice handling 45,000+ daily requests with 99.95% uptime.
• Refactored legacy monolithic endpoints into asynchronous services, reducing average API response latency by 42%.
• Containerized microservices using Docker and automated CI/CD deployment pipelines on AWS, cutting release cycle time by 60%.
• Designed optimized PostgreSQL relational schemas and query indexes, accelerating heavy reporting queries by 35%.
• Mentored 3 junior engineers and established automated code-quality checks with Git and GitHub Actions.

ByteWave Solutions - Junior Backend Developer (2020 - 2022)
• Developed scalable backend services and REST APIs in Python and Flask for enterprise customer onboarding.
• Integrated Redis caching layer, decreasing database load by 28% during peak traffic hours.
• Collaborated with frontend team to implement responsive React user interfaces and data visualization components.

Projects
SkillMatch AI - Automated Career & Skill Analytics Platform
• Engineered an open-source NLP-based skill extraction tool in Python, Streamlit, and SQLite with 1,500+ active GitHub stars.
• Implemented LangChain and Ollama integrations for local privacy-preserving LLM text generation and candidate bullet rewriting.

Distributed Task Queue
• Built an asynchronous task distribution worker engine using Redis and Python, processing over 100,000 background jobs daily.

Technical Skills
Languages: Python, SQL, JavaScript, HTML, CSS
Web & Backend: FastAPI, Flask, Django, REST APIs, React, Node.js
Databases: PostgreSQL, MySQL, SQLite, Redis
Cloud & DevOps: Docker, AWS, Git, GitHub, Linux, CI/CD
Data & ML: Pandas, NumPy, Machine Learning

Education
University of California, Davis
Bachelor of Science in Computer Science | 2016 - 2020
"""

SAMPLE_JOB_DESCRIPTION = """Senior Backend Engineer - Cloud & AI Systems
Company: CloudScale AI
Location: San Francisco, CA (Hybrid / Remote)

About the Role:
We are looking for a Senior Backend Engineer to join our Core Platform team. In this role, you will design and build high-performance microservices, scalable data pipelines, and AI integration systems that power our next-generation enterprise products.

Requirements:
• 3+ years of professional experience developing backend applications in Python.
• Strong expertise in building and deploying high-performance REST APIs with FastAPI or Django.
• Solid background in relational databases (PostgreSQL or MySQL) and query optimization.
• Proven hands-on experience containerizing services with Docker and deploying to AWS or GCP cloud environments.
• Experience with version control (Git, GitHub) and CI/CD automated deployment pipelines.
• Bachelor’s degree in Computer Science, a related STEM discipline, or equivalent practical experience.

Nice to Have / Preferred Qualifications:
• Experience with Kubernetes for container orchestration.
• Familiarity with LLMs, RAG (Retrieval-Augmented Generation), or LangChain.
• Experience with caching and messaging systems like Redis.
• Frontend familiarity with React and TypeScript.
"""


def load_sample_data() -> None:
    """Preload both sample resume and sample job description into session state."""
    st.session_state["resume_text"] = SAMPLE_RESUME
    st.session_state["resume_name"] = "Alex Rivera - Senior Software Engineer (Sample)"
    st.session_state["_replace_resume"] = False
    st.session_state["job_text_input"] = SAMPLE_JOB_DESCRIPTION
    st.session_state["_saved_job_text_input"] = SAMPLE_JOB_DESCRIPTION


def load_sample_job() -> None:
    """Preload sample job description into session state and rerun."""
    st.session_state["job_text_input"] = SAMPLE_JOB_DESCRIPTION
    st.session_state["_saved_job_text_input"] = SAMPLE_JOB_DESCRIPTION
    st.rerun()


def load_sample_resume() -> None:
    """Preload sample resume into session state and rerun."""
    _store_resume(SAMPLE_RESUME, "Alex Rivera - Senior Software Engineer (Sample)")


def _store_resume(text: str, name: str) -> None:
    st.session_state["resume_text"] = text
    st.session_state["resume_name"] = name
    st.session_state["_replace_resume"] = False
    st.rerun()


def resume_loader() -> str | None:
    """Shared responsive resume widget with 1-click sample loader."""
    text = st.session_state.get("resume_text")
    replacing = st.session_state.get("_replace_resume", False)

    if text and not replacing:
        name = st.session_state.get("resume_name", "Resume")
        word_count = len(text.split())
        st.markdown(
            f'<div class="resume-active-card">'
            f'<div class="resume-active-header">'
            f'<div class="resume-active-title">📄 {esc(name)}</div>'
            f'<span class="resume-badge-ok">● Active in Memory</span>'
            f'</div>'
            f'<div class="resume-active-desc">{word_count:,} words parsed · Stored in private session memory</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
        c1, c2 = st.columns(2)
        if c1.button("Replace file", key="resume_replace", use_container_width=True):
            st.session_state["_replace_resume"] = True
            st.rerun()
        if c2.button("Remove resume", key="resume_remove", use_container_width=True):
            for key in ("resume_text", "resume_name"):
                st.session_state.pop(key, None)
            st.rerun()
        return text

    col_btn_sample, col_spacer = st.columns([1, 1], vertical_alignment="center")
    with col_btn_sample:
        if st.button("✨ Load sample resume (1-click)", key="resume_load_sample"):
            load_sample_resume()

    uploaded = st.file_uploader(
        "Upload your resume (PDF or DOCX)",
        type=["pdf", "docx"],
        key="resume_file",
        help="Use a clean layout with selectable text for the best extraction accuracy.",
    )
    with st.expander("Or paste resume text directly"):
        pasted = st.text_area("Resume text", height=140, key="resume_paste",
                              label_visibility="collapsed",
                              placeholder="Paste the raw text of your resume here...")
        use_pasted = st.button("Use pasted text", key="resume_use_paste",
                               disabled=not pasted.strip())
    if text and st.button("Cancel replacement", key="resume_cancel"):
        st.session_state["_replace_resume"] = False
        st.rerun()

    if uploaded is not None:
        try:
            _store_resume(extract_text(uploaded.name, uploaded.getvalue()), uploaded.name)
        except ResumeError as error:
            st.error(str(error))
    elif use_pasted:
        _store_resume(pasted, "Pasted text")
    return text
