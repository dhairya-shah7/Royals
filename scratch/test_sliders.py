import json

data = json.load(open(r'c:\Users\Dhairya\Desktop\Active\Rajasthan Royals\frontend\src\data\clutch_index.json', 'r', encoding='utf-8'))
batters = data['topBatters']

def calc(b, cw, sdw, min_balls=80):
    if b['balls'] < min_balls:
        return -999
    clipped = max(-20, min(50, b['srDelta']))
    raw = b['strikeRate']*0.5 + clipped*sdw + b['boundaryPct']*0.4 - b['dotPct']*0.15
    rel = (1.0 - cw) + cw*(b['consistencyPct']/100.0)
    return round(raw * rel, 1)

print('DEFAULT (cw=0.30, sdw=0.35, min_balls=80):')
s1 = [b for b in sorted(batters, key=lambda b: calc(b, 0.30, 0.35, 80), reverse=True) if calc(b, 0.30, 0.35, 80) > 0]
for i, b in enumerate(s1[:8]):
    print(f"  {i+1}. {b['name']}: Score={calc(b, 0.30, 0.35, 80)} (balls={b['balls']})")

print('\nEXTREME BALL THRESHOLD (min_balls=150):')
s2 = [b for b in sorted(batters, key=lambda b: calc(b, 0.30, 0.35, 150), reverse=True) if calc(b, 0.30, 0.35, 150) > 0]
for i, b in enumerate(s2[:8]):
    print(f"  {i+1}. {b['name']}: Score={calc(b, 0.30, 0.35, 150)} (balls={b['balls']})")

print('\nEXTREME CONSISTENCY (cw=0.60):')
s3 = [b for b in sorted(batters, key=lambda b: calc(b, 0.60, 0.35, 80), reverse=True) if calc(b, 0.60, 0.35, 80) > 0]
for i, b in enumerate(s3[:8]):
    print(f"  {i+1}. {b['name']}: Score={calc(b, 0.60, 0.35, 80)} (balls={b['balls']})")
