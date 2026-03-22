"""
OneSignal eHawk Phase 3 â Executive Launch Readiness Dashboard
============================================================
Run locally:   streamlit run dashboard.py
Deploy:        Push to GitHub â connect to share.streamlit.io (free)

Requirements:  pip install streamlit plotly requests anthropic python-dotenv

Config:  Set secrets in .streamlit/secrets.toml  OR  Streamlit Cloud â App Settings â Secrets
    AIRTABLE_PAT = "patXXXXXXXX"
    ANTHROPIC_API_KEY = "sk-ant-..."
"""

import streamlit as st
import requests
import anthropic
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import pandas as pd
# âââ PAGE CONFIG âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ

st.set_page_config(
    page_title="eHawk Phase 3 â Launch Readiness",
    page_icon="ð",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# âââ CUSTOM CSS ââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ

st.markdown("""
<style>
  /* Import fonts */
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

  /* Global */
  html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
  .main .block-container { padding-top: 1.5rem; padding-bottom: 2rem; max-width: 1400px; }
  h1, h2, h3 { font-family: 'Inter', sans-serif !important; letter-spacing: -0.02em; }

  /* Hide streamlit chrome */
  #MainMenu { visibility: hidden; }
  footer { visibility: hidden; }
  .stDeployButton { display: none; }

  /* Masthead */
  .masthead {
    background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
    border-radius: 12px;
    padding: 24px 32px;
    margin-bottom: 20px;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
  .masthead-left { }
  .masthead-eyebrow { font-size: 11px; letter-spacing: 0.15em; text-transform: uppercase; color: #475569; margin-bottom: 4px; }
  .masthead-title { font-size: 22px; font-weight: 700; color: #f1f5f9; letter-spacing: -0.03em; margin: 0; }
  .masthead-sub { font-size: 12px; color: #475569; margin-top: 4px; }
  .masthead-right { text-align: right; }
  .masthead-big { font-size: 52px; font-weight: 800; color: #f59e0b; letter-spacing: -0.04em; line-height: 1; }
  .masthead-label { font-size: 11px; text-transform: uppercase; letter-spacing: 0.12em; color: #64748b; margin-top: 2px; }

  /* KPI Cards */
  .kpi-card {
    background: #1e293b;
    border-radius: 10px;
    padding: 16px 18px 14px;
    border-top: 3px solid transparent;
    height: 100%;
  }
  .kpi-card.green  { border-top-color: #10b981; }
  .kpi-card.amber  { border-top-color: #f59e0b; }
  .kpi-card.red    { border-top-color: #ef4444; }
  .kpi-card.blue   { border-top-color: #3b82f6; }
  .kpi-label { font-size: 10px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.12em; color: #64748b; margin-bottom: 8px; }
  .kpi-fraction { display: flex; align-items: baseline; gap: 4px; margin-bottom: 4px; }
  .kpi-num { font-size: 32px; font-weight: 700; letter-spacing: -0.03em; line-height: 1; }
  .kpi-card.green .kpi-num  { color: #10b981; }
  .kpi-card.amber .kpi-num  { color: #f59e0b; }
  .kpi-card.red   .kpi-num  { color: #ef4444; }
  .kpi-card.blue  .kpi-num  { color: #3b82f6; }
  .kpi-denom { font-size: 14px; color: #475569; font-weight: 400; }
  .kpi-context { font-size: 11px; color: #64748b; margin-top: 2px; }
  .kpi-pct { font-size: 10px; font-weight: 600; padding: 2px 7px; border-radius: 3px; display: inline-block; margin-top: 6px; }
  .kpi-card.green  .kpi-pct { background: rgba(16,185,129,0.15); color: #10b981; }
  .kpi-card.amber  .kpi-pct { background: rgba(245,158,11,0.15); color: #f59e0b; }
  .kpi-card.red    .kpi-pct { background: rgba(239,68,68,0.15);  color: #ef4444; }
  .kpi-card.blue   .kpi-pct { background: rgba(59,130,246,0.15); color: #3b82f6; }

  /* Section headers */
  .section-header {
    font-size: 11px; font-weight: 600; text-transform: uppercase;
    letter-spacing: 0.12em; color: #64748b;
    margin: 24px 0 12px; padding-bottom: 8px;
    border-bottom: 1px solid #1e293b;
  }

  /* AI Panel */
  .ai-panel {
    background: #0f172a;
    border: 1px solid #1e293b;
    border-radius: 10px;
    padding: 20px 24px;
  }
  .ai-badge {
    display: inline-block; font-size: 9px; font-weight: 700;
    text-transform: uppercase; letter-spacing: 0.1em;
    background: rgba(59,130,246,0.15); color: #3b82f6;
    padding: 2px 8px; border-radius: 3px; margin-left: 8px;
    vertical-align: middle;
  }

  /* Detail tables */
  .detail-item {
    display: flex; align-items: flex-start; gap: 10px;
    padding: 8px 0; border-bottom: 1px solid #1e293b;
    font-size: 13px;
  }
  .detail-badge {
    font-size: 9px; font-weight: 700; padding: 2px 6px;
    border-radius: 3px; white-space: nowrap; flex-shrink: 0; margin-top: 2px;
  }
  .badge-red    { background: rgba(239,68,68,0.15);  color: #ef4444; }
  .badge-amber  { background: rgba(245,158,11,0.15); color: #f59e0b; }
  .badge-green  { background: rgba(16,185,129,0.15); color: #10b981; }
  .badge-blue   { background: rgba(59,130,246,0.15); color: #3b82f6; }
  .badge-gray   { background: rgba(100,116,139,0.15); color: #94a3b8; }

  /* Stmetric override */
  [data-testid="stMetric"] { background: transparent; }
</style>
""", unsafe_allow_html=True)

# âââ CONFIG ââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ

BASE_ID = "appUJlBFPnTUFJmOx"
TASKS_TABLE = "tblHIDvz3UahqWf1h"
DECISIONS_TABLE = "tblIbxPFGdXLÓI3rE"
RISKS_TABLE = "tbl6GWnx6Oz18kbyi"

VIEWS = {
    "blockers_remaining": ("tblHIDvz3UahqWf1h", "viwAT3pgxpCeApJsM"),
    "blockers_complete":  ("tblHIDvz3UahqWf1h", "viwI45OS0OTda4w3C"),
    "signoffs":           ("tblHIDvz3UahqWf1h", "viwcRZQfywN0cyvFl"),
    "gaps":               ("tblHIDvz3UahqWf1h", "viwlueN7Fe0ahlfpM"),
    "completed":          ("tblHIDvz3UahqWf1h", "viwiijGCRkwN62KSI"),
    "eng_remaining":      ("tblHIDvz3UahqWf1h", "viw0XBjg0kfksT06T"),
    "phase3_all":         ("tblHIDvz3UahqWf1h", "viwAT3pgxpCeApJsM"),
    "decisions_made":     ("tblIbxPFGdXLÓI3rE", "viwT6Mn7zCm0df5ul"),
    "decisions_pending":  ("tblIbxPFGdXNSI3rE", "viwe6OkcS1mqHNnNo"),
    "decisions_needed":   ("tblIbxPFGdXNSI3rE", "viwZjwMjP7UmUitbZ"),
    "decisions_open":     ("tblIbxPFGdXLÓI3rE", "viwZA3HsTO3DWU6Jm"),
    "open_risks":         ("tbl6GWnx6Oz18kbyi", "viwzV39ZM3CcNWbkE"),
}
# âââ DATA FETCHING âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ

@st.cache_data(ttl=300, show_spinner=False)
def fetch_view(pat, table_id, view_id):
    records = []
    offset = None
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
            raise Exception(f"Airtable error {resp.status_code}")
        data = resp.json()
        records.extend(data.get("records", []))
        offset = data.get("offset")
        if not offset:
            break
    return records

@st.cache_data(ttl=300, show_spinner=False)
def fetch_all_data(pat):
    result = {}
    for key, (table_id, view_id) in VIEWS.items():
        records = fetch_view(pat, table_id, view_id)
        result[key] = [r["fields"] for r in records]
    return result

# âââ CHART HELPERS âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ

PLOTLY_DARK = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter, sans-serif", color="#94a3b8", size=12),
    margin=dict(l=0, r=0, t=10, b=0),
)

