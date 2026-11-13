import os
import json
import pandas as pd
import numpy as np

DATA_DIR = r"C:\Users\Dhairya\Desktop\Active\Rajasthan Royals"
OUT_JSON = os.path.join(DATA_DIR, "frontend", "src", "data", "clutch_index.json")

print("1. Ingesting datasets...")
matches = pd.read_csv(os.path.join(DATA_DIR, "matches.csv"))
bbb = pd.read_csv(os.path.join(DATA_DIR, "ball_by_ball.csv"))
competitions = pd.read_csv(os.path.join(DATA_DIR, "competitions.csv"))
p11 = pd.read_csv(os.path.join(DATA_DIR, "playing_eleven.csv"))
mapping = pd.read_csv(os.path.join(DATA_DIR, "competition_team_player_mapping.csv"))
teams = pd.read_csv(os.path.join(DATA_DIR, "teams.csv"))

# Identify Pakistani players from mapping.csv to respect IPL regulations
pak_teams = mapping[mapping['team_name'].str.contains('Pakistan', case=False, na=False)]
pak_players = set(pak_teams['player_name'].dropna().unique())
print(f"Total Pakistani players excluded from IPL shortlist: {len(pak_players)}")

# 2. Enrich ball by ball data
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

matches['is_knockout'] = (matches['knock_out'] == 1) | matches['stage'].astype(str).str.lower().isin(['final', 'semi-final', 'semi final', 'qualifier', 'eliminator'])
bbb = pd.merge(bbb, matches[['match_id', 'is_knockout', 'match_date', 'comp_id']], on='match_id', how='left')
bbb = pd.merge(bbb, competitions[['comp_id', 'match_format', 'comp_name']], on='comp_id', how='left')

# 3. Calculate MTGI (Match Tension Gradient Index)
balls_remaining = np.maximum(1, 120 - bbb['innings_ball_num'])
runs_needed = np.maximum(0, bbb['target'] - bbb['cum_runs'])
rrr = np.where(bbb['innings'] == 2, (runs_needed / balls_remaining) * 6, 8.0)
wickets_in_hand = np.maximum(1, 10 - bbb['cum_wkts'])

chase_tension = np.where(
    bbb['innings'] == 2,
    (np.maximum(0, rrr - 8.0) / 4.0) * (6.0 / wickets_in_hand) * 4.0,
    np.where(bbb['cum_wkts'] >= 3, 2.5, 0.5)
)

death_pressure = np.where(
    bbb['overid'] >= 16,
    (bbb['overid'] - 15) * 1.5,
    0.0
)

collapse_pressure = np.where(
    (bbb['overid'] <= 6) & (bbb['cum_wkts'] >= 2),
    3.0 * (bbb['cum_wkts'] - 1),
    0.0
)

knockout_weight = np.where(bbb['is_knockout'], 1.25, 1.0)
comp_weight = np.where(bbb['comp_name'].str.contains('IPL|Indian Premier League', case=False, na=False), 1.2, 1.0)

bbb['mtgi'] = (chase_tension + death_pressure + collapse_pressure + 1.0) * knockout_weight * comp_weight
bbb['is_high_pressure'] = bbb['mtgi'] >= 4.0

# Phase definition
bbb['phase'] = np.where(bbb['overid'] <= 6, 'powerplay', np.where(bbb['overid'] <= 15, 'middle', 'death'))

print("4. Calculating phase breakdowns...")
# Batting Phase
bat_phase = bbb.groupby(['striker_name', 'phase']).agg(
    balls=('match_id', 'count'),
    runs=('runs', 'sum'),
    dots=('runs', lambda s: (s == 0).sum())
).reset_index()

