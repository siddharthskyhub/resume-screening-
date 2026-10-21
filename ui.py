"""Shared Streamlit helpers: the visual system, small components, and the resume loader.

Design system: Modern, responsive, colorful SaaS UI with refined typography,
colorful pill badges, card accents, and responsive layouts across all devices.
"""

import html
import re

import streamlit as st
import streamlit.components.v1 as components

from analyzer import ResumeError, extract_text

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Bricolage+Grotesque:wght@600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

:root {
    --ink: #0f172a;
    --ink-light: #1e293b;
    --muted: #64748b;
    --subtle: #94a3b8;
    --line: #e4daf4;
    --line-subtle: #efe7f8;
    --card-bg: #ffffff;
    --canvas: #f6f1fc;

    /* Light Purple Theme Palette */
    --purple-base: #f5effc;
    --purple-light: #faf5fe;
    --purple-canvas: #f6f1fc;
    --purple-border: #e2d4f5;
    --purple-subtle: #ede3f8;
    --purple-gradient: linear-gradient(135deg, #f7f3fd 0%, #f3ecfb 40%, #f6f0fc 70%, #f4eefa 100%);

    /* Soft Pastel Pink Spotlight & Accent */
    --pink-spotlight: rgba(244, 114, 182, 0.22);
    --pink-glow: rgba(244, 114, 182, 0.16);
    --pink-accent: #f472b6;
    --pink-light: #fdf2f8;
    --pink-border: #fbcfe8;
    --pink-gradient: linear-gradient(135deg, #f472b6 0%, #ec4899 100%);

    /* Vibrant Brand & Accents */
    --primary: #6366f1;
    --primary-hover: #4f46e5;
    --primary-light: #f5f3ff;
    --primary-border: #ddd6fe;
    --primary-glow: rgba(99, 102, 241, 0.22);
    --primary-gradient: linear-gradient(135deg, #7c3aed 0%, #6366f1 50%, #ec4899 100%);

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
    --shadow-colored: 0 4px 14px rgba(124, 58, 237, 0.25);
}

/* ---------- Global Reset & Pastel Light Purple Background ---------- */
html, body, .stApp {
    font-family: var(--sans);
    color: var(--ink);
    background: linear-gradient(135deg, #f7f3fd 0%, #f3ecfb 35%, #f6f0fc 70%, #f4eefa 100%) !important;
    background-attachment: fixed !important;
    min-height: 100vh !important;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
}

[data-testid="stAppViewContainer"],
[data-testid="stAppViewBlockContainer"],
.main,
section.main {
    background: transparent !important;
}

.block-container {
    padding-top: 1.8rem !important;
    padding-bottom: 3.5rem !important;
    max-width: 1180px !important;
    margin: 0 auto;
}

header[data-testid="stHeader"] {
    background: transparent !important;
}
footer {
    visibility: hidden;
}

/* Zero-height custom component iframes cleanly hidden */
div[data-testid="stCustomComponentV1"]:has(iframe[height="0"]),
iframe[height="0"] {
    display: none !important;
    position: absolute !important;
    width: 0 !important;
    height: 0 !important;
    border: none !important;
    overflow: hidden !important;
}

/* ---------- Cursor-Following Soft Light Pink Spotlight ---------- */
#cursor-spotlight-glow {
    position: fixed;
    top: 0;
    left: 0;
    width: 440px;
    height: 440px;
    margin-top: -220px;
    margin-left: -220px;
    border-radius: 50%;
    background: radial-gradient(
        circle,
        rgba(244, 114, 182, 0.22) 0%,
        rgba(251, 182, 206, 0.14) 30%,
        rgba(244, 114, 182, 0.05) 55%,
        rgba(244, 114, 182, 0) 72%
    );
    filter: blur(14px);
    pointer-events: none !important;
    z-index: 999999;
    opacity: 0;
    transform: translate3d(-9999px, -9999px, 0);
    transition: opacity 0.35s ease, width 0.3s cubic-bezier(0.16, 1, 0.3, 1), height 0.3s cubic-bezier(0.16, 1, 0.3, 1), margin 0.3s cubic-bezier(0.16, 1, 0.3, 1), filter 0.3s ease;
    will-change: transform, opacity;
}

#cursor-spotlight-glow.spotlight-visible {
    opacity: 1;
}

#cursor-spotlight-glow.spotlight-hovering {
    width: 520px;
    height: 520px;
    margin-top: -260px;
    margin-left: -260px;
    background: radial-gradient(
        circle,
        rgba(244, 114, 182, 0.32) 0%,
        rgba(251, 113, 133, 0.18) 32%,
        rgba(244, 114, 182, 0.08) 58%,
        rgba(244, 114, 182, 0) 75%
    );
    filter: blur(16px);
}

@media (hover: none) and (pointer: coarse) {
    #cursor-spotlight-glow {
        display: none !important;
    }
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
    transition: all 0.22s cubic-bezier(0.16, 1, 0.3, 1);
    box-shadow: var(--shadow-xs);
    border: 1px solid var(--purple-border);
    background: #ffffff;
    color: var(--ink);
}
div.stButton > button:hover {
    border-color: var(--pink-accent);
    background: #fff5f9;
    color: #be185d;
    transform: translateY(-1px);
    box-shadow: 0 4px 14px rgba(244, 114, 182, 0.25);
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
    background: linear-gradient(135deg, #6d28d9 0%, #4f46e5 50%, #db2777 100%) !important;
    box-shadow: 0 8px 22px rgba(236, 72, 153, 0.4) !important;
    transform: translateY(-1.5px) scale(1.01);
}

div.stDownloadButton > button {
    border-radius: var(--radius-sm);
    font-weight: 600;
    background: #ffffff;
    border: 1px solid var(--purple-border);
    color: var(--primary);
    transition: all 0.2s ease;
}
div.stDownloadButton > button:hover {
    background: #fff5f9;
    border-color: var(--pink-accent);
    color: #be185d;
    transform: translateY(-1px);
    box-shadow: 0 4px 14px rgba(244, 114, 182, 0.22);
}

/* Expanders */
[data-testid="stExpander"] details {
    border: 1px solid var(--purple-border) !important;
    border-radius: var(--radius-md) !important;
    background: #ffffff !important;
    box-shadow: var(--shadow-xs);
    transition: box-shadow 0.2s ease, border-color 0.2s ease;
}
[data-testid="stExpander"] details:hover {
    border-color: var(--pink-border);
    box-shadow: 0 4px 14px rgba(244, 114, 182, 0.12);
}
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
    border-color: var(--purple-border) !important;
    font-family: var(--sans) !important;
    background: #ffffff !important;
}
input[type="text"]:focus, textarea:focus {
    border-color: var(--pink-accent) !important;
    box-shadow: 0 0 0 3px rgba(244, 114, 182, 0.22) !important;
}

/* ---------- Creative Sidebar Styling & Atmosphere ---------- */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #f4edfb 0%, #f8f4fc 50%, #f3ecfa 100%) !important;
    border-right: 1px solid #e5daf5 !important;
    box-shadow: 4px 0 24px rgba(139, 92, 246, 0.05) !important;
    position: relative !important;
}

[data-testid="stSidebar"]::before {
    content: "";
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 220px;
    background: radial-gradient(circle at 50% 0%, rgba(244, 114, 182, 0.16) 0%, rgba(168, 85, 247, 0.08) 60%, transparent 100%);
    pointer-events: none;
    z-index: 0;
}

[data-testid="stSidebarContent"] {
    padding-top: 1.2rem !important;
    padding-bottom: 2rem !important;
}

/* Sidebar Nav Wrapper */
[data-testid="stSidebarNav"] {
    margin-bottom: 14px !important;
}

