filepath = 'c:/Users/Dhairya/Desktop/Active/Rajasthan Royals/frontend/src/App.tsx'

with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Remove displayedBatters and displayedBowlers from between dynamicBatters and dynamicBowlers
bad_block = '''  // Phase-specific derived lists for leaderboard view
  const displayedBatters = useMemo(() => {
    if (phaseFilter === 'all') return dynamicBatters;
    return [...dynamicBatters]
      .filter(b => (b.phases?.[phaseFilter]?.balls || 0) >= 15)
      .sort((a, b) => (b.phases?.[phaseFilter]?.sr || 0) - (a.phases?.[phaseFilter]?.sr || 0));
  }, [dynamicBatters, phaseFilter]);

  const displayedBowlers = useMemo(() => {
    if (phaseFilter === 'all') return dynamicBowlers;
    return [...dynamicBowlers]
      .filter(bw => (bw.phases?.[phaseFilter]?.balls || 0) >= 15)
      .sort((a, b) => (a.phases?.[phaseFilter]?.econ || 99) - (b.phases?.[phaseFilter]?.econ || 99));
  }, [dynamicBowlers, phaseFilter]);'''

content = content.replace(bad_block, '')

# 2. Insert displayedBatters and displayedBowlers right AFTER dynamicBowlers
after_bowlers_target = '''        rank: idx + 1,
        badge: idx === 0 ? "PRIORITY TARGET" : idx < 3 ? "MAIN TARGET" : "TARGET ACQUIRE"
      }));
  }, [activeCalib]);'''

# Find the second occurrence of after_bowlers_target (the one for dynamicBowlers)
idx_first = content.find(after_bowlers_target)
idx_second = content.find(after_bowlers_target, idx_first + len(after_bowlers_target))

displayed_code = '''

  // Phase-specific derived lists for leaderboard view
  const displayedBatters = useMemo(() => {
    if (phaseFilter === 'all') return dynamicBatters;
    return [...dynamicBatters]
      .filter(b => (b.phases?.[phaseFilter]?.balls || 0) >= 15)
      .sort((a, b) => (b.phases?.[phaseFilter]?.sr || 0) - (a.phases?.[phaseFilter]?.sr || 0));
  }, [dynamicBatters, phaseFilter]);

  const displayedBowlers = useMemo(() => {
    if (phaseFilter === 'all') return dynamicBowlers;
    return [...dynamicBowlers]
      .filter(bw => (bw.phases?.[phaseFilter]?.balls || 0) >= 15)
      .sort((a, b) => (a.phases?.[phaseFilter]?.econ || 99) - (b.phases?.[phaseFilter]?.econ || 99));
  }, [dynamicBowlers, phaseFilter]);'''

content = content[:idx_second + len(after_bowlers_target)] + displayed_code + content[idx_second + len(after_bowlers_target):]

# 3. Use displayedBatters and displayedBowlers in the Leaderboard tables
content = content.replace(
    'dynamicBatters.slice(0, 10).map((b) => {',
    'displayedBatters.slice(0, 10).map((b) => {'
)
content = content.replace(
    'dynamicBowlers.slice(0, 10).map((bw) => {',
    'displayedBowlers.slice(0, 10).map((bw) => {'
)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)

print("Updated App.tsx successfully")
