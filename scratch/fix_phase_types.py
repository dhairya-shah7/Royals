filepath = 'c:/Users/Dhairya/Desktop/Active/Rajasthan Royals/frontend/src/App.tsx'

with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Remove misplaced displayedBatters and displayedBowlers from top
bad_pos = '''  // Phase-specific derived lists for leaderboard view
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

  const [searchQuery, setSearchQuery] = useState('');'''

good_top = '''  const [searchQuery, setSearchQuery] = useState('');'''

if bad_pos in content:
    content = content.replace(bad_pos, good_top, 1)
    print("Removed misplaced displayedBatters and displayedBowlers from top")

# 2. Place displayedBatters and displayedBowlers right after dynamicBowlers
after_dynamic_target = '''        rank: idx + 1,
        badge: idx === 0 ? "PRIORITY TARGET" : idx < 3 ? "MAIN TARGET" : "TARGET ACQUIRE"
      }));
  }, [activeCalib]);'''

after_dynamic_replace = '''        rank: idx + 1,
        badge: idx === 0 ? "PRIORITY TARGET" : idx < 3 ? "MAIN TARGET" : "TARGET ACQUIRE"
      }));
  }, [activeCalib]);

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

if after_dynamic_target in content:
    content = content.replace(after_dynamic_target, after_dynamic_replace, 1)
    print("Inserted displayedBatters and displayedBowlers right after dynamicBowlers")
else:
    print("Could not find after_dynamic_target")

# 3. Clean up Phase Breakdown rendering in Modal with explicit typing
old_modal_phase_block = """{/* Phase Breakdown in Modal */}
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
              )}"""

new_modal_phase_block = """{/* Phase Breakdown in Modal */}
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
                    const batPh = selectedPlayerModal.phases?.batting;
                    const bowlPh = selectedPlayerModal.phases?.bowling;

                    return (
                      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '10px' }}>
                        {/* Powerplay Card */}
                        <div style={{ background: '#F8FAFC', padding: '12px 14px', borderRadius: '12px', border: '1px solid rgba(15,23,42,0.06)' }}>
                          <div style={{ fontSize: '0.65rem', fontWeight: 800, color: 'var(--rr-pink)', textTransform: 'uppercase', marginBottom: '4px' }}>
                            ⚡ Powerplay (1–6)
                          </div>
                          {isBowler ? (
                            bowlPh?.powerplay && bowlPh.powerplay.balls > 0 ? (
                              <div>
                                <div className="mono-num" style={{ fontSize: '1.25rem', fontWeight: 900, color: 'var(--text-primary)' }}>
                                  {bowlPh.powerplay.econ.toFixed(2)} Econ
                                </div>
                                <div style={{ fontSize: '0.68rem', color: 'var(--text-secondary)', marginTop: '4px' }}>
                                  {bowlPh.powerplay.wkts} wkts · {bowlPh.powerplay.balls}b · {bowlPh.powerplay.dotPct}% dot
                                </div>
                              </div>
                            ) : (
                              <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', fontStyle: 'italic', marginTop: '6px' }}>No deliveries</div>
                            )
                          ) : (
                            batPh?.powerplay && batPh.powerplay.balls > 0 ? (
                              <div>
                                <div className="mono-num" style={{ fontSize: '1.25rem', fontWeight: 900, color: 'var(--text-primary)' }}>
                                  {batPh.powerplay.sr.toFixed(1)} SR
                                </div>
                                <div style={{ fontSize: '0.68rem', color: 'var(--text-secondary)', marginTop: '4px' }}>
                                  {batPh.powerplay.runs}r · {batPh.powerplay.balls}b · {batPh.powerplay.bdryPct}% bdry
                                </div>
                              </div>
                            ) : (
                              <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', fontStyle: 'italic', marginTop: '6px' }}>No deliveries</div>
                            )
                          )}
                        </div>

                        {/* Middle Overs Card */}
                        <div style={{ background: '#F8FAFC', padding: '12px 14px', borderRadius: '12px', border: '1px solid rgba(15,23,42,0.06)' }}>
                          <div style={{ fontSize: '0.65rem', fontWeight: 800, color: 'var(--rr-blue)', textTransform: 'uppercase', marginBottom: '4px' }}>
                            🛡️ Middle Overs (7–15)
                          </div>
                          {isBowler ? (
                            bowlPh?.middle && bowlPh.middle.balls > 0 ? (
                              <div>
                                <div className="mono-num" style={{ fontSize: '1.25rem', fontWeight: 900, color: 'var(--text-primary)' }}>
                                  {bowlPh.middle.econ.toFixed(2)} Econ
                                </div>
                                <div style={{ fontSize: '0.68rem', color: 'var(--text-secondary)', marginTop: '4px' }}>
                                  {bowlPh.middle.wkts} wkts · {bowlPh.middle.balls}b · {bowlPh.middle.dotPct}% dot
                                </div>
                              </div>
                            ) : (
                              <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', fontStyle: 'italic', marginTop: '6px' }}>No deliveries</div>
                            )
                          ) : (
                            batPh?.middle && batPh.middle.balls > 0 ? (
                              <div>
                                <div className="mono-num" style={{ fontSize: '1.25rem', fontWeight: 900, color: 'var(--text-primary)' }}>
                                  {batPh.middle.sr.toFixed(1)} SR
                                </div>
                                <div style={{ fontSize: '0.68rem', color: 'var(--text-secondary)', marginTop: '4px' }}>
                                  {batPh.middle.runs}r · {batPh.middle.balls}b · {batPh.middle.bdryPct}% bdry
                                </div>
                              </div>
                            ) : (
                              <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', fontStyle: 'italic', marginTop: '6px' }}>No deliveries</div>
                            )
                          )}
                        </div>

                        {/* Death Overs Card */}
                        <div style={{ background: '#F8FAFC', padding: '12px 14px', borderRadius: '12px', border: '1px solid rgba(15,23,42,0.06)' }}>
                          <div style={{ fontSize: '0.65rem', fontWeight: 800, color: '#DC2626', textTransform: 'uppercase', marginBottom: '4px' }}>
                            🎯 Death Overs (16–20)
                          </div>
                          {isBowler ? (
                            bowlPh?.death && bowlPh.death.balls > 0 ? (
                              <div>
                                <div className="mono-num" style={{ fontSize: '1.25rem', fontWeight: 900, color: 'var(--text-primary)' }}>
                                  {bowlPh.death.econ.toFixed(2)} Econ
                                </div>
                                <div style={{ fontSize: '0.68rem', color: 'var(--text-secondary)', marginTop: '4px' }}>
                                  {bowlPh.death.wkts} wkts · {bowlPh.death.balls}b · {bowlPh.death.dotPct}% dot
                                </div>
                              </div>
                            ) : (
                              <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', fontStyle: 'italic', marginTop: '6px' }}>No deliveries</div>
                            )
                          ) : (
                            batPh?.death && batPh.death.balls > 0 ? (
                              <div>
                                <div className="mono-num" style={{ fontSize: '1.25rem', fontWeight: 900, color: 'var(--text-primary)' }}>
                                  {batPh.death.sr.toFixed(1)} SR
                                </div>
                                <div style={{ fontSize: '0.68rem', color: 'var(--text-secondary)', marginTop: '4px' }}>
                                  {batPh.death.runs}r · {batPh.death.balls}b · {batPh.death.bdryPct}% bdry
                                </div>
                              </div>
                            ) : (
                              <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', fontStyle: 'italic', marginTop: '6px' }}>No deliveries</div>
                            )
                          )}
                        </div>
                      </div>
                    );
                  })()}
                </div>
              )}"""

if old_modal_phase_block in content:
    content = content.replace(old_modal_phase_block, new_modal_phase_block, 1)
    print("Replaced old modal phase block with properly typed block")
else:
    print("Could not find old_modal_phase_block")

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)

print("Saved App.tsx successfully")