b_bnd = bbb[bbb['is_four_clean'] | bbb['is_six_clean']].groupby(['striker_name', 'phase'])['match_id'].count().reset_index().rename(columns={'match_id': 'bdry'})
bat_phase = pd.merge(bat_phase, b_bnd, on=['striker_name', 'phase'], how='left').fillna({'bdry': 0})
bat_phase['sr'] = np.where(bat_phase['balls'] > 0, (bat_phase['runs'] / bat_phase['balls'] * 100).round(1), 0.0)
bat_phase['dot_pct'] = np.where(bat_phase['balls'] > 0, (bat_phase['dots'] / bat_phase['balls'] * 100).round(1), 0.0)
bat_phase['bdry_pct'] = np.where(bat_phase['balls'] > 0, (bat_phase['bdry'] / bat_phase['balls'] * 100).round(1), 0.0)

bat_phase_dict = {}
for _, row in bat_phase.iterrows():
    p = row['striker_name']
    if p not in bat_phase_dict:
        bat_phase_dict[p] = {}
    bat_phase_dict[p][row['phase']] = {
        "balls": int(row['balls']),
        "runs": int(row['runs']),
        "sr": float(row['sr']),
        "dotPct": float(row['dot_pct']),
        "bdryPct": float(row['bdry_pct'])
    }

# Bowling Phase
bowl_phase = bbb.groupby(['bowler_name', 'phase']).agg(
    balls=('match_id', 'count'),
    runs=('total_ball_runs', 'sum'),
    wkts=('is_wkt', 'sum'),
    dots=('total_ball_runs', lambda s: (s == 0).sum())
).reset_index()

bowl_phase['econ'] = np.where(bowl_phase['balls'] > 0, (bowl_phase['runs'] / (bowl_phase['balls'] / 6)).round(2), 0.0)
bowl_phase['dot_pct'] = np.where(bowl_phase['balls'] > 0, (bowl_phase['dots'] / bowl_phase['balls'] * 100).round(1), 0.0)

bowl_phase_dict = {}
for _, row in bowl_phase.iterrows():
    p = row['bowler_name']
    if p not in bowl_phase_dict:
        bowl_phase_dict[p] = {}
    bowl_phase_dict[p][row['phase']] = {
        "balls": int(row['balls']),
        "runs": int(row['runs']),
        "wkts": int(row['wkts']),
        "econ": float(row['econ']),
        "dotPct": float(row['dot_pct'])
    }

# Calculate Cold Start SR (Balls 1 to 5 faced in an innings)
print("5. Calculating Cold-Start Entry SR...")
bbb['cum_balls_faced'] = bbb.groupby(['match_id', 'innings', 'striker_name']).cumcount() + 1
cs_df = bbb[bbb['cum_balls_faced'] <= 5].groupby('striker_name').agg(
    cs_balls=('match_id', 'count'),
    cs_runs=('runs', 'sum')
).reset_index()
cs_df['cold_start_sr'] = np.where(cs_df['cs_balls'] >= 10, (cs_df['cs_runs'] / cs_df['cs_balls'] * 100).round(1), 125.0)

# Batting Overall & Pressure
p_bat = bbb[bbb['is_high_pressure']].groupby('striker_name').agg(
    p_balls=('match_id', 'count'),
    p_runs=('runs', 'sum'),
    p_dots=('runs', lambda s: (s == 0).sum()),
    p_bdry=('is_four_clean', lambda s: (s | bbb.loc[s.index, 'is_six_clean']).sum())
).reset_index()

n_bat = bbb[~bbb['is_high_pressure']].groupby('striker_name').agg(
    n_balls=('match_id', 'count'),
    n_runs=('runs', 'sum')
).reset_index()

tourn_n_runs = n_bat['n_runs'].sum()
tourn_n_balls = n_bat['n_balls'].sum()
tourn_base_sr = (tourn_n_runs / tourn_n_balls) * 100 # Tournament non-pressure baseline ~131.8

bat = pd.merge(p_bat, n_bat, on='striker_name', how='inner')
bat['p_sr'] = (bat['p_runs'] / bat['p_balls']) * 100

