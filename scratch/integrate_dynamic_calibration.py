import re

APP_PATH = r"c:\Users\Dhairya\Desktop\Active\Rajasthan Royals\frontend\src\App.tsx"

with open(APP_PATH, "r", encoding="utf-8") as f:
    code = f.read()

# 1. Add calibration state and dynamic calculations at start of App() component
target_state_anchor = "const [tableTab, setTableTab] = useState<'bat' | 'bowl'>('bat');"

calibration_state_and_memos = """  const [tableTab, setTableTab] = useState<'bat' | 'bowl'>('bat');
  
  // Interactive War Room Calibration Weights (Live Re-computation Engine)
  const [calib, setCalib] = useState({
    minBatBalls: 80,
    minBowlBalls: 90,
    consistencyWeight: 0.30, // Reliability factor: (1 - w) + w * (C_rate / 100)
    srDeltaWeight: 0.35,     // Delta SR surge multiplier
    econWeight: 8.0          // Economy penalty multiplier
  });

  // Dynamically recalculated Batters under custom calibration weights
  const dynamicBatters = useMemo(() => {
    return (clutchData.topBatters || [])
      .filter((b: any) => b.balls >= calib.minBatBalls)
      .map((b: any) => {
        const raw = (b.strikeRate * 0.45) + (b.srDelta * calib.srDeltaWeight) + (b.boundaryPct * 0.8) - (b.dotPct * 0.5);
        const rel = (1.0 - calib.consistencyWeight) + calib.consistencyWeight * (b.consistencyPct / 100.0);
        const clutchScore = Math.round(raw * rel * 10) / 10;
        return {
          ...b,
          clutchScore,
          rawClutch: Math.round(raw * 10) / 10,
          pBalls: b.balls,
          pRuns: b.runs,
          pSR: b.strikeRate,
          baseSR: b.normalStrikeRate,
          deltaSR: b.srDelta,
          bndPct: b.boundaryPct,
          role: BATTER_ROLES[b.name] || "Crisis Batting Specialist",
          country: b.team.includes('Pakistan') ? 'PAK' : b.team.includes('England') ? 'ENG' : b.team.includes('Afghanistan') ? 'AFG' : 'IND',
          badge: b.recommendation || "TARGET ACQUIRE",
          strengths: [
            `Elite ${b.consistencyPct.toFixed(1)}% match-level consistency`,
            `Strikes at ${b.strikeRate.toFixed(1)} under pressure (+${b.srDelta.toFixed(1)} surge)`,
            `Low dot ball rate (${b.dotPct.toFixed(1)}%) with ${b.boundaryPct.toFixed(1)}% boundary power`
          ]
        };
      })
      .sort((a: any, b: any) => b.clutchScore - a.clutchScore)
      .map((b: any, idx: number) => ({
        ...b,
        rank: idx + 1,
        badge: idx === 0 ? "PRIORITY TARGET" : idx < 3 ? "MAIN TARGET" : "TARGET ACQUIRE"
      }));
  }, [calib]);

  // Dynamically recalculated Bowlers under custom calibration weights
  const dynamicBowlers = useMemo(() => {
    return (clutchData.topBowlers || [])
      .filter((bw: any) => bw.balls >= calib.minBowlBalls)
      .map((bw: any) => {
        const raw = (100 - bw.economy * calib.econWeight) - (bw.econDelta * 5) + (bw.dotPct * 0.6) + (bw.wickets * 1.5);
        const rel = (1.0 - calib.consistencyWeight) + calib.consistencyWeight * (bw.consistencyPct / 100.0);
        const clutchScore = Math.round(raw * rel * 10) / 10;
        return {
          ...bw,
          clutchScore,
          rawClutch: Math.round(raw * 10) / 10,
          pBalls: bw.balls,
          pWkts: bw.wickets,
          pEcon: bw.economy,
          baseEcon: bw.normalEconomy,
          econDelta: bw.econDelta,
          role: BOWLER_ROLES[bw.name] || "Pressure Containment Specialist",
          country: bw.team.includes('Pakistan') ? 'PAK' : bw.team.includes('Chennai') || bw.team.includes('Sri Lanka') ? 'SL' : bw.team.includes('Afghanistan') ? 'AFG' : bw.team.includes('West Indies') ? 'WI' : 'IND',
          badge: bw.recommendation || "TARGET ACQUIRE",
          strengths: [
            `Delivers in ${bw.consistencyPct.toFixed(1)}% of high-tension matches`,
            `Concedes only ${bw.economy.toFixed(2)} RPO in crisis with ${bw.wickets} wickets`,
            `Forces ${bw.dotPct.toFixed(1)}% dot balls under match-deciding pressure`
          ]
        };
      })
      .sort((a: any, b: any) => b.clutchScore - a.clutchScore)
      .map((bw: any, idx: number) => ({
        ...bw,
        rank: idx + 1,
        badge: idx === 0 ? "PRIORITY TARGET" : idx < 3 ? "MAIN TARGET" : "TARGET ACQUIRE"
      }));
  }, [calib]);"""

