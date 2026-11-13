import re

filepath = 'c:/Users/Dhairya/Desktop/Active/Rajasthan Royals/frontend/src/App.tsx'

with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. State replacement:
calib_state_pattern = re.compile(r'  const \[calib, setCalib\] = useState\(\{.*?\}\);', re.DOTALL)

new_calib_state = '''  interface CalibrationParams {
    minBatBalls: number;
    minBowlBalls: number;
    consistencyWeight: number;
    srDeltaWeight: number;
    econWeight: number;
  }

  const DEFAULT_CALIB: CalibrationParams = {
    minBatBalls: 80,
    minBowlBalls: 90,
    consistencyWeight: 0.30,
    srDeltaWeight: 0.35,
    econWeight: 8.0
  };

  const [activeCalib, setActiveCalib] = useState<CalibrationParams>(() => {
    try {
      const saved = localStorage.getItem('rr_active_calib');
      if (saved) return JSON.parse(saved);
    } catch (e) {}
    return DEFAULT_CALIB;
  });

  const [pendingCalib, setPendingCalib] = useState<CalibrationParams>(() => {
    try {
      const saved = localStorage.getItem('rr_active_calib');
      if (saved) return JSON.parse(saved);
    } catch (e) {}
    return DEFAULT_CALIB;
  });

  const [applyFeedback, setApplyFeedback] = useState<string | null>(null);

  const hasUnappliedChanges = useMemo(() => {
    return (
      pendingCalib.minBatBalls !== activeCalib.minBatBalls ||
      pendingCalib.minBowlBalls !== activeCalib.minBowlBalls ||
      pendingCalib.consistencyWeight !== activeCalib.consistencyWeight ||
      pendingCalib.srDeltaWeight !== activeCalib.srDeltaWeight ||
      pendingCalib.econWeight !== activeCalib.econWeight
    );
  }, [pendingCalib, activeCalib]);'''

if calib_state_pattern.search(content):
    content = calib_state_pattern.sub(new_calib_state, content, count=1)
    print("Successfully replaced calib state with activeCalib, pendingCalib, hasUnappliedChanges")
else:
    print("Could not find calib state pattern")

# 2. Make sure dynamicBatters and dynamicBowlers use activeCalib
content = content.replace('calib.minBatBalls', 'activeCalib.minBatBalls')
content = content.replace('calib.srDeltaWeight', 'activeCalib.srDeltaWeight')
content = content.replace('calib.consistencyWeight', 'activeCalib.consistencyWeight')
content = content.replace('calib.minBowlBalls', 'activeCalib.minBowlBalls')
content = content.replace('calib.econWeight', 'activeCalib.econWeight')
content = content.replace('}, [calib]);', '}, [activeCalib]);')

# 3. Clean human-friendly text
content = content.replace(
    '<span>Dual Engine: MTGI × C_rate Reliability</span>',
    '<span>High-Pressure Performance & Consistency Engine</span>'
)
content = content.replace(
    'Dual Engine: MTGI × C_rate Reliability',
    'High-Pressure Performance & Consistency Engine'
)
content = content.replace(
    'based strictly on our 200,999-ball MTGI dataset.',
    'based strictly on our 200,999-ball high-pressure dataset.'
)
content = content.replace(
    'alongside the comprehensive MTGI Methodology PDF!',
    'alongside the comprehensive Methodology Report PDF!'
)
content = content.replace(
    "{ label: 'Match Consistency Rate (C_rate)', v1: p1.consistencyPct ?? 80, v2: p2.consistencyPct ?? 80 }",
    "{ label: 'Match Consistency Rate', v1: p1.consistencyPct ?? 80, v2: p2.consistencyPct ?? 80 }"
)
content = content.replace(
    "{ label: 'Overall Clutch Score (MTGI × R)', v1: p1.clutchScore, v2: p2.clutchScore }",
    "{ label: 'Overall Clutch Rating', v1: p1.clutchScore, v2: p2.clutchScore }"
)
content = content.replace(
    "{ label: 'Match Consistency Rate (C_rate)', v1: bw1.consistencyPct ?? 75, v2: bw2.consistencyPct ?? 75 }",
    "{ label: 'Match Consistency Rate', v1: bw1.consistencyPct ?? 75, v2: bw2.consistencyPct ?? 75 }"
)
content = content.replace(
    "{ label: 'Overall Clutch Score (MTGI × R)', v1: bw1.clutchScore, v2: bw2.clutchScore }",
    "{ label: 'Overall Clutch Rating', v1: bw1.clutchScore, v2: bw2.clutchScore }"
)
content = content.replace('Raw MTGI: {pRawMTGI}', 'Base Score: {pRawMTGI}')
content = content.replace('Consistency (C_rate)', 'Match Consistency')
content = content.replace('Reliability: {pReliability}x', 'Consistency Factor: {pReliability}x')
content = content.replace(
    'Clutch = MTGI ({pRawMTGI}) × [0.70 + 0.30 × ({pConsist.toFixed(0)}% / 100)] = {selectedPlayerModal.clutchScore.toFixed(1)}',
    'Base Score ({pRawMTGI}) × Consistency Factor ({pReliability}x) = {selectedPlayerModal.clutchScore.toFixed(1)} Clutch Rating'
)
content = content.replace('Dual-Engine Formula:', 'Scoring Breakdown:')