# Bayesian baseline smoothing for batters with small non-pressure sample (< 30 balls)
# Solves the Ashutosh Sharma 0.0 Base SR anomaly with sound empirical Bayesian shrinkage
prior_weight = 30.0
bat['n_sr_smoothed'] = ((bat['n_runs'] + (tourn_base_sr * prior_weight / 100.0)) / (bat['n_balls'] + prior_weight)) * 100.0
bat['n_sr_raw'] = (bat['n_runs'] / np.maximum(1, bat['n_balls'])) * 100.0
bat['n_sr'] = np.where(bat['n_balls'] < 30, bat['n_sr_smoothed'], bat['n_sr_raw'])
bat['sr_delta'] = bat['p_sr'] - bat['n_sr']
bat['p_dot_pct'] = (bat['p_dots'] / bat['p_balls']) * 100
bat['p_bdry_pct'] = (bat['p_bdry'] / bat['p_balls']) * 100

# Merge cold start SR
bat = pd.merge(bat, cs_df[['striker_name', 'cold_start_sr', 'cs_balls']], on='striker_name', how='left').fillna({'cold_start_sr': 125.0, 'cs_balls': 0})

# Attach Death Phase metrics to each batter
bat['death_balls'] = bat['striker_name'].apply(lambda x: bat_phase_dict.get(x, {}).get('death', {}).get('balls', 0))
bat['death_runs'] = bat['striker_name'].apply(lambda x: bat_phase_dict.get(x, {}).get('death', {}).get('runs', 0))
bat['death_sr'] = bat['striker_name'].apply(lambda x: bat_phase_dict.get(x, {}).get('death', {}).get('sr', 0.0))
bat['death_bdry_pct'] = bat['striker_name'].apply(lambda x: bat_phase_dict.get(x, {}).get('death', {}).get('bdryPct', 0.0))
bat['death_dot_pct'] = bat['striker_name'].apply(lambda x: bat_phase_dict.get(x, {}).get('death', {}).get('dotPct', 0.0))

# Consistency calculation
m_bat = bbb[bbb['is_high_pressure']].groupby(['striker_name', 'match_id']).agg(
    m_balls=('match_id', 'count'),
    m_runs=('runs', 'sum')
).reset_index()
m_bat = m_bat[m_bat['m_balls'] >= 6]
m_bat['m_sr'] = (m_bat['m_runs'] / m_bat['m_balls']) * 100
m_bat['is_success'] = m_bat['m_sr'] >= 135

c_bat = m_bat.groupby('striker_name').agg(
    total_m=('match_id', 'count'),
    succ_m=('is_success', 'sum')
).reset_index()
c_bat['consistency_pct'] = (c_bat['succ_m'] / c_bat['total_m']) * 100
bat = pd.merge(bat, c_bat[['striker_name', 'consistency_pct', 'total_m']], on='striker_name', how='left').fillna({'consistency_pct': 50.0, 'total_m': 1})

bat['raw_clutch'] = (
    0.50 * bat['p_sr'] +
    0.30 * bat['sr_delta'].clip(lower=-20, upper=50) +
    0.20 * bat['p_bdry_pct'] * 2.0 -
    0.15 * bat['p_dot_pct']
)
bat['reliability'] = 0.70 + 0.30 * (bat['consistency_pct'] / 100.0)
bat['clutch_score'] = (bat['raw_clutch'] * bat['reliability']).round(1)

# Tactical Role Classification
def assign_batter_archetype(row):
    d_balls = row['death_balls']
    p_balls = row['p_balls']
    sr = row['p_sr']
    cs_sr = row['cold_start_sr']
    if d_balls >= 40 and (d_balls / max(1, p_balls) >= 0.30 or row['death_sr'] >= 170):
        return "Crisis Finisher (#5–#7)"
    elif row['p_sr'] >= 155 and row['sr_delta'] >= 10:
        return "Middle-Overs Enforcer"
    elif row['p_dot_pct'] <= 28 and row['consistency_pct'] >= 75:
        return "Crisis Anchor"
    else:
        return "Top-Order Stabilizer"

