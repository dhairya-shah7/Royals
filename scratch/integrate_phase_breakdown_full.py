import re

filepath = 'c:/Users/Dhairya/Desktop/Active/Rajasthan Royals/frontend/src/App.tsx'

with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Add displayedBatters and displayedBowlers derived from dynamicBatters / dynamicBowlers and phaseFilter
target_derived = "  const [searchQuery, setSearchQuery] = useState('');"

replace_derived = """  // Phase-specific derived lists for leaderboard view
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
  }, [dynamicBowlers, phaseFilter]);

  const [searchQuery, setSearchQuery] = useState('');"""

if target_derived in content and "displayedBatters" not in content:
    content = content.replace(target_derived, replace_derived, 1)
    print("Added displayedBatters and displayedBowlers memos")
else:
    print("Could not find target_derived or displayedBatters already present")

# 2. Update the Leaderboard Section header to include Phase Filter capsules
target_leaderboard_header = """                  {/* Table Switcher Pills */}
                  <div style={{ display: 'flex', gap: '6px', background: 'rgba(15, 23, 42, 0.04)', padding: '4px', borderRadius: '999px' }}>
                    {[
                      { id: 'bat', label: '🏏 Top 10 Batters' },
                      { id: 'bowl', label: '🎯 Top 10 Bowlers' }
                    ].map(tab => (
                      <button
                        key={tab.id}
                        onClick={() => setTableTab(tab.id as any)}
                        style={{
                          padding: '6px 18px',
                          borderRadius: '999px',
                          fontSize: '0.74rem',
                          fontWeight: 700,
                          cursor: 'pointer',
                          border: 'none',
                          background: tableTab === tab.id ? '#FFFFFF' : 'transparent',
                          color: tableTab === tab.id ? 'var(--text-primary)' : 'var(--text-secondary)',
                          boxShadow: tableTab === tab.id ? '0 2px 6px rgba(0,0,0,0.06)' : 'none',
                          transition: 'all 0.15s ease'
                        }}
                      >
                        {tab.label}
                      </button>
                    ))}
                  </div>"""

replace_leaderboard_header = """                  {/* Phase & Role Filter Capsules */}
                  <div style={{ display: 'flex', alignItems: 'center', gap: '10px', flexWrap: 'wrap' }}>
                    {/* Phase Selector Capsules */}
                    <div style={{ display: 'flex', gap: '3px', background: 'rgba(15, 23, 42, 0.04)', padding: '4px', borderRadius: '999px', border: '1px solid rgba(15, 23, 42, 0.06)' }}>
                      {[
                        { id: 'all', label: 'All Match Overs' },
                        { id: 'powerplay', label: '⚡ Powerplay (1–6)' },
                        { id: 'middle', label: '🛡️ Middle (7–15)' },
                        { id: 'death', label: '🎯 Death (16–20)' }
                      ].map(ph => (
                        <button
                          key={ph.id}
                          onClick={() => setPhaseFilter(ph.id as any)}
                          style={{
                            padding: '5px 12px',
                            borderRadius: '999px',
                            fontSize: '0.72rem',
                            fontWeight: 700,
                            cursor: 'pointer',
                            border: 'none',
                            background: phaseFilter === ph.id ? (ph.id === 'death' ? '#DC2626' : ph.id === 'powerplay' ? 'var(--rr-pink)' : ph.id === 'middle' ? 'var(--rr-blue)' : '#FFFFFF') : 'transparent',
                            color: phaseFilter === ph.id ? (ph.id === 'all' ? 'var(--text-primary)' : '#FFFFFF') : 'var(--text-secondary)',
                            boxShadow: phaseFilter === ph.id ? '0 2px 6px rgba(0,0,0,0.08)' : 'none',
                            transition: 'all 0.15s ease'
                          }}
                        >
                          {ph.label}
                        </button>
                      ))}
                    </div>

                    {/* Role Switcher */}
                    <div style={{ display: 'flex', gap: '3px', background: 'rgba(15, 23, 42, 0.04)', padding: '4px', borderRadius: '999px' }}>
                      {[
                        { id: 'bat', label: '🏏 Batters' },
                        { id: 'bowl', label: '🎯 Bowlers' }
                      ].map(tab => (
                        <button
                          key={tab.id}
                          onClick={() => setTableTab(tab.id as any)}
                          style={{
                            padding: '5px 14px',
                            borderRadius: '999px',
                            fontSize: '0.72rem',
                            fontWeight: 700,
                            cursor: 'pointer',
                            border: 'none',
                            background: tableTab === tab.id ? '#FFFFFF' : 'transparent',
                            color: tableTab === tab.id ? 'var(--text-primary)' : 'var(--text-secondary)',
                            boxShadow: tableTab === tab.id ? '0 2px 6px rgba(0,0,0,0.06)' : 'none',
                            transition: 'all 0.15s ease'
                          }}
                        >
                          {tab.label}
                        </button>
                      ))}
                    </div>
                  </div>"""

