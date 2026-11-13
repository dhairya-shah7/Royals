filepath = 'c:/Users/Dhairya/Desktop/Active/Rajasthan Royals/frontend/src/App.tsx'

with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Remove filteredBatters and filteredBowlers declarations
old_filtered = '''  // Filtered lists for live search using dynamic calibration
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
  );'''

content = content.replace(old_filtered, '')

# 2. Replace the Elite Clutch Prospects dynamic player grid section
prospects_start = '{/* Dynamic Player Grid Based on Filter & Search */}'
prospects_end = '{/* ========================================================================= */}\n              {/* TOP 10 RANKINGS'

idx1 = content.find(prospects_start)
idx2 = content.find(prospects_end)

if idx1 != -1 and idx2 != -1:
    new_prospects_grid = '''{/* Dynamic Player Grid Based on Filter (Independent of Search Box) */}
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '16px' }}>
                  {roleFilter === 'bowl' ? (
                    dynamicBowlers.slice(0, 4).map(bw => (
                      <div key={bw.name} className="glass-card" style={{ padding: '20px', display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
                        <div>
                          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '12px' }}>
                            <span style={{
                              fontSize: '0.68rem',
                              fontWeight: 800,
                              padding: '3px 8px',
                              borderRadius: '999px',
                              background: 'var(--rr-blue-light)',
                              color: 'var(--rr-blue)'
                            }}>
                              {bw.badge}
                            </span>
                            <span className="mono-num" style={{ fontSize: '1.15rem', fontWeight: 800, color: 'var(--text-primary)' }}>
                              {bw.clutchScore.toFixed(1)}
                            </span>
                          </div>
                          <h4 style={{ margin: '0 0 4px 0', fontSize: '1.05rem', fontWeight: 800, color: 'var(--text-primary)' }}>{bw.name}</h4>
                          <p style={{ margin: 0, fontSize: '0.75rem', color: 'var(--text-secondary)' }}>{bw.team} · {bw.role}</p>
                        </div>

                        <div style={{ marginTop: '16px', paddingTop: '12px', borderTop: '1px solid rgba(15, 23, 42, 0.05)', display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '8px', textAlign: 'center' }}>
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
                        </div>
                      </div>
                    ))
                  ) : roleFilter === 'bat' ? (
                    dynamicBatters.slice(0, 4).map(b => (
                      <div key={b.name} className="glass-card" style={{ padding: '20px', display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
                        <div>
                          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '12px' }}>
                            <span style={{
                              fontSize: '0.68rem',
                              fontWeight: 800,
                              padding: '3px 8px',
                              borderRadius: '999px',
                              background: b.rank === 1 ? 'var(--rr-pink-light)' : 'var(--rr-gold-light)',
                              color: b.rank === 1 ? 'var(--rr-pink)' : 'var(--rr-gold)'
                            }}>
                              {b.badge}
                            </span>
                            <span className="mono-num" style={{ fontSize: '1.15rem', fontWeight: 800, color: 'var(--text-primary)' }}>
                              {b.clutchScore.toFixed(1)}
                            </span>
                          </div>
                          <h4 style={{ margin: '0 0 4px 0', fontSize: '1.05rem', fontWeight: 800, color: 'var(--text-primary)' }}>{b.name}</h4>
                          <p style={{ margin: 0, fontSize: '0.75rem', color: 'var(--text-secondary)' }}>{b.team} · {b.role}</p>
                        </div>

                        <div style={{ marginTop: '16px', paddingTop: '12px', borderTop: '1px solid rgba(15, 23, 42, 0.05)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
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
                            onClick={() => { setSelectedB1(b.name); setActivePage('matrix'); }}
                            style={{
                              width: '30px',
                              height: '30px',
                              borderRadius: '50%',
                              background: '#FFFFFF',
                              border: '1px solid rgba(15, 23, 42, 0.08)',
                              display: 'flex',
                              alignItems: 'center',
                              justifyContent: 'center',
                              cursor: 'pointer',
                              color: 'var(--text-primary)'
                            }}
                          >
                            <ArrowUpRight size={14} />
                          </button>
                        </div>
                      </div>
                    ))
                  ) : (
                    <>
                      {dynamicBatters.slice(0, 2).map(b => (
                        <div key={b.name} className="glass-card" style={{ padding: '20px', display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
                          <div>
                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '12px' }}>
                              <span style={{
                                fontSize: '0.68rem',
                                fontWeight: 800,
                                padding: '3px 8px',
                                borderRadius: '999px',
                                background: b.rank === 1 ? 'var(--rr-pink-light)' : 'var(--rr-gold-light)',
                                color: b.rank === 1 ? 'var(--rr-pink)' : 'var(--rr-gold)'
                              }}>
                                🏏 {b.badge}
                              </span>
                              <span className="mono-num" style={{ fontSize: '1.15rem', fontWeight: 800, color: 'var(--text-primary)' }}>
                                {b.clutchScore.toFixed(1)}
                              </span>
                            </div>
                            <h4 style={{ margin: '0 0 4px 0', fontSize: '1.05rem', fontWeight: 800, color: 'var(--text-primary)' }}>{b.name}</h4>
                            <p style={{ margin: 0, fontSize: '0.75rem', color: 'var(--text-secondary)' }}>{b.team} · {b.role}</p>
                          </div>

                          <div style={{ marginTop: '16px', paddingTop: '12px', borderTop: '1px solid rgba(15, 23, 42, 0.05)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
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
                              onClick={() => { setSelectedB1(b.name); setActivePage('matrix'); }}
                              style={{
                                width: '30px',
                                height: '30px',
                                borderRadius: '50%',
                                background: '#FFFFFF',
                                border: '1px solid rgba(15, 23, 42, 0.08)',
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'center',
                                cursor: 'pointer',
                                color: 'var(--text-primary)'
                              }}
                            >
                              <ArrowUpRight size={14} />
                            </button>
                          </div>
                        </div>
                      ))}

                      {dynamicBowlers.slice(0, 2).map(bw => (
                        <div key={bw.name} className="glass-card" style={{ padding: '20px', display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
                          <div>
                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '12px' }}>
                              <span style={{
                                fontSize: '0.68rem',
                                fontWeight: 800,
                                padding: '3px 8px',
                                borderRadius: '999px',
                                background: 'var(--rr-blue-light)',
                                color: 'var(--rr-blue)'
                              }}>
                                🎯 {bw.badge}
                              </span>
                              <span className="mono-num" style={{ fontSize: '1.15rem', fontWeight: 800, color: 'var(--text-primary)' }}>
                                {bw.clutchScore.toFixed(1)}
                              </span>
                            </div>
                            <h4 style={{ margin: '0 0 4px 0', fontSize: '1.05rem', fontWeight: 800, color: 'var(--text-primary)' }}>{bw.name}</h4>
                            <p style={{ margin: 0, fontSize: '0.75rem', color: 'var(--text-secondary)' }}>{bw.team} · {bw.role}</p>
                          </div>

                          <div style={{ marginTop: '16px', paddingTop: '12px', borderTop: '1px solid rgba(15, 23, 42, 0.05)', display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '8px', textAlign: 'center' }}>
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
                          </div>
                        </div>
                      ))}
                    </>
                  )}
                </div>
              </div>

              '''
    content = content[:idx1] + new_prospects_grid + content[idx2:]
    print("Replaced Elite Clutch Prospects grid to be completely independent of the search box")
else:
    print(f"Could not find markers: idx1={idx1}, idx2={idx2}")

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)

print("Saved App.tsx successfully")
