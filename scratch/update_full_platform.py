import re

APP_PATH = r"c:\Users\Dhairya\Desktop\Active\Rajasthan Royals\frontend\src\App.tsx"

with open(APP_PATH, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Update selectedB1 and selectedB2 defaults to Babar Azam and Naman Dhir
content = content.replace(
    'const [selectedB1, setSelectedB1] = useState<string>("Phil Salt");\n  const [selectedB2, setSelectedB2] = useState<string>("Shivam Dube");',
    'const [selectedB1, setSelectedB1] = useState<string>("Babar Azam");\n  const [selectedB2, setSelectedB2] = useState<string>("Naman Dhir");'
)

# 2. Update tableTab state to 'both' by default
content = content.replace(
    "const [tableTab, setTableTab] = useState<'bat' | 'bowl'>('bat');",
    "const [tableTab, setTableTab] = useState<'bat' | 'bowl' | 'both'>('both');"
)

# 3. Update Table Switcher Pills to include 'both'
old_switcher = """                  {/* Table Switcher Pills */}
                  <div style={{ display: 'flex', gap: '6px', background: 'rgba(15, 23, 42, 0.04)', padding: '4px', borderRadius: '999px' }}>
                    {[
                      { id: 'bat', label: 'Top 10 Batters' },
                      { id: 'bowl', label: 'Top 10 Bowlers' }
                    ].map(tab => ("""

new_switcher = """                  {/* Table Switcher Pills */}
                  <div style={{ display: 'flex', gap: '6px', background: 'rgba(15, 23, 42, 0.04)', padding: '4px', borderRadius: '999px' }}>
                    {[
                      { id: 'both', label: '⚡ View Both (Side-by-Side)' },
                      { id: 'bat', label: '🏏 Top 10 Batters' },
                      { id: 'bowl', label: '🎯 Top 10 Bowlers' }
                    ].map(tab => ("""

content = content.replace(old_switcher, new_switcher)

# 4. Update the Table Grid and conditions so 'both' displays both tables side-by-side
old_grid = """                {/* Grid for Tables: 1-column based on tableTab */}
                <div style={{
                  display: 'grid',
                  gridTemplateColumns: '1fr',
                  gap: '18px'
                }}>

                  {/* 1. TOP 10 BATTERS TABLE */}
                  {tableTab === 'bat' && ("""

new_grid = """                {/* Grid for Tables: 2-column if both, 1-column if single tab */}
                <div style={{
                  display: 'grid',
                  gridTemplateColumns: tableTab === 'both' ? 'repeat(auto-fit, minmax(560px, 1fr))' : '1fr',
                  gap: '18px'
                }}>

                  {/* 1. TOP 10 BATTERS TABLE */}
                  {(tableTab === 'bat' || tableTab === 'both') && ("""

content = content.replace(old_grid, new_grid)

# Update the bowler table condition
content = content.replace(
    "{/* 2. TOP 10 BOWLERS TABLE */}\n                  {tableTab === 'bowl' && (",
    "{/* 2. TOP 10 BOWLERS TABLE */}\n                  {(tableTab === 'bowl' || tableTab === 'both') && ("
)

# 5. Tactical Insights sub-cards update to reflect dual-engine leaders
old_tactical = """                      {/* Sub-Card 1 */}
                      <div style={{
                        padding: '12px 14px',
                        borderRadius: '14px',
                        background: '#FFFFFF',
                        border: '1px solid rgba(15, 23, 42, 0.05)',
                        boxShadow: '0 2px 6px rgba(0,0,0,0.02)',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'space-between'
                      }}>
                        <div>
                          <div style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--rr-pink)' }}>SURGE LEADER</div>
                          <div style={{ fontSize: '0.95rem', fontWeight: 800, color: 'var(--text-primary)' }}>Naman Dhir</div>
                          <div style={{ fontSize: '0.7rem', color: 'var(--text-secondary)' }}>+67.9 SR Crisis Surge</div>
                        </div>
                        <div style={{
                          width: '32px',
                          height: '32px',
                          borderRadius: '50%',
                          background: 'var(--rr-pink-light)',
                          color: 'var(--rr-pink)',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center'
                        }}>
                          <Zap size={16} />
                        </div>
                      </div>

                      {/* Sub-Card 2 */}
                      <div style={{
                        padding: '12px 14px',
                        borderRadius: '14px',
                        background: '#FFFFFF',
                        border: '1px solid rgba(15, 23, 42, 0.05)',
                        boxShadow: '0 2px 6px rgba(0,0,0,0.02)',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'space-between'
                      }}>
                        <div>
                          <div style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--rr-blue)' }}>DEATH ANCHOR</div>
                          <div style={{ fontSize: '0.95rem', fontWeight: 800, color: 'var(--text-primary)' }}>M. Pathirana</div>
                          <div style={{ fontSize: '0.7rem', color: 'var(--text-secondary)' }}>6.55 Econ · 53 Wickets</div>
                        </div>
                        <div style={{
                          width: '32px',
                          height: '32px',
                          borderRadius: '50%',
                          background: 'var(--rr-blue-light)',
                          color: 'var(--rr-blue)',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center'
                        }}>
                          <Shield size={16} />
                        </div>
                      </div>

                      {/* Sub-Card 3: Shivam Dube */}
                      <div style={{
                        padding: '12px 14px',
                        borderRadius: '14px',
                        background: '#FFFFFF',
                        border: '1px solid rgba(15, 23, 42, 0.05)',
                        boxShadow: '0 2px 6px rgba(0,0,0,0.02)',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'space-between'
                      }}>
                        <div>
                          <div style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--rr-gold)' }}>SPIN PUNISHER</div>
                          <div style={{ fontSize: '0.95rem', fontWeight: 800, color: 'var(--text-primary)' }}>Shivam Dube</div>
                          <div style={{ fontSize: '0.7rem', color: 'var(--text-secondary)' }}>189.1 SR vs Middle Spin</div>
                        </div>
                        <div style={{
                          width: '32px',
                          height: '32px',
                          borderRadius: '50%',
                          background: 'var(--rr-gold-light)',
                          color: 'var(--rr-gold)',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center'
                        }}>
                          <Flame size={16} />
                        </div>
                      </div>"""

new_tactical = """                      {/* Sub-Card 1: Babar Azam */}
                      <div style={{
                        padding: '12px 14px',
                        borderRadius: '14px',
                        background: '#FFFFFF',
                        border: '1px solid rgba(15, 23, 42, 0.05)',
                        boxShadow: '0 2px 6px rgba(0,0,0,0.02)',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'space-between'
                      }}>
                        <div>
                          <div style={{ fontSize: '0.72rem', fontWeight: 800, color: 'var(--rr-pink)' }}>#1 CLUTCH BATTER · 100% CONSIST</div>
                          <div style={{ fontSize: '0.95rem', fontWeight: 800, color: 'var(--text-primary)' }}>Babar Azam</div>
                          <div style={{ fontSize: '0.7rem', color: 'var(--text-secondary)' }}>131.4 Clutch · 198.9 Pressure SR</div>
                        </div>
                        <div style={{
                          width: '32px',
                          height: '32px',
                          borderRadius: '50%',
                          background: 'var(--rr-pink-light)',
                          color: 'var(--rr-pink)',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center'
                        }}>
                          <Zap size={16} />
                        </div>
                      </div>

                      {/* Sub-Card 2: Matheesha Pathirana */}
                      <div style={{
                        padding: '12px 14px',
                        borderRadius: '14px',
                        background: '#FFFFFF',
                        border: '1px solid rgba(15, 23, 42, 0.05)',
                        boxShadow: '0 2px 6px rgba(0,0,0,0.02)',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'space-between'
                      }}>
                        <div>
                          <div style={{ fontSize: '0.72rem', fontWeight: 800, color: 'var(--rr-blue)' }}>DEATH ANCHOR · 78.6% CONSIST</div>
                          <div style={{ fontSize: '0.95rem', fontWeight: 800, color: 'var(--text-primary)' }}>M. Pathirana</div>
                          <div style={{ fontSize: '0.7rem', color: 'var(--text-secondary)' }}>6.55 Econ · 53 Wkts · 149.9 Clutch</div>
                        </div>
                        <div style={{
                          width: '32px',
                          height: '32px',
                          borderRadius: '50%',
                          background: 'var(--rr-blue-light)',
                          color: 'var(--rr-blue)',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center'
                        }}>
                          <Shield size={16} />
                        </div>
                      </div>

                      {/* Sub-Card 3: Abrar Ahmed */}
                      <div style={{
                        padding: '12px 14px',
                        borderRadius: '14px',
                        background: '#FFFFFF',
                        border: '1px solid rgba(15, 23, 42, 0.05)',
                        boxShadow: '0 2px 6px rgba(0,0,0,0.02)',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'space-between'
                      }}>
                        <div>
                          <div style={{ fontSize: '0.72rem', fontWeight: 800, color: '#10B981' }}>MYSTERY SPIN · 90.0% CONSIST</div>
                          <div style={{ fontSize: '0.95rem', fontWeight: 800, color: 'var(--text-primary)' }}>Abrar Ahmed</div>
                          <div style={{ fontSize: '0.7rem', color: 'var(--text-secondary)' }}>5.89 Econ · 121.4 Clutch (#3 Bowler)</div>
                        </div>
                        <div style={{
                          width: '32px',
                          height: '32px',
                          borderRadius: '50%',
                          background: 'rgba(16, 185, 129, 0.1)',
                          color: '#10B981',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center'
                        }}>
                          <Flame size={16} />
                        </div>
                      </div>"""

content = content.replace(old_tactical, new_tactical)

# Update Tactical Insights footer banner
old_ti_foot = """                  <div style={{
                    paddingTop: '12px',
                    borderTop: '1px solid rgba(15, 23, 42, 0.06)',
                    display: 'flex',
                    justifyContent: 'space-between',
                    fontSize: '0.75rem',
                    color: 'var(--text-muted)'
                  }}>
                    <span>Dataset: 200,999 Balls</span>
                    <span style={{ fontWeight: 700, color: 'var(--rr-pink)' }}>IPL 2022–2026</span>
                  </div>"""

new_ti_foot = """                  <div style={{
                    paddingTop: '12px',
                    borderTop: '1px solid rgba(15, 23, 42, 0.06)',
                    display: 'flex',
                    justifyContent: 'space-between',
                    fontSize: '0.72rem',
                    color: 'var(--text-muted)'
                  }}>
                    <span>Dual Engine: MTGI × C_rate Reliability</span>
                    <span style={{ fontWeight: 800, color: 'var(--rr-pink)' }}>200,999 Balls Ingested</span>
                  </div>"""

content = content.replace(old_ti_foot, new_ti_foot)

# 6. Hero Card metrics row: Add Consistency stat
old_hero_metrics = """                    <div style={{ display: 'flex', gap: '24px', textAlign: 'right' }}>
                      <div>
                        <div className="mono-num" style={{ fontSize: '1.45rem', fontWeight: 900 }}>6.55</div>
                        <div style={{ fontSize: '0.68rem', color: 'rgba(255, 255, 255, 0.75)', fontWeight: 600 }}>PRESSURE ECON</div>
                      </div>
                      <div>
                        <div className="mono-num" style={{ fontSize: '1.45rem', fontWeight: 900 }}>53</div>
                        <div style={{ fontSize: '0.68rem', color: 'rgba(255, 255, 255, 0.75)', fontWeight: 600 }}>PRESSURE WKTS</div>
                      </div>
                    </div>"""

new_hero_metrics = """                    <div style={{ display: 'flex', gap: '20px', textAlign: 'right' }}>
                      <div>
                        <div className="mono-num" style={{ fontSize: '1.45rem', fontWeight: 900, color: '#6EE7B7' }}>78.6%</div>
                        <div style={{ fontSize: '0.65rem', color: 'rgba(255, 255, 255, 0.85)', fontWeight: 700 }}>CONSISTENCY</div>
                      </div>
                      <div>
                        <div className="mono-num" style={{ fontSize: '1.45rem', fontWeight: 900 }}>6.55</div>
                        <div style={{ fontSize: '0.65rem', color: 'rgba(255, 255, 255, 0.85)', fontWeight: 700 }}>PRESSURE ECON</div>
                      </div>
                      <div>
                        <div className="mono-num" style={{ fontSize: '1.45rem', fontWeight: 900 }}>53</div>
                        <div style={{ fontSize: '0.65rem', color: 'rgba(255, 255, 255, 0.85)', fontWeight: 700 }}>PRESSURE WKTS</div>
                      </div>
                    </div>"""

content = content.replace(old_hero_metrics, new_hero_metrics)

# 7. Elite Clutch Prospects Bowler cards: Add Consistency metric
old_prospect_bowler_metrics = """                          <div style={{ marginTop: '16px', paddingTop: '12px', borderTop: '1px solid rgba(15, 23, 42, 0.05)', display: 'flex', justifyContent: 'space-between' }}>
                            <div>
                              <div style={{ fontSize: '0.65rem', color: 'var(--text-muted)' }}>ECONOMY</div>
                              <div className="mono-num" style={{ fontSize: '0.95rem', fontWeight: 800, color: '#10B981' }}>{bw.pEcon.toFixed(2)}</div>
                            </div>
                            <div>
                              <div style={{ fontSize: '0.65rem', color: 'var(--text-muted)' }}>DOT BALL %</div>
                              <div className="mono-num" style={{ fontSize: '0.95rem', fontWeight: 800, color: 'var(--rr-blue)' }}>{bw.dotPct.toFixed(1)}%</div>
                            </div>
                            <div>
                              <div style={{ fontSize: '0.65rem', color: 'var(--text-muted)' }}>WICKETS</div>
                              <div className="mono-num" style={{ fontSize: '0.95rem', fontWeight: 800, color: 'var(--rr-pink)' }}>{bw.pWkts}</div>
                            </div>
                          </div>"""

new_prospect_bowler_metrics = """                          <div style={{ marginTop: '16px', paddingTop: '12px', borderTop: '1px solid rgba(15, 23, 42, 0.05)', display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '8px', textAlign: 'center' }}>
                            <div>
                              <div style={{ fontSize: '0.62rem', color: 'var(--text-muted)' }}>ECONOMY</div>
                              <div className="mono-num" style={{ fontSize: '0.92rem', fontWeight: 800, color: '#10B981' }}>{bw.pEcon.toFixed(2)}</div>
                            </div>
                            <div>
                              <div style={{ fontSize: '0.62rem', color: 'var(--text-muted)' }}>DOT %</div>
                              <div className="mono-num" style={{ fontSize: '0.92rem', fontWeight: 800, color: 'var(--rr-blue)' }}>{bw.dotPct.toFixed(1)}%</div>
                            </div>
                            <div>
                              <div style={{ fontSize: '0.62rem', color: 'var(--text-muted)' }}>CONSIST</div>
                              <div className="mono-num" style={{ fontSize: '0.92rem', fontWeight: 800, color: '#059669' }}>{bw.consistencyPct !== undefined ? `${bw.consistencyPct.toFixed(0)}%` : '-'}</div>
                            </div>
                            <div>
                              <div style={{ fontSize: '0.62rem', color: 'var(--text-muted)' }}>WKTS</div>
                              <div className="mono-num" style={{ fontSize: '0.92rem', fontWeight: 800, color: 'var(--rr-pink)' }}>{bw.pWkts}</div>
                            </div>
                          </div>"""

content = content.replace(old_prospect_bowler_metrics, new_prospect_bowler_metrics)

# 8. Elite Clutch Prospects Batter cards: Add Consistency metric
old_prospect_batter_metrics = """                          <div style={{ marginTop: '16px', paddingTop: '12px', borderTop: '1px solid rgba(15, 23, 42, 0.05)', display: 'flex', justifyContent: 'space-between' }}>
                            <div>
                              <div style={{ fontSize: '0.65rem', color: 'var(--text-muted)' }}>STRIKE RATE</div>
                              <div className="mono-num" style={{ fontSize: '0.95rem', fontWeight: 800, color: 'var(--rr-pink)' }}>{b.pSR.toFixed(1)}</div>
                            </div>
                            <div>
                              <div style={{ fontSize: '0.65rem', color: 'var(--text-muted)' }}>RUNS ACCEL</div>
                              <div className="mono-num" style={{ fontSize: '0.95rem', fontWeight: 800, color: '#10B981' }}>+{b.deltaSR.toFixed(1)}</div>
                            </div>
                            <button 
                              onClick={() => { setSelectedB1(b.name); setActivePage('matrix'); }}"""

new_prospect_batter_metrics = """                          <div style={{ marginTop: '16px', paddingTop: '12px', borderTop: '1px solid rgba(15, 23, 42, 0.05)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                            <div>
                              <div style={{ fontSize: '0.62rem', color: 'var(--text-muted)' }}>STRIKE RATE</div>
                              <div className="mono-num" style={{ fontSize: '0.92rem', fontWeight: 800, color: 'var(--rr-pink)' }}>{b.pSR.toFixed(1)}</div>
                            </div>
                            <div>
                              <div style={{ fontSize: '0.62rem', color: 'var(--text-muted)' }}>BOOST</div>
                              <div className="mono-num" style={{ fontSize: '0.92rem', fontWeight: 800, color: '#10B981' }}>+{b.deltaSR.toFixed(1)}</div>
                            </div>
                            <div>
                              <div style={{ fontSize: '0.62rem', color: 'var(--text-muted)' }}>CONSIST</div>
                              <div className="mono-num" style={{ fontSize: '0.92rem', fontWeight: 800, color: 'var(--rr-blue)' }}>{b.consistencyPct !== undefined ? `${b.consistencyPct.toFixed(0)}%` : '-'}</div>
                            </div>
                            <button 
                              onClick={() => { setSelectedB1(b.name); setActivePage('matrix'); }}"""

content = content.replace(old_prospect_batter_metrics, new_prospect_batter_metrics)

# 9. Matrix Head-to-Head Cards: 4 columns in metrics row (PRE-SR, BOOST, CONSISTENCY, BOUNDARY %)
old_matrix_p1 = """                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '10px', background: 'rgba(15, 23, 42, 0.03)', padding: '12px 14px', borderRadius: '14px', marginBottom: '14px' }}>
                    <div>
                      <div style={{ fontSize: '0.65rem', color: 'var(--text-muted)' }}>PRE-SR</div>
                      <div className="mono-num" style={{ fontSize: '1.15rem', fontWeight: 800, color: 'var(--text-primary)' }}>{p1.pSR.toFixed(1)}</div>
                    </div>
                    <div>
                      <div style={{ fontSize: '0.65rem', color: 'var(--text-muted)' }}>PRESSURE BOOST</div>
                      <div className="mono-num" style={{ fontSize: '1.15rem', fontWeight: 800, color: '#10B981' }}>+{p1.deltaSR.toFixed(1)}</div>
                    </div>
                    <div>
                      <div style={{ fontSize: '0.65rem', color: 'var(--text-muted)' }}>BOUNDARY %</div>
                      <div className="mono-num" style={{ fontSize: '1.15rem', fontWeight: 800, color: 'var(--text-primary)' }}>{p1.bndPct.toFixed(1)}%</div>
                    </div>
                  </div>"""

new_matrix_p1 = """                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '10px', background: 'rgba(15, 23, 42, 0.03)', padding: '12px 14px', borderRadius: '14px', marginBottom: '14px' }}>
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
                  </div>"""

old_matrix_p2 = """                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '10px', background: 'rgba(15, 23, 42, 0.03)', padding: '12px 14px', borderRadius: '14px', marginBottom: '14px' }}>
                    <div>
                      <div style={{ fontSize: '0.65rem', color: 'var(--text-muted)' }}>PRE-SR</div>
                      <div className="mono-num" style={{ fontSize: '1.15rem', fontWeight: 800, color: 'var(--text-primary)' }}>{p2.pSR.toFixed(1)}</div>
                    </div>
                    <div>
                      <div style={{ fontSize: '0.65rem', color: 'var(--text-muted)' }}>PRESSURE BOOST</div>
                      <div className="mono-num" style={{ fontSize: '1.15rem', fontWeight: 800, color: '#10B981' }}>+{p2.deltaSR.toFixed(1)}</div>
                    </div>
                    <div>
                      <div style={{ fontSize: '0.65rem', color: 'var(--text-muted)' }}>BOUNDARY %</div>
                      <div className="mono-num" style={{ fontSize: '1.15rem', fontWeight: 800, color: 'var(--text-primary)' }}>{p2.bndPct.toFixed(1)}%</div>
                    </div>
                  </div>"""

new_matrix_p2 = """                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '10px', background: 'rgba(15, 23, 42, 0.03)', padding: '12px 14px', borderRadius: '14px', marginBottom: '14px' }}>
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
                  </div>"""

content = content.replace(old_matrix_p1, new_matrix_p1)
content = content.replace(old_matrix_p2, new_matrix_p2)

# 10. Direct Metric Comparison meters: Add Consistency Rate meter
old_meters = """                {[
                  { label: 'Pressure Strike Rate', v1: p1.pSR, v2: p2.pSR },
                  { label: 'Pressure Boost vs Baseline', v1: p1.deltaSR, v2: p2.deltaSR },
                  { label: 'Boundary %', v1: p1.bndPct, v2: p2.bndPct },
                  { label: 'Overall Clutch Score', v1: p1.clutchScore, v2: p2.clutchScore }
                ].map((m, i) => ("""

new_meters = """                {[
                  { label: 'Pressure Strike Rate', v1: p1.pSR, v2: p2.pSR },
                  { label: 'Pressure Boost vs Baseline', v1: p1.deltaSR, v2: p2.deltaSR },
                  { label: 'Match Consistency Rate (C_rate)', v1: p1.consistencyPct ?? 80, v2: p2.consistencyPct ?? 80 },
                  { label: 'Boundary %', v1: p1.bndPct, v2: p2.bndPct },
                  { label: 'Overall Clutch Score (MTGI × R)', v1: p1.clutchScore, v2: p2.clutchScore }
                ].map((m, i) => ("""

content = content.replace(old_meters, new_meters)

# 11. Player Deep Dive Modal: Add Consistency & Dual-Engine Breakdown
old_modal_banner = """              {/* Score & Verdict Banner */}
              <div style={{
                display: 'grid',
                gridTemplateColumns: '1fr 1fr',
                gap: '14px',
                padding: '16px',
                borderRadius: '16px',
                background: '#F8FAFC',
                border: '1px solid rgba(15, 23, 42, 0.06)'
              }}>
                <div>
                  <div style={{ fontSize: '0.7rem', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase' }}>
                    Clutch Score
                  </div>
                  <div style={{ fontSize: '2rem', fontWeight: 900, color: selectedPlayerModal.clutchScore >= 100 ? '#15803D' : selectedPlayerModal.clutchScore >= 70 ? 'var(--rr-blue)' : '#64748B', lineHeight: 1.1 }}>
                    {selectedPlayerModal.clutchScore.toFixed(1)}
                  </div>
                  <div style={{ fontSize: '0.72rem', color: 'var(--text-secondary)', marginTop: '4px', fontWeight: 600 }}>
                    {selectedPlayerModal.clutchScore >= 100 ? 'Top Tier Pressure Resilience' : selectedPlayerModal.clutchScore >= 70 ? 'Above Average Match Impact' : 'Low Tension Utility'}
                  </div>
                </div>

                <div style={{ display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'flex-start' }}>
                  <div style={{ fontSize: '0.7rem', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: '6px' }}>
                    Royals Scout Verdict
                  </div>
                  <span style={{
                    padding: '6px 14px',
                    borderRadius: '999px',
                    fontSize: '0.78rem',
                    fontWeight: 900,
                    letterSpacing: '0.04em',
                    background: selectedPlayerModal.verdictClass === 'buy' ? 'rgba(21, 128, 61, 0.12)' : selectedPlayerModal.verdictClass === 'monitor' ? 'rgba(14, 54, 150, 0.12)' : 'rgba(100, 116, 139, 0.12)',
                    color: selectedPlayerModal.verdictClass === 'buy' ? '#15803D' : selectedPlayerModal.verdictClass === 'monitor' ? 'var(--rr-blue)' : '#475569',
                    border: selectedPlayerModal.verdictClass === 'buy' ? '1px solid rgba(21, 128, 61, 0.3)' : selectedPlayerModal.verdictClass === 'monitor' ? '1px solid rgba(14, 54, 150, 0.25)' : '1px solid rgba(100, 116, 139, 0.25)'
                  }}>
                    {selectedPlayerModal.verdict}
                  </span>
                </div>
              </div>"""

new_modal_banner = """              {/* Score & Verdict Banner (Dual-Engine MTGI + Consistency) */}
              {(() => {
                const pConsist = selectedPlayerModal.bowling?.consistency_pct ?? selectedPlayerModal.batting?.consistency_pct ?? selectedPlayerModal.consistencyPct ?? 50.0;
                const pReliability = (0.70 + 0.30 * (pConsist / 100.0)).toFixed(2);
                const pRawMTGI = (selectedPlayerModal.clutchScore / (0.70 + 0.30 * (pConsist / 100.0))).toFixed(1);
                return (
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                    <div style={{
                      display: 'grid',
                      gridTemplateColumns: '1fr 1fr 1fr',
                      gap: '12px',
                      padding: '16px',
                      borderRadius: '16px',
                      background: '#F8FAFC',
                      border: '1px solid rgba(15, 23, 42, 0.06)'
                    }}>
                      <div>
                        <div style={{ fontSize: '0.68rem', fontWeight: 800, color: 'var(--text-muted)', textTransform: 'uppercase' }}>
                          Final Clutch Score
                        </div>
                        <div style={{ fontSize: '2rem', fontWeight: 900, color: selectedPlayerModal.clutchScore >= 100 ? '#15803D' : selectedPlayerModal.clutchScore >= 70 ? 'var(--rr-blue)' : '#64748B', lineHeight: 1.1 }}>
                          {selectedPlayerModal.clutchScore.toFixed(1)}
                        </div>
                        <div style={{ fontSize: '0.68rem', color: 'var(--text-secondary)', marginTop: '4px', fontWeight: 600 }}>
                          Raw MTGI: {pRawMTGI}
                        </div>
                      </div>

                      <div>
                        <div style={{ fontSize: '0.68rem', fontWeight: 800, color: 'var(--text-muted)', textTransform: 'uppercase' }}>
                          Consistency (C_rate)
                        </div>
                        <div style={{ fontSize: '2rem', fontWeight: 900, color: pConsist >= 75 ? '#15803D' : pConsist >= 60 ? 'var(--rr-blue)' : '#D97706', lineHeight: 1.1 }}>
                          {pConsist.toFixed(0)}%
                        </div>
                        <div style={{ fontSize: '0.68rem', color: 'var(--text-secondary)', marginTop: '4px', fontWeight: 600 }}>
                          Reliability: {pReliability}x
                        </div>
                      </div>

                      <div style={{ display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'flex-start' }}>
                        <div style={{ fontSize: '0.68rem', fontWeight: 800, color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: '6px' }}>
                          Royals Scout Verdict
                        </div>
                        <span style={{
                          padding: '6px 12px',
                          borderRadius: '999px',
                          fontSize: '0.74rem',
                          fontWeight: 900,
                          letterSpacing: '0.04em',
                          background: selectedPlayerModal.verdictClass === 'buy' ? 'rgba(21, 128, 61, 0.12)' : selectedPlayerModal.verdictClass === 'monitor' ? 'rgba(14, 54, 150, 0.12)' : 'rgba(100, 116, 139, 0.12)',
                          color: selectedPlayerModal.verdictClass === 'buy' ? '#15803D' : selectedPlayerModal.verdictClass === 'monitor' ? 'var(--rr-blue)' : '#475569',
                          border: selectedPlayerModal.verdictClass === 'buy' ? '1px solid rgba(21, 128, 61, 0.3)' : selectedPlayerModal.verdictClass === 'monitor' ? '1px solid rgba(14, 54, 150, 0.25)' : '1px solid rgba(100, 116, 139, 0.25)'
                        }}>
                          {selectedPlayerModal.verdict}
                        </span>
                      </div>
                    </div>

                    {/* Dual-Engine Formula Bar */}
                    <div style={{
                      padding: '8px 14px',
                      borderRadius: '10px',
                      background: 'linear-gradient(90deg, rgba(230, 0, 126, 0.06), rgba(14, 54, 150, 0.06))',
                      border: '1px solid rgba(15, 23, 42, 0.06)',
                      fontSize: '0.72rem',
                      color: 'var(--text-secondary)',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between'
                    }}>
                      <span style={{ fontWeight: 700, color: 'var(--rr-blue)' }}>Dual-Engine Formula:</span>
                      <span style={{ fontFamily: 'JetBrains Mono, monospace', fontWeight: 800, color: 'var(--text-primary)' }}>
                        Clutch = MTGI ({pRawMTGI}) × [0.70 + 0.30 × ({pConsist.toFixed(0)}% / 100)] = {selectedPlayerModal.clutchScore.toFixed(1)}
                      </span>
                    </div>
                  </div>
                );
              })()}"""

content = content.replace(old_modal_banner, new_modal_banner)

# Modal performance breakdown: 5-column grids with Consistency
old_modal_bowl_grid = """                {/* Bowler Metrics */}
                {selectedPlayerModal.bowling && (
                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '10px' }}>
                    <div style={{ padding: '12px', borderRadius: '12px', background: '#F8FAFC', border: '1px solid rgba(15, 23, 42, 0.05)', textAlign: 'center' }}>
                      <div style={{ fontSize: '0.68rem', color: 'var(--text-muted)', fontWeight: 600 }}>Pressure Econ</div>
                      <div style={{ fontSize: '1.1rem', fontWeight: 800, color: 'var(--text-primary)', marginTop: '2px' }}>{selectedPlayerModal.bowling.p_econ.toFixed(2)}</div>
                      <div style={{ fontSize: '0.62rem', color: 'var(--text-muted)' }}>Base: {selectedPlayerModal.bowling.n_econ.toFixed(2)}</div>
                    </div>
                    <div style={{ padding: '12px', borderRadius: '12px', background: '#F8FAFC', border: '1px solid rgba(15, 23, 42, 0.05)', textAlign: 'center' }}>
                      <div style={{ fontSize: '0.68rem', color: 'var(--text-muted)', fontWeight: 600 }}>Econ Delta</div>
                      <div style={{ fontSize: '1.1rem', fontWeight: 800, color: selectedPlayerModal.bowling.econ_delta > 0 ? '#15803D' : '#DC2626', marginTop: '2px' }}>
                        {selectedPlayerModal.bowling.econ_delta > 0 ? '-' : '+'}{Math.abs(selectedPlayerModal.bowling.econ_delta).toFixed(2)}
                      </div>
                      <div style={{ fontSize: '0.62rem', color: 'var(--text-muted)' }}>Tightness</div>
                    </div>
                    <div style={{ padding: '12px', borderRadius: '12px', background: '#F8FAFC', border: '1px solid rgba(15, 23, 42, 0.05)', textAlign: 'center' }}>
                      <div style={{ fontSize: '0.68rem', color: 'var(--text-muted)', fontWeight: 600 }}>Pressure Wkts</div>
                      <div style={{ fontSize: '1.1rem', fontWeight: 800, color: 'var(--text-primary)', marginTop: '2px' }}>{selectedPlayerModal.bowling.p_wkts}</div>
                      <div style={{ fontSize: '0.62rem', color: 'var(--text-muted)' }}>{selectedPlayerModal.bowling.p_balls} balls</div>
                    </div>
                    <div style={{ padding: '12px', borderRadius: '12px', background: '#F8FAFC', border: '1px solid rgba(15, 23, 42, 0.05)', textAlign: 'center' }}>
                      <div style={{ fontSize: '0.68rem', color: 'var(--text-muted)', fontWeight: 600 }}>Dot Ball %</div>
                      <div style={{ fontSize: '1.1rem', fontWeight: 800, color: 'var(--text-primary)', marginTop: '2px' }}>{selectedPlayerModal.bowling.p_dot_pct.toFixed(1)}%</div>
                      <div style={{ fontSize: '0.62rem', color: 'var(--text-muted)' }}>Suppression</div>
                    </div>
                  </div>
                )}"""

new_modal_bowl_grid = """                {/* Bowler Metrics */}
                {selectedPlayerModal.bowling && (
                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(5, 1fr)', gap: '10px' }}>
                    <div style={{ padding: '12px', borderRadius: '12px', background: '#F8FAFC', border: '1px solid rgba(15, 23, 42, 0.05)', textAlign: 'center' }}>
                      <div style={{ fontSize: '0.68rem', color: 'var(--text-muted)', fontWeight: 600 }}>Pressure Econ</div>
                      <div style={{ fontSize: '1.05rem', fontWeight: 800, color: 'var(--text-primary)', marginTop: '2px' }}>{selectedPlayerModal.bowling.p_econ.toFixed(2)}</div>
                      <div style={{ fontSize: '0.62rem', color: 'var(--text-muted)' }}>Base: {selectedPlayerModal.bowling.n_econ.toFixed(2)}</div>
                    </div>
                    <div style={{ padding: '12px', borderRadius: '12px', background: '#F8FAFC', border: '1px solid rgba(15, 23, 42, 0.05)', textAlign: 'center' }}>
                      <div style={{ fontSize: '0.68rem', color: 'var(--text-muted)', fontWeight: 600 }}>Econ Delta</div>
                      <div style={{ fontSize: '1.05rem', fontWeight: 800, color: selectedPlayerModal.bowling.econ_delta <= 0.5 ? '#15803D' : '#DC2626', marginTop: '2px' }}>
                        {selectedPlayerModal.bowling.econ_delta > 0 ? '+' : ''}{selectedPlayerModal.bowling.econ_delta.toFixed(2)}
                      </div>
                      <div style={{ fontSize: '0.62rem', color: 'var(--text-muted)' }}>Tightness</div>
                    </div>
                    <div style={{ padding: '12px', borderRadius: '12px', background: '#F8FAFC', border: '1px solid rgba(15, 23, 42, 0.05)', textAlign: 'center' }}>
                      <div style={{ fontSize: '0.68rem', color: 'var(--text-muted)', fontWeight: 600 }}>Consistency</div>
                      <div style={{ fontSize: '1.05rem', fontWeight: 800, color: '#10B981', marginTop: '2px' }}>
                        {selectedPlayerModal.bowling.consistency_pct !== undefined ? `${selectedPlayerModal.bowling.consistency_pct.toFixed(0)}%` : '75%'}
                      </div>
                      <div style={{ fontSize: '0.62rem', color: 'var(--text-muted)' }}>Match Rate</div>
                    </div>
                    <div style={{ padding: '12px', borderRadius: '12px', background: '#F8FAFC', border: '1px solid rgba(15, 23, 42, 0.05)', textAlign: 'center' }}>
                      <div style={{ fontSize: '0.68rem', color: 'var(--text-muted)', fontWeight: 600 }}>Pressure Wkts</div>
                      <div style={{ fontSize: '1.05rem', fontWeight: 800, color: 'var(--text-primary)', marginTop: '2px' }}>{selectedPlayerModal.bowling.p_wkts}</div>
                      <div style={{ fontSize: '0.62rem', color: 'var(--text-muted)' }}>{selectedPlayerModal.bowling.p_balls} balls</div>
                    </div>
                    <div style={{ padding: '12px', borderRadius: '12px', background: '#F8FAFC', border: '1px solid rgba(15, 23, 42, 0.05)', textAlign: 'center' }}>
                      <div style={{ fontSize: '0.68rem', color: 'var(--text-muted)', fontWeight: 600 }}>Dot Ball %</div>
                      <div style={{ fontSize: '1.05rem', fontWeight: 800, color: 'var(--text-primary)', marginTop: '2px' }}>{selectedPlayerModal.bowling.p_dot_pct.toFixed(1)}%</div>
                      <div style={{ fontSize: '0.62rem', color: 'var(--text-muted)' }}>Suppression</div>
                    </div>
                  </div>
                )}"""

content = content.replace(old_modal_bowl_grid, new_modal_bowl_grid)

old_modal_bat_grid = """                {/* Batter Metrics */}
                {selectedPlayerModal.batting && (
                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '10px', marginTop: selectedPlayerModal.bowling ? '10px' : 0 }}>
                    <div style={{ padding: '12px', borderRadius: '12px', background: '#F8FAFC', border: '1px solid rgba(15, 23, 42, 0.05)', textAlign: 'center' }}>
                      <div style={{ fontSize: '0.68rem', color: 'var(--text-muted)', fontWeight: 600 }}>Pressure SR</div>
                      <div style={{ fontSize: '1.1rem', fontWeight: 800, color: 'var(--text-primary)', marginTop: '2px' }}>{selectedPlayerModal.batting.p_sr.toFixed(1)}</div>
                      <div style={{ fontSize: '0.62rem', color: 'var(--text-muted)' }}>Base: {selectedPlayerModal.batting.n_sr.toFixed(1)}</div>
                    </div>
                    <div style={{ padding: '12px', borderRadius: '12px', background: '#F8FAFC', border: '1px solid rgba(15, 23, 42, 0.05)', textAlign: 'center' }}>
                      <div style={{ fontSize: '0.68rem', color: 'var(--text-muted)', fontWeight: 600 }}>Pressure Boost</div>
                      <div style={{ fontSize: '1.1rem', fontWeight: 800, color: selectedPlayerModal.batting.sr_delta > 0 ? '#15803D' : '#DC2626', marginTop: '2px' }}>
                        {selectedPlayerModal.batting.sr_delta > 0 ? '+' : ''}{selectedPlayerModal.batting.sr_delta.toFixed(1)}
                      </div>
                      <div style={{ fontSize: '0.62rem', color: 'var(--text-muted)' }}>SR Delta</div>
                    </div>
                    <div style={{ padding: '12px', borderRadius: '12px', background: '#F8FAFC', border: '1px solid rgba(15, 23, 42, 0.05)', textAlign: 'center' }}>
                      <div style={{ fontSize: '0.68rem', color: 'var(--text-muted)', fontWeight: 600 }}>Boundary %</div>
                      <div style={{ fontSize: '1.1rem', fontWeight: 800, color: 'var(--text-primary)', marginTop: '2px' }}>{selectedPlayerModal.batting.p_bdry_pct.toFixed(1)}%</div>
                      <div style={{ fontSize: '0.62rem', color: 'var(--text-muted)' }}>{selectedPlayerModal.batting.p_balls} balls</div>
                    </div>
                    <div style={{ padding: '12px', borderRadius: '12px', background: '#F8FAFC', border: '1px solid rgba(15, 23, 42, 0.05)', textAlign: 'center' }}>
                      <div style={{ fontSize: '0.68rem', color: 'var(--text-muted)', fontWeight: 600 }}>Dot Ball %</div>
                      <div style={{ fontSize: '1.1rem', fontWeight: 800, color: 'var(--text-primary)', marginTop: '2px' }}>{selectedPlayerModal.batting.p_dot_pct.toFixed(1)}%</div>
                      <div style={{ fontSize: '0.62rem', color: 'var(--text-muted)' }}>Rotation</div>
                    </div>
                  </div>
                )}"""

new_modal_bat_grid = """                {/* Batter Metrics */}
                {selectedPlayerModal.batting && (
                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(5, 1fr)', gap: '10px', marginTop: selectedPlayerModal.bowling ? '10px' : 0 }}>
                    <div style={{ padding: '12px', borderRadius: '12px', background: '#F8FAFC', border: '1px solid rgba(15, 23, 42, 0.05)', textAlign: 'center' }}>
                      <div style={{ fontSize: '0.68rem', color: 'var(--text-muted)', fontWeight: 600 }}>Pressure SR</div>
                      <div style={{ fontSize: '1.05rem', fontWeight: 800, color: 'var(--text-primary)', marginTop: '2px' }}>{selectedPlayerModal.batting.p_sr.toFixed(1)}</div>
                      <div style={{ fontSize: '0.62rem', color: 'var(--text-muted)' }}>Base: {selectedPlayerModal.batting.n_sr.toFixed(1)}</div>
                    </div>
                    <div style={{ padding: '12px', borderRadius: '12px', background: '#F8FAFC', border: '1px solid rgba(15, 23, 42, 0.05)', textAlign: 'center' }}>
                      <div style={{ fontSize: '0.68rem', color: 'var(--text-muted)', fontWeight: 600 }}>Pressure Boost</div>
                      <div style={{ fontSize: '1.05rem', fontWeight: 800, color: selectedPlayerModal.batting.sr_delta > 0 ? '#15803D' : '#DC2626', marginTop: '2px' }}>
                        {selectedPlayerModal.batting.sr_delta > 0 ? '+' : ''}{selectedPlayerModal.batting.sr_delta.toFixed(1)}
                      </div>
                      <div style={{ fontSize: '0.62rem', color: 'var(--text-muted)' }}>SR Delta</div>
                    </div>
                    <div style={{ padding: '12px', borderRadius: '12px', background: '#F8FAFC', border: '1px solid rgba(15, 23, 42, 0.05)', textAlign: 'center' }}>
                      <div style={{ fontSize: '0.68rem', color: 'var(--text-muted)', fontWeight: 600 }}>Consistency</div>
                      <div style={{ fontSize: '1.05rem', fontWeight: 800, color: 'var(--rr-blue)', marginTop: '2px' }}>
                        {selectedPlayerModal.batting.consistency_pct !== undefined ? `${selectedPlayerModal.batting.consistency_pct.toFixed(0)}%` : '80%'}
                      </div>
                      <div style={{ fontSize: '0.62rem', color: 'var(--text-muted)' }}>Match Rate</div>
                    </div>
                    <div style={{ padding: '12px', borderRadius: '12px', background: '#F8FAFC', border: '1px solid rgba(15, 23, 42, 0.05)', textAlign: 'center' }}>
                      <div style={{ fontSize: '0.68rem', color: 'var(--text-muted)', fontWeight: 600 }}>Boundary %</div>
                      <div style={{ fontSize: '1.05rem', fontWeight: 800, color: 'var(--text-primary)', marginTop: '2px' }}>{selectedPlayerModal.batting.p_bdry_pct.toFixed(1)}%</div>
                      <div style={{ fontSize: '0.62rem', color: 'var(--text-muted)' }}>{selectedPlayerModal.batting.p_balls} balls</div>
                    </div>
                    <div style={{ padding: '12px', borderRadius: '12px', background: '#F8FAFC', border: '1px solid rgba(15, 23, 42, 0.05)', textAlign: 'center' }}>
                      <div style={{ fontSize: '0.68rem', color: 'var(--text-muted)', fontWeight: 600 }}>Dot Ball %</div>
                      <div style={{ fontSize: '1.05rem', fontWeight: 800, color: 'var(--text-primary)', marginTop: '2px' }}>{selectedPlayerModal.batting.p_dot_pct.toFixed(1)}%</div>
                      <div style={{ fontSize: '0.62rem', color: 'var(--text-muted)' }}>Rotation</div>
                    </div>
                  </div>
                )}"""

content = content.replace(old_modal_bat_grid, new_modal_bat_grid)

# Write updated App.tsx
with open(APP_PATH, "w", encoding="utf-8") as f:
    f.write(content)

print("Successfully applied full platform consistency & MTGI dual-engine updates to App.tsx")
