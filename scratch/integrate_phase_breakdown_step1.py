import re

filepath = 'c:/Users/Dhairya/Desktop/Active/Rajasthan Royals/frontend/src/App.tsx'

with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update Batter & Bowler interfaces to support phases
target_interfaces = '''interface Batter {
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
}'''

replace_interfaces = '''export interface PhaseBatting {
  balls: number;
  runs: number;
  sr: number;
  dotPct: number;
  bdryPct: number;
}

export interface PhaseBowling {
  balls: number;
  runs: number;
  wkts: number;
  econ: number;
  dotPct: number;
}

interface Batter {
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
  phases?: {
    powerplay?: PhaseBatting;
    middle?: PhaseBatting;
    death?: PhaseBatting;
  };
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
  phases?: {
    powerplay?: PhaseBowling;
    middle?: PhaseBowling;
    death?: PhaseBowling;
  };
}'''

if target_interfaces in content:
    content = content.replace(target_interfaces, replace_interfaces, 1)
    print("Updated Batter and Bowler interfaces with Phase data types")
else:
    print("Could not find target_interfaces")

# 2. Add phaseFilter state in App component
target_tabletab = "  const [tableTab, setTableTab] = useState<'bat' | 'bowl'>('bat');"
replace_tabletab = """  const [tableTab, setTableTab] = useState<'bat' | 'bowl'>('bat');
  const [phaseFilter, setPhaseFilter] = useState<'all' | 'powerplay' | 'middle' | 'death'>('all');"""

if target_tabletab in content:
    content = content.replace(target_tabletab, replace_tabletab, 1)
    print("Added phaseFilter state")
else:
    print("Could not find target_tabletab")

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)

print("Saved preliminary changes in App.tsx")