code = code.replace(target_state_anchor, calibration_state_and_memos)

# 2. Update p1, p2, filteredBatters, and filteredBowlers to use dynamicBatters and dynamicBowlers
old_p_calc = """  const p1 = BATTERS.find(b => b.name === selectedB1) || BATTERS[0];
  const p2 = BATTERS.find(b => b.name === selectedB2) || BATTERS[4];

  // Filtered lists for live search
  const q = searchQuery.toLowerCase().trim();
  const filteredBatters = BATTERS.filter(b => 
    b.name.toLowerCase().includes(q) || 
    b.team.toLowerCase().includes(q) || 
    b.role.toLowerCase().includes(q) ||
    b.badge.toLowerCase().includes(q)
  );

  const filteredBowlers = BOWLERS.filter(bw => 
    bw.name.toLowerCase().includes(q) || 
    bw.team.toLowerCase().includes(q) || 
    bw.role.toLowerCase().includes(q) ||
    bw.badge.toLowerCase().includes(q)
  );"""

new_p_calc = """  const p1 = dynamicBatters.find(b => b.name === selectedB1) || dynamicBatters[0] || BATTERS[0];
  const p2 = dynamicBatters.find(b => b.name === selectedB2) || dynamicBatters[1] || BATTERS[1];

  // Filtered lists for live search using dynamic calibration
  const q = searchQuery.toLowerCase().trim();
  const filteredBatters = dynamicBatters.filter(b => 
    b.name.toLowerCase().includes(q) || 
    b.team.toLowerCase().includes(q) || 
    b.role.toLowerCase().includes(q) ||
    b.badge.toLowerCase().includes(q)
  );

  const filteredBowlers = dynamicBowlers.filter(bw => 
    bw.name.toLowerCase().includes(q) || 
    bw.team.toLowerCase().includes(q) || 
    bw.role.toLowerCase().includes(q) ||
    bw.badge.toLowerCase().includes(q)
  );"""

code = code.replace(old_p_calc, new_p_calc)

# 3. Update tables to iterate dynamicBatters and dynamicBowlers
code = code.replace(
    "{clutchData.topBatters.slice(0, 10).map((b) => {",
    "{dynamicBatters.slice(0, 10).map((b) => {"
)
code = code.replace(
    "{clutchData.topBowlers.slice(0, 10).map((bw) => {",
    "{dynamicBowlers.slice(0, 10).map((bw) => {"
)

# Also update Matrix dropdowns to use dynamicBatters
code = code.replace(
    "{BATTERS.map(b => (",
    "{dynamicBatters.slice(0, 15).map(b => ("
)