bat['tactical_role'] = bat.apply(assign_batter_archetype, axis=1)

# Bowling Overall & Pressure
p_bowl = bbb[bbb['is_high_pressure']].groupby('bowler_name').agg(
    p_balls=('match_id', 'count'),
    p_runs=('total_ball_runs', 'sum'),
    p_wkts=('is_wkt', 'sum'),
    p_dots=('total_ball_runs', lambda s: (s == 0).sum())
).reset_index()

n_bowl = bbb[~bbb['is_high_pressure']].groupby('bowler_name').agg(
    n_balls=('match_id', 'count'),
    n_runs=('total_ball_runs', 'sum'),
    n_wkts=('is_wkt', 'sum')
).reset_index()

tourn_n_bowl_runs = n_bowl['n_runs'].sum()
tourn_n_bowl_balls = n_bowl['n_balls'].sum()
tourn_base_econ = (tourn_n_bowl_runs / (tourn_n_bowl_balls / 6))

bowl = pd.merge(p_bowl, n_bowl, on='bowler_name', how='inner')
bowl['p_econ'] = (bowl['p_runs'] / bowl['p_balls']) * 6
bowl['n_econ_smoothed'] = ((bowl['n_runs'] + (tourn_base_econ * prior_weight / 6.0)) / ((bowl['n_balls'] + prior_weight) / 6.0))
bowl['n_econ_raw'] = (bowl['n_runs'] / np.maximum(1, bowl['n_balls'] / 6.0))
bowl['n_econ'] = np.where(bowl['n_balls'] < 30, bowl['n_econ_smoothed'], bowl['n_econ_raw'])
bowl['econ_delta'] = bowl['p_econ'] - bowl['n_econ']
bowl['p_dot_pct'] = (bowl['p_dots'] / bowl['p_balls']) * 100

# Attach Death Phase metrics to each bowler
bowl['death_balls'] = bowl['bowler_name'].apply(lambda x: bowl_phase_dict.get(x, {}).get('death', {}).get('balls', 0))
bowl['death_runs'] = bowl['bowler_name'].apply(lambda x: bowl_phase_dict.get(x, {}).get('death', {}).get('runs', 0))
bowl['death_wkts'] = bowl['bowler_name'].apply(lambda x: bowl_phase_dict.get(x, {}).get('death', {}).get('wkts', 0))
bowl['death_econ'] = bowl['bowler_name'].apply(lambda x: bowl_phase_dict.get(x, {}).get('death', {}).get('econ', 0.0))
bowl['death_dot_pct'] = bowl['bowler_name'].apply(lambda x: bowl_phase_dict.get(x, {}).get('death', {}).get('dotPct', 0.0))

m_bowl = bbb[bbb['is_high_pressure']].groupby(['bowler_name', 'match_id']).agg(
    m_balls=('match_id', 'count'),
    m_runs=('total_ball_runs', 'sum'),
    m_wkts=('is_wkt', 'sum')
).reset_index()
m_bowl = m_bowl[m_bowl['m_balls'] >= 6]
m_bowl['m_econ'] = (m_bowl['m_runs'] / m_bowl['m_balls']) * 6
m_bowl['is_success'] = (m_bowl['m_econ'] <= 8.5) | (m_bowl['m_wkts'] >= 1)

c_bowl = m_bowl.groupby('bowler_name').agg(
    total_m=('match_id', 'count'),
    succ_m=('is_success', 'sum')
).reset_index()
c_bowl['consistency_pct'] = (c_bowl['succ_m'] / c_bowl['total_m']) * 100
bowl = pd.merge(bowl, c_bowl[['bowler_name', 'consistency_pct', 'total_m']], on='bowler_name', how='left').fillna({'consistency_pct': 50.0, 'total_m': 1})