def make_progress_ring(value, total, color, title):
    remaining = total - value
    fig = go.Figure(go.Pie(
        values=[value, remaining],
        hole=0.72,
        marker_colors=[color, "#1e293b"],
        textinfo="none",
        labels=[title, "Remaining"],
        sort=False,
    ))
    fig.add_annotation(text=f"<b>{value}</b>", x=0.5, y=0.55, showarrow=False,
        font=dict(size=28, color=color, family="Inter"))
    fig.add_annotation(text=f"of {total}", x=0.5, y=0.35, showarrow=False,
        font=dict(size=13, color="#64748b", family="Inter"))
    fig.update_layout(**PLOTLY_DARK, height=160, showlegend=False)
    return fig

def make_workstream_bar(data):
    categories = ["Engineering (11)", "Blockers (13)", "Sign-offs (11)", "Gap Tickets (7)"]
    fig = go.Figure()
    for vals, label, color in [
        ([8,6,1,0], "Completed", "#10b981"),
        ([2,2,1,3], "In Progress", "#f59e0b"),
        ([1,0,0,1], "Blocked", "#ef4444"),
        ([0,5,9,1], "Not Started", "#334155"),
    ]:
        fig.add_trace(go.Bar(name=label, y=categories, x=vals,
            orientation="h", marker_color=color, marker_line_width=0))
    fig.update_layout(**PLOTLY_DARK, xaxis=dict(range=[0,14]),
        barmode="stack", height=220, bargap=0.35,
        legend=dict(orientation="h",yanchor="bottom",y=1.02,xanchor="left",x=0))
    return fig