/* Grouped Section Headers */
[data-testid="stSidebarNav"] span[data-testid*="stSidebarNavSectionHeader"],
[data-testid="stSidebarNav"] div > span[data-testid],
[data-testid="stSidebarNav"] [data-testid*="section"],
[data-testid="stSidebarNav"] > ul > div > span {
    font-family: var(--display) !important;
    font-size: 0.72rem !important;
    font-weight: 800 !important;
    letter-spacing: 0.1em !important;
    text-transform: uppercase !important;
    color: #64748b !important;
    padding: 12px 14px 6px 14px !important;
    display: flex !important;
    align-items: center !important;
    gap: 8px !important;
}

[data-testid="stSidebarNavSeparator"] {
    border-top: 1px dashed #cbd5e1 !important;
    margin: 8px 8px !important;
}

/* Sidebar Nav Items Container */
[data-testid="stSidebarNavItems"] {
    padding: 4px 8px !important;
    gap: 5px !important;
}

[data-testid="stSidebarNavLinkContainer"] {
    margin: 3px 0 !important;
}

/* Individual Link Button Card */
[data-testid="stSidebarNavLink"] {
    display: flex !important;
    align-items: center !important;
    padding: 9px 14px !important;
    border-radius: 12px !important;
    border: 1px solid rgba(226, 232, 240, 0.85) !important;
    background: #ffffff !important;
    color: #334155 !important;
    font-weight: 600 !important;
    font-size: 0.92rem !important;
    letter-spacing: -0.01em !important;
    box-shadow: 0 1px 3px rgba(15, 23, 42, 0.04) !important;
    transition: all 0.22s cubic-bezier(0.16, 1, 0.3, 1) !important;
    position: relative !important;
    overflow: hidden !important;
    text-decoration: none !important;
}

/* Hover State: Slide right with purple glow */
[data-testid="stSidebarNavLink"]:hover {
    background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%) !important;
    color: #4f46e5 !important;
    border-color: #c7d2fe !important;
    transform: translateX(4px) !important;
    box-shadow: 0 4px 14px rgba(79, 70, 229, 0.14), 0 1px 3px rgba(15, 23, 42, 0.04) !important;
}