if target_leaderboard_header in content:
    content = content.replace(target_leaderboard_header, replace_leaderboard_header, 1)
    print("Added Phase & Role Filter Capsules in Leaderboard header")
else:
    print("Could not find target_leaderboard_header")

# 3. In the Leaderboard tables, use displayedBatters instead of dynamicBatters.slice(0, 10)
content = content.replace(
    "dynamicBatters.slice(0, 10).map((b, idx) => {",
    "displayedBatters.slice(0, 10).map((b, idx) => {"
)
content = content.replace(
    "dynamicBowlers.slice(0, 10).map((bw, idx) => {",
    "displayedBowlers.slice(0, 10).map((bw, idx) => {"
)

# 4. Add Phase Mastery Card in Modal
target_modal_strengths = "{/* Performance Metrics Breakdown */}"
replace_modal_phase = """{/* Phase Breakdown in Modal */}
              {selectedPlayerModal.phases && (
                <div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
                    <div style={{ fontSize: '0.8rem', fontWeight: 800, color: 'var(--text-primary)' }}>
                      ⚡ Tactical Phase Mastery (Powerplay vs Middle vs Death)
                    </div>
                    <span style={{ fontSize: '0.65rem', fontWeight: 700, color: 'var(--text-muted)' }}>
                      Tournament Phase Splits
                    </span>
                  </div>

                  {(() => {
                    const isBowler = selectedPlayerModal.role.toLowerCase().includes('bowl') || (!selectedPlayerModal.batting && selectedPlayerModal.bowling);
                    const batPh = selectedPlayerModal.phases?.batting || {};
                    const bowlPh = selectedPlayerModal.phases?.bowling || {};
                    const pp = isBowler ? bowlPh.powerplay : batPh.powerplay;
                    const mid = isBowler ? bowlPh.middle : batPh.middle;
                    const dth = isBowler ? bowlPh.death : batPh.death;

                    return (
                      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '10px' }}>
                        {/* Powerplay Card */}
                        <div style={{ background: '#F8FAFC', padding: '12px 14px', borderRadius: '12px', border: '1px solid rgba(15,23,42,0.06)' }}>
                          <div style={{ fontSize: '0.65rem', fontWeight: 800, color: 'var(--rr-pink)', textTransform: 'uppercase', marginBottom: '4px' }}>
                            ⚡ Powerplay (1–6)
                          </div>
                          {pp && pp.balls > 0 ? (
                            <div>
                              <div className="mono-num" style={{ fontSize: '1.25rem', fontWeight: 900, color: 'var(--text-primary)' }}>
                                {isBowler ? `${pp.econ.toFixed(2)} Econ` : `${pp.sr.toFixed(1)} SR`}
                              </div>
                              <div style={{ fontSize: '0.68rem', color: 'var(--text-secondary)', marginTop: '4px' }}>
                                {isBowler ? `${pp.wkts} wkts · ${pp.balls}b · ${pp.dotPct}% dot` : `${pp.runs}r · ${pp.balls}b · ${pp.bdryPct}% bdry`}
                              </div>
                            </div>
                          ) : (
                            <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', fontStyle: 'italic', marginTop: '6px' }}>No deliveries</div>
                          )}
                        </div>

                        {/* Middle Overs Card */}
                        <div style={{ background: '#F8FAFC', padding: '12px 14px', borderRadius: '12px', border: '1px solid rgba(15,23,42,0.06)' }}>
                          <div style={{ fontSize: '0.65rem', fontWeight: 800, color: 'var(--rr-blue)', textTransform: 'uppercase', marginBottom: '4px' }}>
                            🛡️ Middle Overs (7–15)
                          </div>
                          {mid && mid.balls > 0 ? (
                            <div>
                              <div className="mono-num" style={{ fontSize: '1.25rem', fontWeight: 900, color: 'var(--text-primary)' }}>
                                {isBowler ? `${mid.econ.toFixed(2)} Econ` : `${mid.sr.toFixed(1)} SR`}
                              </div>
                              <div style={{ fontSize: '0.68rem', color: 'var(--text-secondary)', marginTop: '4px' }}>
                                {isBowler ? `${mid.wkts} wkts · ${mid.balls}b · ${mid.dotPct}% dot` : `${mid.runs}r · ${mid.balls}b · ${mid.bdryPct}% bdry`}
                              </div>
                            </div>
                          ) : (
                            <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', fontStyle: 'italic', marginTop: '6px' }}>No deliveries</div>
                          )}
                        </div>

                        {/* Death Overs Card */}
                        <div style={{ background: '#F8FAFC', padding: '12px 14px', borderRadius: '12px', border: '1px solid rgba(15,23,42,0.06)' }}>
                          <div style={{ fontSize: '0.65rem', fontWeight: 800, color: '#DC2626', textTransform: 'uppercase', marginBottom: '4px' }}>
                            🎯 Death Overs (16–20)
                          </div>
                          {dth && dth.balls > 0 ? (
                            <div>
                              <div className="mono-num" style={{ fontSize: '1.25rem', fontWeight: 900, color: 'var(--text-primary)' }}>
                                {isBowler ? `${dth.econ.toFixed(2)} Econ` : `${dth.sr.toFixed(1)} SR`}
                              </div>
                              <div style={{ fontSize: '0.68rem', color: 'var(--text-secondary)', marginTop: '4px' }}>
                                {isBowler ? `${dth.wkts} wkts · ${dth.balls}b · ${dth.dotPct}% dot` : `${dth.runs}r · ${dth.balls}b · ${dth.bdryPct}% bdry`}
                              </div>
                            </div>
                          ) : (
                            <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', fontStyle: 'italic', marginTop: '6px' }}>No deliveries</div>
                          )}
                        </div>
                      </div>
                    );
                  })()}
                </div>
              )}

              {/* Performance Metrics Breakdown */}"""