bowl['raw_clutch'] = (100 - bowl['p_econ'] * 8.0) - (bowl['econ_delta'] * 5) + (bowl['p_dot_pct'] * 0.6) + (bowl['p_wkts'] * 1.5)
bowl['reliability'] = 0.70 + 0.30 * (bowl['consistency_pct'] / 100.0)
bowl['clutch_score'] = (bowl['raw_clutch'] * bowl['reliability']).round(1)

def assign_bowler_archetype(row):
    d_balls = row['death_balls']
    p_balls = row['p_balls']
    if d_balls >= 60 and row['death_econ'] <= 9.2:
        return "Death-Over Specialist"
    elif row['p_dot_pct'] >= 45.0:
        return "Powerplay Pacing Weapon"
    elif row['consistency_pct'] >= 75.0 and row['p_econ'] <= 7.8:
        return "Middle-Overs Spin Enforcer"
    else:
        return "Containment Seamer"

bowl['tactical_role'] = bowl.apply(assign_bowler_archetype, axis=1)

# Tier 1 Qualification: >= 140 balls
qual_bat_tier1 = bat[(bat['p_balls'] >= 140) & (~bat['striker_name'].isin(pak_players))].sort_values(by='clutch_score', ascending=False)
qual_bowl_tier1 = bowl[(bowl['p_balls'] >= 140) & (~bowl['bowler_name'].isin(pak_players))].sort_values(by='clutch_score', ascending=False)

# Dedicated Death-Overs Finisher Specialists (Min 40 Death Balls)
death_specialists_df = bat[(bat['death_balls'] >= 40) & (~bat['striker_name'].isin(pak_players))].copy()
death_specialists_df['death_raw'] = (
    0.45 * death_specialists_df['death_sr'] +
    0.25 * death_specialists_df['cold_start_sr'] +
    0.20 * death_specialists_df['death_bdry_pct'] * 2.0 -
    0.15 * death_specialists_df['death_dot_pct']
)
death_specialists_df['death_clutch'] = (death_specialists_df['death_raw'] * death_specialists_df['reliability']).round(1)
qual_death_finishers = death_specialists_df.sort_values(by='death_clutch', ascending=False)

# Tier 2: Emerging Watchlist (50 to 139 balls) with Empirical Bayes Shrinkage
bat_tier2 = bat[(bat['p_balls'] >= 50) & (bat['p_balls'] < 140) & (~bat['striker_name'].isin(pak_players))].copy()
prior_clutch = bat['clutch_score'].mean()
bat_tier2['sample_weight'] = bat_tier2['p_balls'] / (bat_tier2['p_balls'] + 40.0)
bat_tier2['shrunk_clutch'] = (prior_clutch * (1.0 - bat_tier2['sample_weight']) + bat_tier2['clutch_score'] * bat_tier2['sample_weight']).round(1)
qual_bat_tier2 = bat_tier2.sort_values(by='shrunk_clutch', ascending=False)

# Player to team map
p_team = mapping[['player_name', 'team_name']].drop_duplicates(subset='player_name')
player_team_map = dict(zip(p_team['player_name'], p_team['team_name']))

top_batters_list = []
for rank_num, (_, r) in enumerate(qual_bat_tier1.head(30).iterrows(), 1):
    pname = r['striker_name']
    team = player_team_map.get(pname, "IPL Franchise")
    top_batters_list.append({
        "rank": rank_num,
        "name": pname,
        "team": team,
        "role": r['tactical_role'],
        "balls": int(r['p_balls']),
        "runs": int(r['p_runs']),
        "strikeRate": round(r['p_sr'], 1),
        "normalStrikeRate": round(r['n_sr'], 1),
        "srDelta": round(r['sr_delta'], 1),
        "dotPct": round(r['p_dot_pct'], 1),
        "boundaryPct": round(r['p_bdry_pct'], 1),
        "consistencyPct": round(r['consistency_pct'], 1),
        "coldStartSR": round(r['cold_start_sr'], 1),
        "clutchScore": round(r['clutch_score'], 1),
        "rawClutch": round(r['raw_clutch'], 1),
        "deathBalls": int(r['death_balls']),
        "deathSR": round(r['death_sr'], 1),
        "phases": bat_phase_dict.get(pname, {}),
        "recommendation": "MUST BUY" if rank_num == 1 else "TARGET ACQUIRE"
    })