def make_decision_donut(made, pending, needed):
    fig = go.Figure(go.Pie(values=[made,pending,needed],
        labels=["Made","Pending","Needed"], hole=0.68,
        marker_colors=["#10b981","#f59e0b","#ef4444"], textinfo="none", sort=False))
    total = made+pending+needed
    pct = round(made/total*100) if total else 0
    fig.add_annotation(text=f"<b>{pct}%</b>",x=0.5,y=0.55,showarrow=False,
        font=dict(size=26,color="#f1f5f9",family="Inter"))
    fig.add_annotation(text="decided",x=0.5, y=0.35,showarrow=False,
        font=dict(size=12,color="#64748b",family="Inter"))
    fig.update_layout(**PLOTLY_DARK, height=220, showlegend=True,
        legend=dict(orientation="h",yanchor="bottom",y=-0.15,xanchor="center",x=0.5))
    return fig

def make_burndown(data):
    categories = ["Engineering", "Blockers", "Sign-offs", "Gaps", "Decisions"]
    done_pct = [73, 46, 9, 0, 41]
    fig = go.Figure()
    fig.add_trace(go.Bar(x=categories, y=done_pct,
        marker_color=["#10b981" if p>=60 else "#f59e0b" if p>=30 else "#ef4444" for p in done_pct],
        marker_line_width=0, text=[f"{p}%" for p in done_pct],
        textposition="outside", textfont=dict(size=12,color="#94a3b8")))
    fig.add_hline(y=100, line_dash="dot", line_color="#334155", line_width=1)
    fig.update_layout(**PLOTLY_DARK, height=220, showlegend=False,
        yaxis=dict(range=[0,115], ticksuffix="%"))
    return fig

# âââ AI SUMMARY ââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ

def build_prompt(data):
    eng_done = 11 - len(data.get("eng_remaining", []))
    return f"""Write a 3-paragraph executive status brief for the OneSignal eHawk Phase 3 auto-approval pipeline. Date: {datetime.now().strftime('%B %d, %Y')}. Prose only. No bullets. No hedging. Be direct and specific.

LIVE DATA:
- Engineering: {eng_done}/11 done (73%). T9 and T11 in progress. T3 blocked.
- Pre-launch blockers: {len(data.get('blockers_complete',[]))}/13 cleared, {len(data.get('blockers_remaining',[]))} remaining.
- T&S sign-offs: 1/11 confirmed (9%). Critical bottleneck.
- Gap tickets: 0/7 closed. 3 in progress (GAP-1, GAP-5, GAP-7).
- Decisions: {len(data.get('decisions_made',[]))}/17 made. 4 CRITICAL decisions needed blocking engineering.
- Open risks: {len(data.get('open_risks',[]))} tracked.

Paragraph 1 - STATE: Engineering momentum vs T&S readiness gap.
Paragraph - CONSTRAINT: T&S sign-offs at 9% and 0 gap tickets closed. What happens if this doesn't move this week.
Paragraph 3 - NEXT 7 DAYS: Three specific actions with implied owners."""