if target_modal_strengths in content and "Tactical Phase Mastery" not in content:
    content = content.replace(target_modal_strengths, replace_modal_phase, 1)
    print("Added Phase Breakdown in Player Modal")
else:
    print("Could not find target_modal_strengths or Phase Breakdown already present in Modal")

# 5. Add Phase Breakdown in Head-to-Head Candidate Comparator (Matrix page)
target_matrix_bat = "{/* Direct Proportion Meters for Batters */}"
replace_matrix_bat = """{/* Tactical Phase Comparison for Batters */}
                  <div className="glass-card" style={{ padding: '20px 24px' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '14px' }}>
                      <h4 style={{ margin: 0, fontSize: '0.92rem', fontWeight: 800, color: 'var(--text-primary)' }}>
                        ⚡ Phase-by-Phase Strike Rate & Boundary Breakdown
                      </h4>
                      <span style={{ fontSize: '0.68rem', fontWeight: 800, color: 'var(--rr-pink)', background: 'var(--rr-pink-light)', padding: '2px 10px', borderRadius: '999px' }}>
                        TACTICAL AUDIT
                      </span>
                    </div>

                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '12px' }}>
                      {[
                        { title: '⚡ Powerplay (1–6)', phase: 'powerplay', color: 'var(--rr-pink)' },
                        { title: '🛡️ Middle Overs (7–15)', phase: 'middle', color: 'var(--rr-blue)' },
                        { title: '🎯 Death Overs (16–20)', phase: 'death', color: '#DC2626' }
                      ].map(ph => {
                        const m1 = p1.phases?.[ph.phase as keyof typeof p1.phases];
                        const m2 = p2.phases?.[ph.phase as keyof typeof p2.phases];
                        return (
                          <div key={ph.phase} style={{ background: '#F8FAFC', padding: '14px', borderRadius: '14px', border: '1px solid rgba(15,23,42,0.06)' }}>
                            <div style={{ fontSize: '0.72rem', fontWeight: 800, color: ph.color, marginBottom: '10px', textTransform: 'uppercase' }}>
                              {ph.title}
                            </div>
                            
                            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.78rem' }}>
                                <span style={{ fontWeight: 800, color: 'var(--rr-pink)' }}>{m1?.sr ? `${m1.sr.toFixed(1)} SR` : '-'}</span>
                                <span style={{ fontSize: '0.68rem', color: 'var(--text-muted)' }}>Strike Rate</span>
                                <span style={{ fontWeight: 800, color: 'var(--rr-blue)' }}>{m2?.sr ? `${m2.sr.toFixed(1)} SR` : '-'}</span>
                              </div>

                              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.74rem', color: 'var(--text-secondary)' }}>
                                <span>{m1?.bdryPct ? `${m1.bdryPct.toFixed(1)}%` : '-'}</span>
                                <span style={{ fontSize: '0.65rem', color: 'var(--text-muted)' }}>Boundary %</span>
                                <span>{m2?.bdryPct ? `${m2.bdryPct.toFixed(1)}%` : '-'}</span>
                              </div>

                              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.7rem', color: 'var(--text-muted)' }}>
                                <span>{m1?.balls ? `${m1.balls} balls` : '0b'}</span>
                                <span style={{ fontSize: '0.62rem' }}>Sample</span>
                                <span>{m2?.balls ? `${m2.balls} balls` : '0b'}</span>
                              </div>
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  </div>

                  {/* Direct Proportion Meters for Batters */}"""