# 4. Replace Settings page with Interactive War Room Sliders
old_settings_page = """          {/* PAGE 5: SETTINGS / METRICS CONFIG                                         */}
          {/* ========================================================================= */}
          {activePage === 'settings' && (
            <div className="glass-card" style={{ padding: '24px', flex: 1, overflowY: 'auto' }}>
              <h3 style={{ margin: '0 0 6px 0', fontSize: '1.15rem', fontWeight: 800, color: 'var(--text-primary)' }}>
                War Room Calibration Parameters
              </h3>
              <p style={{ margin: '0 0 16px 0', fontSize: '0.78rem', color: 'var(--text-secondary)' }}>
                Configure pressure calculation thresholds for the SupeRR Selector model.
              </p>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', maxWidth: '600px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '12px 16px', background: '#FFFFFF', borderRadius: '12px', border: '1px solid rgba(15,23,42,0.06)' }}>
                  <div>
                    <div style={{ fontWeight: 700, fontSize: '0.82rem' }}>Minimum Required Run Rate (RRR)</div>
                    <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>Defines the tension threshold for chase deliveries</div>
                  </div>
                  <span className="mono-num" style={{ fontWeight: 800, color: 'var(--rr-pink)' }}>≥ 10.0 RPO</span>
                </div>

                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '12px 16px', background: '#FFFFFF', borderRadius: '12px', border: '1px solid rgba(15,23,42,0.06)' }}>
                  <div>
                    <div style={{ fontWeight: 700, fontSize: '0.82rem' }}>Death Overs Window</div>
                    <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>High-leverage end game balls</div>
                  </div>
                  <span className="mono-num" style={{ fontWeight: 800, color: 'var(--rr-blue)' }}>Overs 17–20</span>
                </div>

                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '12px 16px', background: '#FFFFFF', borderRadius: '12px', border: '1px solid rgba(15,23,42,0.06)' }}>
                  <div>
                    <div style={{ fontWeight: 700, fontSize: '0.82rem' }}>Minimum High-Tension Balls Sample</div>
                    <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>Filter out noise and low sample sizes</div>
                  </div>
                  <span className="mono-num" style={{ fontWeight: 800, color: 'var(--rr-gold)' }}>80 Balls</span>
                </div>
              </div>


            </div>
          )}"""

