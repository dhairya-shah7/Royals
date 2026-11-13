import pandas as pd
import numpy as np

bbb = pd.read_csv(r'c:\Users\Dhairya\Desktop\Active\Rajasthan Royals\ball_by_ball.csv')
mapping = pd.read_csv(r'c:\Users\Dhairya\Desktop\Active\Rajasthan Royals\competition_team_player_mapping.csv')
matches = pd.read_csv(r'c:\Users\Dhairya\Desktop\Active\Rajasthan Royals\matches.csv')

pak_players = set(mapping[mapping['team_name'].str.contains('Pakistan|Peshawar|Lahore|Karachi|Islamabad|Quetta|Multan|Rawalpindi', case=False, na=False)]['player_name'].unique())

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

balls_remaining = np.maximum(1, 120 - bbb['innings_ball_num'])
runs_needed = np.maximum(0, bbb['target'] - bbb['cum_runs'])
rrr = np.where(bbb['innings'] == 2, (runs_needed / balls_remaining) * 6, 8.0)
wickets_in_hand = np.maximum(1, 10 - bbb['cum_wkts'])

chase_tension = np.where(
    bbb['innings'] == 2,
    (np.maximum(0, rrr - 8.0) / 4.0) * (6.0 / wickets_in_hand) * 4.0,
    0.0
)
death_tension = np.where(bbb['overid'] >= 16, (bbb['overid'] - 15) * 1.2, 0.0)
collapse_tension = np.where(
    (bbb['overid'] <= 6) & (bbb['cum_wkts'] >= 2),
    (bbb['cum_wkts']) * 1.5,
    0.0
)
ko_multiplier = np.where(bbb['is_knockout'], 1.25, 1.0)
raw_tension = (chase_tension + death_tension + collapse_tension) * ko_multiplier
bbb['tension_score'] = np.clip(raw_tension, 0.0, 10.0)
bbb['is_high_pressure'] = bbb['tension_score'] >= 4.0

# Bat
bat_high = bbb[bbb['is_high_pressure']].groupby('striker_name').agg(
    p_balls=('runs', 'count'),
    p_runs=('runs', 'sum'),
    p_dots=('runs', lambda x: (x == 0).sum()),
    p_bnd=('runs', lambda x: ((bbb.loc[x.index, 'is_four_clean']) | (bbb.loc[x.index, 'is_six_clean'])).sum())
).reset_index()

bat_base = bbb[~bbb['is_high_pressure']].groupby('striker_name').agg(
    b_balls=('runs', 'count'),
    b_runs=('runs', 'sum')
).reset_index()

bat = pd.merge(bat_high, bat_base, on='striker_name', how='inner')
bat['p_sr'] = (bat['p_runs'] / bat['p_balls']) * 100
bat['b_sr'] = (bat['b_runs'] / bat['b_balls']) * 100
bat['delta_sr'] = bat['p_sr'] - bat['b_sr']
bat['p_dot_pct'] = (bat['p_dots'] / bat['p_balls']) * 100
bat['p_bnd_pct'] = (bat['p_bnd'] / bat['p_balls']) * 100

bat['raw_clutch'] = (
    0.50 * bat['p_sr'] +
    0.30 * bat['delta_sr'].clip(lower=-20, upper=50) +
    0.20 * bat['p_bnd_pct'] * 2.0 -
    0.15 * bat['p_dot_pct']
)

# Consistency:
m_bat = bbb[bbb['is_high_pressure']].groupby(['striker_name', 'match_id']).agg(
    m_balls=('match_id', 'count'),
    m_runs=('runs', 'sum')
).reset_index()
m_bat = m_bat[m_bat['m_balls'] >= 6]
m_bat['m_sr'] = (m_bat['m_runs'] / m_bat['m_balls']) * 100
m_bat['is_success'] = (m_bat['m_sr'] >= 140) | (m_bat['m_runs'] >= 15)

c_bat = m_bat.groupby('striker_name').agg(
    total_m=('match_id', 'count'),
    succ_m=('is_success', 'sum')
).reset_index()
c_bat['consistency_pct'] = (c_bat['succ_m'] / c_bat['total_m']) * 100
bat = pd.merge(bat, c_bat[['striker_name', 'consistency_pct', 'total_m']], on='striker_name', how='left').fillna({'consistency_pct': 50.0, 'total_m': 1})

bat['reliability'] = 0.70 + 0.30 * (bat['consistency_pct'] / 100.0)
bat['clutch_score'] = (bat['raw_clutch'] * bat['reliability']).round(1)

qual = bat[(bat['p_balls'] >= 80) & (~bat['striker_name'].isin(pak_players))].sort_values(by='clutch_score', ascending=False)
print('Top 15 Batters by Clutch Score:')
for i, r in qual.head(15).reset_index().iterrows():
    print(f"{i+1}. {r['striker_name']}: score={r['clutch_score']:.1f}, raw={r['raw_clutch']:.1f}, consist={r['consistency_pct']:.1f}%, balls={r['p_balls']}")

# Bowlers
bowl_high = bbb[bbb['is_high_pressure']].groupby('bowler_name').agg(
    p_balls=('total_ball_runs', 'count'),
    p_runs=('total_ball_runs', 'sum'),
    p_wkts=('is_wkt', 'sum'),
    p_dots=('total_ball_runs', lambda x: (x == 0).sum())
).reset_index()

bowl_base = bbb[~bbb['is_high_pressure']].groupby('bowler_name').agg(
    b_balls=('total_ball_runs', 'count'),
    b_runs=('total_ball_runs', 'sum')
).reset_index()

bowl = pd.merge(bowl_high, bowl_base, on='bowler_name', how='inner')
bowl['p_econ'] = (bowl['p_runs'] / bowl['p_balls']) * 6
bowl['b_econ'] = (bowl['b_runs'] / bowl['b_balls']) * 6
bowl['econ_delta'] = bowl['b_econ'] - bowl['p_econ']
bowl['p_dot_pct'] = (bowl['p_dots'] / bowl['p_balls']) * 100
bowl['p_strike_rate'] = np.where(bowl['p_wkts'] > 0, bowl['p_balls'] / bowl['p_wkts'], 99.0)

bowl['raw_clutch'] = (
    80.0 - (bowl['p_econ'] * 4.5) +
    (bowl['p_dot_pct'] * 0.45) +
    (np.clip(100.0 / bowl['p_strike_rate'], 0, 15) * 2.5) +
    (bowl['econ_delta'] * 2.0)
)

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

bowl['reliability'] = 0.70 + 0.30 * (bowl['consistency_pct'] / 100.0)
bowl['clutch_score'] = (bowl['raw_clutch'] * bowl['reliability']).round(1)

qual_b = bowl[(bowl['p_balls'] >= 100) & (~bowl['bowler_name'].isin(pak_players))].sort_values(by='clutch_score', ascending=False)
print('\nTop 15 Bowlers by Clutch Score:')
for i, r in qual_b.head(15).reset_index().iterrows():
    print(f"{i+1}. {r['bowler_name']}: score={r['clutch_score']:.1f}, raw={r['raw_clutch']:.1f}, consist={r['consistency_pct']:.1f}%, balls={r['p_balls']}")
