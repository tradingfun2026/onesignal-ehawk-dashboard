"""
OneSignal eHawk Phase 3 - Executive Launch Readiness Dashboard
Run: streamlit run dashboard.py
Secrets needed:
  AIRTABLE_PAT = "patXXX"
  GEMINI_API_KEY = "AIza..."
"""

import streamlit as st
import requests
import hashlib
import time
import plotly.graph_objects as go
from datetime import datetime

st.set_page_config(
    page_title="eHawk Phase 3 - Launch Readiness",
    page_icon="🦅",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# -- IMPROVED HIGH-CONTRAST DARK THEME --
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
  html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
  .main .block-container { padding-top: 1.5rem; padding-bottom: 2rem; max-width: 1400px; }
  #MainMenu { visibility: hidden; } footer { visibility: hidden; } .stDeployButton { display: none; }

  /* Masthead */
  .masthead {
    background: linear-gradient(135deg, #0c1222 0%, #162032 50%, #1a2744 100%);
    border-radius: 14px; padding: 28px 36px; margin-bottom: 24px;
    display: flex; justify-content: space-between; align-items: center;
    border: 1px solid #1e3a5f;
  }
  .masthead-eyebrow { font-size: 11px; letter-spacing: 0.15em; text-transform: uppercase; color: #7b93b3; margin-bottom: 6px; }
  .masthead-title { font-size: 26px; font-weight: 700; color: #e8edf5; letter-spacing: -0.03em; margin: 0; }
  .masthead-sub { font-size: 13px; color: #7b93b3; margin-top: 6px; }
  .masthead-big { font-size: 56px; font-weight: 800; color: #f97316; letter-spacing: -0.04em; line-height: 1; }
  .masthead-label { font-size: 12px; text-transform: uppercase; letter-spacing: 0.12em; color: #8ba3c4; margin-top: 4px; }

  /* KPI Cards */
  .kpi-card {
    background: #141e30; border-radius: 12px; padding: 18px 20px 16px;
    border: 1px solid #1e3050; border-top: 3px solid transparent;
  }
  .kpi-card.green { border-top-color: #22c55e; }
  .kpi-card.amber { border-top-color: #f59e0b; }
  .kpi-card.red { border-top-color: #ef4444; }
  .kpi-card.blue { border-top-color: #3b82f6; }
  .kpi-label { font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.1em; color: #8ba3c4; margin-bottom: 10px; }
  .kpi-num { font-size: 36px; font-weight: 700; letter-spacing: -0.03em; line-height: 1; }
  .kpi-card.green .kpi-num { color: #22c55e; }
  .kpi-card.amber .kpi-num { color: #f59e0b; }
  .kpi-card.red .kpi-num { color: #ef4444; }
  .kpi-card.blue .kpi-num { color: #3b82f6; }
  .kpi-denom { font-size: 16px; color: #7b93b3; }
  .kpi-context { font-size: 12px; color: #8ba3c4; margin-top: 4px; }
  .kpi-pct {
    font-size: 11px; font-weight: 600; padding: 3px 8px; border-radius: 4px;
    display: inline-block; margin-top: 8px;
  }
  .kpi-card.green .kpi-pct { background: rgba(34,197,94,0.15); color: #22c55e; }
  .kpi-card.amber .kpi-pct { background: rgba(245,158,11,0.15); color: #f59e0b; }
  .kpi-card.red .kpi-pct { background: rgba(239,68,68,0.15); color: #ef4444; }
  .kpi-card.blue .kpi-pct { background: rgba(59,130,246,0.15); color: #3b82f6; }

  /* Section Headers */
  .section-header {
    font-size: 13px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.12em;
    color: #8ba3c4; margin: 28px 0 14px; padding-bottom: 10px;
    border-bottom: 1px solid #1e3050;
  }

  /* Detail Items */
  .detail-item {
    display: flex; align-items: flex-start; gap: 10px; padding: 10px 0;
    border-bottom: 1px solid #1a2744; font-size: 14px;
  }
  .detail-badge {
    font-size: 10px; font-weight: 700; padding: 3px 8px; border-radius: 4px;
    white-space: nowrap; flex-shrink: 0; margin-top: 2px;
  }
  .badge-red { background: rgba(239,68,68,0.18); color: #f87171; }
  .badge-amber { background: rgba(245,158,11,0.18); color: #fbbf24; }
  .badge-green { background: rgba(34,197,94,0.18); color: #4ade80; }
  .badge-blue { background: rgba(59,130,246,0.18); color: #60a5fa; }
  .badge-gray { background: rgba(148,163,184,0.15); color: #94a3b8; }

  /* Baseline Metric Cards */
  .baseline-card {
    background: #141e30; border-radius: 12px; padding: 18px 20px;
    border: 1px solid #1e3050;
  }
  .baseline-title { font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.1em; color: #8ba3c4; margin-bottom: 12px; }
  .baseline-value { font-size: 28px; font-weight: 700; line-height: 1; }
  .baseline-label { font-size: 12px; color: #7b93b3; margin-top: 4px; }
  .baseline-row { display: flex; justify-content: space-between; align-items: center; padding: 6px 0; border-bottom: 1px solid #1a2744; }
  .baseline-row:last-child { border-bottom: none; }
  .baseline-metric { font-size: 13px; color: #c8d6e5; }
  .baseline-val { font-size: 13px; font-weight: 600; }
  .val-good { color: #4ade80; }
  .val-warn { color: #fbbf24; }
  .val-bad { color: #f87171; }

  /* Phase Overview */
  .phase-card {
    background: #141e30; border-radius: 12px; padding: 20px 22px;
    border: 1px solid #1e3050; margin-bottom: 12px;
  }
  .phase-title { font-size: 15px; font-weight: 600; color: #e8edf5; margin-bottom: 6px; }
  .phase-desc { font-size: 13px; color: #8ba3c4; line-height: 1.6; }
  .owner-tag {
    font-size: 10px; font-weight: 600; padding: 3px 8px; border-radius: 4px;
    background: rgba(59,130,246,0.15); color: #60a5fa; margin-right: 6px;
  }

  /* Streamlit tab styling */
  .stTabs [data-baseweb="tab-list"] { gap: 4px; }
  .stTabs [data-baseweb="tab"] {
    font-size: 13px; font-weight: 500; color: #8ba3c4;
    border-radius: 8px 8px 0 0; padding: 8px 16px;
  }
</style>
""", unsafe_allow_html=True)

# -- CONFIG --

BASE_ID = "appUJlBFPnTUFJmOx"

VIEWS = {
    "blockers_remaining": ("tblHIDvz3UahqWf1h", "viwAT3pgxpCeApJsM"),
    "blockers_complete":  ("tblHIDvz3UahqWf1h", "viwI45OS0OTda4w3C"),
    "signoffs":           ("tblHIDvz3UahqWf1h", "viwcRZQfywN0cyvFl"),
    "gaps":               ("tblHIDvz3UahqWf1h", "viwlueN7Fe0ahlfpM"),
    "completed":          ("tblHIDvz3UahqWf1h", "viwiijG1RkwN62KSI"),
    "eng_remaining":      ("tblHIDvz3UahqWf1h", "viw0XBjg0kfksT06T"),
    "decisions_made":     ("tblIbxPFGdXNSI3rE", "viwT6Mn7zCm0df5ul"),
    "decisions_pending":  ("tblIbxPFGdXNSI3rE", "viwe6OkcS1mqHNnNo"),
    "decisions_needed":   ("tblIbxPFGdXNSI3rE", "viwZjwMjP7UmUitbZ"),
    "decisions_open":     ("tblIbxPFGdXNSI3rE", "viwZA3HsTO3DWU6Jm"),
    "open_risks":         ("tbl6GWnx6Oz18kbyi", "viwzV39ZM3CcNWbkE"),
}

# -- DATA FETCHING --

@st.cache_data(ttl=300, show_spinner=False)
def fetch_view(pat, table_id, view_id):
    records, offset = [], None
    while True:
        params = {"view": view_id, "pageSize": 100}
        if offset:
            params["offset"] = offset
        resp = requests.get(
            f"https://api.airtable.com/v0/{BASE_ID}/{table_id}",
            headers={"Authorization": f"Bearer {pat}"},
            params=params,
            timeout=15,
        )
        if not resp.ok:
            err = resp.json().get("error", {})
            raise Exception(f"Airtable error {resp.status_code}: {err.get('message', 'unknown')}")
        data = resp.json()
        records.extend(data.get("records", []))
        offset = data.get("offset")
        if not offset:
            break
    return records

@st.cache_data(ttl=300, show_spinner=False)
def fetch_all(pat):
    result = {}
    for key, (table_id, view_id) in VIEWS.items():
        records = fetch_view(pat, table_id, view_id)
        result[key] = [r["fields"] for r in records]
    return result

# -- CHARTS --

DARK = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter, sans-serif", color="#8ba3c4", size=13),
    margin=dict(l=0, r=0, t=10, b=0),
)

def ring(value, total, color, title):
    fig = go.Figure(go.Pie(
        values=[value, max(total - value, 0)],
        hole=0.72, marker_colors=[color, "#1a2744"],
        textinfo="none", labels=[title, "Remaining"], sort=False,
    ))
    fig.add_annotation(text=f"<b>{value}</b>", x=0.5, y=0.55, showarrow=False,
                       font=dict(size=30, color=color, family="Inter"))
    fig.add_annotation(text=f"of {total}", x=0.5, y=0.35, showarrow=False,
                       font=dict(size=14, color="#7b93b3", family="Inter"))
    fig.update_layout(**DARK, height=160, showlegend=False)
    return fig

def workstream_bar(eng_done, eng_total, blockers_done, blockers_rem, signoffs_done, signoffs_total, gaps_done, gaps_total):
    cats = [
        f"Engineering ({eng_total})",
        f"Blockers ({blockers_done + blockers_rem})",
        f"Sign-offs ({signoffs_total})",
        f"Gap Tickets ({gaps_total})",
    ]
    # Calculate dynamic values from live data
    eng_remaining = eng_total - eng_done
    blockers_total = blockers_done + blockers_rem
    signoffs_remaining = signoffs_total - signoffs_done
    gaps_remaining = gaps_total - gaps_done

    fig = go.Figure()
    for vals, label, color in [
        ([eng_done, blockers_done, signoffs_done, gaps_done], "Completed", "#22c55e"),
        ([eng_remaining, blockers_rem, signoffs_remaining, gaps_remaining], "Remaining", "#334155"),
    ]:
        fig.add_trace(go.Bar(
            name=label, y=cats, x=vals, orientation="h",
            marker_color=color, marker_line_width=0,
        ))
    max_val = max(eng_total, blockers_total, signoffs_total, gaps_total) + 2
    fig.update_layout(
        **DARK, barmode="stack", height=220, bargap=0.35,
        xaxis=dict(range=[0, max_val], showgrid=True, gridcolor="#1a2744"),
        yaxis=dict(showgrid=False, tickfont=dict(size=13, color="#c8d6e5")),
        legend=dict(orientation="h", y=1.02, x=0, font=dict(size=12, color="#8ba3c4"),
                    bgcolor="rgba(0,0,0,0)"),
    )
    return fig

def decision_donut(made, pending, needed):
    total = made + pending + needed
    pct = round(made / total * 100) if total else 0
    fig = go.Figure(go.Pie(
        values=[made, pending, needed], labels=["Made", "Pending", "Needed"],
        hole=0.68, marker_colors=["#22c55e", "#f59e0b", "#ef4444"],
        textinfo="none", sort=False,
    ))
    fig.add_annotation(text=f"<b>{pct}%</b>", x=0.5, y=0.55, showarrow=False,
                       font=dict(size=28, color="#e8edf5", family="Inter"))
    fig.add_annotation(text="decided", x=0.5, y=0.35, showarrow=False,
                       font=dict(size=13, color="#7b93b3", family="Inter"))
    fig.update_layout(
        **DARK, height=220, showlegend=True,
        legend=dict(orientation="h", y=-0.15, x=0.5, xanchor="center",
                    font=dict(size=12, color="#8ba3c4"), bgcolor="rgba(0,0,0,0)"),
    )
    return fig

def completion_bar(eng_pct, blockers_pct, signoffs_pct, gaps_pct, decisions_pct):
    cats = ["Engineering", "Blockers", "Sign-offs", "Gaps", "Decisions"]
    pcts = [eng_pct, blockers_pct, signoffs_pct, gaps_pct, decisions_pct]
    fig = go.Figure(go.Bar(
        x=cats, y=pcts,
        marker_color=["#22c55e" if p >= 60 else "#f59e0b" if p >= 30 else "#ef4444" for p in pcts],
        marker_line_width=0,
        text=[f"{p}%" for p in pcts], textposition="outside",
        textfont=dict(size=13, color="#c8d6e5"),
    ))
    fig.add_hline(y=100, line_dash="dot", line_color="#334155", line_width=1)
    fig.update_layout(
        **DARK, height=220, showlegend=False,
        xaxis=dict(showgrid=False, tickfont=dict(size=13, color="#c8d6e5")),
        yaxis=dict(range=[0, 115], ticksuffix="%", showgrid=True, gridcolor="#1a2744"),
    )
    return fig

def fnr_trend_chart():
    """False Negative Rate trend from baseline analysis."""
    months = ["Oct 2025", "Nov 2025", "Dec 2025", "Jan 2026", "Feb 2026"]
    fnr = [48.9, 61.3, 6.7, 9.6, 0.0]
    apps = [435, 374, 327, 344, 296]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=months, y=apps, name="Non-Ent Apps",
        marker_color="#1e40af", opacity=0.6, yaxis="y",
    ))
    fig.add_trace(go.Scatter(
        x=months, y=fnr, name="False Negative Rate %",
        mode="lines+markers+text", line=dict(color="#ef4444", width=3),
        marker=dict(size=8, color="#ef4444"),
        text=[f"{v}%" for v in fnr], textposition="top center",
        textfont=dict(size=11, color="#f87171"),
        yaxis="y2",
    ))
    fig.add_hline(y=15, line_dash="dash", line_color="#f59e0b", line_width=1,
                  annotation_text="Alert: 15%", annotation_font_color="#fbbf24",
                  annotation_font_size=10, yref="y2")
    fig.update_layout(
        **DARK, height=280, showlegend=True,
        legend=dict(orientation="h", y=1.12, x=0, font=dict(size=11, color="#8ba3c4"),
                    bgcolor="rgba(0,0,0,0)"),
        yaxis=dict(title="Apps", showgrid=True, gridcolor="#1a2744",
                   titlefont=dict(size=11, color="#7b93b3"),
                   tickfont=dict(color="#7b93b3")),
        yaxis2=dict(title="FNR %", overlaying="y", side="right", range=[0, 70],
                    titlefont=dict(size=11, color="#f87171"),
                    tickfont=dict(color="#f87171"), showgrid=False),
        xaxis=dict(tickfont=dict(size=12, color="#c8d6e5")),
    )
    return fig

def tld_risk_chart():
    """TLD-based bypass rate chart from baseline analysis."""
    tlds = [".ai", ".io", ".com", ".uk", ".co", ".me", ".online", ".net"]
    rates = [10.3, 16.3, 31.7, 42.3, 43.6, 46.7, 56.2, 63.6]
    colors = ["#22c55e" if r < 20 else "#f59e0b" if r < 40 else "#ef4444" for r in rates]

    fig = go.Figure(go.Bar(
        y=tlds, x=rates, orientation="h",
        marker_color=colors, marker_line_width=0,
        text=[f"{r}%" for r in rates], textposition="outside",
        textfont=dict(size=12, color="#c8d6e5"),
    ))
    fig.add_vline(x=30, line_dash="dash", line_color="#f59e0b", line_width=1)
    fig.update_layout(
        **DARK, height=280, showlegend=False,
        xaxis=dict(title="Bypass Rate %", showgrid=True, gridcolor="#1a2744",
                   titlefont=dict(size=11, color="#7b93b3"),
                   tickfont=dict(color="#7b93b3")),
        yaxis=dict(tickfont=dict(size=13, color="#c8d6e5")),
    )
    return fig

# -- AI SUMMARY --

@st.cache_data(ttl=600, show_spinner=False)
def ai_summary(pat_hash, data_hash, prompt):
    try:
        key = st.secrets.get("GEMINI_API_KEY", "")
        if not key:
            return "Add GEMINI_API_KEY to Streamlit secrets to enable AI summaries."
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={key}"
        for attempt in range(3):
            resp = requests.post(url, json={"contents": [{"parts": [{"text": prompt}]}]}, timeout=30)
            if resp.status_code == 429:
                time.sleep(2 ** attempt)
                continue
            resp.raise_for_status()
            return resp.json()["candidates"][0]["content"]["parts"][0]["text"]
        return "Gemini rate limit hit -- summary will appear on next refresh."
    except Exception as e:
        return f"Gemini API error: {str(e)}"

STATUS_BADGE = {
    "Completed":   ("DONE",        "badge-green"),
    "In Progress": ("IN PROGRESS", "badge-amber"),
    "In Review":   ("IN REVIEW",   "badge-blue"),
    "Blocked":     ("BLOCKED",     "badge-red"),
    "Not Started": ("NOT STARTED", "badge-gray"),
    "Made":        ("MADE",        "badge-green"),
    "Pending":     ("PENDING",     "badge-amber"),
    "Needed":      ("NEEDED",      "badge-red"),
}

def status_badge(status):
    label, cls = STATUS_BADGE.get(status, (status.upper(), "badge-gray"))
    return f'<span class="detail-badge {cls}">{label}</span>'

def priority_badge(priority):
    cls = {"High": "badge-red", "Medium": "badge-amber", "Low": "badge-gray"}.get(priority, "badge-gray")
    return f'<span class="detail-badge {cls}">{priority.upper()}</span>'

# -- MAIN --

def main():
    pat = st.secrets.get("AIRTABLE_PAT", "")
    if not pat:
        st.markdown("""<div style="background:#141e30;border-radius:12px;padding:24px;margin-bottom:20px;border:1px solid #1e3050">
          <div style="font-size:13px;color:#8ba3c4;margin-bottom:8px;font-weight:600">AIRTABLE PERSONAL ACCESS TOKEN</div>
          <div style="font-size:14px;color:#c8d6e5">Add <code>AIRTABLE_PAT</code> to Streamlit Cloud secrets.</div>
        </div>""", unsafe_allow_html=True)
        pat = st.text_input("Or enter your Airtable PAT:", type="password", key="pat_input")
        if not pat:
            st.stop()

    with st.spinner("Fetching live Airtable data..."):
        try:
            data = fetch_all(pat)
        except Exception as e:
            st.error(f"Airtable connection failed: {e}")
            st.stop()

    # -- Compute metrics from live data --
    eng_total = 11
    eng_done = eng_total - len(data.get("eng_remaining", []))
    blockers_done = len(data.get("blockers_complete", []))
    blockers_rem = len(data.get("blockers_remaining", []))
    blockers_total = blockers_done + blockers_rem
    signoffs_total = 11
    signoffs_list = data.get("signoffs", [])
    signoffs_rem = len(signoffs_list)
    signoffs_done = signoffs_total - signoffs_rem
    gaps_total = 7
    gaps_list = data.get("gaps", [])
    gaps_rem = len(gaps_list)
    gaps_done = gaps_total - gaps_rem
    decisions_made = len(data.get("decisions_made", []))
    decisions_pending = len(data.get("decisions_pending", []))
    decisions_needed = len(data.get("decisions_needed", []))
    decisions_total = decisions_made + decisions_pending + decisions_needed
    open_risks = len(data.get("open_risks", []))

    eng_pct = round(eng_done / eng_total * 100) if eng_total else 0
    blockers_pct = round(blockers_done / blockers_total * 100) if blockers_total else 0
    signoffs_pct = round(signoffs_done / signoffs_total * 100) if signoffs_total else 0
    gaps_pct = round(gaps_done / gaps_total * 100) if gaps_total else 0
    decisions_pct = round(decisions_made / decisions_total * 100) if decisions_total else 0

    # =====================================================
    # MASTHEAD
    # =====================================================
    st.markdown(f"""
    <div class="masthead">
      <div>
        <div class="masthead-eyebrow">OneSignal &nbsp;|&nbsp; Trust &amp; Safety Operations &nbsp;|&nbsp; eHawk Phase 3</div>
        <div class="masthead-title">Launch Readiness Dashboard</div>
        <div class="masthead-sub">{datetime.now().strftime('%A, %B %d, %Y')} &nbsp;|&nbsp; Live data from Airtable &nbsp;|&nbsp; Refreshes every 5 min</div>
      </div>
      <div style="text-align:right">
        <div class="masthead-big">{blockers_rem}</div>
        <div class="masthead-label">blockers to launch</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # =====================================================
    # PHASE 3 OVERVIEW
    # =====================================================
    st.markdown('<div class="section-header">Phase 3 Overview</div>', unsafe_allow_html=True)
    ov1, ov2, ov3 = st.columns(3)
    with ov1:
        st.markdown("""<div class="phase-card">
          <div class="phase-title">What is eHawk Phase 3?</div>
          <div class="phase-desc">
            Auto-approval pipeline for email domain verification. Replaces manual review with
            eHawk scoring to automatically verify low-risk email app provisioning requests,
            reducing T&amp;S workload while maintaining fraud detection coverage.
          </div>
        </div>""", unsafe_allow_html=True)
    with ov2:
        st.markdown(f"""<div class="phase-card">
          <div class="phase-title">Current Status</div>
          <div class="phase-desc">
            <span class="owner-tag">ENG</span> {eng_pct}% complete &nbsp;
            <span class="owner-tag">T&amp;S</span> {signoffs_pct}% signed off<br><br>
            {open_risks} open risks tracked &nbsp;|&nbsp; {decisions_needed} critical decisions pending<br>
            {blockers_rem} pre-launch blockers remaining
          </div>
        </div>""", unsafe_allow_html=True)
    with ov3:
        st.markdown("""<div class="phase-card">
          <div class="phase-title">Workstream Owners</div>
          <div class="phase-desc">
            <span class="owner-tag">ENGINEERING</span> Tickets T1-T11, gap remediation<br>
            <span class="owner-tag">T&amp;S OPS</span> Sign-offs, scoring thresholds, policy<br>
            <span class="owner-tag">PRODUCT</span> Decision log, launch criteria<br>
            <span class="owner-tag">LEADERSHIP</span> Final go/no-go approval
          </div>
        </div>""", unsafe_allow_html=True)

    # =====================================================
    # KPI ROW
    # =====================================================
    st.markdown('<div class="section-header">Launch Readiness KPIs</div>', unsafe_allow_html=True)
    k1, k2, k3, k4, k5 = st.columns(5)
    color_map = {"green": "#22c55e", "amber": "#f59e0b", "red": "#ef4444", "blue": "#3b82f6"}
    kpi_data = [
        (k1, eng_done, eng_total, "green", "Engineering Tickets",
         f"T9 &amp; T11 in progress", f"{eng_pct}% complete"),
        (k2, blockers_done, blockers_total, "amber" if blockers_pct >= 30 else "red", "Pre-Launch Blockers",
         f"{blockers_done} cleared", f"{blockers_pct}% cleared"),
        (k3, signoffs_done, signoffs_total, "green" if signoffs_pct >= 60 else "red", "T&S Sign-offs",
         f"{signoffs_rem} outstanding", f"{signoffs_pct}% confirmed"),
        (k4, gaps_done, gaps_total, "green" if gaps_pct >= 60 else "red", "Gap Tickets",
         f"{gaps_rem} open", f"{gaps_pct}% closed"),
        (k5, decisions_made, decisions_total, "blue", "Decisions",
         f"{decisions_needed} critical needed", f"{decisions_pct}% decided"),
    ]
    for col, val, tot, color, label, ctx, pct in kpi_data:
        with col:
            st.plotly_chart(
                ring(val, tot, color_map[color], label),
                use_container_width=True, config={"displayModeBar": False},
            )
            st.markdown(f"""<div class="kpi-card {color}">
              <div class="kpi-label">{label}</div>
              <div style="display:flex;align-items:baseline;gap:4px;margin-bottom:4px">
                <span class="kpi-num">{val}</span><span class="kpi-denom">/{tot}</span>
              </div>
              <div class="kpi-context">{ctx}</div>
              <span class="kpi-pct">{pct}</span>
            </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # =====================================================
    # PIPELINE PROGRESS CHARTS
    # =====================================================
    st.markdown('<div class="section-header">Pipeline Progress</div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns([5, 3, 3])
    with c1:
        st.markdown("**Work status by category**")
        st.plotly_chart(
            workstream_bar(eng_done, eng_total, blockers_done, blockers_rem,
                           signoffs_done, signoffs_total, gaps_done, gaps_total),
            use_container_width=True, config={"displayModeBar": False},
        )
    with c2:
        st.markdown("**Decision velocity**")
        st.plotly_chart(
            decision_donut(decisions_made, decisions_pending, decisions_needed),
            use_container_width=True, config={"displayModeBar": False},
        )
    with c3:
        st.markdown("**Completion % by workstream**")
        st.plotly_chart(
            completion_bar(eng_pct, blockers_pct, signoffs_pct, gaps_pct, decisions_pct),
            use_container_width=True, config={"displayModeBar": False},
        )

    # =====================================================
    # FRAUD BASELINE METRICS
    # =====================================================
    st.markdown('<div class="section-header">Fraud Baseline Metrics <span style="font-size:9px;background:rgba(139,163,196,0.15);color:#8ba3c4;padding:2px 7px;border-radius:3px;font-weight:700;margin-left:6px">OCT 2025 - FEB 2026</span></div>', unsafe_allow_html=True)

    b1, b2, b3, b4 = st.columns(4)
    with b1:
        st.markdown("""<div class="baseline-card">
          <div class="baseline-title">False Negative Rate</div>
          <div style="display:flex;justify-content:space-between;align-items:flex-end;margin-bottom:12px">
            <div>
              <div class="baseline-value val-warn">30.7%</div>
              <div class="baseline-label">Non-Enterprise overall</div>
            </div>
            <div style="text-align:right">
              <div class="baseline-value val-good" style="font-size:20px">0.0%</div>
              <div class="baseline-label">Feb 2026 (latest)</div>
            </div>
          </div>
          <div class="baseline-row">
            <span class="baseline-metric">Enterprise FNR</span>
            <span class="baseline-val val-warn">14.7%</span>
          </div>
          <div class="baseline-row">
            <span class="baseline-metric">Peak (Nov 2025)</span>
            <span class="baseline-val val-bad">61.3%</span>
          </div>
          <div class="baseline-row">
            <span class="baseline-metric">Alert threshold</span>
            <span class="baseline-val" style="color:#fbbf24">&gt;15%/month</span>
          </div>
        </div>""", unsafe_allow_html=True)
    with b2:
        st.markdown("""<div class="baseline-card">
          <div class="baseline-title">Detection Time</div>
          <div style="display:flex;justify-content:space-between;align-items:flex-end;margin-bottom:12px">
            <div>
              <div class="baseline-value" style="color:#60a5fa">7.7d</div>
              <div class="baseline-label">Non-Ent median (manual)</div>
            </div>
            <div style="text-align:right">
              <div class="baseline-value" style="color:#60a5fa;font-size:20px">2.3d</div>
              <div class="baseline-label">Non-Ent (auto)</div>
            </div>
          </div>
          <div class="baseline-row">
            <span class="baseline-metric">Enterprise manual</span>
            <span class="baseline-val val-bad">34.0 days</span>
          </div>
          <div class="baseline-row">
            <span class="baseline-metric">Enterprise auto</span>
            <span class="baseline-val val-warn">18.5 days</span>
          </div>
          <div class="baseline-row">
            <span class="baseline-metric">Alert threshold</span>
            <span class="baseline-val" style="color:#fbbf24">&gt;7 days</span>
          </div>
        </div>""", unsafe_allow_html=True)
    with b3:
        st.markdown("""<div class="baseline-card">
          <div class="baseline-title">App Population</div>
          <div style="display:flex;justify-content:space-between;align-items:flex-end;margin-bottom:12px">
            <div>
              <div class="baseline-value" style="color:#c8d6e5">2,333</div>
              <div class="baseline-label">Non-Enterprise apps</div>
            </div>
            <div style="text-align:right">
              <div class="baseline-value" style="color:#c8d6e5;font-size:20px">163</div>
              <div class="baseline-label">Enterprise apps</div>
            </div>
          </div>
          <div class="baseline-row">
            <span class="baseline-metric">Non-Ent verified</span>
            <span class="baseline-val val-warn">58.9%</span>
          </div>
          <div class="baseline-row">
            <span class="baseline-metric">Non-Ent never enabled</span>
            <span class="baseline-val val-bad">40.8%</span>
          </div>
          <div class="baseline-row">
            <span class="baseline-metric">Enterprise verified</span>
            <span class="baseline-val val-good">87.7%</span>
          </div>
        </div>""", unsafe_allow_html=True)
    with b4:
        st.markdown("""<div class="baseline-card">
          <div class="baseline-title">Enforcement &amp; Volume</div>
          <div style="display:flex;justify-content:space-between;align-items:flex-end;margin-bottom:12px">
            <div>
              <div class="baseline-value val-bad">88.6%</div>
              <div class="baseline-label">100K+ enforced rate</div>
            </div>
            <div style="text-align:right">
              <div class="baseline-value" style="color:#c8d6e5;font-size:20px">12M</div>
              <div class="baseline-label">Spam ring emails</div>
            </div>
          </div>
          <div class="baseline-row">
            <span class="baseline-metric">Spam ring apps</span>
            <span class="baseline-val val-bad">31 apps</span>
          </div>
          <div class="baseline-row">
            <span class="baseline-metric">Fraud domain rate</span>
            <span class="baseline-val val-warn">19.0%</span>
          </div>
          <div class="baseline-row">
            <span class="baseline-metric">Push:Email ratio (clean)</span>
            <span class="baseline-val val-good">53.4:1</span>
          </div>
        </div>""", unsafe_allow_html=True)

    # Baseline trend charts
    st.markdown("<br>", unsafe_allow_html=True)
    bc1, bc2 = st.columns(2)
    with bc1:
        st.markdown("**False Negative Rate Trend (Non-Enterprise)**")
        st.plotly_chart(fnr_trend_chart(), use_container_width=True, config={"displayModeBar": False})
    with bc2:
        st.markdown("**TLD Bypass Rate (Non-Enterprise)**")
        st.plotly_chart(tld_risk_chart(), use_container_width=True, config={"displayModeBar": False})

    # Recommendations from baseline
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("**Baseline Recommendations & Alert Thresholds**")
    rec_data = [
        ("CRITICAL", "badge-red", "Volume-based auto-escalation", "88.6% enforcement at 100K+", "Auto-escalate >10K, suspend >50K"),
        ("CRITICAL", "badge-red", "Cross-org domain blocking", "20 fraud domains org-hopping", "Block domain if prior enforcement (eHawk scoring)"),
        ("HIGH", "badge-amber", "Spam ring fingerprinting", "31 apps, 12M emails", "[Brand] App pattern + clustering (eHawk scoring)"),
        ("HIGH", "badge-amber", "TLD risk weighting", ".net 63.6%, .online 56.2%", "Enhanced scrutiny high-risk TLDs (eHawk scoring)"),
        ("MEDIUM", "badge-blue", "Enterprise detection acceleration", "34-day median detection", "Target <14 day detection"),
    ]
    for priority, badge_cls, rec, current, target in rec_data:
        st.markdown(f"""<div class="detail-item">
          <span class="detail-badge {badge_cls}">{priority}</span>
          <span style="color:#e8edf5;min-width:220px;font-weight:500">{rec}</span>
          <span style="color:#8ba3c4;flex:1">Current: {current}</span>
          <span style="color:#4ade80;flex:1">Target: {target}</span>
        </div>""", unsafe_allow_html=True)

    # =====================================================
    # AI EXECUTIVE SUMMARY
    # =====================================================
    st.markdown('<div class="section-header">AI Executive Summary <span style="font-size:9px;background:rgba(59,130,246,0.15);color:#60a5fa;padding:2px 7px;border-radius:3px;font-weight:700;margin-left:6px">GEMINI 2.0 FLASH</span></div>', unsafe_allow_html=True)
    prompt = f"""Write a 3-paragraph executive status brief for the OneSignal eHawk Phase 3 auto-approval pipeline. Date: {datetime.now().strftime('%B %d, %Y')}. Prose only. No bullets. No hedging. Be direct.

LIVE DATA:
- Engineering: {eng_done}/{eng_total} done ({eng_pct}%). T9 and T11 in progress. T3 blocked.
- Pre-launch blockers: {blockers_done}/{blockers_total} cleared, {blockers_rem} remaining.
- T&S sign-offs: {signoffs_done}/{signoffs_total} confirmed ({signoffs_pct}%). Critical bottleneck.
- Gap tickets: {gaps_done}/{gaps_total} closed. {gaps_rem} open.
- Decisions: {decisions_made}/{decisions_total} made. {decisions_needed} critical decisions blocking downstream engineering.
- Open risks: {open_risks} tracked.

BASELINE CONTEXT:
- Non-Enterprise False Negative Rate dropped from 61.3% peak (Nov 2025) to 0.0% (Feb 2026).
- 31-app spam ring identified accounting for 12M emails (58.3% of Non-Ent volume).
- High-risk TLDs: .net 63.6% bypass, .online 56.2% bypass.
- 88.6% enforcement rate at 100K+ email volume band.
- Enterprise median detection time: 34 days (target <14 days).

Paragraph 1 -- STATE: Engineering momentum vs T&S readiness gap.
Paragraph 2 -- CONSTRAINT: What happens if T&S sign-offs don't move this week.
Paragraph 3 -- NEXT 7 DAYS: Three specific actions with implied owners."""

    data_hash = hashlib.md5(str([(k, len(v)) for k, v in sorted(data.items())]).encode()).hexdigest()
    pat_hash = hashlib.md5(pat[:8].encode()).hexdigest()
    _, btn_col = st.columns([10, 1])
    with btn_col:
        if st.button("Refresh", help="Regenerate AI summary"):
            st.cache_data.clear()
            st.rerun()
    with st.spinner("Generating AI analysis..."):
        summary = ai_summary(pat_hash, data_hash, prompt)
    paras = [p.strip() for p in summary.strip().split("\n\n") if p.strip()]
    labels = ["State", "Constraint", "Next 7 Days"]
    colors = ["#3b82f6", "#ef4444", "#22c55e"]
    cols = st.columns(min(len(paras), 3))
    for i, (col, para) in enumerate(zip(cols, paras)):
        with col:
            label = labels[i] if i < len(labels) else ""
            color = colors[i] if i < len(colors) else "#7b93b3"
            st.markdown(f"""<div style="background:#0f172a;border-radius:10px;padding:18px 20px;border-top:2px solid {color};border:1px solid #1e3050;border-top:3px solid {color}">
              <div style="font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:.12em;color:{color};margin-bottom:12px">{label}</div>
              <div style="font-size:14px;line-height:1.75;color:#c8d6e5">{para}</div>
            </div>""", unsafe_allow_html=True)

    # =====================================================
    # DRILL-DOWN TABS
    # =====================================================
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="section-header">Drill-Down Detail</div>', unsafe_allow_html=True)
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        f"Blockers ({blockers_rem})",
        f"Sign-offs ({signoffs_rem})",
        f"Decisions Needed ({decisions_needed})",
        f"Gap Tickets ({gaps_rem})",
        f"Open Risks ({open_risks})",
        "Recently Completed",
    ])
    with tab1:
        st.markdown("**Pre-launch blockers -- must clear before launch**")
        if not data.get("blockers_remaining"):
            st.markdown('<div style="color:#4ade80;padding:12px;font-size:14px">All blockers cleared!</div>', unsafe_allow_html=True)
        for item in data.get("blockers_remaining", []):
            name = item.get("Task Name", "Untitled")
            p = priority_badge(item.get("Priority", "")) if item.get("Priority") else ""
            st.markdown(f'<div class="detail-item">{status_badge(item.get("Status","Not Started"))}{p}<span style="color:#e8edf5">{name}</span></div>', unsafe_allow_html=True)
    with tab2:
        st.markdown("**T&S sign-offs outstanding -- T&S owns all of these**")
        if not data.get("signoffs"):
            st.markdown('<div style="color:#4ade80;padding:12px;font-size:14px">All sign-offs confirmed!</div>', unsafe_allow_html=True)
        for item in data.get("signoffs", []):
            name = item.get("Task Name", "Untitled")
            st.markdown(f'<div class="detail-item">{status_badge(item.get("Status","Not Started"))}<span style="color:#e8edf5">{name}</span></div>', unsafe_allow_html=True)
    with tab3:
        st.markdown("**Critical decisions blocking downstream engineering**")
        if not data.get("decisions_needed"):
            st.markdown('<div style="color:#4ade80;padding:12px;font-size:14px">All decisions made!</div>', unsafe_allow_html=True)
        for item in data.get("decisions_needed", []):
            title = item.get("Title", "Untitled")
            notes = item.get("Unblocks / Notes", "")[:120]
            notes_html = f'<div style="font-size:12px;color:#7b93b3;margin-top:4px">{notes}</div>' if notes else ""
            st.markdown(f'<div class="detail-item"><span class="detail-badge badge-red">NEEDED</span><div><div style="color:#e8edf5">{title}</div>{notes_html}</div></div>', unsafe_allow_html=True)
    with tab4:
        st.markdown("**Gap tickets -- all must close before launch**")
        if not data.get("gaps"):
            st.markdown('<div style="color:#4ade80;padding:12px;font-size:14px">All gap tickets closed!</div>', unsafe_allow_html=True)
        for item in data.get("gaps", []):
            name = item.get("Task Name", "Untitled")
            p = priority_badge(item.get("Priority", "")) if item.get("Priority") else ""
            st.markdown(f'<div class="detail-item">{status_badge(item.get("Status","Not Started"))}{p}<span style="color:#e8edf5">{name}</span></div>', unsafe_allow_html=True)
    with tab5:
        st.markdown("**Open risks being tracked**")
        if not data.get("open_risks"):
            st.markdown('<div style="color:#4ade80;padding:12px;font-size:14px">No open risks!</div>', unsafe_allow_html=True)
        for item in data.get("open_risks", []):
            name = item.get("Risk", item.get("Title", item.get("Name", "Untitled")))
            severity = item.get("Severity", item.get("Priority", ""))
            sev_badge = priority_badge(severity) if severity else ""
            st.markdown(f'<div class="detail-item">{sev_badge}<span style="color:#e8edf5">{name}</span></div>', unsafe_allow_html=True)
    with tab6:
        st.markdown("**What's been completed -- engineering foundation is solid**")
        if not data.get("completed"):
            st.markdown('<div style="color:#7b93b3;padding:12px;font-size:14px">No completed items yet.</div>', unsafe_allow_html=True)
        for item in data.get("completed", []):
            name = item.get("Task Name", "Untitled")
            section = item.get("Section", "")
            sec_html = f'<span class="detail-badge badge-gray">{section.upper()[:12]}</span>' if section else ""
            st.markdown(f'<div class="detail-item"><span class="detail-badge badge-green">DONE</span>{sec_html}<span style="color:#e8edf5">{name}</span></div>', unsafe_allow_html=True)

    # =====================================================
    # FOOTER
    # =====================================================
    st.markdown(f"""<div style="margin-top:36px;padding-top:18px;border-top:1px solid #1e3050;font-size:12px;color:#4a6080;text-align:center">
      OneSignal eHawk Phase 3 Auto-Approval Pipeline &nbsp;|&nbsp; Confidential &nbsp;|&nbsp;
      {datetime.now().strftime('%B %d, %Y %H:%M')} &nbsp;|&nbsp; Data cached 5 min &nbsp;|&nbsp; Streamlit + Airtable + Gemini
    </div>""", unsafe_allow_html=True)


if __name__ == "__main__":
    main()