top_bowlers_list = []
for rank_num, (_, r) in enumerate(qual_bowl_tier1.head(30).iterrows(), 1):
    pname = r['bowler_name']
    team = player_team_map.get(pname, "IPL Franchise")
    top_bowlers_list.append({
        "rank": rank_num,
        "name": pname,
        "team": team,
        "role": r['tactical_role'],
        "balls": int(r['p_balls']),
        "overs": round(r['p_balls'] / 6, 1),
        "runs": int(r['p_runs']),
        "wickets": int(r['p_wkts']),
        "economy": round(r['p_econ'], 2),
        "normalEconomy": round(r['n_econ'], 2),
        "econDelta": round(r['econ_delta'], 2),
        "dotPct": round(r['p_dot_pct'], 1),
        "consistencyPct": round(r['consistency_pct'], 1),
        "clutchScore": round(r['clutch_score'], 1),
        "rawClutch": round(r['raw_clutch'], 1),
        "deathBalls": int(r['death_balls']),
        "deathEcon": round(r['death_econ'], 2),
        "phases": bowl_phase_dict.get(pname, {}),
        "recommendation": "LOCK DOWN" if r['clutch_score'] >= 140 else "TARGET ACQUIRE"
    })

death_finishers_list = []
for rank_num, (_, r) in enumerate(qual_death_finishers.head(20).iterrows(), 1):
    pname = r['striker_name']
    team = player_team_map.get(pname, "IPL Franchise")
    death_finishers_list.append({
        "rank": rank_num,
        "name": pname,
        "team": team,
        "role": "Crisis Finisher (#5–#7)",
        "deathBalls": int(r['death_balls']),
        "deathRuns": int(r['death_runs']),
        "deathSR": round(r['death_sr'], 1),
        "coldStartSR": round(r['cold_start_sr'], 1),
        "deathBdryPct": round(r['death_bdry_pct'], 1),
        "deathDotPct": round(r['death_dot_pct'], 1),
        "consistencyPct": round(r['consistency_pct'], 1),
        "deathClutch": round(r['death_clutch'], 1),
        "recommendation": "IMPACT FINISHER" if rank_num <= 3 else "SPECIALIST DEPTH"
    })

emerging_watchlist_list = []
for rank_num, (_, r) in enumerate(qual_bat_tier2.head(15).iterrows(), 1):
    pname = r['striker_name']
    team = player_team_map.get(pname, "IPL Franchise")
    emerging_watchlist_list.append({
        "rank": rank_num,
        "name": pname,
        "team": team,
        "balls": int(r['p_balls']),
        "strikeRate": round(r['p_sr'], 1),
        "rawClutch": round(r['clutch_score'], 1),
        "shrunkClutch": round(r['shrunk_clutch'], 1),
        "consistencyPct": round(r['consistency_pct'], 1),
        "recommendation": "HIGH-UPSIDE STEAL"
    })

# Master player dictionary for search & modal deep-dive
all_players_dict = {}
all_names = (set(bat['striker_name']).union(set(bowl['bowler_name']))) - pak_players

