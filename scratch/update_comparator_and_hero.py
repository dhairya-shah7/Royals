import sys

filepath = 'c:/Users/Dhairya/Desktop/Active/Rajasthan Royals/frontend/src/App.tsx'

with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update state to include compareRole, selectedBW1, selectedBW2
state_target = '''  const [selectedB1, setSelectedB1] = useState<string>("Naman Dhir");
  const [selectedB2, setSelectedB2] = useState<string>("Phil Salt");'''

state_replace = '''  const [selectedB1, setSelectedB1] = useState<string>("Naman Dhir");
  const [selectedB2, setSelectedB2] = useState<string>("Phil Salt");
  const [compareRole, setCompareRole] = useState<'bat' | 'bowl'>('bat');
  const [selectedBW1, setSelectedBW1] = useState<string>("Arshdeep Singh");
  const [selectedBW2, setSelectedBW2] = useState<string>("Matheesha Pathirana");'''

if state_target in content:
    content = content.replace(state_target, state_replace, 1)
    print("Added compareRole and selectedBW states")
else:
    print("Could not find state_target")

# 2. Update p1, p2 to also derive bw1, bw2
p_target = '''  const p1 = dynamicBatters.find(b => b.name === selectedB1) || dynamicBatters[0];
  const p2 = dynamicBatters.find(b => b.name === selectedB2) || dynamicBatters[1];'''

p_replace = '''  const p1 = dynamicBatters.find(b => b.name === selectedB1) || dynamicBatters[0];
  const p2 = dynamicBatters.find(b => b.name === selectedB2) || dynamicBatters[1];
  const bw1 = dynamicBowlers.find(b => b.name === selectedBW1) || dynamicBowlers[0];
  const bw2 = dynamicBowlers.find(b => b.name === selectedBW2) || dynamicBowlers[1];'''

if p_target in content:
    content = content.replace(p_target, p_replace, 1)
    print("Added bw1 and bw2")
else:
    print("Could not find p_target")

# 3. Update Hero Section buttons (smaller capsules, and 'Compare' instead of 'Compare Head-to-Head')
hero_target = '''                  {/* Actions & Metrics Row */}
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginTop: '28px' }}>
                    <div style={{ display: 'flex', gap: '12px' }}>
                      <button 
                        onClick={() => setActivePage('auction')}
                        style={{
                          display: 'flex',
                          alignItems: 'center',
                          gap: '8px',
                          padding: '10px 22px',
                          borderRadius: '999px',
                          background: '#FFFFFF',
                          color: 'var(--rr-blue)',
                          fontWeight: 800,
                          fontSize: '0.85rem',
                          border: 'none',
                          cursor: 'pointer',
                          boxShadow: '0 4px 14px rgba(0,0,0,0.15)'
                        }}
                      >
                        <Play size={14} fill="var(--rr-blue)" />
                        View War Room Plan
                      </button>

                      <button
                        onClick={() => setActivePage('matrix')}
                        style={{
                          padding: '10px 20px',
                          borderRadius: '999px',
                          background: 'rgba(255, 255, 255, 0.15)',
                          backdropFilter: 'blur(10px)',
                          color: '#FFFFFF',
                          fontWeight: 700,
                          fontSize: '0.85rem',
                          border: '1px solid rgba(255, 255, 255, 0.25)',
                          cursor: 'pointer'
                        }}
                      >
                        Compare Head-to-Head
                      </button>
                    </div>

                    <div style={{ display: 'flex', gap: '20px', textAlign: 'right' }}>'''

hero_replace = '''                  {/* Actions & Metrics Row */}
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginTop: '24px', flexWrap: 'wrap', gap: '14px' }}>
                    <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
                      <button 
                        onClick={() => setActivePage('auction')}
                        style={{
                          display: 'flex',
                          alignItems: 'center',
                          gap: '5px',
                          padding: '6px 14px',
                          borderRadius: '999px',
                          background: '#FFFFFF',
                          color: 'var(--rr-blue)',
                          fontWeight: 700,
                          fontSize: '0.76rem',
                          border: 'none',
                          cursor: 'pointer',
                          boxShadow: '0 2px 8px rgba(0,0,0,0.12)',
                          whiteSpace: 'nowrap'
                        }}
                      >
                        <Play size={11} fill="var(--rr-blue)" />
                        View War Room Plan
                      </button>

                      <button
                        onClick={() => setActivePage('matrix')}
                        style={{
                          padding: '6px 14px',
                          borderRadius: '999px',
                          background: 'rgba(255, 255, 255, 0.18)',
                          backdropFilter: 'blur(10px)',
                          color: '#FFFFFF',
                          fontWeight: 700,
                          fontSize: '0.76rem',
                          border: '1px solid rgba(255, 255, 255, 0.35)',
                          cursor: 'pointer',
                          whiteSpace: 'nowrap'
                        }}
                      >
                        Compare
                      </button>
                    </div>

                    <div style={{ display: 'flex', gap: '16px', textAlign: 'right', alignItems: 'center' }}>'''