if target_matrix_bat in content and "Tactical Phase Comparison for Batters" not in content:
    content = content.replace(target_matrix_bat, replace_matrix_bat, 1)
    print("Added Phase Comparison in Matrix for Batters")

target_matrix_bowl = "{/* Direct Proportion Meters for Bowlers */}"
replace_matrix_bowl = """{/* Tactical Phase Comparison for Bowlers */}
                  <div className="glass-card" style={{ padding: '20px 24px' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '14px' }}>
                      <h4 style={{ margin: 0, fontSize: '0.92rem', fontWeight: 800, color: 'var(--text-primary)' }}>
                        🎯 Phase-by-Phase Economy & Wicket Suppression Breakdown
                      </h4>
                      <span style={{ fontSize: '0.68rem', fontWeight: 800, color: 'var(--rr-blue)', background: 'var(--rr-blue-light)', padding: '2px 10px', borderRadius: '999px' }}>
                        TACTICAL AUDIT
                      </span>
                    </div>

                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '12px' }}>
                      {[
                        { title: '⚡ Powerplay (1–6)', phase: 'powerplay', color: 'var(--rr-pink)' },
                        { title: '🛡️ Middle Overs (7–15)', phase: 'middle', color: 'var(--rr-blue)' },
                        { title: '🎯 Death Overs (16–20)', phase: 'death', color: '#DC2626' }
                      ].map(ph => {
                        const m1 = bw1.phases?.[ph.phase as keyof typeof bw1.phases];
                        const m2 = bw2.phases?.[ph.phase as keyof typeof bw2.phases];
                        return (
                          <div key={ph.phase} style={{ background: '#F8FAFC', padding: '14px', borderRadius: '14px', border: '1px solid rgba(15,23,42,0.06)' }}>
                            <div style={{ fontSize: '0.72rem', fontWeight: 800, color: ph.color, marginBottom: '10px', textTransform: 'uppercase' }}>
                              {ph.title}
                            </div>
                            
                            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.78rem' }}>
                                <span style={{ fontWeight: 800, color: 'var(--rr-pink)' }}>{m1?.econ ? `${m1.econ.toFixed(2)} Econ` : '-'}</span>
                                <span style={{ fontSize: '0.68rem', color: 'var(--text-muted)' }}>Economy</span>
                                <span style={{ fontWeight: 800, color: 'var(--rr-blue)' }}>{m2?.econ ? `${m2.econ.toFixed(2)} Econ` : '-'}</span>
                              </div>

                              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.74rem', color: 'var(--text-secondary)' }}>
                                <span>{m1?.wkts !== undefined ? `${m1.wkts} wkts` : '-'}</span>
                                <span style={{ fontSize: '0.65rem', color: 'var(--text-muted)' }}>Wickets</span>
                                <span>{m2?.wkts !== undefined ? `${m2.wkts} wkts` : '-'}</span>
                              </div>

                              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.7rem', color: 'var(--text-muted)' }}>
                                <span>{m1?.dotPct !== undefined ? `${m1.dotPct.toFixed(1)}%` : '-'}</span>
                                <span style={{ fontSize: '0.62rem' }}>Dot %</span>
                                <span>{m2?.dotPct !== undefined ? `${m2.dotPct.toFixed(1)}%` : '-'}</span>
                              </div>
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  </div>

                  {/* Direct Proportion Meters for Bowlers */}"""

if target_matrix_bowl in content and "Tactical Phase Comparison for Bowlers" not in content:
    content = content.replace(target_matrix_bowl, replace_matrix_bowl, 1)
    print("Added Phase Comparison in Matrix for Bowlers")

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)

print("Saved App.tsx successfully with full Phase-Specific Breakdowns")
