APP_PATH = r"c:\Users\Dhairya\Desktop\Active\Rajasthan Royals\frontend\src\App.tsx"

with open(APP_PATH, "r", encoding="utf-8") as f:
    text = f.read()

# 1. Update selectedB1 and selectedB2 defaults to Naman Dhir and Phil Salt
text = text.replace(
    'const [selectedB1, setSelectedB1] = useState<string>("Babar Azam");\n  const [selectedB2, setSelectedB2] = useState<string>("Naman Dhir");',
    'const [selectedB1, setSelectedB1] = useState<string>("Naman Dhir");\n  const [selectedB2, setSelectedB2] = useState<string>("Phil Salt");'
)

# 2. Update coachShortlist default array
text = text.replace(
    "return ['Phil Salt', 'Naman Dhir', 'Matheesha Pathirana', 'Arshdeep Singh', 'Babar Azam'];",
    "return ['Naman Dhir', 'Phil Salt', 'Matheesha Pathirana', 'Arshdeep Singh', 'Rashid Khan'];"
)

# 3. Update Tactical Insights sub-cards
old_tactical = """                      {/* Sub-Card 1: Babar Azam */}
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

new_tactical = """                      {/* Sub-Card 1: Naman Dhir */}
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
                          <div style={{ fontSize: '0.72rem', fontWeight: 800, color: 'var(--rr-pink)' }}>#1 CLUTCH BATTER · 87.5% CONSIST</div>
                          <div style={{ fontSize: '0.95rem', fontWeight: 800, color: 'var(--text-primary)' }}>Naman Dhir</div>
                          <div style={{ fontSize: '0.7rem', color: 'var(--text-secondary)' }}>126.8 Clutch · +67.9 SR Crisis Surge</div>
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

                      {/* Sub-Card 3: Rashid Khan */}
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
                          <div style={{ fontSize: '0.72rem', fontWeight: 800, color: '#10B981' }}>WRIST-SPIN LOCKDOWN · 73.6% CONSIST</div>
                          <div style={{ fontSize: '0.95rem', fontWeight: 800, color: 'var(--text-primary)' }}>Rashid Khan</div>
                          <div style={{ fontSize: '0.7rem', color: 'var(--text-secondary)' }}>6.95 Econ · 118.7 Clutch (#3 Bowler)</div>
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

text = text.replace(old_tactical, new_tactical)

with open(APP_PATH, "w", encoding="utf-8") as f:
    f.write(text)

print("Updated App.tsx successfully.")