new_settings_page = """          {/* PAGE 5: SETTINGS / METRICS CONFIG (DYNAMIC LIVE CALIBRATION)               */}
          {/* ========================================================================= */}
          {activePage === 'settings' && (
            <div className="glass-card" style={{ padding: '26px 30px', flex: 1, overflowY: 'auto' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '20px', flexWrap: 'wrap', gap: '12px' }}>
                <div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <span style={{ fontSize: '1.2rem' }}>🎛️</span>
                    <h3 style={{ margin: 0, fontSize: '1.25rem', fontWeight: 900, color: 'var(--text-primary)' }}>
                      Interactive War Room Calibration
                    </h3>
                  </div>
                  <p style={{ margin: '4px 0 0 0', fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
                    Adjust MTGI and Match Consistency weights below. All leaderboards, prospect cards, and comparison metrics recalculate live across the platform.
                  </p>
                </div>

                <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                  <span style={{
                    fontSize: '0.72rem',
                    fontWeight: 800,
                    padding: '5px 12px',
                    borderRadius: '999px',
                    background: 'rgba(16, 185, 129, 0.1)',
                    color: '#059669',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '6px'
                  }}>
                    <span style={{ width: '6px', height: '6px', borderRadius: '50%', background: '#10B981', display: 'inline-block' }} />
                    Live Engine Active
                  </span>
                  <button
                    onClick={() => setCalib({
                      minBatBalls: 80,
                      minBowlBalls: 90,
                      consistencyWeight: 0.30,
                      srDeltaWeight: 0.35,
                      econWeight: 8.0
                    })}
                    style={{
                      padding: '6px 14px',
                      borderRadius: '999px',
                      background: '#FFFFFF',
                      border: '1px solid rgba(15, 23, 42, 0.12)',
                      fontSize: '0.75rem',
                      fontWeight: 700,
                      color: 'var(--text-secondary)',
                      cursor: 'pointer',
                      boxShadow: '0 1px 3px rgba(0,0,0,0.05)'
                    }}
                  >
                    Reset to Defaults
                  </button>
                </div>
              </div>

              {/* Live Preview Box */}
              <div style={{
                padding: '14px 18px',
                borderRadius: '16px',
                background: 'linear-gradient(135deg, rgba(230, 0, 126, 0.04) 0%, rgba(14, 54, 150, 0.05) 100%)',
                border: '1px solid rgba(230, 0, 126, 0.12)',
                marginBottom: '22px',
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                flexWrap: 'wrap',
                gap: '12px'
              }}>
                <div>
                  <div style={{ fontSize: '0.72rem', fontWeight: 800, color: 'var(--rr-pink)', textTransform: 'uppercase' }}>Current #1 Recalibrated Leader</div>
                  <div style={{ fontSize: '1.05rem', fontWeight: 900, color: 'var(--text-primary)' }}>
                    🏏 Batter: <span style={{ color: 'var(--rr-pink)' }}>{dynamicBatters[0]?.name}</span> ({dynamicBatters[0]?.clutchScore}) · 🎯 Bowler: <span style={{ color: 'var(--rr-blue)' }}>{dynamicBowlers[0]?.name}</span> ({dynamicBowlers[0]?.clutchScore})
                  </div>
                </div>
                <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', fontFamily: 'JetBrains Mono, monospace' }}>
                  Pool: {dynamicBatters.length} Batters · {dynamicBowlers.length} Bowlers
                </div>
              </div>

              {/* Sliders Grid */}
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(360px, 1fr))', gap: '18px', maxWidth: '980px' }}>
                
                {/* 1. Consistency Weight Slider */}
                <div style={{ padding: '16px 20px', background: '#FFFFFF', borderRadius: '16px', border: '1px solid rgba(15,23,42,0.08)', boxShadow: '0 2px 6px rgba(0,0,0,0.02)' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                    <div style={{ fontWeight: 800, fontSize: '0.85rem', color: 'var(--text-primary)' }}>Match Consistency Weight (wC)</div>
                    <span className="mono-num" style={{ fontWeight: 900, color: '#059669', fontSize: '1.05rem' }}>{Math.round(calib.consistencyWeight * 100)}%</span>
                  </div>
                  <div style={{ fontSize: '0.7rem', color: 'var(--text-secondary)', marginBottom: '12px' }}>
                    Governs reliability multiplier R = [{(1 - calib.consistencyWeight).toFixed(2)} + {calib.consistencyWeight.toFixed(2)} × (C_rate/100)]
                  </div>
                  <input
                    type="range"
                    min="0"
                    max="0.60"
                    step="0.05"
                    value={calib.consistencyWeight}
                    onChange={(e) => setCalib(prev => ({ ...prev, consistencyWeight: parseFloat(e.target.value) }))}
                    style={{ width: '100%', accentColor: '#10B981', cursor: 'pointer' }}
                  />
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.65rem', color: 'var(--text-muted)', marginTop: '4px' }}>
                    <span>0% (Raw MTGI Only)</span>
                    <span>30% (Default)</span>
                    <span>60% (High Penalty)</span>
                  </div>
                </div>

                {/* 2. SR Surge Weight Slider */}
                <div style={{ padding: '16px 20px', background: '#FFFFFF', borderRadius: '16px', border: '1px solid rgba(15,23,42,0.08)', boxShadow: '0 2px 6px rgba(0,0,0,0.02)' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                    <div style={{ fontWeight: 800, fontSize: '0.85rem', color: 'var(--text-primary)' }}>Crisis Strike Rate Boost Weight (w_boost)</div>
                    <span className="mono-num" style={{ fontWeight: 900, color: 'var(--rr-pink)', fontSize: '1.05rem' }}>{calib.srDeltaWeight.toFixed(2)}x</span>
                  </div>
                  <div style={{ fontSize: '0.7rem', color: 'var(--text-secondary)', marginBottom: '12px' }}>
                    Multiplier applied to &Delta;SR (Pressure Strike Rate minus Baseline Strike Rate)
                  </div>
                  <input
                    type="range"
                    min="0.10"
                    max="0.70"
                    step="0.05"
                    value={calib.srDeltaWeight}
                    onChange={(e) => setCalib(prev => ({ ...prev, srDeltaWeight: parseFloat(e.target.value) }))}
                    style={{ width: '100%', accentColor: 'var(--rr-pink)', cursor: 'pointer' }}
                  />
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.65rem', color: 'var(--text-muted)', marginTop: '4px' }}>
                    <span>0.10x (Low Surge)</span>
                    <span>0.35x (Default)</span>
                    <span>0.70x (Extreme Surge)</span>
                  </div>
                </div>

                {/* 3. Economy Suppression Penalty */}
                <div style={{ padding: '16px 20px', background: '#FFFFFF', borderRadius: '16px', border: '1px solid rgba(15,23,42,0.08)', boxShadow: '0 2px 6px rgba(0,0,0,0.02)' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                    <div style={{ fontWeight: 800, fontSize: '0.85rem', color: 'var(--text-primary)' }}>Death Economy Suppression Weight</div>
                    <span className="mono-num" style={{ fontWeight: 900, color: 'var(--rr-blue)', fontSize: '1.05rem' }}>{calib.econWeight.toFixed(1)}x</span>
                  </div>
                  <div style={{ fontSize: '0.7rem', color: 'var(--text-secondary)', marginBottom: '12px' }}>
                    Penalizes bowler economy in death overs: 100 - [P_Econ × {calib.econWeight.toFixed(1)}]
                  </div>
                  <input
                    type="range"
                    min="4.0"
                    max="14.0"
                    step="0.5"
                    value={calib.econWeight}
                    onChange={(e) => setCalib(prev => ({ ...prev, econWeight: parseFloat(e.target.value) }))}
                    style={{ width: '100%', accentColor: 'var(--rr-blue)', cursor: 'pointer' }}
                  />
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.65rem', color: 'var(--text-muted)', marginTop: '4px' }}>
                    <span>4.0x (Forgiving)</span>
                    <span>8.0x (Default)</span>
                    <span>14.0x (Strict Death Lockdown)</span>
                  </div>
                </div>

                {/* 4. Min High-Tension Balls Sample Filter */}
                <div style={{ padding: '16px 20px', background: '#FFFFFF', borderRadius: '16px', border: '1px solid rgba(15,23,42,0.08)', boxShadow: '0 2px 6px rgba(0,0,0,0.02)' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                    <div style={{ fontWeight: 800, fontSize: '0.85rem', color: 'var(--text-primary)' }}>Sample Threshold Filter</div>
                    <span className="mono-num" style={{ fontWeight: 900, color: 'var(--rr-gold)', fontSize: '1.05rem' }}>Bat: {calib.minBatBalls}b · Bowl: {calib.minBowlBalls}b</span>
                  </div>
                  <div style={{ fontSize: '0.7rem', color: 'var(--text-secondary)', marginBottom: '12px' }}>
                    Minimum delivery sample size in high-pressure match situations
                  </div>
                  <div style={{ display: 'flex', gap: '10px' }}>
                    <div style={{ flex: 1 }}>
                      <label style={{ fontSize: '0.65rem', color: 'var(--text-muted)' }}>Batters Min Balls: {calib.minBatBalls}</label>
                      <input
                        type="range"
                        min="40"
                        max="140"
                        step="10"
                        value={calib.minBatBalls}
                        onChange={(e) => setCalib(prev => ({ ...prev, minBatBalls: parseInt(e.target.value) }))}
                        style={{ width: '100%', accentColor: 'var(--rr-gold)', cursor: 'pointer' }}
                      />
                    </div>
                    <div style={{ flex: 1 }}>
                      <label style={{ fontSize: '0.65rem', color: 'var(--text-muted)' }}>Bowlers Min Balls: {calib.minBowlBalls}</label>
                      <input
                        type="range"
                        min="40"
                        max="140"
                        step="10"
                        value={calib.minBowlBalls}
                        onChange={(e) => setCalib(prev => ({ ...prev, minBowlBalls: parseInt(e.target.value) }))}
                        style={{ width: '100%', accentColor: 'var(--rr-gold)', cursor: 'pointer' }}
                      />
                    </div>
                  </div>
                </div>

              </div>

            </div>
          )}"""

code = code.replace(old_settings_page, new_settings_page)

with open(APP_PATH, "w", encoding="utf-8") as f:
    f.write(code)

print("Dynamic calibration sliders successfully wired into App.tsx")
