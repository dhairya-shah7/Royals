import json

data = json.load(open(r'c:\Users\Dhairya\Desktop\Active\Rajasthan Royals\frontend\src\data\clutch_index.json', 'r', encoding='utf-8'))
print('Top 12 Batters now:')
for b in data['topBatters'][:12]:
    print(f"{b['rank']}. {b['name']} ({b['team']}): score={b['clutchScore']}, raw={b['rawClutch']}, consist={b['consistencyPct']}%")