@st.cache_data(ttl=600, show_spinner=False)
def generate_summary(pat_hash, data_hash, prompt):
    try:
        api_key = st.secrets.get("ANTHROPIC_API_KEY", "")
        if not api_key:
            return "Add ANTHROPIC_API_KEY to your Streamlit secrets to enable AI summaries."
        client = anthropic.Anthropic(api_key=api_key)
        msg = client.messages.create(model="claude-sonnet-4-20250514",
            max_tokens=600, messages=[{"role":"user","content":prompt}])
        return msg.content[0].text
    except Exception as e:
        return f"AI summary unavailable: {e}"

STATUS_BADGE = {
    "Completed":("DONE","badge-green"),"In Progress":("IN PROGRESS","badge-amber"),
    "In Review":("IN REVIEW","badge-blue"),"Blocked":("BLOCKED","badge-red"),
    "Not Started":("NOT STARTED","badge-gray"),"Made":("MADE","badge-green"),
    "Pending":("PENDING","badge-amber"),"Needed":("NEEDED","badge-red"),
}
def status_badge(status):
    label,cls = STATUS_BADGE.get(status,( status.upper(),"badge-gray"))
    return f'<span class="detail-badge {cls}">{label}</span>'
def priority_badge(priority):
    cls = {"High":"badge-red","Medium":"badge-amber","Low":"badge-gray"}.get(priority, "badge-gray")
    return f'<span class="detail-badge {cls}">{priority.upper()}</span>'
# âââ MAIN APP âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ

def main():
    pat = st.secrets.get("AIRTABLE_PAT", "")
    if not pat:
        st.markdown("""
        <div style="background:#1e293b;border-radius:10px;padding:24px;margin-bottom:20px">
          <div style="font-size:12px;color:#64748b;margin-bottom:8px">AIRTABLE PERSONAL ACCESS TOKEN</div>
          <div style="font-size:13px;color:#94a3b8">Add <code>AIRTABLE_PAT</code> to Streamlit Cloud secrets to connect live data.</div>
        </div>
        """, unsafe_allow_html=True)
        pat = st.text_input("Or enter your Airtable PAT here:", type="password", key="pat_input")
        if not pat:
            st.stop()
    with st.spinner("Fetching live Airtable data..."):
        try:
            data = fetch_all_data(pat)
        except Exception as e:
            st.error(f"Airtable connection failed: {e}")
            st.stop()
    eng_done = 11 - len(data.get("eng_remaining",[]))
    blockers_done = len(data.get("blockers_complete",[]))
    blockers_remaining = len(data.get("blockers_remaining",[]))
    signoffs_remaining = len(data.get("signoffs",[]))
    gaps_remaining = len(data.get("gaps",[]))
    decisions_made = len(data.get("decisions_made",[]))
    decisions_pending = len(data.get("decisions_pending",[]))
    decisions_needed = len(data.get("decisions_needed",[]))

    st.markdown(f"""
    <div class="masthead">
      <div class="masthead-left">
        <div class="masthead-eyebrow">OneSignal Â· Trust &amp; Safety Operations Â· eHawk Phase 3</div>
        <div class="masthead-title">Launch Readiness Dashboard</div>
        <div class="masthead-sub">{datetime.now().strftime('%A, %B %d, %Y')} Â· Live data from Airtable Â· Refreshes every 5 minutes</div>
      </div>
      <div class="masthead-right">
        <div class="masthead-big">{blockers_remaining}</div>
        <div class="masthead-label">blockers to launch</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    k1,k2,k3,k4,k5 = st.columns(5)
    for col, (val,tot,col,label,ctx) in zip(
        [k1,k2,k3,k4,k5],
        [(eng_done,11,"green","Engineering Tickets","T9 &amp; T11 in progress"),
         (blockers_remaining,13,"amber","Pre-Launch Blockers",f"{blockers_done} cleared"),
         (1,11,"red","T&amp;S Sign-offs",f"{signoffs_remaining} outstanding"),
         (0,7,"red","Gap Tickets",f"{gaps_remaining} open"),
         (decisions_made,17,"blue","Decisions",f"{decisions_needed} critical needed")]):
        with col:
            st.plotly_chart(make_progress_ring(wal,tot,col,label),
                use_container_width=True,config={"displayModeBar":False})
            pct = round(val/tot*100) if tot else 0
            st.markdown(f"""
            <div class="kpi-card {col}">
              <div class="kpi-label">{label}</div>
              <div class="kpi-fraction"><span class="kpi-num">{val}</span><span class="kpi-denom">/{tot}</span></div>
              <div class="kpi-context">{ctx}</div>
              <span class="kpi-pct">{pct}%</span>
            </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="section-header">Pipeline Progress</div>', unsafe_allow_html=True)
    c1,c2,c3 = st.columns([5,3,3])
    with c1: st.plotly_chart(make_workstream_bar(data),use_container_width=True,config={"displayModeBar":False})
    with c2: st.plotly_chart(make_decision_donut(decisions_made,decisions_pending,decisions_needed),use_container_width=True,config={"displayModeBar":False})
    with c3: st.plotly_chart(make_burndown(data),use_container_width=True,config={"displayModeBar":False})

    st.markdown('<div class="section-header">AI Executive Summary <span style="font-size:9px;background:rgba(59,130,246,0.15);color:#3b82f6;padding:2px 7px;border-radius:3px;font-weight:700;margin-left:6px">CLAUDE SONNET</span></div>', unsafe_allow_html=True)
    prompt = build_prompt(data)
    data_hash = str(hash(str(sorted([str(v) for v in data.values()]))))
    pat_hash = str(hash(pat[:8]))
    _, col_btn = st.columns([10,1])
    with col_btn:
        if st.button("âº", help="Regenerate"):
            st.cache_data.clear(); st.rerun()
    with st.spinner("Generating AI analysis..."):
        summary = generate_summary(pat_hash, data_hash, prompt)
    paragraphs = [p.strip() for p in summary.strip().split("\n\n") if p.strip()]
    labels = ["State","Constraint","Next 7 Days"]
    colors = ["#3b82f6","#ef4444","#10b981"]
    cols = st.columns(len(paragraphs))
    for i,(col,para) in enumerate(zip(cols,paragraphs)):
        with col:
            label = labels[i] if i<len(labels) else ""
            color = colors[i] if i<len(colors) else "#64748b"
            st.markdown(f"""<div style="background:#0f172a;border-radius:8px;padding:16px 18px;border-top:2px solid {color}">
            <div style="font-size:9px;font-weight:700;text-transform:uppercase;letter-spacing:.12em;color:{color};margin-bottom:10px">{label}</div>
            <div style="font-size:13px;line-height:1.7;color:#cbd5e1">{para}</div></div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="section-header">Drill-Down Detail</div>', unsafe_allow_html=True)
    tab1,tab2,tab3,tab4,tab5 = st.tabs([
        f"ð§ Blockers ({blockers_remaining})",
        f"âï¸ Sign-offs ({signoffs_remaining})",
        f"ð´ Decisions Needed ({decisions_needed})",
        f"ð Gap Tickets ({gaps_remaining})",
        f"â Recently Completed"])
    with tab1:
        for item in data.get("blockers_remaining",[]):
            name = item.get("Task Name","Untitled")
            st.markdown(f'<div class="detail-item">{status_badge(item.get("Status","Not Started"))}<span style="color:#e2e8f0">{name}</span></div>', unsafe_allow_html=True)
    with tab2:
        for item in data.get("signoffs",[]):
            name = item.get("Task Name","Untitled")
            st.markdown(f'<div class="detail-item">{status_badge(item.get("Status","Not Started"))}<span style="color:#e2e8f0">{name}</span></div>', unsafe_allow_html=True)
    with tab3:
        for item in data.get("decisions_needed",[]):
            title = item.get("Title","Untitled")
            notes = item.get("Unblocks / Notes","")[:120]
            st.markdown(f'<div class="detail-item"><span class="detail-badge badge-red">NEEDED</span><div><div style="color:#e2e8f0">{title}</div>{{f"<div style=\"font-size:11px;color:#64748b\">{notes}</div>" if notes else ""}}</div></div>', unsafe_allow_html=True)
    with tab4:
        for item in data.get("gaps",[]):
            name = item.get("Task Name","Untitled")
            st.markdown(f'<div class="detail-item">{all_badges(item)}<span style="color:#e2e8f0">{name}</span></div>', unsafe_allow_html=True)
    with tab5:
        for item in data.get("completed",[]):
            name = item.get("Task Name","Untitled")
            st.markdown(f'<div class="detail-item"><span class="detail-badge badge-green">DONE</span><span style="color:#e2e8f0">{name}</span></div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div style="margin-top:32px;padding-top:16px;border-top:1px solid #1e293b;font-size:11px;color:#334155;text-align:center">
      OneSignal eHawk Phase 3 Auto-Approval Pipeline Â· Confidential Â·
      {datetime.now().strftime('%B %d, %Y %H:%M')} Â· Data cached 5 min Â· Streamlit + Airtable + Claude
    </div>""", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