for name in all_names:
    b_row = bat[bat['striker_name'] == name]
    bw_row = bowl[bowl['bowler_name'] == name]
    team = player_team_map.get(name, "IPL / T20")
    
    b_data = None
    if len(b_row) > 0:
        br = b_row.iloc[0]
        b_data = {
            "p_balls": int(br['p_balls']),
            "p_runs": int(br['p_runs']),
            "p_sr": round(br['p_sr'], 1),
            "n_sr": round(br['n_sr'], 1),
            "sr_delta": round(br['sr_delta'], 1),
            "p_dot_pct": round(br['p_dot_pct'], 1),
            "p_bdry_pct": round(br['p_bdry_pct'], 1),
            "cold_start_sr": round(br['cold_start_sr'], 1),
            "consistency_pct": round(br['consistency_pct'], 1),
            "clutch_score": round(br['clutch_score'], 1),
            "tactical_role": br['tactical_role'],
            "phases": bat_phase_dict.get(name, {})
        }
    
    bw_data = None
    if len(bw_row) > 0:
        bwr = bw_row.iloc[0]
        bw_data = {
            "p_balls": int(bwr['p_balls']),
            "p_runs": int(bwr['p_runs']),
            "p_econ": round(bwr['p_econ'], 2),
            "n_econ": round(bwr['n_econ'], 2),
            "econ_delta": round(bwr['econ_delta'], 2),
            "p_wkts": int(bwr['p_wkts']),
            "p_dot_pct": round(bwr['p_dot_pct'], 1),
            "consistency_pct": round(bwr['consistency_pct'], 1),
            "clutch_score": round(bwr['clutch_score'], 1),
            "tactical_role": bwr['tactical_role'],
            "phases": bowl_phase_dict.get(name, {})
        }
    
    role = "Batter"
    overall_clutch = 0
    verdict = "AUCTION PASS"
    verdict_class = "pass"
    summary = ""
    
    bat_vol = b_data['p_balls'] if b_data else 0
    bowl_vol = bw_data['p_balls'] if bw_data else 0

    if bat_vol >= 40 and bowl_vol >= 40 and b_data['p_sr'] >= 115 and bw_data['p_wkts'] >= 3:
        role = "All-Rounder"
        overall_clutch = round((b_data['clutch_score'] * 0.5) + (bw_data['clutch_score'] * 0.5), 1)
        verdict = "DEFINITE BUY" if overall_clutch >= 120 else "MONITOR / TARGET"
        verdict_class = "buy" if overall_clutch >= 120 else "monitor"
        summary = f"Two-way balance asset: {b_data['p_sr']} pressure SR and {bw_data['p_econ']} economy."
    elif bowl_vol > bat_vol or (bw_data and bw_data['p_balls'] >= 40 and (not b_data or b_data['p_balls'] < 40)):
        role = bw_data['tactical_role'] if bw_data else "Bowler"
        overall_clutch = bw_data['clutch_score'] if bw_data else 0
        if bw_data and bw_data['p_balls'] >= 60 and bw_data['p_econ'] <= 8.5:
            verdict = "DEFINITE BUY"
            verdict_class = "buy"
            summary = f"World-class pressure executor: {bw_data['p_econ']} economy in crisis with {bw_data['p_wkts']} wickets."
        elif bw_data and bw_data['p_balls'] >= 30 and bw_data['p_econ'] <= 9.2:
            verdict = "MONITOR / SQUAD DEPTH"
            verdict_class = "monitor"
            summary = f"Dependable pressure bowler: {bw_data['p_econ']} economy rate with {bw_data['p_dot_pct']}% dot ball rate."
        else:
            verdict = "AUCTION PASS"
            verdict_class = "pass"
            summary = f"Economy inflates under pressure: {bw_data['p_econ'] if bw_data else 0} RPO."
    else:
        role = b_data['tactical_role'] if b_data else "Batter"
        overall_clutch = b_data['clutch_score'] if b_data else 0
        if b_data and b_data['p_balls'] >= 60 and b_data['p_sr'] >= 140 and b_data['sr_delta'] >= 0:
            verdict = "DEFINITE BUY"
            verdict_class = "buy"
            summary = f"High-impact pressure batter: Strikes at {b_data['p_sr']} under pressure (+{b_data['sr_delta']} SR surge)."
        elif b_data and b_data['p_balls'] >= 30 and b_data['p_sr'] >= 125:
            verdict = "MONITOR / TARGET"
            verdict_class = "monitor"
            summary = f"Reliable contributor with {b_data['p_sr']} strike rate."
        else:
            verdict = "AUCTION PASS"
            verdict_class = "pass"
            summary = f"Performance dips under pressure: SR drops by {abs(b_data['sr_delta']) if b_data else 0}."
            
    all_players_dict[name.lower()] = {
        "name": name,
        "team": team,
        "role": role,
        "clutchScore": overall_clutch,
        "verdict": verdict,
        "verdictClass": verdict_class,
        "summary": summary,
        "batting": b_data,
        "bowling": bw_data
    }

