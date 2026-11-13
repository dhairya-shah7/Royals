import pandas as pd
import json

df = pd.read_csv(r'C:\Users\Dhairya\Desktop\Active\Rajasthan Royals\competition_team_player_mapping.csv')
pak_players = set(df[df['team_name'].str.contains('Pakistan|Peshawar|Lahore|Karachi|Islamabad|Quetta|Multan|Rawalpindi', case=False, na=False)]['player_name'].unique())

data = json.load(open(r'C:\Users\Dhairya\Desktop\Active\Rajasthan Royals\frontend\src\data\clutch_index.json', 'r', encoding='utf-8'))
batters = [b for b in data['topBatters'] if b['name'] not in pak_players][:10]
bowlers = [bw for bw in data['topBowlers'] if bw['name'] not in pak_players][:10]

print('Top 10 Batters (No Pak):')
for i, b in enumerate(batters):
    print(f"{i+1}. {b['name']} ({b['team']}): Clutch={b['clutchScore']}, Consist={b['consistencyPct']}%")

print('\nTop 10 Bowlers (No Pak):')
for i, bw in enumerate(bowlers):
    print(f"{i+1}. {bw['name']} ({bw['team']}): Clutch={bw['clutchScore']}, Consist={bw['consistencyPct']}%")
