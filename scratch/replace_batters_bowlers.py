import os

APP_PATH = r"c:\Users\Dhairya\Desktop\Active\Rajasthan Royals\frontend\src\App.tsx"

replacement_code = """interface Batter {
  rank: number;
  name: string;
  role: string;
  team: string;
  country: string;
  pBalls: number;
  pRuns: number;
  pSR: number;
  baseSR: number;
  deltaSR: number;
  dotPct: number;
  bndPct: number;
  consistencyPct: number;
  clutchScore: number;
  badge: string;
  strengths: string[];
}

interface Bowler {
  rank: number;
  name: string;
  role: string;
  team: string;
  country: string;
  pBalls: number;
  pWkts: number;
  pEcon: number;
  baseEcon: number;
  econDelta: number;
  dotPct: number;
  consistencyPct: number;
  clutchScore: number;
  badge: string;
  strengths: string[];
}

const BATTER_ROLES: Record<string, string> = {
  "Babar Azam": "Innings Anchor / Crisis Stabilizer",
  "Naman Dhir": "Middle-Overs Enforcer / Finisher",
  "Phil Salt": "Wicketkeeper / Explosive Opener",
  "Najibullah Zadran": "Spin Punisher / Power Finisher",
  "Donovan Ferreira": "Explosive Finisher / Wicketkeeper",
  "Shubham Dubey": "Death-Overs Power Hitter",
  "Jos Buttler": "World-Class Crisis Match-Winner",
  "Rinku Singh": "Death-Overs Elite Finisher",
  "Rishabh Pant": "Left-Hand Dynamic Enforcer",
  "Sanju Samson": "Royals Captain / Crisis Anchor"
};

const BOWLER_ROLES: Record<string, string> = {
  "Arshdeep Singh": "Death Overs Strike Pacer",
  "Matheesha Pathirana": "Sling Action Death Specialist",
  "Abrar Ahmed": "Mystery Spin Crisis Lockdown",
  "Rashid Khan": "World-Class Clutch Leg-Spinner",
  "Yuzvendra Chahal": "High-Pressure Wicket Taker",
  "Mohammad Nawaz": "Left-Arm Restrictive Spin",
  "Harshal Patel": "Death Dip Slower-Ball Specialist",
  "Jasprit Bumrah": "Generational Death Overs Pacer",
  "Akeal Hosein": "Powerplay & Death Arm Ball Specialist",
  "Shaheen Afridi": "Left-Arm High-Pace Wicket Taker"
};

const BATTERS: Batter[] = (clutchData.topBatters || []).slice(0, 15).map((b: any) => ({
  rank: b.rank,
  name: b.name,
  role: BATTER_ROLES[b.name] || "Crisis Batting Specialist",
  team: b.team,
  country: b.team.includes('Pakistan') ? 'PAK' :
           b.team.includes('England') ? 'ENG' :
           b.team.includes('Afghanistan') ? 'AFG' : 'IND',
  pBalls: b.balls,
  pRuns: b.runs,
  pSR: b.strikeRate,
  baseSR: b.normalStrikeRate,
  deltaSR: b.srDelta,
  dotPct: b.dotPct,
  bndPct: b.boundaryPct,
  consistencyPct: b.consistencyPct ?? 80.0,
  clutchScore: b.clutchScore,
  badge: b.recommendation || (b.rank === 1 ? "PRIORITY TARGET" : b.rank <= 3 ? "MAIN TARGET" : "TARGET ACQUIRE"),
  strengths: [
    `Elite ${(b.consistencyPct ?? 80.0).toFixed(1)}% match-level consistency`,
    `Strikes at ${b.strikeRate.toFixed(1)} under pressure (+${b.srDelta.toFixed(1)} surge)`,
    `Low dot ball rate (${b.dotPct.toFixed(1)}%) with ${b.boundaryPct.toFixed(1)}% boundary power`
  ]
}));

const BOWLERS: Bowler[] = (clutchData.topBowlers || []).slice(0, 15).map((bw: any) => ({
  rank: bw.rank,
  name: bw.name,
  role: BOWLER_ROLES[bw.name] || "Pressure Containment Specialist",
  team: bw.team,
  country: bw.team.includes('Pakistan') ? 'PAK' :
           bw.team.includes('Chennai') || bw.team.includes('Sri Lanka') ? 'SL' :
           bw.team.includes('Afghanistan') ? 'AFG' :
           bw.team.includes('West Indies') ? 'WI' : 'IND',
  pBalls: bw.balls,
  pWkts: bw.wickets,
  pEcon: bw.economy,
  baseEcon: bw.normalEconomy,
  econDelta: bw.econDelta,
  dotPct: bw.dotPct,
  consistencyPct: bw.consistencyPct ?? 75.0,
  clutchScore: bw.clutchScore,
  badge: bw.recommendation || (bw.rank === 1 ? "PRIORITY TARGET" : bw.rank <= 3 ? "MAIN TARGET" : "TARGET ACQUIRE"),
  strengths: [
    `Delivers in ${(bw.consistencyPct ?? 75.0).toFixed(1)}% of high-tension matches`,
    `Concedes only ${bw.economy.toFixed(2)} RPO in crisis with ${bw.wickets} wickets`,
    `Forces ${bw.dotPct.toFixed(1)}% dot balls under match-deciding pressure`
  ]
}));
"""

with open(APP_PATH, "r", encoding="utf-8") as f:
    lines = f.readlines()

start_idx = -1
end_idx = -1
for i, l in enumerate(lines):
    if l.startswith("interface Batter {"):
        start_idx = i
    if l.startswith("interface ChatMessage {"):
        end_idx = i

if start_idx != -1 and end_idx != -1:
    new_lines = lines[:start_idx] + [replacement_code + "\n"] + lines[end_idx:]
    with open(APP_PATH, "w", encoding="utf-8") as f:
        f.writelines(new_lines)
    print(f"Successfully replaced lines {start_idx} to {end_idx} in App.tsx")
else:
    print(f"Error finding boundaries: start_idx={start_idx}, end_idx={end_idx}")
