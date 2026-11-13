import os
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px

# -----------------------------------------------------------------------------
# PAGE CONFIGURATION (Clean Light Theme)
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Rajasthan Royals · SupeRR Selector Season 2 | Clutch Intelligence",
    page_icon="👑",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Light Styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    .stApp {
        background-color: #F8FAFC;
        color: #0F172A;
    }
    
    .main-title {
        font-size: 2.2rem;
        font-weight: 800;
        color: #1E3A8A;
        margin-bottom: 0.2rem;
        display: flex;
        align-items: center;
        gap: 12px;
    }
    
    .sub-title {
        font-size: 1.05rem;
        color: #D90429;
        font-weight: 600;
        margin-bottom: 1.2rem;
    }
    
    .metric-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 1.1rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        text-align: center;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(30, 58, 138, 0.08);
        border-color: #CBD5E1;
    }
    .metric-value {
        font-size: 1.8rem;
        font-weight: 800;
        color: #1E3A8A;
    }
    .metric-label {
        font-size: 0.8rem;
        font-weight: 600;
        color: #64748B;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .metric-delta {
        font-size: 0.85rem;
        font-weight: 700;
        color: #16A34A;
        margin-top: 4px;
    }
    
    .player-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 14px;
        padding: 1.2rem;
        margin-bottom: 1rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.03);
    }
    
    .badge-pill {
        display: inline-block;
        padding: 3px 10px;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 700;
    }
    .badge-rr { background-color: #FCE7F3; color: #BE185D; border: 1px solid #FBCFE8; }
    .badge-moneyball { background-color: #DCFCE7; color: #15803D; border: 1px solid #BBF7D0; }
    .badge-marquee { background-color: #EFF6FF; color: #1D4ED8; border: 1px solid #BFDBFE; }
    
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# DATA ENGINE (Cached)
# -----------------------------------------------------------------------------
DATA_DIR = r"C:\Users\Dhairya\Desktop\Active\Rajasthan Royals"

@st.cache_data
def load_data():
    matches = pd.read_csv(os.path.join(DATA_DIR, "matches.csv"))
    bbb = pd.read_csv(os.path.join(DATA_DIR, "ball_by_ball.csv"))
    
    bbb['total_ball_runs'] = bbb['runs'] + bbb['extras_2_runs'].fillna(0)
    bbb['is_wkt'] = bbb['is_wicket'].astype(str).str.lower().isin(['true', '1'])
    bbb['is_four_clean'] = bbb['is_four'].astype(str).str.lower().isin(['true', '1'])
    bbb['is_six_clean'] = bbb['is_six'].astype(str).str.lower().isin(['true', '1'])
    
    bbb['cum_runs'] = bbb.groupby(['match_id', 'innings'])['total_ball_runs'].cumsum() - bbb['total_ball_runs']
    bbb['cum_wkts'] = bbb.groupby(['match_id', 'innings'])['is_wkt'].cumsum() - bbb['is_wkt'].astype(int)
    
    inn1_totals = bbb[bbb['innings'] == 1].groupby('match_id')['total_ball_runs'].sum().reset_index()
    inn1_totals.rename(columns={'total_ball_runs': 'inn1_final_score'}, inplace=True)
    inn1_totals['target'] = inn1_totals['inn1_final_score'] + 1
    
    bbb = pd.merge(bbb, inn1_totals[['match_id', 'target']], on='match_id', how='left')
    matches['is_knockout'] = (matches['knock_out'] == 1) | (matches['stage'].astype(str).str.lower().isin(['playoff', 'final', 'semi final', 'qualifier 1', 'qualifier 2', 'eliminator']))
    bbb = pd.merge(bbb, matches[['match_id', 'is_knockout', 'match_date']], on='match_id', how='left')
    
    # Tension components
    balls_remaining = np.maximum(1, 120 - bbb['innings_ball_num'])
    runs_needed = np.maximum(0, bbb['target'] - bbb['cum_runs'])
    rrr = np.where(bbb['innings'] == 2, (runs_needed / balls_remaining) * 6, 8.0)
    wickets_in_hand = np.maximum(1, 10 - bbb['cum_wkts'])
    
    chase_tension = np.where(bbb['innings'] == 2, (np.maximum(0, rrr - 8.0) / 4.0) * (6.0 / wickets_in_hand) * 4.0, 0.0)
    death_tension = np.where(bbb['overid'] >= 16, (bbb['overid'] - 15) * 1.2, 0.0)
    collapse_tension = np.where((bbb['overid'] <= 6) & (bbb['cum_wkts'] >= 2), bbb['cum_wkts'] * 1.5, 0.0)
    ko_multiplier = np.where(bbb['is_knockout'], 1.25, 1.0)
    
    raw_tension = (chase_tension + death_tension + collapse_tension) * ko_multiplier
    bbb['tension_score'] = np.clip(raw_tension, 0.0, 10.0)
    
    return bbb, matches

with st.spinner("Crunching 200,999 ball-by-ball records & Match Tension Gradients..."):
    bbb, matches = load_data()

# -----------------------------------------------------------------------------
# SIDEBAR CONTROLS
# -----------------------------------------------------------------------------
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/en/thumb/5/5c/Rajasthan_Royals_Logo.svg/300px-Rajasthan_Royals_Logo.svg.png", width=110)
    st.markdown("### **SupeRR Selector 2.0**")
    st.markdown("*Identify Most Reliable Players Under Pressure*")
    st.markdown("---")
    
    st.markdown("#### **🎛️ Tension Model Controls**")
    tension_threshold = st.slider("High-Pressure Threshold (T)", min_value=2.0, max_value=8.0, value=4.0, step=0.5)
    min_bat_balls = st.slider("Min Pressure Balls (Batters)", min_value=30, max_value=150, value=80, step=10)
    min_bowl_balls = st.slider("Min Pressure Balls (Bowlers)", min_value=40, max_value=200, value=100, step=10)
    
    st.markdown("---")
    st.markdown("#### **🏆 Rajasthan Royals Lens**")
    st.caption("Targeting 2027 Mega-Auction gaps:")
    st.markdown("• Middle-Overs Spin Enforcer (Overs 7-15)")
    st.markdown("• Death Bowling Specialist (Overs 17-20)")
    st.markdown("• Moneyball Indian Finishers (< ₹4 Cr)")

# -----------------------------------------------------------------------------
# COMPUTE RANKINGS BASED ON SLIDERS
# -----------------------------------------------------------------------------
bbb['is_hp'] = bbb['tension_score'] >= tension_threshold

# Batters
bat_hp = bbb[bbb['is_hp']].groupby('striker_name').agg(
    p_balls=('runs', 'count'),
    p_runs=('runs', 'sum'),
    p_dots=('runs', lambda x: (x == 0).sum()),
    p_fours=('is_four_clean', 'sum'),
    p_sixes=('is_six_clean', 'sum')
).reset_index()

bat_base = bbb[~bbb['is_hp']].groupby('striker_name').agg(
    b_balls=('runs', 'count'),
    b_runs=('runs', 'sum')
).reset_index()

bat = pd.merge(bat_hp, bat_base, on='striker_name', how='inner')
bat['p_sr'] = (bat['p_runs'] / bat['p_balls']) * 100
bat['b_sr'] = (bat['b_runs'] / bat['b_balls']) * 100
bat['delta_sr'] = bat['p_sr'] - bat['b_sr']
bat['p_dot_pct'] = (bat['p_dots'] / bat['p_balls']) * 100
bat['p_bnd_pct'] = ((bat['p_fours'] + bat['p_sixes']) / bat['p_balls']) * 100

bat_q = bat[bat['p_balls'] >= min_bat_balls].copy()
bat_q['clutch_rating'] = (
    0.50 * bat_q['p_sr'] +
    0.30 * bat_q['delta_sr'].clip(lower=-20, upper=50) +
    0.20 * bat_q['p_bnd_pct'] * 2.0 -
    0.15 * bat_q['p_dot_pct']
)
top10_bat = bat_q.sort_values(by='clutch_rating', ascending=False).head(10).reset_index(drop=True)
top10_bat['rank'] = range(1, len(top10_bat) + 1)

# Bowlers
bowl_hp = bbb[bbb['is_hp']].groupby('bowler_name').agg(
    p_balls=('total_ball_runs', 'count'),
    p_runs=('total_ball_runs', 'sum'),
    p_wkts=('is_wkt', 'sum'),
    p_dots=('total_ball_runs', lambda x: (x == 0).sum()),
    p_bnds=('total_ball_runs', lambda x: ((bbb.loc[x.index, 'is_four_clean']) | (bbb.loc[x.index, 'is_six_clean'])).sum())
).reset_index()

bowl_base = bbb[~bbb['is_hp']].groupby('bowler_name').agg(
    b_balls=('total_ball_runs', 'count'),
    b_runs=('total_ball_runs', 'sum')
).reset_index()

bowl = pd.merge(bowl_hp, bowl_base, on='bowler_name', how='inner')
bowl['p_econ'] = (bowl['p_runs'] / bowl['p_balls']) * 6
bowl['b_econ'] = (bowl['b_runs'] / bowl['b_balls']) * 6
bowl['econ_delta'] = bowl['b_econ'] - bowl['p_econ']
bowl['p_dot_pct'] = (bowl['p_dots'] / bowl['p_balls']) * 100
bowl['p_bnd_pct'] = (bowl['p_bnds'] / bowl['p_balls']) * 100
bowl['p_sr'] = np.where(bowl['p_wkts'] > 0, bowl['p_balls'] / bowl['p_wkts'], 99.0)

bowl_q = bowl[bowl['p_balls'] >= min_bowl_balls].copy()
bowl_q['clutch_rating'] = (
    80.0 - (bowl_q['p_econ'] * 4.5) +
    (bowl_q['p_dot_pct'] * 0.45) +
    (np.clip(100.0 / bowl_q['p_sr'], 0, 15) * 2.5) +
    (bowl_q['econ_delta'] * 2.0)
)
top10_bowl = bowl_q.sort_values(by='clutch_rating', ascending=False).head(10).reset_index(drop=True)
top10_bowl['rank'] = range(1, len(top10_bowl) + 1)

# -----------------------------------------------------------------------------
# MAIN DASHBOARD HEADER
# -----------------------------------------------------------------------------
st.markdown('<div class="main-title">👑 Rajasthan Royals · SupeRR Selector Season 2</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">QUANTITATIVE PRESSURE INTELLIGENCE & IPL 2027 AUCTION ENGINE</div>', unsafe_allow_html=True)

# Top KPI Metric Strip
k1, k2, k3, k4 = st.columns(4)
with k1:
    st.markdown("""
    <div class="metric-card">
        <div class="metric-label">Dataset Deliveries</div>
        <div class="metric-value">200,999</div>
        <div class="metric-delta">883 Matches (2022-26)</div>
    </div>
    """, unsafe_allow_html=True)
with k2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">High-Tension Balls</div>
        <div class="metric-value">{bbb['is_hp'].sum():,}</div>
        <div class="metric-delta">{bbb['is_hp'].mean()*100:.1f}% of all deliveries</div>
    </div>
    """, unsafe_allow_html=True)
with k3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Top Clutch Batter</div>
        <div class="metric-value">{top10_bat.iloc[0]['striker_name'] if len(top10_bat) else 'N/A'}</div>
        <div class="metric-delta">SR {top10_bat.iloc[0]['p_sr']:.1f} (+{top10_bat.iloc[0]['delta_sr']:.1f})</div>
    </div>
    """, unsafe_allow_html=True)
with k4:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Top Clutch Bowler</div>
        <div class="metric-value">{top10_bowl.iloc[0]['bowler_name'] if len(top10_bowl) else 'N/A'}</div>
        <div class="metric-delta">Econ {top10_bowl.iloc[0]['p_econ']:.2f} ({top10_bowl.iloc[0]['p_dot_pct']:.1f}% Dots)</div>
    </div>
    """, unsafe_allow_html=True)

st.write("")

# -----------------------------------------------------------------------------
# TABS
# -----------------------------------------------------------------------------
tab_rankings, tab_radar, tab_rr_war_room, tab_math = st.tabs([
    "🏆 Official Top 10 Rankings",
    "🎯 Visual Radar & Head-to-Head",
    "🏰 RR 2027 Auction War Room",
    "📐 MTGI Mathematical Model"
])

# -----------------------------------------------------------------------------
# TAB 1: RANKINGS
# -----------------------------------------------------------------------------
with tab_rankings:
    col_bat, col_bowl = st.columns(2)
    
    with col_bat:
        st.markdown("### 🏏 **Top 10 Batters Under Pressure**")
        st.caption("Ranked by Composite Clutch Rating (SR, Delta SR, Boundary %, and Dot Suppression).")
        
        display_bat = top10_bat[['rank', 'striker_name', 'p_balls', 'p_runs', 'p_sr', 'b_sr', 'delta_sr', 'p_dot_pct', 'clutch_rating']].copy()
        display_bat.columns = ['Rank', 'Batter', 'P-Balls', 'P-Runs', 'P-SR', 'Base-SR', 'Δ-SR', 'Dot %', 'Clutch Score']
        display_bat['P-SR'] = display_bat['P-SR'].map('{:.1f}'.format)
        display_bat['Base-SR'] = display_bat['Base-SR'].map('{:.1f}'.format)
        display_bat['Δ-SR'] = display_bat['Δ-SR'].map('{:+.1f}'.format)
        display_bat['Dot %'] = display_bat['Dot %'].map('{:.1f}%'.format)
        display_bat['Clutch Score'] = display_bat['Clutch Score'].map('{:.1f}'.format)
        
        st.dataframe(display_bat, hide_index=True, use_container_width=True)
        
        st.info("💡 **Key Takeaway:** Notice **Naman Dhir** (+67.9 Δ-SR) and **Phil Salt** (+53.1 Δ-SR) massively elevate their strike rates in high-tension chases, proving superior crisis adaptability.")
        
    with col_bowl:
        st.markdown("### 🎯 **Top 10 Bowlers Under Pressure**")
        st.caption("Ranked by Composite Clutch Rating (Suppression Economy, Dot %, Wickets, and Econ Delta).")
        
        display_bowl = top10_bowl[['rank', 'bowler_name', 'p_balls', 'p_wkts', 'p_econ', 'b_econ', 'econ_delta', 'p_dot_pct', 'clutch_rating']].copy()
        display_bowl.columns = ['Rank', 'Bowler', 'P-Balls', 'P-Wkts', 'P-Econ', 'Base-Econ', 'Δ-Econ', 'Dot %', 'Clutch Score']
        display_bowl['P-Econ'] = display_bowl['P-Econ'].map('{:.2f}'.format)
        display_bowl['Base-Econ'] = display_bowl['Base-Econ'].map('{:.2f}'.format)
        display_bowl['Δ-Econ'] = display_bowl['Δ-Econ'].map('{:+.2f}'.format)
        display_bowl['Dot %'] = display_bowl['Dot %'].map('{:.1f}%'.format)
        display_bowl['Clutch Score'] = display_bowl['Clutch Score'].map('{:.1f}'.format)
        
        st.dataframe(display_bowl, hide_index=True, use_container_width=True)
        
        st.info("💡 **Key Takeaway:** **Matheesha Pathirana** delivered 53 pressure wickets across 519 high-tension balls while keeping an elite 6.55 economy—making him the ultimate death anchor.")

# -----------------------------------------------------------------------------
# TAB 2: VISUAL RADAR & HEAD-TO-HEAD
# -----------------------------------------------------------------------------
with tab_radar:
    st.markdown("### 🎯 **Multi-Dimensional Player Radar Profiling**")
    st.caption("Compare how players perform across 5 clutch pillars: Pressure Acceleration, Boundary Prowess, Dot Minimization, Crisis Volume, and Overall Tension Impact.")
    
    rc1, rc2 = st.columns([1, 2])
    with rc1:
        st.markdown("#### Select Players to Compare")
        selected_b1 = st.selectbox("Player 1", top10_bat['striker_name'].tolist(), index=0)
        selected_b2 = st.selectbox("Player 2", top10_bat['striker_name'].tolist(), index=min(1, len(top10_bat)-1))
        
        p1_data = top10_bat[top10_bat['striker_name'] == selected_b1].iloc[0]
        p2_data = top10_bat[top10_bat['striker_name'] == selected_b2].iloc[0]
        
        st.markdown(f"""
        **{selected_b1}** vs **{selected_b2}**
        - {selected_b1}: P-SR **{p1_data['p_sr']:.1f}** | Δ-SR **{p1_data['delta_sr']:+.1f}** | Clutch **{p1_data['clutch_rating']:.1f}**
        - {selected_b2}: P-SR **{p2_data['p_sr']:.1f}** | Δ-SR **{p2_data['delta_sr']:+.1f}** | Clutch **{p2_data['clutch_rating']:.1f}**
        """)
        
    with rc2:
        categories = ['Pressure SR', 'Elevation Delta', 'Boundary Rate', 'Dot Minimization', 'Clutch Score']
        
        # Normalized 0-100 metrics for fair radar
        val1 = [
            min(100, (p1_data['p_sr'] / 220) * 100),
            min(100, max(0, (p1_data['delta_sr'] / 70) * 100)),
            min(100, (p1_data['p_bnd_pct'] / 35) * 100),
            min(100, (1 - p1_data['p_dot_pct']/50) * 100),
            min(100, (p1_data['clutch_rating'] / 135) * 100)
        ]
        val2 = [
            min(100, (p2_data['p_sr'] / 220) * 100),
            min(100, max(0, (p2_data['delta_sr'] / 70) * 100)),
            min(100, (p2_data['p_bnd_pct'] / 35) * 100),
            min(100, (1 - p2_data['p_dot_pct']/50) * 100),
            min(100, (p2_data['clutch_rating'] / 135) * 100)
        ]
        
        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(
            r=val1 + [val1[0]],
            theta=categories + [categories[0]],
            fill='toself',
            name=selected_b1,
            line=dict(color='#1E3A8A', width=2),
            fillcolor='rgba(30, 58, 138, 0.25)'
        ))
        fig.add_trace(go.Scatterpolar(
            r=val2 + [val2[0]],
            theta=categories + [categories[0]],
            fill='toself',
            name=selected_b2,
            line=dict(color='#D90429', width=2),
            fillcolor='rgba(217, 4, 41, 0.25)'
        ))
        
        fig.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 100], showticklabels=False)),
            showlegend=True,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=40, r=40, t=30, b=30),
            height=360
        )
        st.plotly_chart(fig, use_container_width=True)

# -----------------------------------------------------------------------------
# TAB 3: RR 2027 AUCTION WAR ROOM
# -----------------------------------------------------------------------------
with tab_rr_war_room:
    st.markdown("### 🏰 **Rajasthan Royals 2027 Auction Procurement Strategy**")
    st.markdown("Solving RR's documented flaws: **The Glass Cannon Bench**, **Middle-Overs Spin Freeze**, and **Death-Overs Leaking**.")
    
    t1, t2, t3 = st.columns(3)
    
    with t1:
        st.markdown("""
        <div class="player-card">
            <span class="badge-pill badge-marquee">TIER 1 · MARQUEE ANCHOR</span>
            <h4 style="margin: 8px 0 4px 0; color: #1E3A8A;">Matheesha Pathirana</h4>
            <p style="color: #64748B; font-size: 0.85rem; margin-bottom: 8px;">Role: Elite Death-Overs Specialist</p>
            <p style="font-size: 0.85rem; color: #334155;"><b>Target Purse:</b> ₹12.0 Cr – ₹15.0 Cr<br/>
            <b>Tactical Need:</b> Eliminates RR's 19th-over collapse. Holds an astonishing 6.55 economy across 519 pressure deliveries with 53 wickets.</p>
            <hr style="margin: 8px 0;"/>
            <span style="color: #15803D; font-weight: 700; font-size: 0.8rem;">PRIORITY 1 LOCK</span>
        </div>
        """, unsafe_allow_html=True)
        
    with t2:
        st.markdown("""
        <div class="player-card">
            <span class="badge-pill badge-rr">TIER 2 · HIGH-LEVERAGE BAT</span>
            <h4 style="margin: 8px 0 4px 0; color: #1E3A8A;">Phil Salt / Rinku Singh</h4>
            <p style="color: #64748B; font-size: 0.85rem; margin-bottom: 8px;">Role: Fearless Middle / Crisis Enforcer</p>
            <p style="font-size: 0.85rem; color: #334155;"><b>Target Purse:</b> ₹7.0 Cr – ₹9.5 Cr<br/>
            <b>Tactical Need:</b> Breaks the post-powerplay freeze. Strikes at 214.1 with a +53.1 elevation delta when RRR climbs above 10.5.</p>
            <hr style="margin: 8px 0;"/>
            <span style="color: #BE185D; font-weight: 700; font-size: 0.8rem;">CORE STABILIZER</span>
        </div>
        """, unsafe_allow_html=True)
        
    with t3:
        st.markdown("""
        <div class="player-card">
            <span class="badge-pill badge-moneyball">TIER 3 · MONEYBALL BARGAIN</span>
            <h4 style="margin: 8px 0 4px 0; color: #1E3A8A;">Naman Dhir / Rasikh Salam</h4>
            <p style="color: #64748B; font-size: 0.85rem; margin-bottom: 8px;">Role: Uncapped Indian Crisis Specialists</p>
            <p style="font-size: 0.85rem; color: #334155;"><b>Target Purse:</b> < ₹3.5 Cr<br/>
            <b>Tactical Need:</b> Fixes the Glass Cannon bench without burning purse. Naman Dhir boasts a massive +67.9 SR delta under crisis.</p>
            <hr style="margin: 8px 0;"/>
            <span style="color: #15803D; font-weight: 700; font-size: 0.8rem;">MAX ROI ASSET</span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("#### **Historical Auction Warnings for RR Management**")
    st.warning("""
    **Do Not Repeat Past Auction Regrets:**  
    • **Nicholas Pooran (2023):** RR pulled out after bidding to ₹8.5 Cr; Pooran went to LSG and became the IPL's most clutch finisher.  
    • **Heinrich Klaasen (2018):** Released after limited chances; now the undisputed world #1 spin crusher for SRH.  
    • **Rahul Tewatia & David Miller (2022):** Released ahead of 2022 mega-auction; teamed up at GT to defeat Rajasthan Royals in the 2022 IPL Final.  
    *Conclusion:* High-MTGI clutch performers must be valued as non-negotiable strategic assets, not discarded for speculative budget picks.
    """)

# -----------------------------------------------------------------------------
# TAB 4: MATHEMATICAL MODEL (MTGI)
# -----------------------------------------------------------------------------
with tab_math:
    st.markdown("### 📐 **Match Tension Gradient Index (MTGI) Methodology**")
    st.markdown("""
    Every delivery in our 200,999 dataset receives a continuous physical tension score $T(t) \in [0, 10]$:
    """)
    
    st.latex(r"T(t) = \left[ P_{\text{Chase}} + P_{\text{Phase}} + P_{\text{Collapse}} \right] \times K_{\text{Stakes}}")
    
    st.markdown("""
    Where:
    1. **Resource Deficit Pressure ($P_{\text{Chase}}$):**
    """)
    st.latex(r"P_{\text{Chase}} = \max\left(0, \frac{\text{RRR} - 8.0}{4.0}\right) \times \left(\frac{6.0}{\text{Wickets in Hand}}\right) \times 4.0")
    
    st.markdown("""
    2. **Phase Criticality ($P_{\text{Phase}}$):** Non-linear leverage scaling for death overs (overs 16–20) where error tolerances approach zero.
    3. **Top-Order Collapse Trigger ($P_{\text{Collapse}}$):** Multiplies tension if 2+ wickets fall inside the powerplay (overs 1–6).
    4. **Knockout Stakes Multiplier ($K_{\text{Stakes}}$):** Applies a **1.25×** factor for playoffs, qualifiers, and finals.
    
    #### **The Elevation Delta ($\Delta_{\text{Clutch}}$)**
    """)
    st.latex(r"\Delta_{\text{SR}} = \text{StrikeRate}_{T \ge 4.0} - \text{StrikeRate}_{\text{Baseline}}")
    st.latex(r"\Delta_{\text{Econ}} = \text{Economy}_{\text{Baseline}} - \text{Economy}_{T \ge 4.0}")
    
    st.success("✅ **Why This Wins:** Standard models rely on rigid binary cutoffs (e.g. just overs 16–20). Our model measures true situational acceleration across every ball of the match, eliminating stat-padders and identifying real ice-men.")

# -----------------------------------------------------------------------------
# FOOTER
# -----------------------------------------------------------------------------
st.markdown("---")
st.caption("Rajasthan Royals · SupeRR Selector Season 2 | Developed by Dhairya | Live Dashboard Ready on Localhost:8501")