# All-rounders evaluation
ar = pd.merge(bat, bowl, left_on='striker_name', right_on='bowler_name', how='inner')
ar = ar[(ar['p_balls_x'] >= 40) & (ar['p_balls_y'] >= 40) & (~ar['striker_name'].isin(pak_players))].copy()
ar['ar_rating'] = (ar['clutch_score_x'] * 0.5) + (ar['clutch_score_y'] * 0.5)
qual_ar = ar.sort_values(by='ar_rating', ascending=False)

top_ar_list = []
for idx, (_, r) in enumerate(qual_ar.head(15).iterrows(), 1):
    pname = r['striker_name']
    team = player_team_map.get(pname, "IPL Franchise")
    top_ar_list.append({
        "rank": idx,
        "name": pname,
        "team": team,
        "batBalls": int(r['p_balls_x']),
        "batRuns": int(r['p_runs_x']),
        "batSR": round(r['p_sr'], 1),
        "srDelta": round(r['sr_delta'], 1),
        "bowlBalls": int(r['p_balls_y']),
        "bowlEcon": round(r['p_econ'], 2),
        "bowlWkts": int(r['p_wkts']),
        "clutchScore": round(r['ar_rating'], 1),
        "recommendation": "ELITE ALL-ROUNDER" if r['ar_rating'] >= 140 else "HIGH-LEVERAGE UTILITY"
    })

output_payload = {
    "metadata": {
        "tournament": "IPL & International T20 (2022-2026)",
        "totalMatches": int(matches['match_id'].nunique()),
        "totalBalls": len(bbb),
        "totalDeliveries": len(bbb),
        "pressureBalls": int(bbb['is_high_pressure'].sum()),
        "highPressureDeliveries": int(bbb['is_high_pressure'].sum()),
        "pressureBallPct": round((bbb['is_high_pressure'].sum() / len(bbb)) * 100, 1),
        "highPressurePct": round((bbb['is_high_pressure'].sum() / len(bbb)) * 100, 1),
        "totalPlayers": len(all_players_dict),
        "tier1BatMinBalls": 140,
        "tier1BowlMinBalls": 140,
        "deathMinBalls": 40,
        "tournBaseSR": round(tourn_base_sr, 1),
        "tournBaseEcon": round(tourn_base_econ, 2),
        "generatedAt": "2026-11-13"
    },
    "topBatters": top_batters_list,
    "topBowlers": top_bowlers_list,
    "topAllRounders": top_ar_list,
    "deathSpecialists": death_finishers_list,
    "emergingWatchlist": emerging_watchlist_list,
    "allPlayers": all_players_dict,
    "players": all_players_dict
}

with open(OUT_JSON, "w", encoding="utf-8") as f:
    json.dump(output_payload, f, indent=2)

print(f"SUCCESS: Generated {OUT_JSON} with {len(top_batters_list)} Tier-1 Batters, {len(top_bowlers_list)} Tier-1 Bowlers, {len(death_finishers_list)} Death Specialists, and {len(emerging_watchlist_list)} Emerging Watchlist talents!")