if hero_target in content:
    content = content.replace(hero_target, hero_replace, 1)
    print("Updated Hero capsules to smaller size and 'Compare'")
else:
    print("Could not find hero_target")

# 4. Replace entire Matrix Comparison section (activePage === 'matrix') with the 2-capsule switch (Batters / Bowlers)
matrix_start = "{/* PAGE 2: MATRIX COMPARISON                                                 */}"
matrix_end = "{/* PAGE 3: WAR ROOM 2027 (SOLVING THE 4 SQUAD CONSTRUCTION FLAWS)"

idx1 = content.find(matrix_start)
idx2 = content.find(matrix_end)

if idx1 != -1 and idx2 != -1:
    matrix_code = '''{/* PAGE 2: MATRIX COMPARISON                                                 */}
          {/* ========================================================================= */}
          {activePage === 'matrix' && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '16px', flex: 1, overflowY: 'auto' }}>
              
              {/* Role Toggle Capsules */}
              <div style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                background: '#FFFFFF',
                borderRadius: '16px',
                padding: '12px 20px',
                border: '1px solid rgba(15, 23, 42, 0.06)',
                boxShadow: '0 2px 8px rgba(0,0,0,0.02)'
              }}>
                <div>
                  <div style={{ fontSize: '0.88rem', fontWeight: 800, color: 'var(--text-primary)' }}>
                    Head-to-Head Candidate Comparator
                  </div>
                  <div style={{ fontSize: '0.74rem', color: 'var(--text-secondary)' }}>
                    Select between Batters and Bowlers to compare high-tension clutch metrics.
                  </div>
                </div>

                {/* 2 Capsules for Batsman and Bowler */}
                <div style={{
                  display: 'flex',
                  gap: '6px',
                  background: 'rgba(15, 23, 42, 0.04)',
                  padding: '4px',
                  borderRadius: '999px',
                  border: '1px solid rgba(15, 23, 42, 0.06)'
                }}>
                  <button
                    onClick={() => setCompareRole('bat')}
                    style={{
                      padding: '6px 16px',
                      borderRadius: '999px',
                      border: 'none',
                      fontSize: '0.78rem',
                      fontWeight: 800,
                      cursor: 'pointer',
                      transition: 'all 0.18s ease',
                      background: compareRole === 'bat' ? 'var(--rr-pink)' : 'transparent',
                      color: compareRole === 'bat' ? '#FFFFFF' : 'var(--text-secondary)',
                      boxShadow: compareRole === 'bat' ? '0 2px 8px rgba(227, 0, 114, 0.25)' : 'none'
                    }}
                  >
                    🏏 Batsmen
                  </button>
                  <button
                    onClick={() => setCompareRole('bowl')}
                    style={{
                      padding: '6px 16px',
                      borderRadius: '999px',
                      border: 'none',
                      fontSize: '0.78rem',
                      fontWeight: 800,
                      cursor: 'pointer',
                      transition: 'all 0.18s ease',
                      background: compareRole === 'bowl' ? 'var(--rr-blue)' : 'transparent',
                      color: compareRole === 'bowl' ? '#FFFFFF' : 'var(--text-secondary)',
                      boxShadow: compareRole === 'bowl' ? '0 2px 8px rgba(0, 75, 141, 0.25)' : 'none'
                    }}
                  >
                    🎯 Bowlers
                  </button>
                </div>
              </div>

              {/* Selection Dropdowns */}
              {compareRole === 'bat' ? (
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
                  <div className="glass-card" style={{ padding: '16px 20px', borderLeft: '4px solid var(--rr-pink)' }}>
                    <label style={{ fontSize: '0.7rem', fontWeight: 800, color: 'var(--text-muted)', textTransform: 'uppercase' }}>
                      Candidate Alpha (Choose from {dynamicBatters.length} Batters)
                    </label>
                    <select
                      value={selectedB1}
                      onChange={(e) => setSelectedB1(e.target.value)}
                      style={{
                        width: '100%',
                        padding: '10px 14px',
                        borderRadius: '12px',
                        background: '#FFFFFF',
                        border: '1px solid rgba(15, 23, 42, 0.08)',
                        color: 'var(--text-primary)',
                        fontSize: '0.92rem',
                        fontWeight: 700,
                        marginTop: '6px',
                        outline: 'none'
                      }}
                    >
                      {dynamicBatters.map(b => (
                        <option key={b.name} value={b.name}>
                          #{b.rank} {b.name} — {b.team} ({b.role})
                        </option>
                      ))}
                    </select>
                  </div>

                  <div className="glass-card" style={{ padding: '16px 20px', borderLeft: '4px solid var(--rr-blue)' }}>
                    <label style={{ fontSize: '0.7rem', fontWeight: 800, color: 'var(--text-muted)', textTransform: 'uppercase' }}>
                      Candidate Beta (Choose from {dynamicBatters.length} Batters)
                    </label>
                    <select
                      value={selectedB2}
                      onChange={(e) => setSelectedB2(e.target.value)}
                      style={{
                        width: '100%',
                        padding: '10px 14px',
                        borderRadius: '12px',
                        background: '#FFFFFF',
                        border: '1px solid rgba(15, 23, 42, 0.08)',
                        color: 'var(--text-primary)',
                        fontSize: '0.92rem',
                        fontWeight: 700,
                        marginTop: '6px',
                        outline: 'none'
                      }}
                    >
                      {dynamicBatters.map(b => (
                        <option key={b.name} value={b.name}>
                          #{b.rank} {b.name} — {b.team} ({b.role})
                        </option>
                      ))}
                    </select>
                  </div>
                </div>
              ) : (
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
                  <div className="glass-card" style={{ padding: '16px 20px', borderLeft: '4px solid var(--rr-pink)' }}>
                    <label style={{ fontSize: '0.7rem', fontWeight: 800, color: 'var(--text-muted)', textTransform: 'uppercase' }}>
                      Candidate Alpha (Choose from {dynamicBowlers.length} Bowlers)
                    </label>
                    <select
                      value={selectedBW1}
                      onChange={(e) => setSelectedBW1(e.target.value)}
                      style={{
                        width: '100%',
                        padding: '10px 14px',
                        borderRadius: '12px',
                        background: '#FFFFFF',
                        border: '1px solid rgba(15, 23, 42, 0.08)',
                        color: 'var(--text-primary)',
                        fontSize: '0.92rem',
                        fontWeight: 700,
                        marginTop: '6px',
                        outline: 'none'
                      }}
                    >
                      {dynamicBowlers.map(bw => (
                        <option key={bw.name} value={bw.name}>
                          #{bw.rank} {bw.name} — {bw.team} ({bw.role})
                        </option>
                      ))}
                    </select>
                  </div>

                  <div className="glass-card" style={{ padding: '16px 20px', borderLeft: '4px solid var(--rr-blue)' }}>
                    <label style={{ fontSize: '0.7rem', fontWeight: 800, color: 'var(--text-muted)', textTransform: 'uppercase' }}>
                      Candidate Beta (Choose from {dynamicBowlers.length} Bowlers)
                    </label>
                    <select
                      value={selectedBW2}
                      onChange={(e) => setSelectedBW2(e.target.value)}
                      style={{
                        width: '100%',
                        padding: '10px 14px',
                        borderRadius: '12px',
                        background: '#FFFFFF',
                        border: '1px solid rgba(15, 23, 42, 0.08)',
                        color: 'var(--text-primary)',
                        fontSize: '0.92rem',
                        fontWeight: 700,
                        marginTop: '6px',
                        outline: 'none'
                      }}
                    >
                      {dynamicBowlers.map(bw => (
                        <option key={bw.name} value={bw.name}>
                          #{bw.rank} {bw.name} — {bw.team} ({bw.role})
                        </option>
                      ))}
                    </select>
                  </div>
                </div>
              )}

              {/* BATTER COMPARISON VIEW */}
              {compareRole === 'bat' && p1 && p2 && (
                <>
                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
                    {/* Alpha Batter Card */}
                    <div className="glass-card" style={{ padding: '22px' }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '14px' }}>
                        <div>
                          <span style={{ fontSize: '0.7rem', fontWeight: 800, color: 'var(--rr-pink)', background: 'var(--rr-pink-light)', padding: '3px 10px', borderRadius: '999px' }}>
                            RANK #{p1.rank}
                          </span>
                          <h3 style={{ margin: '8px 0 2px 0', fontSize: '1.35rem', fontWeight: 800, color: 'var(--text-primary)' }}>{p1.name}</h3>
                          <p style={{ margin: 0, fontSize: '0.8rem', color: 'var(--text-secondary)' }}>{p1.role} · {p1.team}</p>
                        </div>
                        <div style={{ textAlign: 'right' }}>
                          <div className="mono-num" style={{ fontSize: '1.75rem', fontWeight: 900, color: 'var(--rr-pink)' }}>{p1.clutchScore.toFixed(1)}</div>
                          <div style={{ fontSize: '0.65rem', color: 'var(--text-muted)', fontWeight: 700 }}>CLUTCH SCORE</div>
                        </div>
                      </div>

                      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '10px', background: 'rgba(15, 23, 42, 0.03)', padding: '12px 14px', borderRadius: '14px', marginBottom: '14px' }}>
                        <div>
                          <div style={{ fontSize: '0.65rem', color: 'var(--text-muted)' }}>PRE-SR</div>
                          <div className="mono-num" style={{ fontSize: '1.1rem', fontWeight: 800, color: 'var(--text-primary)' }}>{p1.pSR.toFixed(1)}</div>
                        </div>
                        <div>
                          <div style={{ fontSize: '0.65rem', color: 'var(--text-muted)' }}>BOOST</div>
                          <div className="mono-num" style={{ fontSize: '1.1rem', fontWeight: 800, color: '#10B981' }}>+{p1.deltaSR.toFixed(1)}</div>
                        </div>
                        <div>
                          <div style={{ fontSize: '0.65rem', color: 'var(--text-muted)' }}>CONSIST</div>
                          <div className="mono-num" style={{ fontSize: '1.1rem', fontWeight: 800, color: 'var(--rr-pink)' }}>{p1.consistencyPct !== undefined ? `${p1.consistencyPct.toFixed(0)}%` : '80%'}</div>
                        </div>
                        <div>
                          <div style={{ fontSize: '0.65rem', color: 'var(--text-muted)' }}>BNDRY %</div>
                          <div className="mono-num" style={{ fontSize: '1.1rem', fontWeight: 800, color: 'var(--text-primary)' }}>{p1.bndPct.toFixed(1)}%</div>
                        </div>
                      </div>

                      <div>
                        <h5 style={{ margin: '0 0 6px 0', fontSize: '0.75rem', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase' }}>Key Player Strengths</h5>
                        <ul style={{ margin: 0, paddingLeft: '18px', fontSize: '0.8rem', color: 'var(--text-secondary)', display: 'flex', flexDirection: 'column', gap: '4px' }}>
                          {p1.strengths.map((s: string, i: number) => <li key={i}>{s}</li>)}
                        </ul>
                      </div>
                    </div>

                    {/* Beta Batter Card */}
                    <div className="glass-card" style={{ padding: '22px' }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '14px' }}>
                        <div>
                          <span style={{ fontSize: '0.7rem', fontWeight: 800, color: 'var(--rr-blue)', background: 'var(--rr-blue-light)', padding: '3px 10px', borderRadius: '999px' }}>
                            RANK #{p2.rank}
                          </span>
                          <h3 style={{ margin: '8px 0 2px 0', fontSize: '1.35rem', fontWeight: 800, color: 'var(--text-primary)' }}>{p2.name}</h3>
                          <p style={{ margin: 0, fontSize: '0.8rem', color: 'var(--text-secondary)' }}>{p2.role} · {p2.team}</p>
                        </div>
                        <div style={{ textAlign: 'right' }}>
                          <div className="mono-num" style={{ fontSize: '1.75rem', fontWeight: 900, color: 'var(--rr-blue)' }}>{p2.clutchScore.toFixed(1)}</div>
                          <div style={{ fontSize: '0.65rem', color: 'var(--text-muted)', fontWeight: 700 }}>CLUTCH SCORE</div>
                        </div>
                      </div>

                      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '10px', background: 'rgba(15, 23, 42, 0.03)', padding: '12px 14px', borderRadius: '14px', marginBottom: '14px' }}>
                        <div>
                          <div style={{ fontSize: '0.65rem', color: 'var(--text-muted)' }}>PRE-SR</div>
                          <div className="mono-num" style={{ fontSize: '1.1rem', fontWeight: 800, color: 'var(--text-primary)' }}>{p2.pSR.toFixed(1)}</div>
                        </div>
                        <div>
                          <div style={{ fontSize: '0.65rem', color: 'var(--text-muted)' }}>BOOST</div>
                          <div className="mono-num" style={{ fontSize: '1.1rem', fontWeight: 800, color: '#10B981' }}>+{p2.deltaSR.toFixed(1)}</div>
                        </div>
                        <div>
                          <div style={{ fontSize: '0.65rem', color: 'var(--text-muted)' }}>CONSIST</div>
                          <div className="mono-num" style={{ fontSize: '1.1rem', fontWeight: 800, color: 'var(--rr-blue)' }}>{p2.consistencyPct !== undefined ? `${p2.consistencyPct.toFixed(0)}%` : '80%'}</div>
                        </div>
                        <div>
                          <div style={{ fontSize: '0.65rem', color: 'var(--text-muted)' }}>BNDRY %</div>
                          <div className="mono-num" style={{ fontSize: '1.1rem', fontWeight: 800, color: 'var(--text-primary)' }}>{p2.bndPct.toFixed(1)}%</div>
                        </div>
                      </div>

                      <div>
                        <h5 style={{ margin: '0 0 6px 0', fontSize: '0.75rem', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase' }}>Key Player Strengths</h5>
                        <ul style={{ margin: 0, paddingLeft: '18px', fontSize: '0.8rem', color: 'var(--text-secondary)', display: 'flex', flexDirection: 'column', gap: '4px' }}>
                          {p2.strengths.map((s: string, i: number) => <li key={i}>{s}</li>)}
                        </ul>
                      </div>
                    </div>
                  </div>

                  {/* Direct Proportion Meters for Batters */}
                  <div className="glass-card" style={{ padding: '20px 24px' }}>
                    <h4 style={{ margin: '0 0 14px 0', fontSize: '0.92rem', fontWeight: 800, color: 'var(--text-primary)' }}>Direct Metric Comparison</h4>
                    {[
                      { label: 'Pressure Strike Rate', v1: p1.pSR, v2: p2.pSR },
                      { label: 'Pressure Boost vs Baseline', v1: p1.deltaSR, v2: p2.deltaSR },
                      { label: 'Match Consistency Rate (C_rate)', v1: p1.consistencyPct ?? 80, v2: p2.consistencyPct ?? 80 },
                      { label: 'Boundary %', v1: p1.bndPct, v2: p2.bndPct },
                      { label: 'Overall Clutch Score (MTGI × R)', v1: p1.clutchScore, v2: p2.clutchScore }
                    ].map((m, i) => (
                      <div key={i} style={{ marginBottom: '12px' }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.76rem', fontWeight: 700, marginBottom: '5px' }}>
                          <span style={{ color: 'var(--rr-pink)' }}>{p1.name}: {m.v1.toFixed(1)}</span>
                          <span style={{ color: 'var(--text-muted)' }}>{m.label}</span>
                          <span style={{ color: 'var(--rr-blue)' }}>{p2.name}: {m.v2.toFixed(1)}</span>
                        </div>
                        <div style={{ display: 'flex', height: '6px', background: 'rgba(15, 23, 42, 0.06)', borderRadius: '999px', overflow: 'hidden' }}>
                          <div style={{ width: `${(Math.max(0, m.v1) / (Math.max(0, m.v1) + Math.max(0, m.v2) || 1)) * 100}%`, background: 'var(--rr-pink)' }} />
                          <div style={{ width: `${(Math.max(0, m.v2) / (Math.max(0, m.v1) + Math.max(0, m.v2) || 1)) * 100}%`, background: 'var(--rr-blue)' }} />
                        </div>
                      </div>
                    ))}
                  </div>
                </>
              )}

              {/* BOWLER COMPARISON VIEW */}
              {compareRole === 'bowl' && bw1 && bw2 && (
                <>
                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
                    {/* Alpha Bowler Card */}
                    <div className="glass-card" style={{ padding: '22px' }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '14px' }}>
                        <div>
                          <span style={{ fontSize: '0.7rem', fontWeight: 800, color: 'var(--rr-pink)', background: 'var(--rr-pink-light)', padding: '3px 10px', borderRadius: '999px' }}>
                            RANK #{bw1.rank}
                          </span>
                          <h3 style={{ margin: '8px 0 2px 0', fontSize: '1.35rem', fontWeight: 800, color: 'var(--text-primary)' }}>{bw1.name}</h3>
                          <p style={{ margin: 0, fontSize: '0.8rem', color: 'var(--text-secondary)' }}>{bw1.role} · {bw1.team}</p>
                        </div>
                        <div style={{ textAlign: 'right' }}>
                          <div className="mono-num" style={{ fontSize: '1.75rem', fontWeight: 900, color: 'var(--rr-pink)' }}>{bw1.clutchScore.toFixed(1)}</div>
                          <div style={{ fontSize: '0.65rem', color: 'var(--text-muted)', fontWeight: 700 }}>CLUTCH SCORE</div>
                        </div>
                      </div>

                      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '10px', background: 'rgba(15, 23, 42, 0.03)', padding: '12px 14px', borderRadius: '14px', marginBottom: '14px' }}>
                        <div>
                          <div style={{ fontSize: '0.65rem', color: 'var(--text-muted)' }}>PRE-ECON</div>
                          <div className="mono-num" style={{ fontSize: '1.1rem', fontWeight: 800, color: 'var(--text-primary)' }}>{bw1.pEcon.toFixed(2)}</div>
                        </div>
                        <div>
                          <div style={{ fontSize: '0.65rem', color: 'var(--text-muted)' }}>PRESSURE WKTS</div>
                          <div className="mono-num" style={{ fontSize: '1.1rem', fontWeight: 800, color: '#10B981' }}>{bw1.pWkts}</div>
                        </div>
                        <div>
                          <div style={{ fontSize: '0.65rem', color: 'var(--text-muted)' }}>CONSIST</div>
                          <div className="mono-num" style={{ fontSize: '1.1rem', fontWeight: 800, color: 'var(--rr-pink)' }}>{bw1.consistencyPct !== undefined ? `${bw1.consistencyPct.toFixed(0)}%` : '75%'}</div>
                        </div>
                        <div>
                          <div style={{ fontSize: '0.65rem', color: 'var(--text-muted)' }}>DOT %</div>
                          <div className="mono-num" style={{ fontSize: '1.1rem', fontWeight: 800, color: 'var(--text-primary)' }}>{bw1.dotPct.toFixed(1)}%</div>
                        </div>
                      </div>

                      <div>
                        <h5 style={{ margin: '0 0 6px 0', fontSize: '0.75rem', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase' }}>Key Player Strengths</h5>
                        <ul style={{ margin: 0, paddingLeft: '18px', fontSize: '0.8rem', color: 'var(--text-secondary)', display: 'flex', flexDirection: 'column', gap: '4px' }}>
                          {bw1.strengths.map((s: string, i: number) => <li key={i}>{s}</li>)}
                        </ul>
                      </div>
                    </div>

                    {/* Beta Bowler Card */}
                    <div className="glass-card" style={{ padding: '22px' }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '14px' }}>
                        <div>
                          <span style={{ fontSize: '0.7rem', fontWeight: 800, color: 'var(--rr-blue)', background: 'var(--rr-blue-light)', padding: '3px 10px', borderRadius: '999px' }}>
                            RANK #{bw2.rank}
                          </span>
                          <h3 style={{ margin: '8px 0 2px 0', fontSize: '1.35rem', fontWeight: 800, color: 'var(--text-primary)' }}>{bw2.name}</h3>
                          <p style={{ margin: 0, fontSize: '0.8rem', color: 'var(--text-secondary)' }}>{bw2.role} · {bw2.team}</p>
                        </div>
                        <div style={{ textAlign: 'right' }}>
                          <div className="mono-num" style={{ fontSize: '1.75rem', fontWeight: 900, color: 'var(--rr-blue)' }}>{bw2.clutchScore.toFixed(1)}</div>
                          <div style={{ fontSize: '0.65rem', color: 'var(--text-muted)', fontWeight: 700 }}>CLUTCH SCORE</div>
                        </div>
                      </div>

                      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '10px', background: 'rgba(15, 23, 42, 0.03)', padding: '12px 14px', borderRadius: '14px', marginBottom: '14px' }}>
                        <div>
                          <div style={{ fontSize: '0.65rem', color: 'var(--text-muted)' }}>PRE-ECON</div>
                          <div className="mono-num" style={{ fontSize: '1.1rem', fontWeight: 800, color: 'var(--text-primary)' }}>{bw2.pEcon.toFixed(2)}</div>
                        </div>
                        <div>
                          <div style={{ fontSize: '0.65rem', color: 'var(--text-muted)' }}>PRESSURE WKTS</div>
                          <div className="mono-num" style={{ fontSize: '1.1rem', fontWeight: 800, color: '#10B981' }}>{bw2.pWkts}</div>
                        </div>
                        <div>
                          <div style={{ fontSize: '0.65rem', color: 'var(--text-muted)' }}>CONSIST</div>
                          <div className="mono-num" style={{ fontSize: '1.1rem', fontWeight: 800, color: 'var(--rr-blue)' }}>{bw2.consistencyPct !== undefined ? `${bw2.consistencyPct.toFixed(0)}%` : '75%'}</div>
                        </div>
                        <div>
                          <div style={{ fontSize: '0.65rem', color: 'var(--text-muted)' }}>DOT %</div>
                          <div className="mono-num" style={{ fontSize: '1.1rem', fontWeight: 800, color: 'var(--text-primary)' }}>{bw2.dotPct.toFixed(1)}%</div>
                        </div>
                      </div>

                      <div>
                        <h5 style={{ margin: '0 0 6px 0', fontSize: '0.75rem', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase' }}>Key Player Strengths</h5>
                        <ul style={{ margin: 0, paddingLeft: '18px', fontSize: '0.8rem', color: 'var(--text-secondary)', display: 'flex', flexDirection: 'column', gap: '4px' }}>
                          {bw2.strengths.map((s: string, i: number) => <li key={i}>{s}</li>)}
                        </ul>
                      </div>
                    </div>
                  </div>

                  {/* Direct Proportion Meters for Bowlers */}
                  <div className="glass-card" style={{ padding: '20px 24px' }}>
                    <h4 style={{ margin: '0 0 14px 0', fontSize: '0.92rem', fontWeight: 800, color: 'var(--text-primary)' }}>Direct Metric Comparison</h4>
                    {[
                      { label: 'Pressure Economy (Lower is Better)', v1: bw1.pEcon, v2: bw2.pEcon, invert: true },
                      { label: 'Pressure Wickets Taken', v1: bw1.pWkts, v2: bw2.pWkts },
                      { label: 'Match Consistency Rate (C_rate)', v1: bw1.consistencyPct ?? 75, v2: bw2.consistencyPct ?? 75 },
                      { label: 'Dot Ball % under Pressure', v1: bw1.dotPct, v2: bw2.dotPct },
                      { label: 'Overall Clutch Score (MTGI × R)', v1: bw1.clutchScore, v2: bw2.clutchScore }
                    ].map((m, i) => {
                      const w1 = m.invert ? (m.v2 / (m.v1 + m.v2 || 1)) * 100 : (m.v1 / (m.v1 + m.v2 || 1)) * 100;
                      const w2 = 100 - w1;
                      return (
                        <div key={i} style={{ marginBottom: '12px' }}>
                          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.76rem', fontWeight: 700, marginBottom: '5px' }}>
                            <span style={{ color: 'var(--rr-pink)' }}>{bw1.name}: {m.v1.toFixed(m.invert ? 2 : 1)}</span>
                            <span style={{ color: 'var(--text-muted)' }}>{m.label}</span>
                            <span style={{ color: 'var(--rr-blue)' }}>{bw2.name}: {m.v2.toFixed(m.invert ? 2 : 1)}</span>
                          </div>
                          <div style={{ display: 'flex', height: '6px', background: 'rgba(15, 23, 42, 0.06)', borderRadius: '999px', overflow: 'hidden' }}>
                            <div style={{ width: `${w1}%`, background: 'var(--rr-pink)' }} />
                            <div style={{ width: `${w2}%`, background: 'var(--rr-blue)' }} />
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </>
              )}
            </div>
          )}

          '''
    content = content[:idx1] + matrix_code + content[idx2:]
    print("Replaced Matrix page with 2-capsule role toggle and full batter/bowler comparators")
else:
    print(f"Could not find matrix section markers (idx1={idx1}, idx2={idx2})")

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)
print("Finished writing App.tsx")