# 4. Replace Settings page with clean human UI and "Apply Changes" button
idx_settings = content.find("activePage === 'settings'")
if idx_settings != -1:
    idx_settings_start = content.rfind("{/* ====", 0, idx_settings)
    if idx_settings_start == -1:
        idx_settings_start = idx_settings
    
    idx_settings_close = content.find("          )}", idx_settings)
    idx_settings_end = idx_settings_close + len("          )}")

    new_settings_page = '''{/* ========================================================================= */}
          {/* PAGE 5: SETTINGS & CALIBRATIONS                                           */}
          {/* ========================================================================= */}
          {activePage === 'settings' && (
            <div className="glass-card" style={{ padding: '26px 30px', flex: 1, overflowY: 'auto' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '20px', flexWrap: 'wrap', gap: '14px' }}>
                <div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <span style={{ fontSize: '1.2rem' }}>🎛️</span>
                    <h3 style={{ margin: 0, fontSize: '1.25rem', fontWeight: 900, color: 'var(--text-primary)' }}>
                      Interactive War Room Calibration
                    </h3>
                  </div>
                  <p style={{ margin: '4px 0 0 0', fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
                    Customize evaluation weights and delivery thresholds below. Click "Apply Changes" to recalculate all rankings and player scores across the entire platform.
                  </p>
                </div>

                <div style={{ display: 'flex', alignItems: 'center', gap: '10px', flexWrap: 'wrap' }}>
                  {hasUnappliedChanges && (
                    <span style={{
                      fontSize: '0.72rem',
                      fontWeight: 800,
                      padding: '4px 10px',
                      borderRadius: '999px',
                      background: '#FEF3C7',
                      color: '#B45309',
                      border: '1px solid #FDE68A'
                    }}>
                      ● Unapplied Changes
                    </span>
                  )}
                  
                  <button
                    onClick={() => {
                      setPendingCalib(DEFAULT_CALIB);
                      setActiveCalib(DEFAULT_CALIB);
                      try {
                        localStorage.setItem('rr_active_calib', JSON.stringify(DEFAULT_CALIB));
                      } catch (e) {}
                      setApplyFeedback("Restored default calibration across the entire platform!");
                      setTimeout(() => setApplyFeedback(null), 3500);
                    }}
                    style={{
                      padding: '7px 16px',
                      borderRadius: '999px',
                      background: '#FFFFFF',
                      border: '1px solid rgba(15, 23, 42, 0.14)',
                      fontSize: '0.76rem',
                      fontWeight: 700,
                      color: 'var(--text-secondary)',
                      cursor: 'pointer',
                      boxShadow: '0 1px 3px rgba(0,0,0,0.05)',
                      transition: 'all 0.15s ease'
                    }}
                  >
                    Reset to Defaults
                  </button>

                  <button
                    onClick={() => {
                      setActiveCalib({ ...pendingCalib });
                      try {
                        localStorage.setItem('rr_active_calib', JSON.stringify(pendingCalib));
                      } catch (e) {}
                      setApplyFeedback("Changes applied! All rankings, leaderboards, and prospect scores have been updated across the entire platform.");
                      setTimeout(() => setApplyFeedback(null), 4000);
                    }}
                    style={{
                      padding: '7px 18px',
                      borderRadius: '999px',
                      background: hasUnappliedChanges ? 'var(--rr-pink)' : 'var(--rr-blue)',
                      border: 'none',
                      fontSize: '0.76rem',
                      fontWeight: 800,
                      color: '#FFFFFF',
                      cursor: 'pointer',
                      boxShadow: hasUnappliedChanges ? '0 3px 12px rgba(227, 0, 114, 0.35)' : '0 2px 8px rgba(0, 75, 141, 0.25)',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '6px',
                      transition: 'all 0.15s ease'
                    }}
                  >
                    <CheckCircle2 size={13} />
                    Apply Changes
                  </button>
                </div>
              </div>

              {/* Feedback Banner */}
              {applyFeedback && (
                <div style={{
                  padding: '12px 18px',
                  borderRadius: '12px',
                  background: 'rgba(16, 185, 129, 0.12)',
                  border: '1px solid #10B981',
                  color: '#065F46',
                  fontSize: '0.82rem',
                  fontWeight: 800,
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px',
                  marginBottom: '16px'
                }}>
                  <CheckCircle2 size={16} color="#059669" />
                  <span>{applyFeedback}</span>
                </div>
              )}

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
                  <div style={{ fontSize: '0.72rem', fontWeight: 800, color: 'var(--rr-pink)', textTransform: 'uppercase' }}>
                    Active Platform Leaders (Currently Applied)
                  </div>
                  <div style={{ fontSize: '1.05rem', fontWeight: 900, color: 'var(--text-primary)' }}>
                    🏏 Batter: <span style={{ color: 'var(--rr-pink)' }}>{dynamicBatters[0]?.name}</span> ({dynamicBatters[0]?.clutchScore}) · 🎯 Bowler: <span style={{ color: 'var(--rr-blue)' }}>{dynamicBowlers[0]?.name}</span> ({dynamicBowlers[0]?.clutchScore})
                  </div>
                  {hasUnappliedChanges && previewBatters.length > 0 && previewBowlers.length > 0 && (
                    <div style={{ fontSize: '0.8rem', fontWeight: 700, color: '#D97706', marginTop: '4px' }}>
                      Pending Preview: 🏏 {previewBatters[0]?.name} ({previewBatters[0]?.clutchScore}) · 🎯 {previewBowlers[0]?.name} ({previewBowlers[0]?.clutchScore})
                      <span style={{ fontWeight: 600, marginLeft: '6px', fontSize: '0.74rem', color: 'var(--text-secondary)' }}>(Click "Apply Changes" to activate)</span>
                    </div>
                  )}
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
                    <div style={{ fontWeight: 800, fontSize: '0.85rem', color: 'var(--text-primary)' }}>Match Consistency Weight</div>
                    <span className="mono-num" style={{ fontWeight: 900, color: '#059669', fontSize: '1.05rem' }}>{Math.round(pendingCalib.consistencyWeight * 100)}%</span>
                  </div>
                  <div style={{ fontSize: '0.72rem', color: 'var(--text-secondary)', marginBottom: '12px' }}>
                    Rewards players who repeatedly deliver match-winning performances across multiple matches.
                  </div>
                  <input
                    type="range"
                    min="0"
                    max="0.60"
                    step="0.05"
                    value={pendingCalib.consistencyWeight}
                    onChange={(e) => setPendingCalib(prev => ({ ...prev, consistencyWeight: parseFloat(e.target.value) }))}
                    style={{ width: '100%', accentColor: '#10B981', cursor: 'pointer' }}
                  />
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.65rem', color: 'var(--text-muted)', marginTop: '4px' }}>
                    <span>0% (Raw Numbers)</span>
                    <span>30% (Standard)</span>
                    <span>60% (High Consistency Focus)</span>
                  </div>
                </div>

                {/* 2. SR Surge Weight Slider */}
                <div style={{ padding: '16px 20px', background: '#FFFFFF', borderRadius: '16px', border: '1px solid rgba(15,23,42,0.08)', boxShadow: '0 2px 6px rgba(0,0,0,0.02)' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                    <div style={{ fontWeight: 800, fontSize: '0.85rem', color: 'var(--text-primary)' }}>Pressure Strike Rate Boost</div>
                    <span className="mono-num" style={{ fontWeight: 900, color: 'var(--rr-pink)', fontSize: '1.05rem' }}>{pendingCalib.srDeltaWeight.toFixed(2)}x</span>
                  </div>
                  <div style={{ fontSize: '0.72rem', color: 'var(--text-secondary)', marginBottom: '12px' }}>
                    Rewards batsmen who accelerate their scoring speed under pressure compared to normal play.
                  </div>
                  <input
                    type="range"
                    min="0.10"
                    max="0.70"
                    step="0.05"
                    value={pendingCalib.srDeltaWeight}
                    onChange={(e) => setPendingCalib(prev => ({ ...prev, srDeltaWeight: parseFloat(e.target.value) }))}
                    style={{ width: '100%', accentColor: 'var(--rr-pink)', cursor: 'pointer' }}
                  />
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.65rem', color: 'var(--text-muted)', marginTop: '4px' }}>
                    <span>0.10x (Low Boost)</span>
                    <span>0.35x (Standard)</span>
                    <span>0.70x (High Boost)</span>
                  </div>
                </div>

                {/* 3. Economy Suppression Penalty */}
                <div style={{ padding: '16px 20px', background: '#FFFFFF', borderRadius: '16px', border: '1px solid rgba(15,23,42,0.08)', boxShadow: '0 2px 6px rgba(0,0,0,0.02)' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                    <div style={{ fontWeight: 800, fontSize: '0.85rem', color: 'var(--text-primary)' }}>Death Overs Economy Weight</div>
                    <span className="mono-num" style={{ fontWeight: 900, color: 'var(--rr-blue)', fontSize: '1.05rem' }}>{pendingCalib.econWeight.toFixed(1)}x</span>
                  </div>
                  <div style={{ fontSize: '0.72rem', color: 'var(--text-secondary)', marginBottom: '12px' }}>
                    Places high value on bowlers who restrict runs and take wickets in the final overs.
                  </div>
                  <input
                    type="range"
                    min="4.0"
                    max="14.0"
                    step="0.5"
                    value={pendingCalib.econWeight}
                    onChange={(e) => setPendingCalib(prev => ({ ...prev, econWeight: parseFloat(e.target.value) }))}
                    style={{ width: '100%', accentColor: 'var(--rr-blue)', cursor: 'pointer' }}
                  />
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.65rem', color: 'var(--text-muted)', marginTop: '4px' }}>
                    <span>4.0x (Moderate)</span>
                    <span>8.0x (Standard)</span>
                    <span>14.0x (Strict Lockdown)</span>
                  </div>
                </div>

                {/* 4. Min High-Tension Balls Sample Filter */}
                <div style={{ padding: '16px 20px', background: '#FFFFFF', borderRadius: '16px', border: '1px solid rgba(15,23,42,0.08)', boxShadow: '0 2px 6px rgba(0,0,0,0.02)' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                    <div style={{ fontWeight: 800, fontSize: '0.85rem', color: 'var(--text-primary)' }}>Minimum Deliveries Filter</div>
                    <span className="mono-num" style={{ fontWeight: 900, color: 'var(--rr-gold)', fontSize: '1.05rem' }}>Bat: {pendingCalib.minBatBalls}b · Bowl: {pendingCalib.minBowlBalls}b</span>
                  </div>
                  <div style={{ fontSize: '0.72rem', color: 'var(--text-secondary)', marginBottom: '12px' }}>
                    Minimum balls faced or bowled in crunch moments to qualify for the rankings.
                  </div>
                  <div style={{ display: 'flex', gap: '10px' }}>
                    <div style={{ flex: 1 }}>
                      <label style={{ fontSize: '0.65rem', color: 'var(--text-muted)' }}>Batters Minimum Balls: {pendingCalib.minBatBalls}</label>
                      <input
                        type="range"
                        min="40"
                        max="140"
                        step="10"
                        value={pendingCalib.minBatBalls}
                        onChange={(e) => setPendingCalib(prev => ({ ...prev, minBatBalls: parseInt(e.target.value) }))}
                        style={{ width: '100%', accentColor: 'var(--rr-gold)', cursor: 'pointer' }}
                      />
                    </div>
                    <div style={{ flex: 1 }}>
                      <label style={{ fontSize: '0.65rem', color: 'var(--text-muted)' }}>Bowlers Minimum Balls: {pendingCalib.minBowlBalls}</label>
                      <input
                        type="range"
                        min="40"
                        max="140"
                        step="10"
                        value={pendingCalib.minBowlBalls}
                        onChange={(e) => setPendingCalib(prev => ({ ...prev, minBowlBalls: parseInt(e.target.value) }))}
                        style={{ width: '100%', accentColor: 'var(--rr-gold)', cursor: 'pointer' }}
                      />
                    </div>
                  </div>
                </div>

              </div>
            </div>
          )}'''

    content = content[:idx_settings_start] + new_settings_page + content[idx_settings_end:]
    print("Settings page fully replaced with human-readable cards and Apply Changes button")
else:
    print("Could not find settings page")

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)

print("Saved App.tsx successfully")
