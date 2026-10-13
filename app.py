"""
Signalpost Enterprise Agent - Final iOS Glassmorphic Sunset Edition
Clean responsive typography, no ellipsis truncation, dynamic hierarchy, and crash-safe evidence inspection.
"""

import streamlit as st
import requests
import json
from agent import SignalpostAgent

# --- Page Setup ---
st.set_page_config(
    page_title="Signalpost | Norwegian Enterprise AI",
    page_icon="✨",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# --- Clean Sunset Amber & Frosted Glass Styling ---
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, sans-serif;
        color: #1C1917;
    }

    /* Ambient Warm Canvas */
    .stApp {
        background: radial-gradient(circle at 15% 15%, rgba(254, 215, 170, 0.45) 0%, transparent 40%),
                    radial-gradient(circle at 85% 20%, rgba(251, 146, 60, 0.25) 0%, transparent 45%),
                    radial-gradient(circle at 50% 90%, rgba(254, 240, 138, 0.2) 0%, transparent 50%),
                    #FAF8F5;
        background-attachment: fixed;
    }

    #MainMenu, header, footer {visibility: hidden !important;}
    .block-container {
        padding-top: 2.2rem !important;
        padding-bottom: 4rem !important;
        max-width: 780px !important;
    }

    .hero-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        font-size: 0.8rem;
        font-weight: 600;
        letter-spacing: 0.04em;
        text-transform: uppercase;
        color: #C2410C;
        background: rgba(254, 215, 170, 0.5);
        border: 1px solid rgba(251, 146, 60, 0.3);
        padding: 4px 14px;
        border-radius: 999px;
        margin-bottom: 0.8rem;
    }

    .hero-title {
        font-size: 2.6rem;
        font-weight: 700;
        letter-spacing: -0.03em;
        background: linear-gradient(135deg, #1C1917 20%, #EA580C 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.3rem;
    }

    .hero-sub {
        font-size: 1.02rem;
        color: #78716C;
        margin-bottom: 1.8rem;
    }

    .glass-card {
        background: rgba(255, 255, 255, 0.82);
        backdrop-filter: blur(28px) saturate(200%);
        -webkit-backdrop-filter: blur(28px) saturate(200%);
        border: 1px solid rgba(255, 255, 255, 0.95);
        border-radius: 22px;
        padding: 24px 28px;
        box-shadow: 0 12px 36px -4px rgba(234, 88, 12, 0.08),
                    0 2px 8px rgba(0, 0, 0, 0.02);
        margin: 1.2rem 0;
    }

    .pill-group {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        margin-top: 14px;
    }

    .glass-pill {
        background: rgba(254, 243, 199, 0.45);
        border: 1px solid rgba(251, 146, 60, 0.25);
        border-radius: 12px;
        padding: 6px 12px;
        font-size: 0.82rem;
        color: #44403C;
    }

    .glass-pill strong {
        color: #C2410C;
    }

    .health-pill {
        display: inline-flex;
        align-items: center;
        gap: 5px;
        font-size: 0.8rem;
        font-weight: 600;
        padding: 4px 12px;
        border-radius: 999px;
    }
    .health-good {
        background: #DCFCE7;
        color: #15803D;
        border: 1px solid #BBF7D0;
    }
    .health-warn {
        background: #FEF3C7;
        color: #B45309;
        border: 1px solid #FDE68A;
    }

    /* Prevent Metric Values from truncating into ellipsis */
    [data-testid="stMetricValue"] {
        font-size: 1.45rem !important;
        font-weight: 700 !important;
        white-space: normal !important;
        word-break: break-word !important;
    }

    div[data-testid="stTextInput"] > div > div > input {
        border-radius: 999px !important;
        border: 1.5px solid rgba(251, 146, 60, 0.3) !important;
        background: rgba(255, 255, 255, 0.95) !important;
        backdrop-filter: blur(16px) !important;
        padding: 14px 24px !important;
        font-size: 0.98rem !important;
        color: #1C1917 !important;
        box-shadow: 0 4px 16px rgba(234, 88, 12, 0.06) !important;
        transition: all 0.2s ease !important;
    }

    div[data-testid="stTextInput"] > div > div > input:focus {
        border-color: #EA580C !important;
        box-shadow: 0 0 0 4px rgba(234, 88, 12, 0.15) !important;
    }

    div[data-testid="stButton"] > button {
        background: linear-gradient(135deg, #F97316 0%, #EA580C 100%) !important;
        color: #FFFFFF !important;
        border-radius: 999px !important;
        border: none !important;
        font-weight: 600 !important;
        font-size: 0.92rem !important;
        padding: 10px 22px !important;
        box-shadow: 0 4px 14px rgba(234, 88, 12, 0.28) !important;
        transition: all 0.15s ease !important;
    }

    div[data-testid="stButton"] > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 6px 18px rgba(234, 88, 12, 0.38) !important;
    }

    .chip-btn div[data-testid="stButton"] > button {
        background: rgba(255, 255, 255, 0.8) !important;
        color: #57534E !important;
        border: 1px solid rgba(234, 88, 12, 0.2) !important;
        box-shadow: none !important;
        font-size: 0.82rem !important;
        font-weight: 500 !important;
        padding: 6px 14px !important;
    }

    .chip-btn div[data-testid="stButton"] > button:hover {
        background: rgba(254, 215, 170, 0.5) !important;
        color: #C2410C !important;
        border-color: #FB923C !important;
    }

    button[data-baseweb="tab"] {
        border-radius: 999px !important;
        color: #78716C !important;
        font-weight: 500 !important;
        padding: 5px 16px !important;
    }

    button[data-baseweb="tab"][aria-selected="true"] {
        background: rgba(254, 215, 170, 0.55) !important;
        color: #C2410C !important;
        font-weight: 600 !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def format_currency_compact(val: float | None) -> str:
    """Formats large monetary numbers into clean readable strings."""
    if val is None:
        return "N/A"
    abs_v = abs(val)
    if abs_v >= 1_000_000_000:
        return f"{val / 1_000_000_000:,.2f}B NOK"
    if abs_v >= 1_000_000:
        return f"{val / 1_000_000:,.1f}M NOK"
    return f"{val:,.0f} NOK"


def resolve_to_org_nr(query: str) -> str:
    cleaned = query.strip()
    if cleaned.isdigit() and len(cleaned) == 9:
        return cleaned
    try:
        search_url = "https://data.brreg.no/enhetsregisteret/api/enheter"
        res = requests.get(
            search_url,
            params={"navn": cleaned, "size": 3},
            headers={"Accept": "application/json"},
            timeout=5,
        )
        if res.status_code == 200:
            units = res.json().get("_embedded", {}).get("enheter", [])
            if units:
                return units[0].get("organisasjonsnummer", cleaned)
    except Exception:
        pass
    return cleaned


# --- Hero ---
st.markdown('<div style="text-align: center;"><span class="hero-badge">✨ Ground-Truth Enterprise Intelligence</span></div>', unsafe_allow_html=True)
st.markdown('<div class="hero-title" style="text-align: center;">Signalpost Intelligence</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-sub" style="text-align: center;">Verified legal facts, governance networks, hierarchy trees, and legal gazettes.</div>', unsafe_allow_html=True)

# --- Search Box ---
col1, col2 = st.columns([5, 1.2])
with col1:
    search_input = st.text_input(
        "Search",
        placeholder="Enter 9-digit Org Number or Name (e.g. Equinor, DNB, Kongsberg)",
        label_visibility="collapsed",
        key="query_input"
    )
with col2:
    search_clicked = st.button("Search", use_container_width=True)

# Suggested Query Chips
st.markdown("<div style='font-size: 0.8rem; color: #A8A29E; margin: 4px 0 4px 6px;'>Examples:</div>", unsafe_allow_html=True)
quick_cols = st.columns(4)
sample_prompts = [
    ("Equinor ASA", "923609016"),
    ("DNB Bank", "984851006"),
    ("Telenor ASA", "998888882"),
    ("Kongsberg Gruppen", "943753709"),
]

selected_query = search_input
for idx, (label, org_code) in enumerate(sample_prompts):
    with quick_cols[idx]:
        st.markdown('<div class="chip-btn">', unsafe_allow_html=True)
        if st.button(label, key=f"q_{idx}", use_container_width=True):
            selected_query = org_code
            search_clicked = True
        st.markdown('</div>', unsafe_allow_html=True)

# --- Processing & Rendering ---
if search_clicked or (selected_query and len(selected_query) >= 3):
    target_org = resolve_to_org_nr(selected_query)

    with st.spinner("Querying Brønnøysundregistrene & cross-verifying..."):
        agent = SignalpostAgent()
        profile = agent.get_profile(target_org)

    if profile:
        health_score = profile.risk_assessment.health_score
        health_class = "health-good" if health_score >= 70 else "health-warn"

        st.markdown(
            f"""
            <div class="glass-card">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                    <span style="font-size: 0.78rem; font-weight: 600; text-transform: uppercase; color: #EA580C; letter-spacing: 0.05em;">
                        ✓ Official Legal Entity Verified
                    </span>
                    <span class="health-pill {health_class}">
                        Health {health_score}/100 • {profile.risk_assessment.risk_level} Risk
                    </span>
                </div>
                <div style="font-size: 1.55rem; font-weight: 700; letter-spacing: -0.02em; color: #1C1917; margin-bottom: 2px;">
                    {profile.company_name}
                </div>
                <div style="font-size: 0.85rem; color: #78716C; margin-bottom: 12px;">
                    Org Nr: <strong style="color: #1C1917;">{profile.org_number}</strong> &nbsp;•&nbsp; 
                    Status: <strong style="color: {'#15803D' if profile.status == 'ACTIVE' else '#DC2626'};">{profile.status}</strong> &nbsp;•&nbsp; 
                    Form: {profile.legal_form.value or 'Entity'}
                </div>
                <div style="font-size: 0.95rem; line-height: 1.6; color: #292524;">
                    {profile.explanation}
                </div>
                <div class="pill-group">
                    <div class="glass-pill">👥 Employees: <strong>{profile.registered_employees.value or 'Not reported'}</strong></div>
                    <div class="glass-pill">🏢 Sector: <strong>{profile.industry_nace_description.value or 'General'}</strong></div>
                    <div class="glass-pill">📍 Location: <strong>{profile.business_address.value.get('kommune', 'Norway') if profile.business_address.value else 'Norway'}</strong></div>
                    <div class="glass-pill">🌐 Web: <strong>{profile.website.value or 'N/A'}</strong></div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Tabbed Inspection
        tab_fin, tab_gov, tab_subs, tab_gaz, tab_audit = st.tabs([
            "📊 Financials", 
            "👔 Governance", 
            "🏢 Sub-Units", 
            "📜 Gazettes", 
            "🔍 Evidence Audit"
        ])

        with tab_fin:
            if profile.financials.status == "available" and profile.financials.year:
                f_data = profile.financials
                m1, m2, m3 = st.columns(3)
                m1.metric("Accounting Year", f_data.year)
                m2.metric("Total Revenue", format_currency_compact(f_data.revenue_nok))
                m3.metric("Operating Profit", format_currency_compact(f_data.operating_profit_nok))
                st.caption("Source: Regnskapsregisteret (Official Public Annual Financial Accounts)")
            else:
                st.info("Direct micro-entity or holding account: No standalone public income statement returned.")

        with tab_gov:
            if profile.leadership:
                for person in profile.leadership:
                    st.write(f"• **{person.role}**: {person.name}")
                st.caption("Source: Foretaksregisteret Roller")
            else:
                st.info("No publicly listed executive roles registered.")

        with tab_subs:
            if profile.subsidiaries:
                st.write(f"Registered operating branch locations ({len(profile.subsidiaries)}):")
                for sub in profile.subsidiaries:
                    st.write(f"• **{sub.name}** (`{sub.sub_org_number}`) — {sub.location or 'Norway'}")
            else:
                st.info("No separate branch offices or sub-units registered under this entity.")

        with tab_gaz:
            if profile.recent_announcements:
                st.write("Recent official legal notices published in the Norwegian Gazette:")
                for ann in profile.recent_announcements:
                    st.write(f"• **{ann.date}** | {ann.announcement_type}: *{ann.description}*")
            else:
                st.info("No recent legal announcements published for this company.")

        with tab_audit:
            st.caption("Ground-truth evidence audit trail:")
            flat_ev_list = []
            for item in profile.evidence_trail:
                d = item.model_dump()
                # Safely serialize nested dictionaries and lists to prevent PyArrow type crashes
                if isinstance(d.get("value"), (dict, list)):
                    d["value"] = json.dumps(d["value"], ensure_ascii=False)
                flat_ev_list.append(d)
            st.dataframe(flat_ev_list, use_container_width=True, hide_index=True)

        # Download Verified JSON
        profile_json = json.dumps(profile.model_dump(), indent=2, ensure_ascii=False)
        st.download_button(
            label="⬇️ Download Verified JSON Profile",
            data=profile_json,
            file_name=f"company_{profile.org_number}.json",
            mime="application/json",
            use_container_width=True
        )

    else:
        st.warning(f"Could not locate entity for '{selected_query}'. Try entering the 9-digit organization number directly.")