/* Active State: Radiant SaaS Gradient Pill with Luminous Glow */
[data-testid="stSidebarNavLink"][aria-current="page"] {
    background: linear-gradient(135deg, #4f46e5 0%, #6366f1 50%, #4338ca 100%) !important;
    color: #ffffff !important;
    font-weight: 700 !important;
    border-color: rgba(255, 255, 255, 0.25) !important;
    box-shadow: 0 8px 18px -2px rgba(79, 70, 229, 0.45), 0 2px 6px rgba(79, 70, 229, 0.25) !important;
    transform: translateX(4px) scale(1.01) !important;
}

/* Glowing Left Cyan Indicator on Active Page */
[data-testid="stSidebarNavLink"][aria-current="page"]::before {
    content: "" !important;
    position: absolute !important;
    left: 0 !important;
    top: 18% !important;
    bottom: 18% !important;
    width: 4px !important;
    border-radius: 0 4px 4px 0 !important;
    background: #67e8f9 !important;
    box-shadow: 0 0 10px #22d3ee !important;
}

/* Active item text stays crisp white */
[data-testid="stSidebarNavLink"][aria-current="page"] span,
[data-testid="stSidebarNavLink"][aria-current="page"] p,
[data-testid="stSidebarNavLink"][aria-current="page"] div {
    color: #ffffff !important;
}

/* Completely remove all stacked rounded-square elements from navigation icons */
[data-testid="stSidebarNavLink"] span:first-child,
[data-testid="stSidebarNavLink"] span:first-child span {
    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;
    background: transparent !important;
    border: none !important;
    border-radius: 0 !important;
    box-shadow: none !important;
    margin: 0 10px 0 0 !important;
    padding: 0 !important;
    width: auto !important;
    height: auto !important;
    color: #7c3aed !important;
    font-size: 1.2rem !important;
    transition: transform 0.22s cubic-bezier(0.34, 1.56, 0.64, 1), color 0.2s ease !important;
}

/* Subtle, sleek hover animation on icons without any background boxes */
[data-testid="stSidebarNavLink"]:hover span:first-child,
[data-testid="stSidebarNavLink"]:hover span:first-child span {
    transform: scale(1.15) !important;
    color: #d946ef !important;
}

/* Active Page: Icon turns pure crisp white */
[data-testid="stSidebarNavLink"][aria-current="page"] span:first-child,
[data-testid="stSidebarNavLink"][aria-current="page"] span:first-child span {
    color: #ffffff !important;
    transform: scale(1.05) !important;
}

/* Ensure no ellipsis truncation on labels */
[data-testid="stSidebarNavLink"] span:not(:first-child),
[data-testid="stSidebarNavLink"] p {
    white-space: nowrap !important;
    overflow: visible !important;
    text-overflow: clip !important;
}

/* Professional SaaS Badges on Navigation Links without text emojis */
[data-testid="stSidebarNavLink"][href*="ats-checker"]::after {
    content: "AUDIT" !important;
    margin-left: auto !important;
    font-size: 0.6rem !important;
    font-weight: 800 !important;
    padding: 2px 7px !important;
    border-radius: 9999px !important;
    background: linear-gradient(135deg, #10b981 0%, #059669 100%) !important;
    color: #ffffff !important;
    letter-spacing: 0.05em !important;
    box-shadow: 0 2px 6px rgba(16, 185, 129, 0.3) !important;
}

[data-testid="stSidebarNavLink"][href*="analyzer"]::after {
    content: "POPULAR" !important;
    margin-left: auto !important;
    font-size: 0.6rem !important;
    font-weight: 800 !important;
    padding: 2px 7px !important;
    border-radius: 9999px !important;
    background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%) !important;
    color: #ffffff !important;
    letter-spacing: 0.05em !important;
    box-shadow: 0 2px 6px rgba(245, 158, 11, 0.3) !important;
}

[data-testid="stSidebarNavLink"][href*="ai-coach"] span:first-child {
    color: #0ea5e9 !important;
}
[data-testid="stSidebarNavLink"][href*="ai-coach"]:hover span:first-child {
    color: #06b6d4 !important;
}

[data-testid="stSidebarNavLink"][href*="ai-coach"]::after {
    content: "AI PRO" !important;
    margin-left: auto !important;
    font-size: 0.6rem !important;
    font-weight: 800 !important;
    padding: 2px 7px !important;
    border-radius: 9999px !important;
    background: linear-gradient(135deg, #ec4899 0%, #be185d 100%) !important;
    color: #ffffff !important;
    letter-spacing: 0.05em !important;
    box-shadow: 0 2px 6px rgba(236, 72, 153, 0.3) !important;
}

/* Active Page Badge Adjustment */
[data-testid="stSidebarNavLink"][aria-current="page"]::after {
    background: rgba(255, 255, 255, 0.25) !important;
    color: #ffffff !important;
    border: 1px solid rgba(255, 255, 255, 0.45) !important;
    box-shadow: none !important;
}

/* ---------- Creative Sidebar Brand Card & Widgets ---------- */
.brand-container {
    padding: 6px 0 12px;
}
.brand-header {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 4px;
}
.brand-logo-wrap {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
    transition: transform 0.25s cubic-bezier(0.34, 1.56, 0.64, 1);
}
.brand-logo-wrap:hover {
    transform: translateY(-2px) scale(1.06);
}
.brand-logo-svg {
    border-radius: 12px;
    box-shadow: 0 4px 14px rgba(124, 58, 237, 0.22);
    display: block;
}
.brand-title-row {
    display: flex;
    align-items: center;
    gap: 6px;
}
.brand-text {
    font-family: var(--display);
    font-weight: 800;
    font-size: 1.35rem;
    background: linear-gradient(135deg, #0f172a 0%, #4338ca 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    letter-spacing: -0.025em;
    line-height: 1.1;
}
.brand-pill-ai {
    font-size: 0.65rem;
    font-weight: 800;
    padding: 2px 7px;
    background: linear-gradient(135deg, #ec4899 0%, #be185d 100%);
    color: white;
    border-radius: 9999px;
    letter-spacing: 0.05em;
    box-shadow: 0 2px 6px rgba(236, 72, 153, 0.35);
}
.brand-sub {
    color: var(--muted);
    font-size: 0.82rem;
    line-height: 1.35;
    margin-top: 3px;
}

/* Sidebar Status Card */
.sidebar-status-card {
    background: #ffffff;
    border: 1px solid var(--line);
    border-radius: var(--radius-md);
    padding: 12px 14px;
    margin: 12px 0 10px;
    display: flex;
    align-items: center;
    gap: 12px;
    box-shadow: 0 2px 6px rgba(15, 23, 42, 0.04);
    transition: transform 0.2s ease, border-color 0.2s ease;
}
.sidebar-status-card:hover {
    border-color: #cbd5e1;
    transform: translateY(-1px);
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
    animation: radarPulseRing 2s infinite;
}
.status-indicator.idle {
    background: var(--yellow-strong);
    box-shadow: 0 0 0 4px rgba(245, 158, 11, 0.2);
}
.sidebar-status-info {
    overflow: hidden;
    line-height: 1.3;
}
.sidebar-status-title {
    font-size: 0.86rem;
    font-weight: 700;
    color: var(--ink);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}
.sidebar-status-sub {
    font-size: 0.75rem;
    color: var(--muted);
    margin-top: 1px;
}

/* Creative Sidebar Tip Widget */
.sidebar-tip-card {
    background: linear-gradient(135deg, #eff6ff 0%, #eef2ff 100%);
    border: 1px solid #c7d2fe;
    border-radius: 12px;
    padding: 11px 13px;
    margin: 12px 0 10px 0;
    box-shadow: 0 2px 6px rgba(79, 70, 229, 0.05);
}
.sidebar-tip-head {
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 0.72rem;
    font-weight: 800;
    color: #4338ca;
    letter-spacing: 0.06em;
    margin-bottom: 4px;
}
.sidebar-tip-body {
    font-size: 0.78rem;
    color: #475569;
    line-height: 1.4;
}

/* System Health Footer Bar */
.sidebar-health-bar {
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 0.74rem;
    color: #64748b;
    font-weight: 600;
    margin-top: 8px;
    padding: 6px 4px;
}
.health-dot {
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: #10b981;
    display: inline-block;
    box-shadow: 0 0 6px #10b981;
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
    border: 1px solid var(--purple-border);
    border-radius: var(--radius-md);
    padding: 16px 20px;
    box-shadow: var(--shadow-xs);
    position: relative;
    overflow: hidden;
    transition: transform 0.22s cubic-bezier(0.16, 1, 0.3, 1), box-shadow 0.22s ease, border-color 0.22s ease;
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
.stat-card:nth-child(1) { --stat-c: #7c3aed; }
.stat-card:nth-child(2) { --stat-c: #ec4899; }
.stat-card:nth-child(3) { --stat-c: #10b981; }
.stat-card:nth-child(4) { --stat-c: #f59e0b; }
.stat-card:nth-child(5) { --stat-c: #8b5cf6; }

.stat-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 22px -2px rgba(244, 114, 182, 0.20), 0 2px 6px rgba(124, 58, 237, 0.05);
    border-color: var(--pink-border);
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
    border: 1px solid var(--purple-border);
    border-radius: var(--radius-md);
    padding: 20px 22px;
    margin-bottom: 14px;
    box-shadow: var(--shadow-xs);
    transition: box-shadow 0.22s ease, border-color 0.22s ease, transform 0.22s ease;
}
.panel:hover {
    box-shadow: 0 8px 24px -4px rgba(244, 114, 182, 0.18), 0 2px 6px rgba(124, 58, 237, 0.05);
    border-color: var(--pink-border);
    transform: translateY(-1px);
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
    border: 1px solid var(--purple-border);
    border-radius: var(--radius-lg);
    padding: 24px 28px;
    margin-bottom: 16px;
    box-shadow: 0 4px 20px -2px rgba(139, 92, 246, 0.06);
    position: relative;
    overflow: hidden;
    transition: all 0.24s ease;
}
.proof:hover {
    border-color: var(--pink-border);
    box-shadow: 0 8px 26px -2px rgba(244, 114, 182, 0.16);
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
    border: 1px solid var(--purple-border);
    border-radius: var(--radius-lg);
    padding: 24px 26px;
    box-shadow: 0 10px 25px -4px rgba(139, 92, 246, 0.08);
    line-height: 1.8;
    font-size: 0.96rem;
    position: relative;
    transition: border-color 0.22s ease, box-shadow 0.22s ease;
}
.sheet:hover {
    border-color: var(--pink-border);
    box-shadow: 0 14px 30px -4px rgba(244, 114, 182, 0.18);
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

/* ---------- Standardised Fully Clickable Feature Cards ---------- */
.feature-cards-container {
    display: flex;
    flex-direction: column;
    gap: 12px;
    margin-bottom: 20px;
    width: 100%;
}

.feature-card {
    display: flex !important;
    align-items: center !important;
    gap: 16px !important;
    padding: 16px 20px !important;
    background: #ffffff !important;
    border: 1px solid var(--purple-border) !important;
    border-radius: var(--radius-md) !important;
    text-decoration: none !important;
    color: var(--ink) !important;
    box-shadow: 0 2px 6px rgba(139, 92, 246, 0.04) !important;
    transition: all 0.22s cubic-bezier(0.16, 1, 0.3, 1) !important;
    cursor: pointer !important;
    position: relative !important;
    overflow: hidden !important;
    width: 100% !important;
    box-sizing: border-box !important;
}

.feature-card:hover {
    border-color: var(--pink-border) !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 22px -2px rgba(244, 114, 182, 0.20), 0 2px 6px rgba(124, 58, 237, 0.05) !important;
    background: #ffffff !important;
    text-decoration: none !important;
    color: var(--ink) !important;
}

.feature-card:active {
    transform: translateY(0px) scale(0.997) !important;
    box-shadow: 0 3px 8px rgba(244, 114, 182, 0.16) !important;
}

.feature-card:focus-visible {
    outline: 2px solid #a855f7 !important;
    outline-offset: 3px !important;
    border-color: #a855f7 !important;
    box-shadow: 0 0 0 4px rgba(168, 85, 247, 0.25) !important;
}

.feature-card-badge {
    flex: 0 0 36px !important;
    height: 36px !important;
    border-radius: 10px !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    font-size: 0.95rem !important;
    font-weight: 800 !important;
    color: #ffffff !important;
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.12) !important;
    flex-shrink: 0 !important;
    user-select: none !important;
}

.feature-card-badge.flow-opt {
    flex: 0 0 auto !important;
    padding: 6px 12px !important;
    height: auto !important;
    border: 1px solid var(--purple-border) !important;
    background: var(--purple-bg) !important;
    border-radius: var(--radius-sm) !important;
    color: var(--purple-text) !important;
    font-size: 0.82rem !important;
    box-shadow: none !important;
}

.feature-card-content {
    flex: 1 1 auto !important;
    min-width: 0 !important;
}

.feature-card-title {
    font-family: var(--display) !important;
    font-weight: 700 !important;
    font-size: 1.08rem !important;
    color: var(--ink) !important;
    letter-spacing: -0.015em !important;
    line-height: 1.25 !important;
    margin-bottom: 3px !important;
    transition: color 0.2s ease !important;
}

.feature-card:hover .feature-card-title {
    color: #4f46e5 !important;
}

.feature-card-desc {
    color: var(--muted) !important;
    font-size: 0.92rem !important;
    line-height: 1.48 !important;
    margin: 0 !important;
    overflow-wrap: break-word !important;
    word-break: normal !important;
}

/* Workflow Step Cards */
.flow {
    display: flex;
    gap: 16px;
    align-items: flex-start;
    padding: 14px 16px;
    background: #ffffff;
    border: 1px solid var(--purple-border);
    border-radius: var(--radius-md);
    margin-bottom: 10px;
    box-shadow: var(--shadow-xs);
    transition: all 0.22s cubic-bezier(0.16, 1, 0.3, 1);
}
.flow:hover {
    border-color: var(--pink-border);
    transform: translateY(-2px);
    box-shadow: 0 8px 22px -2px rgba(244, 114, 182, 0.18);
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

/* ---------- Enhancv-Style Live Scanner & Floating Badges ---------- */
@keyframes scanLaser {
    0% {
        top: 0%;
        opacity: 0.95;
    }
    48% {
        top: calc(100% - 3px);
        opacity: 1;
    }
    52% {
        top: calc(100% - 3px);
        opacity: 1;
    }
    100% {
        top: 0%;
        opacity: 0.95;
    }
}

@keyframes orbFloat {
    0% {
        transform: translate(0px, 0px) scale(1);
    }
    100% {
        transform: translate(14px, -12px) scale(1.08);
    }
}

@keyframes floatBadge1 {
    0%, 100% {
        transform: translateY(0px);
    }
    50% {
        transform: translateY(-8px);
    }
}

@keyframes floatBadge2 {
    0%, 100% {
        transform: translate(0px, 0px);
    }
    50% {
        transform: translate(3px, -7px);
    }
}

@keyframes floatBadge3 {
    0%, 100% {
        transform: translateY(0px);
    }
    50% {
        transform: translateY(-8px);
    }
}

@keyframes floatBadge4 {
    0%, 100% {
        transform: translate(0px, 0px);
    }
    50% {
        transform: translate(-3px, -6px);
    }
}

@keyframes radarPulseRing {
    0% {
        transform: scale(0.95);
        box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.65);
    }
    70% {
        transform: scale(1);
        box-shadow: 0 0 0 7px rgba(16, 185, 129, 0);
    }
    100% {
        transform: scale(0.95);
        box-shadow: 0 0 0 0 rgba(16, 185, 129, 0);
    }
}

.scanner-hero-stage {
    position: relative;
    padding: 22px 14px;
    margin: 0 auto;
    max-width: 490px;
    z-index: 1;
}

.scanner-orb {
    position: absolute;
    border-radius: 50%;
    filter: blur(48px);
    opacity: 0.45;
    pointer-events: none;
    z-index: 0;
    animation: orbFloat 7s ease-in-out infinite alternate;
}

.scanner-orb-1 {
    width: 220px;
    height: 220px;
    top: -24px;
    right: -24px;
    background: radial-gradient(circle, #a855f7 0%, rgba(168, 85, 247, 0) 70%);
}

.scanner-orb-2 {
    width: 200px;
    height: 200px;
    bottom: -24px;
    left: -20px;
    background: radial-gradient(circle, #f472b6 0%, rgba(244, 114, 182, 0) 70%);
    animation-delay: -3.5s;
}

.scanner-badge {
    position: absolute;
    z-index: 20;
    display: inline-flex;
    align-items: center;
    gap: 9px;
    padding: 7px 13px;
    background: #ffffff;
    border: 1px solid rgba(226, 232, 240, 0.95);
    border-radius: 9999px;
    box-shadow: 0 10px 24px -4px rgba(15, 23, 42, 0.12), 0 4px 8px -2px rgba(15, 23, 42, 0.05);
    backdrop-filter: blur(8px);
    user-select: none;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.scanner-badge:hover {
    box-shadow: 0 14px 28px -4px rgba(15, 23, 42, 0.16);
    transform: scale(1.03);
}

.scanner-badge.badge-top-right {
    top: 2px;
    right: -12px;
    animation: floatBadge1 4.2s ease-in-out infinite;
}

.scanner-badge.badge-top-left {
    top: 52px;
    left: -18px;
    animation: floatBadge2 4.8s ease-in-out infinite 0.4s;
}

.scanner-badge.badge-bottom-right {
    bottom: 46px;
    right: -16px;
    animation: floatBadge3 4.4s ease-in-out infinite 0.9s;
}

.scanner-badge.badge-bottom-left {
    bottom: -6px;
    left: 4px;
    animation: floatBadge4 5.2s ease-in-out infinite 1.4s;
}

.badge-icon {
    width: 26px;
    height: 26px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.85rem;
    font-weight: 700;
    flex-shrink: 0;
}

.badge-title {
    font-size: 0.72rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: var(--muted);
    font-weight: 700;
    line-height: 1.1;
}

.badge-val {
    font-size: 0.84rem;
    font-weight: 800;
    line-height: 1.2;
}

.scanner-doc-card {
    position: relative;
    background: #ffffff;
    border: 1px solid var(--purple-border);
    border-radius: 18px;
    padding: 22px 24px;
    box-shadow: 0 20px 40px -8px rgba(139, 92, 246, 0.12), 0 2px 6px rgba(15, 23, 42, 0.04);
    overflow: hidden;
    z-index: 2;
    transition: border-color 0.22s ease, box-shadow 0.22s ease;
}
.scanner-doc-card:hover {
    border-color: var(--pink-border);
    box-shadow: 0 24px 48px -8px rgba(244, 114, 182, 0.22), 0 4px 10px rgba(124, 58, 237, 0.06);
}

.scanner-laser-line {
    position: absolute;
    left: 0;
    right: 0;
    height: 3px;
    background: linear-gradient(90deg, rgba(99, 102, 241, 0) 0%, rgba(6, 182, 212, 0.9) 25%, rgba(16, 185, 129, 1) 50%, rgba(6, 182, 212, 0.9) 75%, rgba(99, 102, 241, 0) 100%);
    box-shadow: 0 0 14px 3px rgba(16, 185, 129, 0.75), 0 0 28px rgba(6, 182, 212, 0.45);
    pointer-events: none;
    z-index: 15;
    animation: scanLaser 3.8s ease-in-out infinite;
}

.scanner-laser-glow {
    position: absolute;
    left: 0;
    right: 0;
    top: -36px;
    height: 38px;
    background: linear-gradient(180deg, rgba(16, 185, 129, 0) 0%, rgba(16, 185, 129, 0.14) 100%);
    pointer-events: none;
}

.scanner-doc-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding-bottom: 12px;
    margin-bottom: 14px;
    border-bottom: 1px solid var(--line);
}

.scanner-radar {
    display: inline-flex;
    align-items: center;
    gap: 7px;
}

.radar-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: #10b981;
    animation: radarPulseRing 1.8s infinite;
    display: inline-block;
}

.radar-text {
    font-size: 0.74rem;
    font-weight: 800;
    letter-spacing: 0.06em;
    color: #047857;
    text-transform: uppercase;
}

.scanner-doc-badge {
    font-size: 0.76rem;
    font-weight: 800;
    color: #1d4ed8;
    background: #eff6ff;
    border: 1px solid #bfdbfe;
    padding: 3px 9px;
    border-radius: var(--radius-full);
    text-transform: uppercase;
    letter-spacing: 0.04em;
}

.scanner-doc-body {
    line-height: 1.6;
    font-size: 0.94rem;
}

.doc-person-name {
    font-family: var(--display);
    font-size: 1.35rem;
    font-weight: 800;
    color: var(--ink);
    letter-spacing: -0.02em;
}

.doc-person-sub {
    font-size: 0.82rem;
    color: var(--muted);
    margin-bottom: 12px;
}

.doc-section-h {
    font-size: 0.78rem;
    font-weight: 800;
    letter-spacing: 0.06em;
    color: var(--muted);
    text-transform: uppercase;
    margin-top: 10px;
    margin-bottom: 6px;
}

.doc-chips-row {
    display: flex;
    flex-wrap: wrap;
    gap: 4px;
    margin-bottom: 10px;
}

.doc-exp-item {
    background: #f8fafc;
    border: 1px solid var(--line);
    border-radius: var(--radius-sm);
    padding: 9px 12px;
    margin-bottom: 10px;
    font-size: 0.86rem;
}

.doc-exp-title {
    color: var(--ink);
    margin-bottom: 3px;
}

.doc-exp-bullet {
    color: var(--ink-light);
    line-height: 1.45;
}

.doc-ask-strip {
    background: #ffffff;
    border: 1px dashed var(--line);
    border-radius: var(--radius-sm);
    padding: 8px 11px;
    display: flex;
    align-items: center;
    flex-wrap: wrap;
    gap: 5px;
    margin-bottom: 12px;
}

.doc-ask-label {
    font-size: 0.72rem;
    font-weight: 800;
    color: var(--muted);
    margin-right: 4px;
}

.doc-metrics-footer {
    display: grid;
    grid-template-columns: 1fr 1fr 1fr;
    gap: 8px;
    padding-top: 10px;
    border-top: 1px solid var(--line-subtle);
    text-align: center;
}

.doc-metric-item {
    background: #f8fafc;
    border: 1px solid var(--line-subtle);
    border-radius: var(--radius-sm);
    padding: 6px 4px;
}

.doc-metric-num {
    font-family: var(--display);
    font-size: 1.05rem;
    font-weight: 800;
    color: var(--ink);
    line-height: 1.1;
}

.doc-metric-lbl {
    font-size: 0.68rem;
    color: var(--muted);
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.03em;
    margin-top: 2px;
}

/* ---------- Responsive Media Queries ---------- */
@media (max-width: 900px) {
    .home-title { font-size: 2.5rem; }
    .proof-num { font-size: 3rem; }
    .stats-grid { grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); }
    .scanner-hero-stage { max-width: 440px; }
}

@media (max-width: 640px) {
    .block-container { padding: 1.2rem 0.8rem 2.5rem !important; }
    .home-title { font-size: 2.15rem; word-break: break-word; }
    .home-sub { font-size: 1.02rem; }
    .proof-num { font-size: 2.5rem; }
    .proof { padding: 18px; }
    .stats-grid { grid-template-columns: 1fr 1fr; gap: 10px; }
    .demand { grid-template-columns: 1fr; gap: 6px; }
    .demand-meta { text-align: left; }
    .flow { flex-direction: column; gap: 10px; }
    .feature-card { padding: 14px 16px !important; gap: 14px !important; }
    .feature-card-title { font-size: 1.02rem !important; }
    .feature-card-desc { font-size: 0.88rem !important; }
    .scanner-hero-stage { padding: 12px 2px; max-width: 100%; }
    .scanner-doc-card { padding: 16px 14px; }
    .scanner-badge { padding: 4px 8px; font-size: 0.72rem; }
    .scanner-badge.badge-top-left { left: 2px; top: -14px; }
    .scanner-badge.badge-top-right { right: 2px; top: -14px; }
    .scanner-badge.badge-bottom-left { left: 2px; bottom: -12px; }
    .scanner-badge.badge-bottom-right { display: none; }
    .doc-metrics-footer { gap: 4px; }
    .doc-metric-num { font-size: 0.95rem; }
    .doc-metric-lbl { font-size: 0.62rem; }
}

/* ---------- Lucide SVG Icon System ---------- */
.lucide-icon {
    display: inline-block;
    vertical-align: -0.18em;
    flex-shrink: 0;
    transition: transform 0.2s cubic-bezier(0.16, 1, 0.3, 1), stroke 0.2s ease;
}

.icon-box {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    border-radius: 9px;
    flex-shrink: 0;
    box-shadow: 0 1px 2px rgba(15, 23, 42, 0.04);
    transition: all 0.22s cubic-bezier(0.16, 1, 0.3, 1);
}

.icon-box:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 10px rgba(124, 58, 237, 0.15);
}

.inline-icon-wrap {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    vertical-align: middle;
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


LUCIDE_ICONS: dict[str, str] = {
    "house": '<path d="M15 21v-8a1 1 0 0 0-1-1h-4a1 1 0 0 0-1 1v8"/><path d="M3 10a2 2 0 0 1 .709-1.528l7-5.999a2 2 0 0 1 2.582 0l7 5.999A2 2 0 0 1 21 10v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>',
    "home": '<path d="M15 21v-8a1 1 0 0 0-1-1h-4a1 1 0 0 0-1 1v8"/><path d="M3 10a2 2 0 0 1 .709-1.528l7-5.999a2 2 0 0 1 2.582 0l7 5.999A2 2 0 0 1 21 10v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>',
    "target": '<circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/>',
    "file-search": '<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><circle cx="11.5" cy="14.5" r="2.5"/><path d="M13.25 16.25 16 19"/>',
    "shield-check": '<path d="M20 13c0 5-3.5 7.5-7.66 8.95a1 1 0 0 1-.67-.01C7.5 20.5 4 18 4 13V6a1 1 0 0 1 1-1c2 0 4.5-1.2 6.24-2.72a1.17 1.17 0 0 1 1.52 0C14.51 3.81 17 5 19 5a1 1 0 0 1 1 1z"/><path d="m9 12 2 2 4-4"/>',
    "compass": '<circle cx="12" cy="12" r="10"/><polygon points="16.24 7.76 14.12 14.12 7.76 16.24 9.88 9.88 16.24 7.76"/>',
    "clipboard-list": '<rect width="8" height="4" x="8" y="2" rx="1" ry="1"/><path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"/><path d="M12 11h4"/><path d="M12 16h4"/><path d="M8 11h.01"/><path d="M8 16h.01"/>',
    "map": '<polygon points="3 6 9 3 15 6 21 3 21 18 15 21 9 18 3 21"/><line x1="9" x2="9" y1="3" y2="18"/><line x1="15" x2="15" y1="6" y2="21"/>',
    "brain-circuit": '<path d="M12 5a3 3 0 1 0-5.997.125 4 4 0 0 0-2.526 5.77 4 4 0 0 0 .556 6.588A4 4 0 1 0 12 18Z"/><path d="M12 5a3 3 0 1 1 5.997.125 4 4 0 0 1 2.526 5.77 4 4 0 0 1-.556 6.588A4 4 0 1 1 12 18Z"/><path d="M15 13a4.5 4.5 0 0 1-3-4 4.5 4.5 0 0 1-3 4"/><path d="M12 18v4"/><path d="M8 8.5V11"/><path d="M16 8.5V11"/>',
    "sparkles": '<path d="m12 3-1.912 5.813a2 2 0 0 1-1.275 1.275L3 12l5.813 1.912a2 2 0 0 1 1.275 1.275L12 21l1.912-5.813a2 2 0 0 1 1.275-1.275L21 12l-5.813-1.912a2 2 0 0 1-1.275-1.275L12 3Z"/><path d="M5 3v4"/><path d="M19 17v4"/><path d="M3 5h4"/><path d="M17 19h4"/>',
    "zap": '<polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/>',
    "rocket": '<path d="M4.5 16.5c-1.5 1.26-2 5-2 5s3.74-.5 5-2c.71-.84.7-2.13-.09-2.91a2.18 2.18 0 0 0-2.91-.09z"/><path d="m12 15-3-3a22 22 0 0 1 2-3.95A12.88 12.88 0 0 1 22 2c0 2.72-.78 7.5-6 11a22.35 22.35 0 0 1-4 2z"/><path d="M9 12H4s.55-3.03 2-4c1.62-1.08 5 0 5 0"/><path d="M12 9V4s3.03.55 4 2c1.08 1.62 0 5 0 5"/>',
    "lightbulb": '<path d="M15 14c.2-1 .7-1.7 1.5-2.5 1-.9 1.5-2.2 1.5-3.5A6 6 0 0 0 6 8c0 1 .2 2.2 1.5 3.5.7.7 1.3 1.5 1.5 2.5"/><path d="M9 18h6"/><path d="M10 22h4"/>',
    "check": '<polyline points="20 6 9 17 4 12"/>',
    "check-circle-2": '<circle cx="12" cy="12" r="10"/><path d="m9 12 2 2 4-4"/>',
    "alert-triangle": '<path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/>',
    "alert-circle": '<circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/>',
    "x": '<line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>',
    "x-circle": '<circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/>',
    "circle": '<circle cx="12" cy="12" r="10"/>',
    "circle-dot": '<circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="2"/>',
    "info": '<circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/>',
    "help-circle": '<circle cx="12" cy="12" r="10"/><path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"/><line x1="12" y1="17" x2="12.01" y2="17"/>',
    "download": '<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/>',
    "upload": '<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/>',
    "upload-cloud": '<path d="M4 14.899A7 7 0 1 1 15.71 8h1.79a4.5 4.5 0 0 1 2.5 8.242"/><path d="M12 12v9"/><path d="m16 16-4-4-4 4"/>',
    "file-text": '<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><polyline points="10 9 9 9 8 9"/>',
    "file-plus": '<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="12" y1="18" x2="12" y2="12"/><line x1="9" y1="15" x2="15" y2="15"/>',
    "file-edit": '<path d="M4 13.5V4a2 2 0 0 1 2-2h8.5L20 7.5V20a2 2 0 0 1-2 2h-5.5"/><polyline points="14 2 14 8 20 8"/><path d="M10.42 12.61a2.1 2.1 0 1 1 2.97 2.97L7.95 21 4 22l1-3.95 5.42-5.44Z"/>',
    "search": '<circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>',
    "settings": '<circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"/>',
    "sliders": '<line x1="4" y1="21" x2="4" y2="14"/><line x1="4" y1="10" x2="4" y2="3"/><line x1="12" y1="21" x2="12" y2="12"/><line x1="12" y1="8" x2="12" y2="3"/><line x1="20" y1="21" x2="20" y2="16"/><line x1="20" y1="12" x2="20" y2="3"/><line x1="1" y1="14" x2="7" y2="14"/><line x1="9" y1="8" x2="15" y2="8"/><line x1="17" y1="16" x2="23" y2="16"/>',
    "lock": '<rect width="18" height="11" x="3" y="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/>',
    "briefcase": '<rect width="20" height="14" x="2" y="7" rx="2" ry="2"/><path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"/>',
    "calendar": '<rect width="18" height="18" x="3" y="4" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/>',
    "trash-2": '<polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/><line x1="10" y1="11" x2="10" y2="17"/><line x1="14" y1="11" x2="14" y2="17"/>',
    "external-link": '<path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/><polyline points="15 3 21 3 21 9"/><line x1="10" y1="14" x2="21" y2="3"/>',
    "plus": '<line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/>',
    "plus-circle": '<circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="16"/><line x1="8" y1="12" x2="16" y2="12"/>',
    "bookmark": '<path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z"/>',
    "trending-up": '<polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/><polyline points="17 6 23 6 23 12"/>',
    "bar-chart-3": '<line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/>',
    "columns": '<rect width="18" height="18" x="3" y="3" rx="2" ry="2"/><line x1="12" y1="3" x2="12" y2="21"/>',
    "layers": '<polygon points="12 2 2 7 12 12 22 7 12 2"/><polyline points="2 17 12 22 22 17"/><polyline points="2 12 12 17 22 12"/>',
    "pen-tool": '<path d="M12 20h9"/><path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z"/>',
    "book-open": '<path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"/><path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"/>',
    "wrench": '<path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"/>',
    "trophy": '<path d="M6 9H4.5a2.5 2.5 0 0 1 0-5H6"/><path d="M18 9h1.5a2.5 2.5 0 0 0 0-5H18"/><path d="M4 22h16"/><path d="M10 14.66V17c0 .55-.47.98-.97 1.21C7.85 18.75 7 20.24 7 22"/><path d="M14 14.66V17c0 .55.47.98.97 1.21C16.15 18.75 17 20.24 17 22"/><path d="M18 2H6v7a6 6 0 0 0 12 0V2Z"/>',
    "clipboard-check": '<rect width="8" height="4" x="8" y="2" rx="1" ry="1"/><path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"/><path d="m9 14 2 2 4-4"/>',
    "user-check": '<path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><polyline points="16 11 18 13 22 9"/>',
    "message-square": '<path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>',
    "atom": '<circle cx="12" cy="12" r="2.2" fill="currentColor"/><ellipse cx="12" cy="12" rx="9" ry="3.8"/><ellipse cx="12" cy="12" rx="9" ry="3.8" transform="rotate(60 12 12)"/><ellipse cx="12" cy="12" rx="9" ry="3.8" transform="rotate(120 12 12)"/>',
}


def icon(name: str, size: int = 18, color: str | None = None, stroke_width: float = 2.0, class_name: str = "") -> str:
    """Return inline SVG for a Lucide icon with consistent sizing, stroke and alignment."""
    key = str(name).lower().strip().replace("_", "-")
    path_data = LUCIDE_ICONS.get(key)
    if not path_data:
        # Fallback to file-text or target if unknown
        path_data = LUCIDE_ICONS.get("target", "")
    stroke_attr = f'stroke="{color}"' if color else 'stroke="currentColor"'
    classes = f"lucide-icon lucide-{key} {class_name}".strip()
    return (
        f'<svg class="{classes}" width="{size}" height="{size}" viewBox="0 0 24 24" '
        f'fill="none" {stroke_attr} stroke-width="{stroke_width}" stroke-linecap="round" stroke-linejoin="round" '
        f'aria-hidden="true">{path_data}</svg>'
    )


def icon_box(name: str, size: int = 18, box_size: int = 32, bg: str | None = None, color: str | None = None, border: str | None = None, class_name: str = "") -> str:
    """Return a subtle, rounded-square icon container suited for SaaS dashboards."""
    svg = icon(name, size=size, color=color or "currentColor")
    bg_val = bg or "var(--purple-subtle)"
    color_val = color or "var(--primary)"
    border_val = border or "var(--purple-border)"
    style = f"width:{box_size}px; height:{box_size}px; background:{bg_val}; color:{color_val}; border:1px solid {border_val};"
    return f'<div class="icon-box {class_name}" style="{style}">{svg}</div>'


def icon_label(name: str, text: str, icon_size: int = 16, color: str | None = None, spacing: int = 6, class_name: str = "") -> str:
    """Combine a Lucide SVG icon with text label for HTML/Markdown components."""
    svg = icon(name, size=icon_size, color=color)
    return f'<span class="inline-icon-wrap {class_name}" style="gap:{spacing}px;">{svg}<span>{esc(text)}</span></span>'


def brand_logo(size: int = 42, inline: bool = False, class_name: str = "") -> str:
    """Return an inline SVG of the modern SkillMatch geometric 'S' ribbon logo with purple-to-pink gradient."""
    uid = f"sm_{size}_{abs(hash(size)) % 10000}"
    inline_style = "vertical-align:middle; margin-right:6px;" if inline else ""
    classes = f"brand-logo-svg {class_name}".strip()
    return (
        f'<svg class="{classes}" width="{size}" height="{size}" viewBox="0 0 100 100" '
        f'style="{inline_style}" aria-label="SkillMatch AI Logo" xmlns="http://www.w3.org/2000/svg">'
        f'<defs>'
        f'<linearGradient id="bg_{uid}" x1="0%" y1="0%" x2="100%" y2="100%">'
        f'<stop offset="0%" stop-color="#070a1e"/>'
        f'<stop offset="50%" stop-color="#0a0e27"/>'
        f'<stop offset="100%" stop-color="#0d112d"/>'
        f'</linearGradient>'
        f'<linearGradient id="pt_{uid}" x1="15%" y1="85%" x2="85%" y2="15%">'
        f'<stop offset="0%" stop-color="#e879f9"/>'
        f'<stop offset="45%" stop-color="#f472b6"/>'
        f'<stop offset="85%" stop-color="#fbcfe8"/>'
        f'<stop offset="100%" stop-color="#ffffff"/>'
        f'</linearGradient>'
        f'<linearGradient id="wt_{uid}" x1="0%" y1="0%" x2="100%" y2="100%">'
        f'<stop offset="0%" stop-color="#c084fc"/>'
        f'<stop offset="40%" stop-color="#e879f9"/>'
        f'<stop offset="100%" stop-color="#f472b6"/>'
        f'</linearGradient>'
        f'<linearGradient id="ft_{uid}" x1="0%" y1="0%" x2="0%" y2="100%">'
        f'<stop offset="0%" stop-color="#9333ea"/>'
        f'<stop offset="40%" stop-color="#7c3aed"/>'
        f'<stop offset="100%" stop-color="#4f46e5"/>'
        f'</linearGradient>'
        f'<linearGradient id="pb_{uid}" x1="85%" y1="15%" x2="15%" y2="85%">'
        f'<stop offset="0%" stop-color="#e879f9"/>'
        f'<stop offset="45%" stop-color="#f472b6"/>'
        f'<stop offset="85%" stop-color="#fbcfe8"/>'
        f'<stop offset="100%" stop-color="#ffffff"/>'
        f'</linearGradient>'
        f'<linearGradient id="wb_{uid}" x1="100%" y1="100%" x2="0%" y2="0%">'
        f'<stop offset="0%" stop-color="#c084fc"/>'
        f'<stop offset="40%" stop-color="#e879f9"/>'
        f'<stop offset="100%" stop-color="#f472b6"/>'
        f'</linearGradient>'
        f'<linearGradient id="fb_{uid}" x1="0%" y1="100%" x2="0%" y2="0%">'
        f'<stop offset="0%" stop-color="#9333ea"/>'
        f'<stop offset="40%" stop-color="#7c3aed"/>'
        f'<stop offset="100%" stop-color="#4f46e5"/>'
        f'</linearGradient>'
        f'</defs>'
        f'<rect width="100" height="100" rx="26" fill="url(#bg_{uid})"/>'
        f'<rect width="98" height="98" x="1" y="1" rx="25" fill="none" stroke="rgba(255,255,255,0.09)" stroke-width="1.2"/>'
        f'<g>'
        f'<path d="M26,50 C26,34 32,22 45,22 L45,37 C37,37 36,43 36,50 Z" fill="url(#pt_{uid})"/>'
        f'<path d="M45,22 L57,22 L57,37 L45,37 Z" fill="url(#ft_{uid})"/>'
        f'<path d="M57,22 L74,37 L57,37 Z" fill="url(#wt_{uid})"/>'
        f'<path d="M74,50 C74,66 68,78 55,78 L55,63 C63,63 64,57 64,50 Z" fill="url(#pb_{uid})"/>'
        f'<path d="M55,78 L43,78 L43,63 L55,63 Z" fill="url(#fb_{uid})"/>'
        f'<path d="M43,78 L26,63 L43,63 Z" fill="url(#wb_{uid})"/>'
        f'</g>'
        f'</svg>'
    )


def ai_coach_logo(size: int = 42, inline: bool = False, class_name: str = "") -> str:
    """Return an inline SVG of the cyan quantum atom AI Coach logo inspired by user reference."""
    uid = f"ai_{size}_{abs(hash(size)) % 10000}"
    inline_style = "vertical-align:middle; margin-right:6px;" if inline else ""
    classes = f"ai-coach-logo-svg {class_name}".strip()
    return (
        f'<svg class="{classes}" width="{size}" height="{size}" viewBox="0 0 100 100" '
        f'style="{inline_style}" aria-label="AI Coach Atom Logo" xmlns="http://www.w3.org/2000/svg">'
        f'<defs>'
        f'<linearGradient id="abg_{uid}" x1="0%" y1="0%" x2="100%" y2="100%">'
        f'<stop offset="0%" stop-color="#040711"/>'
        f'<stop offset="50%" stop-color="#080c1b"/>'
        f'<stop offset="100%" stop-color="#0b1126"/>'
        f'</linearGradient>'
        f'<filter id="acg_{uid}" x="-30%" y="-30%" width="160%" height="160%">'
        f'<feDropShadow dx="0" dy="0" stdDeviation="3.5" flood-color="#38bdf8" flood-opacity="0.8"/>'
        f'<feDropShadow dx="0" dy="1" stdDeviation="6" flood-color="#0284c7" flood-opacity="0.45"/>'
        f'</filter>'
        f'</defs>'
        f'<rect width="100" height="100" rx="26" fill="url(#abg_{uid})"/>'
        f'<rect width="98" height="98" x="1" y="1" rx="25" fill="none" stroke="rgba(56, 189, 248, 0.28)" stroke-width="1.2"/>'
        f'<g filter="url(#acg_{uid})">'
        f'<ellipse cx="50" cy="50" rx="33" ry="13.5" fill="none" stroke="#38bdf8" stroke-width="3.2" stroke-linecap="round"/>'
        f'<ellipse cx="50" cy="50" rx="33" ry="13.5" fill="none" stroke="#38bdf8" stroke-width="3.2" stroke-linecap="round" transform="rotate(60 50 50)"/>'
        f'<ellipse cx="50" cy="50" rx="33" ry="13.5" fill="none" stroke="#38bdf8" stroke-width="3.2" stroke-linecap="round" transform="rotate(120 50 50)"/>'
        f'<circle cx="50" cy="50" r="7" fill="#38bdf8"/>'
        f'<circle cx="50" cy="50" r="3.2" fill="#e0f2fe"/>'
        f'</g>'
        f'</svg>'
    )


def inject_cursor_spotlight() -> None:
    """Inject a lightweight, fluid, 60fps cursor-following soft pink spotlight."""
    components.html(
        r"""
        <script>
        (function() {
            try {
                const doc = window.parent.document;
                if (!doc) return;

                let spotlight = doc.getElementById('cursor-spotlight-glow');
                if (!spotlight) {
                    spotlight = doc.createElement('div');
                    spotlight.id = 'cursor-spotlight-glow';
                    doc.body.appendChild(spotlight);
                }

                let mouseX = -9999, mouseY = -9999;
                let currentX = -9999, currentY = -9999;
                let isVisible = false;
                let isInteractive = false;

                function render() {
                    if (isVisible) {
                        currentX += (mouseX - currentX) * 0.22;
                        currentY += (mouseY - currentY) * 0.22;
                        spotlight.style.transform = 'translate3d(' + Math.round(currentX) + 'px, ' + Math.round(currentY) + 'px, 0)';
                    }
                    requestAnimationFrame(render);
                }

                if (!window.parent._cursorSpotlightInit) {
                    window.parent._cursorSpotlightInit = true;

                    doc.addEventListener('mousemove', function(e) {
                        mouseX = e.clientX;
                        mouseY = e.clientY;
                        if (!isVisible) {
                            isVisible = true;
                            currentX = mouseX;
                            currentY = mouseY;
                            spotlight.classList.add('spotlight-visible');
                        }

                        const target = e.target;
                        const interactive = target && target.closest && target.closest(
                            'button, a, input, textarea, select, .stButton, .stat-card, .panel, .flow, .feature-card, .scanner-doc-card, .sidebar-status-card, [data-testid="stSidebarNavLink"], .page-head, .home-hero-badge, .mk, .doc-metric-item, .sidebar-tip-card'
                        );
                        if (interactive && !isInteractive) {
                            isInteractive = true;
                            spotlight.classList.add('spotlight-hovering');
                        } else if (!interactive && isInteractive) {
                            isInteractive = false;
                            spotlight.classList.remove('spotlight-hovering');
                        }
                    }, { passive: true });

                    doc.addEventListener('click', function(e) {
                        const card = e.target && e.target.closest && e.target.closest('.feature-card');
                        if (!card) return;

                        // Allow middle click or modifier keys (Ctrl/Cmd/Shift) for opening new tab
                        if (e.button !== 0 || e.ctrlKey || e.metaKey || e.shiftKey) return;

                        const href = card.getAttribute('href');
                        if (!href) return;

                        const slug = href.replace(/^(\/|\.\/)/, '').split(/[?#]/)[0];
                        const sidebarLink = doc.querySelector('a[data-testid="stSidebarNavLink"][href*="' + slug + '"]');
                        if (sidebarLink) {
                            e.preventDefault();
                            sidebarLink.click();
                        }
                    }, false);

                    doc.addEventListener('mouseleave', function() {
                        isVisible = false;
                        spotlight.classList.remove('spotlight-visible');
                    }, { passive: true });

                    doc.addEventListener('mouseenter', function(e) {
                        isVisible = true;
                        mouseX = e.clientX;
                        mouseY = e.clientY;
                        currentX = mouseX;
                        currentY = mouseY;
                        spotlight.classList.add('spotlight-visible');
                    }, { passive: true });

                    requestAnimationFrame(render);
                }
            } catch (err) {
                // Silently ignore if cross-origin restricted
            }
        })();
        </script>
        """,
        height=0,
        width=0,
    )


def inject_css() -> None:
    st.markdown(CSS, unsafe_allow_html=True)
    inject_cursor_spotlight()


def hero(title: str, subtitle: str, badge: str | None = None, icon_html: str | None = None) -> None:
    """Modern, colorful page header with optional pill badge and optional emblem."""
    badge_html = f'<div class="page-head-badge">{esc(badge)}</div>' if badge else ""
    icon_wrap = f'<div style="margin-bottom:12px; display:inline-flex;">{icon_html}</div><br/>' if icon_html else ""
    st.markdown(
        f'<div class="page-head">'
        f'{icon_wrap}'
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


def interactive_scanner_preview() -> str:
    """Enhancv-inspired dynamic scanner card with vertical sweeping laser,
    pulsing ambient glow orbs, and animated floating insight badges."""
    return (
        '<div class="scanner-hero-stage">'
        '<div class="scanner-orb scanner-orb-1"></div>'
        '<div class="scanner-orb scanner-orb-2"></div>'
        '<div class="scanner-badge badge-top-right">'
        f'<span class="badge-icon" style="background:#ecfdf5; color:#047857;">{icon("target", size=13, color="#047857")}</span>'
        '<div><div class="badge-title">ATS Score</div>'
        '<div class="badge-val" style="color:#047857;">94% Optimal</div></div>'
        '</div>'
        '<div class="scanner-badge badge-top-left">'
        f'<span class="badge-icon" style="background:#eef2ff; color:#4f46e5;">{icon("file-search", size=13, color="#4f46e5")}</span>'
        '<div><div class="badge-title">Keywords</div>'
        '<div class="badge-val" style="color:#4f46e5;">14 Matched</div></div>'
        '</div>'
        '<div class="scanner-badge badge-bottom-right">'
        f'<span class="badge-icon" style="background:#fffbeb; color:#b45309;">{icon("zap", size=13, color="#b45309")}</span>'
        '<div><div class="badge-title">Action Verbs</div>'
        '<div class="badge-val" style="color:#b45309;">18 High-Impact</div></div>'
        '</div>'
        '<div class="scanner-badge badge-bottom-left">'
        f'<span class="badge-icon" style="background:#ecfeff; color:#0e7490;">{icon("shield-check", size=13, color="#0e7490")}</span>'
        '<div><div class="badge-title">Format Hygiene</div>'
        '<div class="badge-val" style="color:#0e7490;">Single Column ATS</div></div>'
        '</div>'
        '<div class="scanner-doc-card">'
        '<div class="scanner-laser-line">'
        '<div class="scanner-laser-glow"></div>'
        '</div>'
        '<div class="scanner-doc-header">'
        '<div class="scanner-radar">'
        '<span class="radar-dot"></span>'
        '<span class="radar-text">SCANNING IN PROGRESS</span>'
        '</div>'
        '<span class="scanner-doc-badge">ATS COMPLIANT</span>'
        '</div>'
        '<div class="scanner-doc-body">'
        '<div class="doc-person-name">Alex Rivera</div>'
        '<div class="doc-person-sub">Senior Software Engineer · San Francisco, CA</div>'
        '<div class="doc-section-h">TECHNICAL SKILLS</div>'
        '<div class="doc-chips-row">'
        f'{chip("Python", "matched")}'
        f'{chip("FastAPI", "matched")}'
        f'{chip("PostgreSQL", "matched")}'
        f'{chip("Docker", "unproven")}'
        '</div>'
        '<div class="doc-section-h">EXPERIENCE &amp; PROJECTS</div>'
        '<div class="doc-exp-item">'
        '<div class="doc-exp-title"><b>Apex Cloud Technologies</b> — Senior Backend Engineer</div>'
        f'<div class="doc-exp-bullet">• Architected {chip("FastAPI", "matched")} microservices cutting latency by <b>35%</b> and scaling to <b>45k req/day</b>.</div>'
        '</div>'
        '<div class="doc-section-h" style="margin-top:10px;">TARGET JOB MATCH COMPARISON</div>'
        '<div class="doc-ask-strip">'
        '<span class="doc-ask-label">REQUIREMENTS:</span>'
        f'{chip("FastAPI", "matched")}'
        f'{chip("Docker", "unproven")}'
        f'{chip("Kubernetes", "missing")}'
        '</div>'
        '<div class="doc-metrics-footer">'
        '<div class="doc-metric-item"><div class="doc-metric-num">92%</div><div class="doc-metric-lbl">Keyword Match</div></div>'
        '<div class="doc-metric-item"><div class="doc-metric-num">0</div><div class="doc-metric-lbl">Parsing Errors</div></div>'
        '<div class="doc-metric-item"><div class="doc-metric-num">100%</div><div class="doc-metric-lbl">Section Detection</div></div>'
        '</div>'
        '</div>'
        '</div>'
        '</div>'
    )


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
        f'<div class="proof-meta-pill">{icon("check", size=13, color="var(--green-strong)")} <b>{len(proven_skills)}</b> proven</div>'
        f'<div class="proof-meta-pill">{icon("circle-dot", size=11, color="var(--yellow-strong)")} <b>{len(result["unproven"])}</b> listed only</div>'
        f'<div class="proof-meta-pill">{icon("x", size=13, color="var(--red-strong)")} <b>{len(result["missing"])}</b> missing</div>'
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
            f'<div class="resume-active-title">{icon("file-text", size=16, color="var(--primary)")} {esc(name)}</div>'
            f'<span class="resume-badge-ok">{icon("check-circle-2", size=12, color="var(--green-strong)")} Active in Memory</span>'
            f'</div>'
            f'<div class="resume-active-desc">{word_count:,} words parsed · Stored in private session memory</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
        c1, c2 = st.columns(2)
        if c1.button("Replace file", icon=":material/refresh:", key="resume_replace", use_container_width=True):
            st.session_state["_replace_resume"] = True
            st.rerun()
        if c2.button("Remove resume", icon=":material/delete:", key="resume_remove", use_container_width=True):
            for key in ("resume_text", "resume_name"):
                st.session_state.pop(key, None)
            st.rerun()
        return text

    col_btn_sample, col_spacer = st.columns([1, 1], vertical_alignment="center")
    with col_btn_sample:
        if st.button("Load sample resume (1-click)", icon=":material/auto_awesome:", key="resume_load_sample"):
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
