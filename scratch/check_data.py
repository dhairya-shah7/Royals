import json

data = json.load(open('c:/Users/Dhairya/Desktop/Active/Rajasthan Royals/frontend/src/data/clutch_index.json', 'r', encoding='utf-8'))
print('Top 10 Batters in clutch_index.json:')
for b in data['topBatters'][:10]:
    print(f"{b['rank']}. {b['name']} ({b['team']}): Clutch={b['clutchScore']}, Consist={b.get('consistencyPct', 'N/A')}%")

print('\nTop 10 Bowlers in clutch_index.json:')
for bw in data['topBowlers'][:10]:
    print(f"{bw['rank']}. {bw['name']} ({bw['team']}): Clutch={bw['clutchScore']}, Consist={bw.get('consistencyPct', 'N/A')}%")
