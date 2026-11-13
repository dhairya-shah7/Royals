import { useState, useRef, useEffect, useMemo } from 'react';
import { 
  Trophy, Crosshair, Target, Shield, Settings, Search,
  Zap, Flame, CheckCircle2, Play, ArrowUpRight,
  Bot, X, Send, User as UserIcon, ClipboardList, Plus, Trash2,
  AlertTriangle, Bookmark, Sparkles, Scale, FileText
} from 'lucide-react';
import rrLogo from './assets/rr-logo.png';
import clutchData from './data/clutch_index.json';
import {
  findBestPlayerMatch,
  compareTwoPlayers,
  auditCoachShortlist,
  searchPlayers,
  type PlayerStat,
  type ComparisonResult,
  type CoachShortlistAudit
} from './utils/scoutEngine';

export interface PhaseBatting {
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
}

const BATTER_ROLES: Record<string, string> = {
  "Babar Azam": "Innings Anchor / Crisis Stabilizer",
  "Naman Dhir": "Middle-Overs Enforcer / Finisher",
  "Phil Salt": "Wicketkeeper / Explosive Opener",
  "Najibullah Zadran": "Spin Punisher / Power Finisher",
  "Donovan Ferreira": "Explosive Finisher / Wicketkeeper",
  "Shubham Dubey": "Death-Overs Power Hitter",
  "Jos Buttler": "World-Class Crisis Match-Winner",
  "Rinku Singh": "Death-Overs Elite Finisher",
  "Rishabh Pant": "Left-Hand Dynamic Enforcer",
  "Sanju Samson": "Royals Captain / Crisis Anchor"
};

const BOWLER_ROLES: Record<string, string> = {
  "Arshdeep Singh": "Death Overs Strike Pacer",
  "Matheesha Pathirana": "Sling Action Death Specialist",
  "Abrar Ahmed": "Mystery Spin Crisis Lockdown",
  "Rashid Khan": "World-Class Clutch Leg-Spinner",
  "Yuzvendra Chahal": "High-Pressure Wicket Taker",
  "Mohammad Nawaz": "Left-Arm Restrictive Spin",
  "Harshal Patel": "Death Dip Slower-Ball Specialist",
  "Jasprit Bumrah": "Generational Death Overs Pacer",
  "Akeal Hosein": "Powerplay & Death Arm Ball Specialist",
  "Shaheen Afridi": "Left-Arm High-Pace Wicket Taker"
};

const _BATTERS: Batter[] = (clutchData.topBatters || []).slice(0, 15).map((b: any) => ({
  rank: b.rank,
  name: b.name,
  role: BATTER_ROLES[b.name] || "Crisis Batting Specialist",
  team: b.team,
  country: b.team.includes('Pakistan') ? 'PAK' :
           b.team.includes('England') ? 'ENG' :
           b.team.includes('Afghanistan') ? 'AFG' : 'IND',
  pBalls: b.balls,
  pRuns: b.runs,
  pSR: b.strikeRate,
  baseSR: b.normalStrikeRate,
  deltaSR: b.srDelta,
  dotPct: b.dotPct,
  bndPct: b.boundaryPct,
  consistencyPct: b.consistencyPct ?? 80.0,
  clutchScore: b.clutchScore,
  badge: b.recommendation || (b.rank === 1 ? "PRIORITY TARGET" : b.rank <= 3 ? "MAIN TARGET" : "TARGET ACQUIRE"),
  strengths: [
    `Elite ${(b.consistencyPct ?? 80.0).toFixed(1)}% match-level consistency`,
    `Strikes at ${b.strikeRate.toFixed(1)} under pressure (+${b.srDelta.toFixed(1)} surge)`,
    `Low dot ball rate (${b.dotPct.toFixed(1)}%) with ${b.boundaryPct.toFixed(1)}% boundary power`
  ]
}));

const _BOWLERS: Bowler[] = (clutchData.topBowlers || []).slice(0, 15).map((bw: any) => ({
  rank: bw.rank,
  name: bw.name,
  role: BOWLER_ROLES[bw.name] || "Pressure Containment Specialist",
  team: bw.team,
  country: bw.team.includes('Pakistan') ? 'PAK' :
           bw.team.includes('Chennai') || bw.team.includes('Sri Lanka') ? 'SL' :
           bw.team.includes('Afghanistan') ? 'AFG' :
           bw.team.includes('West Indies') ? 'WI' : 'IND',
  pBalls: bw.balls,
  pWkts: bw.wickets,
  pEcon: bw.economy,
  baseEcon: bw.normalEconomy,
  econDelta: bw.econDelta,
  dotPct: bw.dotPct,
  consistencyPct: bw.consistencyPct ?? 75.0,
  clutchScore: bw.clutchScore,
  badge: bw.recommendation || (bw.rank === 1 ? "PRIORITY TARGET" : bw.rank <= 3 ? "MAIN TARGET" : "TARGET ACQUIRE"),
  strengths: [
    `Delivers in ${(bw.consistencyPct ?? 75.0).toFixed(1)}% of high-tension matches`,
    `Concedes only ${bw.economy.toFixed(2)} RPO in crisis with ${bw.wickets} wickets`,
    `Forces ${bw.dotPct.toFixed(1)}% dot balls under match-deciding pressure`
  ]
}));
void _BATTERS;
void _BOWLERS;

interface ChatMessage {
  id: string;
  sender: 'user' | 'bot';
  text: string;
  verdict?: 'MUST BUY' | 'CONSIDER' | 'AVOID' | 'INFO';
  metrics?: { label: string; value: string }[];
  comparison?: ComparisonResult;
  coachAudit?: CoachShortlistAudit;
}

export default function App() {
  const [activePage, setActivePage] = useState<'leaderboard' | 'matrix' | 'auction' | 'playbook' | 'settings'>('leaderboard');
  const [roleFilter, setRoleFilter] = useState<'all' | 'bat' | 'bowl'>('all');
  const [searchQuery, setSearchQuery] = useState('');
    const [tableTab, setTableTab] = useState<'bat' | 'bowl'>('bat');
  const [phaseFilter, setPhaseFilter] = useState<'all' | 'powerplay' | 'middle' | 'death'>('all');
  
  // Interactive War Room Calibration Weights (Live Re-computation Engine)
  interface CalibrationParams {
    minBatBalls: number;
    minBowlBalls: number;
    minDeathBalls: number;
    consistencyWeight: number;
    srDeltaWeight: number;
    econWeight: number;
  }

  const DEFAULT_CALIB: CalibrationParams = {
    minBatBalls: 140,
    minBowlBalls: 140,
    minDeathBalls: 40,
    consistencyWeight: 1.0,
    srDeltaWeight: 0.70,
    econWeight: 14.0
  };

  const [activeCalib, setActiveCalib] = useState<CalibrationParams>(() => {
    try {
      const saved = localStorage.getItem('rr_active_calib_v3');
      if (saved) return JSON.parse(saved);
    } catch (e) {}
    return DEFAULT_CALIB;
  });

  const [pendingCalib, setPendingCalib] = useState<CalibrationParams>(() => {
    try {
      const saved = localStorage.getItem('rr_active_calib_v3');
      if (saved) return JSON.parse(saved);
    } catch (e) {}
    return DEFAULT_CALIB;
  });

  const [applyFeedback, setApplyFeedback] = useState<string | null>(null);

  const hasUnappliedChanges = useMemo(() => {
    return (
      pendingCalib.minBatBalls !== activeCalib.minBatBalls ||
      pendingCalib.minBowlBalls !== activeCalib.minBowlBalls ||
      pendingCalib.minDeathBalls !== activeCalib.minDeathBalls ||
      pendingCalib.consistencyWeight !== activeCalib.consistencyWeight ||
      pendingCalib.srDeltaWeight !== activeCalib.srDeltaWeight ||
      pendingCalib.econWeight !== activeCalib.econWeight
    );
  }, [pendingCalib, activeCalib]);

  // Dynamically recalculated Batters under custom calibration weights
  const dynamicBatters = useMemo(() => {
    return (clutchData.topBatters || [])
      .filter((b: any) => b.balls >= activeCalib.minBatBalls)
      .map((b: any) => {
        const clippedDelta = Math.max(-20, Math.min(50, b.srDelta));
        const raw = (b.strikeRate * 0.50) + (clippedDelta * activeCalib.srDeltaWeight) + (b.boundaryPct * 0.4) - (b.dotPct * 0.15);
        const rel = (1.0 - activeCalib.consistencyWeight) + activeCalib.consistencyWeight * (b.consistencyPct / 100.0);
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
          role: b.role || BATTER_ROLES[b.name] || "Crisis Batting Specialist",
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
  }, [activeCalib]);



  // Dynamically recalculated Bowlers under custom calibration weights
  const dynamicBowlers = useMemo(() => {
    return (clutchData.topBowlers || [])
      .filter((bw: any) => bw.balls >= activeCalib.minBowlBalls)
      .map((bw: any) => {
        const raw = (100 - bw.economy * activeCalib.econWeight) - (bw.econDelta * 5) + (bw.dotPct * 0.6) + (bw.wickets * 1.5);
        const rel = (1.0 - activeCalib.consistencyWeight) + activeCalib.consistencyWeight * (bw.consistencyPct / 100.0);
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
          role: bw.role || BOWLER_ROLES[bw.name] || "Pressure Containment Specialist",
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
  }, [activeCalib]);

  // Phase-specific derived lists for leaderboard view (with adaptive death specialist qualification)
  const displayedBatters = useMemo(() => {
    if (phaseFilter === 'all') return dynamicBatters;
    if (phaseFilter === 'death') {
      const specialists = ((clutchData as any).deathSpecialists || [])
        .filter((b: any) => (b.deathBalls || 0) >= activeCalib.minDeathBalls);
      if (specialists.length > 0) {
        return specialists.map((b: any, idx: number) => ({
          ...b,
          rank: idx + 1,
          balls: b.deathBalls,
          strikeRate: b.deathSR,
          normalStrikeRate: b.coldStartSR,
          srDelta: Math.round((b.deathSR - b.coldStartSR) * 10) / 10,
          boundaryPct: b.deathBdryPct,
          dotPct: b.deathDotPct,
          clutchScore: b.deathClutch,
          badge: idx === 0 ? "PRIORITY FINISHER" : idx < 3 ? "MAIN FINISHER" : "IMPACT FINISHER"
        }));
      }
    }
    return [...dynamicBatters]
      .filter(b => (b.phases?.[phaseFilter]?.balls || 0) >= 15)
      .sort((a, b) => (b.phases?.[phaseFilter]?.sr || 0) - (a.phases?.[phaseFilter]?.sr || 0));
  }, [dynamicBatters, phaseFilter, activeCalib.minDeathBalls]);

  const displayedBowlers = useMemo(() => {
    if (phaseFilter === 'all') return dynamicBowlers;
    return [...dynamicBowlers]
      .filter(bw => (bw.phases?.[phaseFilter]?.balls || 0) >= 15)
      .sort((a, b) => (a.phases?.[phaseFilter]?.econ || 99) - (b.phases?.[phaseFilter]?.econ || 99));
  }, [dynamicBowlers, phaseFilter]);
  
  // Preview calculated from pending slider adjustments in Settings
  const previewBatters = useMemo(() => {
    return (clutchData.topBatters || [])
      .filter((b: any) => b.balls >= pendingCalib.minBatBalls)
      .map((b: any) => {
        const clippedDelta = Math.max(-20, Math.min(50, b.srDelta));
        const raw = (b.strikeRate * 0.50) + (clippedDelta * pendingCalib.srDeltaWeight) + (b.boundaryPct * 0.4) - (b.dotPct * 0.15);
        const rel = (1.0 - pendingCalib.consistencyWeight) + pendingCalib.consistencyWeight * (b.consistencyPct / 100.0);
        const clutchScore = Math.round(raw * rel * 10) / 10;
        return { name: b.name, clutchScore };
      })
      .sort((a: any, b: any) => b.clutchScore - a.clutchScore);
  }, [pendingCalib]);

  const previewBowlers = useMemo(() => {
    return (clutchData.topBowlers || [])
      .filter((bw: any) => bw.balls >= pendingCalib.minBowlBalls)
      .map((bw: any) => {
        const raw = (100 - bw.economy * pendingCalib.econWeight) - (bw.econDelta * 5) + (bw.dotPct * 0.6) + (bw.wickets * 1.5);
        const rel = (1.0 - pendingCalib.consistencyWeight) + pendingCalib.consistencyWeight * (bw.consistencyPct / 100.0);
        const clutchScore = Math.round(raw * rel * 10) / 10;
        return { name: bw.name, clutchScore };
      })
      .sort((a: any, b: any) => b.clutchScore - a.clutchScore);
  }, [pendingCalib]);

  // Global Player Search & Modal State
  const [isSearchOpen, setIsSearchOpen] = useState(false);
  const [selectedPlayerModal, setSelectedPlayerModal] = useState<PlayerStat | null>(null);
  const searchContainerRef = useRef<HTMLDivElement>(null);

  const searchedPlayers = useMemo(() => {
    return searchPlayers(searchQuery, clutchData.players as any, 12);
  }, [searchQuery]);

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (searchContainerRef.current && !searchContainerRef.current.contains(event.target as Node)) {
        setIsSearchOpen(false);
      }
    }
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);
  
  const [selectedB1, setSelectedB1] = useState<string>("Naman Dhir");
  const [selectedB2, setSelectedB2] = useState<string>("Phil Salt");
  const [compareRole, setCompareRole] = useState<'bat' | 'bowl'>('bat');
  const [selectedBW1, setSelectedBW1] = useState<string>("Arshdeep Singh");
  const [selectedBW2, setSelectedBW2] = useState<string>("Matheesha Pathirana");

  // Coach Shortlist State
  const [coachShortlist, setCoachShortlist] = useState<string[]>(() => {
    try {
      const saved = localStorage.getItem('rr_coach_shortlist');
      if (saved) return JSON.parse(saved);
    } catch (e) {}
    return ['Naman Dhir', 'Phil Salt', 'Matheesha Pathirana', 'Arshdeep Singh', 'Rashid Khan'];
  });
  const [isShortlistOpen, setIsShortlistOpen] = useState(false);
  const [shortlistInput, setShortlistInput] = useState('');

  useEffect(() => {
    try {
      localStorage.setItem('rr_coach_shortlist', JSON.stringify(coachShortlist));
    } catch (e) {}
  }, [coachShortlist]);

  // Sync modal and drawer open states to body class so floating nav is strictly hidden
  useEffect(() => {
    if (selectedPlayerModal) {
      document.body.classList.add('modal-open');
    } else {
      document.body.classList.remove('modal-open');
    }
  }, [selectedPlayerModal]);

  useEffect(() => {
    if (isShortlistOpen) {
      document.body.classList.add('shortlist-open');
    } else {
      document.body.classList.remove('shortlist-open');
    }
  }, [isShortlistOpen]);

  const togglePlayerInShortlist = (name: string) => {
    setCoachShortlist(prev => {
      if (prev.includes(name)) return prev.filter(n => n !== name);
      return [...prev, name];
    });
  };

  const addCustomPlayerToShortlist = (name: string) => {
    const trimmed = name.trim();
    if (!trimmed) return;
    if (!coachShortlist.includes(trimmed)) {
      setCoachShortlist(prev => [...prev, trimmed]);
    }
    setShortlistInput('');
  };

  // Scout Bot State
  const [isBotOpen, setIsBotOpen] = useState(false);

  useEffect(() => {
    if (isBotOpen) {
      document.body.classList.add('scout-open');
    } else {
      document.body.classList.remove('scout-open');
    }
  }, [isBotOpen]);
  const [chatInput, setChatInput] = useState('');
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([
    {
      id: '1',
      sender: 'bot',
      text: "Royals Scout Engine online. I can audit coach shortlists, evaluate player viability under crisis, compare players head-to-head, and recommend 2027 auction targets based strictly on our 200,999-ball high-pressure dataset.",
      verdict: 'INFO'
    }
  ]);
  const chatEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (isBotOpen) {
      chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }
  }, [chatMessages, isBotOpen]);

  // Coach Shortlist Audit Execution
  const triggerCoachAudit = (customList?: string[]) => {
    const listToAudit = customList || coachShortlist;
    const audit = auditCoachShortlist(listToAudit, clutchData.players as any, clutchData);
    
    const botResponse: ChatMessage = {
      id: Date.now().toString(),
      sender: 'bot',
      text: `Coach Shortlist Evaluation (${audit.totalPlayers} Targets Analyzed): Grade ${audit.grade}. ${audit.buyCount} must-buys, ${audit.monitorCount} value options, and ${audit.avoidCount} trap picks detected against our 200,999-ball index.`,
      coachAudit: audit
    };

    setChatMessages(prev => [...prev, botResponse]);
    setIsBotOpen(true);
    setIsShortlistOpen(false);
  };

  // Deterministic evaluation function for Scout Bot (Zero AI, 100% Rule & Index Based)
  const handleSendMessage = (overrideQuery?: string) => {
    const query = (overrideQuery !== undefined ? overrideQuery : chatInput).trim();
    if (!query) return;

    const userMsg: ChatMessage = {
      id: Date.now().toString(),
      sender: 'user',
      text: query
    };

    setChatMessages(prev => [...prev, userMsg]);
    if (overrideQuery === undefined) setChatInput('');

    // Process query deterministically
    setTimeout(() => {
      const lower = query.toLowerCase();
      let botResponse: ChatMessage;

      // 1. COACH SHORTLIST EVALUATION
      if (lower.includes('audit coach') || lower.includes('shortlist') || lower.includes('coach list') || lower.includes('coach targets')) {
        const audit = auditCoachShortlist(coachShortlist, clutchData.players as any, clutchData);
        botResponse = {
          id: (Date.now() + 1).toString(),
          sender: 'bot',
          text: `Scout Audit of Coach's ${audit.totalPlayers} Shortlisted Targets: Grade ${audit.grade}. ${audit.buyCount} verified clutch buys, ${audit.monitorCount} value monitors, and ${audit.avoidCount} trap picks detected.`,
          coachAudit: audit
        };
      }
      // 2. HEAD-TO-HEAD COMPARISON (e.g. "Salt vs Dube", "compare bumrah and pathirana")
      else if (lower.includes(' vs ') || lower.includes('compare ') || (lower.includes('who is better') && lower.includes(' or '))) {
        let p1Name = "";
        let p2Name = "";

        if (lower.includes(' vs ')) {
          const parts = query.split(/ vs /i);
          p1Name = parts[0].replace(/compare/i, '').trim();
          p2Name = parts[1].trim();
        } else if (lower.includes('compare ')) {
          const clean = query.replace(/compare/i, '').trim();
          const parts = clean.split(/ and | & /i);
          p1Name = parts[0]?.trim();
          p2Name = parts[1]?.trim();
        } else if (lower.includes('who is better')) {
          const clean = query.replace(/who is better (between )?/i, '').trim();
          const parts = clean.split(/ or | and /i);
          p1Name = parts[0]?.trim();
          p2Name = parts[1]?.trim();
        }

        const compResult = compareTwoPlayers(p1Name, p2Name, clutchData.players as any);
        if (compResult) {
          botResponse = {
            id: (Date.now() + 1).toString(),
            sender: 'bot',
            text: `Head-to-Head Comparison: ${compResult.p1.name} vs ${compResult.p2.name}. ${compResult.rationale}`,
            verdict: compResult.verdictWinner !== 'TIE / CONTEXT DEPENDENT' ? 'MUST BUY' : 'CONSIDER',
            comparison: compResult
          };
        } else {
          botResponse = {
            id: (Date.now() + 1).toString(),
            sender: 'bot',
            text: `Could not identify both players for comparison in our dataset. Try specific player names like "Phil Salt vs Shivam Dube" or "Jasprit Bumrah vs Matheesha Pathirana".`,
            verdict: 'INFO'
          };
        }
      }
      // 3. RR SPECIFIC TACTICAL QUESTIONS (Death overs, spin crushers)
      else if (lower.includes('finisher') || lower.includes('death bat') || lower.includes('death over bat') || lower.includes('lower order')) {
        const topFinishers = ((clutchData as any).deathSpecialists || []).slice(0, 3);
        botResponse = {
          id: (Date.now() + 1).toString(),
          sender: 'bot',
          text: `RR Tactical Solution for Crisis Finishers (Overs 16–20): Finishers face fewer deliveries per game (~10-15 balls), so we evaluate them using a phase-normalized ≥40 death ball sample. Top verified impact finishers are: 1) ${topFinishers[0]?.name || 'Naman Dhir'} (${topFinishers[0]?.deathSR || 193.0} Death SR, ${topFinishers[0]?.deathBdryPct || 29.9}% boundaries), 2) ${topFinishers[1]?.name || 'Phil Salt'}, and 3) ${topFinishers[2]?.name || 'Ashutosh Sharma'}. All strike at 175+ at the death with zero setup time.`,
          verdict: 'MUST BUY',
          metrics: [
            { label: '#1 Finisher', value: `${topFinishers[0]?.name || 'Naman Dhir'} (${topFinishers[0]?.deathSR || 193.0} SR)` },
            { label: 'Death Boundary %', value: `${topFinishers[0]?.deathBdryPct || 29.9}% at Death` },
            { label: 'Tactical Value', value: 'Eliminates reliance on top-order batting' }
          ]
        };
      }
      else if (lower.includes('death over') || lower.includes('death bowling') || lower.includes('solve death')) {
        const top1 = clutchData.topBowlers[1]; // Pathirana
        const top2 = clutchData.topBowlers[0]; // Arshdeep
        botResponse = {
          id: (Date.now() + 1).toString(),
          sender: 'bot',
          text: `RR Tactical Solution for Death Overs (Overs 17–20): Our 200k-ball index proves Matheesha Pathirana (${top1.economy} pressure economy, 53 wkts) and Arshdeep Singh (${top2.economy} economy, 91 wkts) are the two highest-conviction targets. Both hold negative elevation deltas, meaning their execution sharpens rather than falters when target defenses reach 10+ RRR.`,
          verdict: 'MUST BUY',
          metrics: [
            { label: 'Priority Target 1', value: `${top1.name} (${top1.economy} Econ, 53 Wkts)` },
            { label: 'Priority Target 2', value: `${top2.name} (${top2.economy} Econ, 91 Wkts)` },
            { label: 'RR Squad Fit', value: 'Resolves Sandeep Sharma death-over isolation' }
          ]
        };
      }
      // 4. BEST ALL-ROUNDER
      else if (lower.includes('all rounder') || lower.includes('allrounder') || lower.includes('all-rounder')) {
        const top1 = clutchData.topAllRounders[0];
        const top2 = clutchData.topAllRounders[1];
        const top3 = clutchData.topAllRounders[2];
        botResponse = {
          id: (Date.now() + 1).toString(),
          sender: 'bot',
          text: `Top Clutch All-Rounder Identified: ${top1.name} (${top1.team}) ranks #1 with a ${top1.clutchScore} Clutch Rating across ${top1.batBalls} pressure balls faced (${top1.batSR} SR, +${top1.srDelta} delta) and ${top1.bowlBalls} pressure balls bowled (${top1.bowlWkts} wkts, ${top1.bowlEcon} econ). Followed closely by ${top2.name} and ${top3.name}.`,
          verdict: 'MUST BUY',
          metrics: [
            { label: `#1 All-Rounder`, value: `${top1.name} (${top1.clutchScore} Clutch)` },
            { label: `Batting Punch`, value: `${top1.batSR} SR (+${top1.srDelta} Delta)` },
            { label: `Bowling Pressure`, value: `${top1.bowlWkts} Wkts (${top1.bowlEcon} Econ)` }
          ]
        };
      }
      // 5. BEST BOWLER
      else if (lower.includes('best bowler') || lower.includes('top bowler') || lower.includes('who is the bowler')) {
        const top1 = clutchData.topBowlers[0];
        const top2 = clutchData.topBowlers[1];
        const top3 = clutchData.topBowlers[2];
        botResponse = {
          id: (Date.now() + 1).toString(),
          sender: 'bot',
          text: `Top Pressure Bowler: ${top1.name} (${top1.team}) is ranked #1 in high-stress leverage with ${top1.wickets} wickets across ${top1.balls} pressure balls (${top1.economy} Econ). For pure death-overs suppression (overs 17–20), ${top2.name} delivers an unplayable ${top2.economy} economy with ${top2.wickets} wickets. ${top3.name} is ranked #3.`,
          verdict: 'MUST BUY',
          metrics: [
            { label: `#1 Bowler Overall`, value: `${top1.name} (${top1.wickets} Wkts)` },
            { label: `#2 Death Lockdown`, value: `${top2.name} (${top2.economy} Econ)` },
            { label: `#3 Clutch Pacer`, value: `${top3.name} (${top3.wickets} Wkts)` }
          ]
        };
      }
      // 6. BEST BATSMAN / BATTER
      else if (lower.includes('best batsman') || lower.includes('best batter') || lower.includes('top batter') || lower.includes('top batsman') || lower.includes('finisher')) {
        const top1 = clutchData.topBatters[0];
        const top2 = clutchData.topBatters[1];
        const top3 = clutchData.topBatters[2];
        botResponse = {
          id: (Date.now() + 1).toString(),
          sender: 'bot',
          text: `Top Pressure Batter: ${top1.name} (${top1.team}) ranks #1 with a ${top1.strikeRate} Strike Rate under pressure and an unprecedented +${top1.srDelta} surge. ${top2.name} is #2 with ${top2.strikeRate} SR, and ${top3.name} ranks #3 (${top3.strikeRate} SR, +${top3.srDelta} surge).`,
          verdict: 'MUST BUY',
          metrics: [
            { label: `#1 Pressure Batter`, value: `${top1.name} (${top1.strikeRate} SR)` },
            { label: `Pressure Boost`, value: `+${top1.srDelta} SR Elevation` },
            { label: `#2 Ranked Batter`, value: `${top2.name} (${top2.strikeRate} SR)` }
          ]
        };
      }
      // 7. DATASETS / SUBMISSION QUERY
      else if (lower.includes('dataset') || lower.includes('submit') || lower.includes('submission') || lower.includes('csv')) {
        botResponse = {
          id: (Date.now() + 1).toString(),
          sender: 'bot',
          text: `All 6 competition datasets are ingested live: ball_by_ball (200k balls), matches (883 matches, RRR & Knockout 1.25x), competitions (141 tournaments, IPL weight), teams (353 teams), playing_eleven (28k entries, batting orders & roles), mapping (entity resolution). To win 1000%, submit the exact Top 10 Batters & Bowlers on Unstop dropdowns alongside the comprehensive Methodology Report PDF!`,
          verdict: 'INFO',
          metrics: [
            { label: 'Deliveries Ingested', value: `${clutchData.metadata.totalDeliveries.toLocaleString()}` },
            { label: 'High Pressure Balls', value: `${clutchData.metadata.highPressureDeliveries.toLocaleString()} (${clutchData.metadata.highPressurePct}%)` },
            { label: 'Indexed Players', value: `${Object.keys(clutchData.players).length} Players` }
          ]
        };
      }
      // 8. DYNAMIC FUZZY LOOKUP ACROSS ALL PLAYERS IN DATASET
      else {
        const p = findBestPlayerMatch(query, clutchData.players as any);

        if (p) {
          const hasBat = p.batting !== null && p.batting !== undefined;
          const hasBowl = p.bowling !== null && p.bowling !== undefined;
          const metricsList = [];

          if (hasBat && p.batting) {
            metricsList.push({ label: 'Pressure SR', value: `${p.batting.p_sr} (${p.batting.sr_delta >= 0 ? '+' : ''}${p.batting.sr_delta} delta)` });
            metricsList.push({ label: 'Balls Faced', value: `${p.batting.p_balls} balls` });
            metricsList.push({ label: 'Boundary %', value: `${p.batting.p_bdry_pct}%` });
          }
          if (hasBowl && p.bowling) {
            metricsList.push({ label: 'Pressure Econ', value: `${p.bowling.p_econ} (${p.bowling.econ_delta >= 0 ? '+' : ''}${p.bowling.econ_delta} delta)` });
            metricsList.push({ label: 'Pressure Wkts', value: `${p.bowling.p_wkts} wkts` });
            metricsList.push({ label: 'Dot %', value: `${p.bowling.p_dot_pct}%` });
          }
          metricsList.push({ label: 'Clutch Score', value: `${p.clutchScore}` });

          botResponse = {
            id: (Date.now() + 1).toString(),
            sender: 'bot',
            text: `${p.name} (${p.team} | ${p.role}): ${p.verdict}. ${p.summary}`,
            verdict: p.verdictClass === 'buy' ? 'MUST BUY' : p.verdictClass === 'monitor' ? 'CONSIDER' : 'AVOID',
            metrics: metricsList
          };
        } else {
          botResponse = {
            id: (Date.now() + 1).toString(),
            sender: 'bot',
            text: `I scanned our 200,999-ball dataset for "${query}". You can ask me to "Audit coach shortlist", compare players (e.g. "Salt vs Dube"), query top targets (e.g. "solve death bowling"), or look up any player directly.`,
            verdict: 'INFO'
          };
        }
      }

      setChatMessages(prev => [...prev, botResponse]);
    }, 180);
  };

  const p1 = dynamicBatters.find(b => b.name === selectedB1) || dynamicBatters[0];
  const p2 = dynamicBatters.find(b => b.name === selectedB2) || dynamicBatters[1];
  const bw1 = dynamicBowlers.find(b => b.name === selectedBW1) || dynamicBowlers[0];
  const bw2 = dynamicBowlers.find(b => b.name === selectedBW2) || dynamicBowlers[1];



  // The 4 main modules + settings directly in the capsule dock
  const dockNavItems = [
    { id: 'leaderboard', icon: Trophy, label: 'Leaderboard', title: 'Top High Tension Performers' },
    { id: 'matrix', icon: Crosshair, label: 'Matrix Compare', title: 'Head-to-Head Comparison (15 Batters & 15 Bowlers)' },
    { id: 'auction', icon: Target, label: 'War Room 2027', title: 'Fixing the 4 Major Flaws & Targets' },
    { id: 'playbook', icon: Shield, label: 'Coaches Playbook', title: '4 Crucial Match Directives' },
    { id: 'settings', icon: Settings, label: 'Settings', title: 'Model & Metric Parameters' }
  ];

  return (
    <div className="app-container">
      
      {/* OUTER APP FRAME */}
      <div className="glass-surface app-layout">

        {/* 1. COMPACT CAPSULE SIDEBAR DOCK (LEFT ON DESKTOP ONLY) */}
        <aside className="app-aside desktop-aside">
          <div className="pill-dock">
            {dockNavItems.map(item => {
              const Icon = item.icon;
              const isActive = activePage === item.id;
              return (
                <button
                  key={item.id}
                  onClick={() => setActivePage(item.id as any)}
                  className={`dock-btn ${isActive ? 'active' : ''}`}
                  aria-label={item.label}
                >
                  <Icon size={19} strokeWidth={isActive ? 2.3 : 1.9} />
                  <span className="dock-tooltip">{item.label}</span>
                </button>
              );
            })}
          </div>

          {/* RAJASTHAN ROYALS OFFICIAL CREST */}
          <div 
            className="sidebar-crest"
            style={{
              marginTop: 'auto',
              width: '44px',
              height: '44px',
              borderRadius: '50%',
              background: '#FFFFFF',
              border: '1px solid rgba(230, 0, 126, 0.25)',
              boxShadow: '0 4px 16px rgba(230, 0, 126, 0.18)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              padding: '4px',
              cursor: 'pointer'
            }}
            title="Rajasthan Royals"
          >
            <img 
              src={rrLogo} 
              alt="Rajasthan Royals Crest" 
              style={{ width: '100%', height: '100%', objectFit: 'contain' }} 
            />
          </div>
        </aside>

        {/* 2. MAIN APPLICATION CONTENT CANVAS */}
        <main className="app-main">
          
          {/* TOP APP HEADER BAR */}
          <header className="app-header">
            {/* BRAND / SITE LOGO & TITLE */}
            <div 
              className="header-brand-title"
              onClick={() => setActivePage('leaderboard')}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                cursor: 'pointer',
                flexShrink: 0,
                textDecoration: 'none',
                userSelect: 'none'
              }}
              title="SupeRR · Rajasthan Royals Official Intelligence Platform"
            >
              <div style={{
                width: '32px',
                height: '32px',
                borderRadius: '50%',
                background: '#FFFFFF',
                border: '1.5px solid rgba(230, 0, 126, 0.25)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                padding: '3px',
                boxShadow: '0 2px 8px rgba(230,0,126,0.15)'
              }}>
                <img src={rrLogo} alt="RR Crest" style={{ width: '100%', height: '100%', objectFit: 'contain' }} />
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', lineHeight: 1 }}>
                <span style={{
                  fontSize: '1.15rem',
                  fontWeight: 900,
                  letterSpacing: '-0.02em',
                  color: 'var(--rr-blue)',
                  display: 'flex',
                  alignItems: 'center'
                }}>
                  Supe<span style={{ color: 'var(--rr-pink)' }}>RR</span>
                </span>
                <span style={{
                  fontSize: '0.58rem',
                  fontWeight: 800,
                  letterSpacing: '0.08em',
                  textTransform: 'uppercase',
                  color: 'var(--text-muted)'
                }}>
                  Selector S2
                </span>
              </div>
            </div>

            {/* SEARCH CAPSULE WITH INTEGRATED SEARCH BUTTON & LIVE RESULTS FLYOUT */}
            <div 
              ref={searchContainerRef}
              className="search-capsule-container"
            >
              <div 
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '6px',
                  height: '38px',
                  padding: '0 4px 0 12px',
                  borderRadius: '999px',
                  background: '#FFFFFF',
                  border: isSearchOpen && searchQuery ? '1px solid var(--rr-pink)' : '1px solid rgba(15, 23, 42, 0.1)',
                  boxShadow: isSearchOpen && searchQuery ? '0 4px 14px rgba(230,0,126,0.12)' : '0 2px 6px rgba(15, 23, 42, 0.04)',
                  transition: 'all 0.2s ease'
                }}
              >
                <Search size={14} color={isSearchOpen && searchQuery ? 'var(--rr-pink)' : 'var(--text-muted)'} style={{ flexShrink: 0 }} />
                <input
                  type="text"
                  placeholder="Search player (e.g. Ahmed)..."
                  value={searchQuery}
                  onFocus={() => setIsSearchOpen(true)}
                  onChange={(e) => {
                    setSearchQuery(e.target.value);
                    setIsSearchOpen(true);
                  }}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter') {
                      if (searchedPlayers.length > 0) {
                        setSelectedPlayerModal(searchedPlayers[0]);
                        setIsSearchOpen(false);
                      }
                    }
                  }}
                  style={{
                    border: 'none',
                    outline: 'none',
                    background: 'transparent',
                    fontSize: '0.8rem',
                    fontWeight: 500,
                    color: 'var(--text-primary)',
                    width: '100%',
                    minWidth: 0
                  }}
                />
                {searchQuery && (
                  <button
                    onClick={() => {
                      setSearchQuery('');
                      setIsSearchOpen(false);
                    }}
                    style={{
                      background: 'none',
                      border: 'none',
                      cursor: 'pointer',
                      padding: '2px',
                      display: 'flex',
                      alignItems: 'center',
                      color: 'var(--text-muted)'
                    }}
                    title="Clear search"
                  >
                    <X size={13} />
                  </button>
                )}
                {/* Search Action Button Capsule */}
                <button
                  onClick={() => {
                    if (searchedPlayers.length > 0) {
                      setSelectedPlayerModal(searchedPlayers[0]);
                      setIsSearchOpen(false);
                    } else if (searchQuery.trim().length > 0) {
                      setIsSearchOpen(true);
                    }
                  }}
                  style={{
                    height: '28px',
                    padding: '0 10px',
                    borderRadius: '999px',
                    background: 'linear-gradient(135deg, var(--rr-pink) 0%, #C4006B 100%)',
                    color: '#FFFFFF',
                    border: 'none',
                    fontWeight: 700,
                    fontSize: '0.72rem',
                    cursor: 'pointer',
                    display: 'inline-flex',
                    alignItems: 'center',
                    whiteSpace: 'nowrap',
                    flexShrink: 0,
                    boxShadow: '0 2px 6px rgba(230,0,126,0.22)',
                    transition: 'all 0.15s ease'
                  }}
                  title="Search tournament database"
                >
                  Search
                </button>
              </div>

              {/* Instant Search Results Dropdown Flyout */}
              {isSearchOpen && searchQuery.trim().length >= 2 && (
                <div style={{
                  position: 'absolute',
                  top: '44px',
                  left: 0,
                  width: 'min(380px, calc(100vw - 32px))',
                  maxHeight: '380px',
                  overflowY: 'auto',
                  background: '#FFFFFF',
                  borderRadius: '16px',
                  border: '1px solid rgba(15, 23, 42, 0.1)',
                  boxShadow: '0 20px 40px -10px rgba(15, 23, 42, 0.2), 0 0 1px 1px rgba(0,0,0,0.04)',
                  padding: '8px',
                  zIndex: 1000
                }}>
                  <div style={{ 
                    padding: '6px 10px', 
                    fontSize: '0.7rem', 
                    fontWeight: 800, 
                    color: 'var(--text-muted)', 
                    textTransform: 'uppercase', 
                    letterSpacing: '0.05em',
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    borderBottom: '1px solid rgba(15, 23, 42, 0.06)',
                    marginBottom: '4px'
                  }}>
                    <span>Matches for "{searchQuery}" ({searchedPlayers.length})</span>
                    <span style={{ fontSize: '0.65rem', color: 'var(--rr-pink)' }}>Click to view details</span>
                  </div>

                  {searchedPlayers.length === 0 ? (
                    <div style={{ padding: '24px 16px', textAlign: 'center', color: 'var(--text-muted)', fontSize: '0.8rem' }}>
                      No players found matching "{searchQuery}" in 793 registered players.
                    </div>
                  ) : (
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
                      {searchedPlayers.map(p => {
                        const isBowler = p.role.toLowerCase().includes('bowl') || (!p.batting && p.bowling);
                        return (
                          <div
                            key={p.name}
                            onClick={() => {
                              setSelectedPlayerModal(p);
                              setIsSearchOpen(false);
                            }}
                            style={{
                              padding: '10px 12px',
                              borderRadius: '10px',
                              cursor: 'pointer',
                              transition: 'all 0.15s ease',
                              background: '#F8FAFC',
                              border: '1px solid rgba(15, 23, 42, 0.04)',
                              display: 'flex',
                              flexDirection: 'column',
                              gap: '4px'
                            }}
                            onMouseEnter={(e) => {
                              e.currentTarget.style.background = '#FFF5F9';
                              e.currentTarget.style.borderColor = 'rgba(230, 0, 126, 0.25)';
                            }}
                            onMouseLeave={(e) => {
                              e.currentTarget.style.background = '#F8FAFC';
                              e.currentTarget.style.borderColor = 'rgba(15, 23, 42, 0.04)';
                            }}
                          >
                            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                                <span style={{ fontWeight: 800, fontSize: '0.84rem', color: 'var(--text-primary)' }}>{p.name}</span>
                                <span style={{
                                  fontSize: '0.65rem',
                                  fontWeight: 700,
                                  padding: '2px 7px',
                                  borderRadius: '999px',
                                  background: isBowler ? 'rgba(6, 95, 70, 0.1)' : 'rgba(230, 0, 126, 0.1)',
                                  color: isBowler ? '#065F46' : 'var(--rr-pink)'
                                }}>
                                  {p.role}
                                </span>
                              </div>
                              <div style={{
                                fontSize: '0.74rem',
                                fontWeight: 800,
                                color: p.clutchScore >= 100 ? '#15803D' : p.clutchScore >= 70 ? 'var(--rr-blue)' : '#64748B',
                                background: '#FFFFFF',
                                padding: '2px 8px',
                                borderRadius: '6px',
                                border: '1px solid rgba(15, 23, 42, 0.08)'
                              }}>
                                Clutch: {p.clutchScore.toFixed(1)}
                              </div>
                            </div>

                            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', fontSize: '0.72rem', color: 'var(--text-secondary)' }}>
                              <span style={{ color: 'var(--text-muted)' }}>{p.team || 'Tournament Player'}</span>
                              <span>
                                {isBowler && p.bowling ? (
                                  `P-Econ: ${p.bowling.p_econ} | Wkts: ${p.bowling.p_wkts} | Econ Delta: ${p.bowling.econ_delta > 0 ? '-' : '+'}${Math.abs(p.bowling.econ_delta).toFixed(2)}`
                                ) : p.batting ? (
                                  `P-SR: ${p.batting.p_sr} | Boost: ${p.batting.sr_delta > 0 ? '+' : ''}${p.batting.sr_delta.toFixed(1)} | Dot: ${p.batting.p_dot_pct}%`
                                ) : (
                                  `Clutch Rating: ${p.clutchScore.toFixed(1)}`
                                )}
                              </span>
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  )}
                </div>
              )}
            </div>

            {/* Header Center Title & Official Report Button */}
            <div className="header-title-group" style={{ display: 'flex', alignItems: 'center', gap: '8px', flexShrink: 0 }}>
              {/* Current Active Page Title Indicator (Compact Pill) */}
              <div 
                className="header-page-title"
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '6px',
                  padding: '5px 12px',
                  borderRadius: '999px',
                  background: 'rgba(230, 0, 126, 0.05)',
                  border: '1px solid rgba(230, 0, 126, 0.12)',
                  whiteSpace: 'nowrap',
                  flexShrink: 0
                }}
              >
                <span style={{
                  fontSize: '0.72rem',
                  fontWeight: 800,
                  color: 'var(--rr-pink)',
                  letterSpacing: '0.08em',
                  textTransform: 'uppercase'
                }}>
                  {dockNavItems.find(d => d.id === activePage)?.label}
                </span>
              </div>

              {/* OFFICIAL METHODOLOGY REPORT BUTTON */}
              <a
                href="./Royals_SupeRR_Selector_Season_2_Methodology_Report.pdf"
                target="_blank"
                rel="noopener noreferrer"
                className="header-report-btn"
                title="Open Official Methodology Report (5-Page PDF)"
              >
                <FileText size={13} className="header-report-icon" />
                <span className="header-report-btn-text">Report PDF</span>
                <ArrowUpRight size={11} className="header-report-arrow" />
              </a>
            </div>

            {/* Scout Bot Launcher Button & Coach Shortlist & Profile */}
            <div className="header-actions">
              
              {/* COACH SHORTLIST TRIGGER */}
              <button
                onClick={() => setIsShortlistOpen(!isShortlistOpen)}
                style={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: '6px',
                  height: '38px',
                  padding: '0 12px',
                  borderRadius: '999px',
                  background: isShortlistOpen ? 'linear-gradient(135deg, #0E3696 0%, #082467 100%)' : '#FFFFFF',
                  color: isShortlistOpen ? '#FFFFFF' : 'var(--text-primary)',
                  border: isShortlistOpen ? '1px solid #0E3696' : '1px solid rgba(14, 54, 150, 0.16)',
                  cursor: 'pointer',
                  boxShadow: isShortlistOpen ? '0 4px 12px rgba(14, 54, 150, 0.25)' : '0 2px 6px rgba(15, 23, 42, 0.03)',
                  fontWeight: 700,
                  fontSize: '0.78rem',
                  whiteSpace: 'nowrap',
                  flexShrink: 0,
                  transition: 'all 0.2s cubic-bezier(0.16, 1, 0.3, 1)'
                }}
                title="Coach Target Shortlist"
              >
                <ClipboardList size={14} color={isShortlistOpen ? '#FFFFFF' : 'var(--rr-blue)'} />
                <span className="header-btn-text">Coach Shortlist</span>
                <span 
                  className="badge-count"
                  style={{
                    minWidth: '18px',
                    height: '18px',
                    padding: '0 5px',
                    borderRadius: '999px',
                    fontSize: '0.68rem',
                    fontWeight: 800,
                    display: 'inline-flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    background: isShortlistOpen ? 'rgba(255,255,255,0.25)' : 'rgba(14, 54, 150, 0.1)',
                    color: isShortlistOpen ? '#FFFFFF' : 'var(--rr-blue)'
                  }}
                >
                  {coachShortlist.length}
                </span>
              </button>

              {/* ROYALS SCOUT BOT TRIGGER */}
              <button
                onClick={() => setIsBotOpen(!isBotOpen)}
                style={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: '6px',
                  height: '38px',
                  padding: '0 12px',
                  borderRadius: '999px',
                  background: isBotOpen ? 'linear-gradient(135deg, #E6007E 0%, #C4006B 100%)' : '#FFFFFF',
                  color: isBotOpen ? '#FFFFFF' : 'var(--text-primary)',
                  border: isBotOpen ? '1px solid #E6007E' : '1px solid rgba(230, 0, 126, 0.2)',
                  cursor: 'pointer',
                  boxShadow: isBotOpen ? '0 4px 12px rgba(230, 0, 126, 0.28)' : '0 2px 6px rgba(15, 23, 42, 0.03)',
                  fontWeight: 700,
                  fontSize: '0.78rem',
                  whiteSpace: 'nowrap',
                  flexShrink: 0,
                  transition: 'all 0.2s cubic-bezier(0.16, 1, 0.3, 1)'
                }}
                title="Royals Scout Bot - Deterministic Index Evaluator"
              >
                <Bot size={14} color={isBotOpen ? '#FFFFFF' : 'var(--rr-pink)'} />
                <span className="header-btn-text">Royals Scout</span>
                <span style={{
                  width: '6px',
                  height: '6px',
                  borderRadius: '50%',
                  background: isBotOpen ? '#FFFFFF' : '#10B981',
                  boxShadow: isBotOpen ? '0 0 6px #FFFFFF' : '0 0 0 2px rgba(16, 185, 129, 0.2), 0 0 6px #10B981',
                  flexShrink: 0
                }} />
              </button>

              {/* Profile Emblem Avatar Badge with RR Logo */}
              <div 
                style={{
                  width: '38px',
                  height: '38px',
                  borderRadius: '50%',
                  background: 'linear-gradient(135deg, #FFF0F6 0%, #FFFFFF 100%)',
                  border: '1.5px solid rgba(230, 0, 126, 0.25)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  padding: '4px',
                  boxShadow: '0 2px 8px rgba(230,0,126,0.12)',
                  cursor: 'pointer',
                  flexShrink: 0,
                  transition: 'all 0.2s ease'
                }}
                title="Rajasthan Royals · SupeRR War Room"
              >
                <img 
                  src={rrLogo} 
                  alt="RR Crest" 
                  style={{ width: '100%', height: '100%', objectFit: 'contain' }} 
                />
              </div>


            </div>
          </header>

          {/* ========================================================================= */}
          {/* PAGE 1: LEADERBOARD                                                       */}
          {/* ========================================================================= */}
          {activePage === 'leaderboard' && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '20px', flex: 1, overflowY: 'auto', paddingRight: '4px' }}>
              
              {/* UPPER SECTION: Split Left Highlights + Main Trending Hero Feature */}
              <div className="hero-split-grid" style={{ alignItems: 'stretch' }}>
                
                {/* Left Mini Highlights Column */}
                <div className="glass-card" style={{ padding: '20px', display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
                  <div>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
                      <span style={{ fontSize: '0.85rem', fontWeight: 800, color: 'var(--text-primary)', display: 'flex', alignItems: 'center', gap: '6px' }}>
                        🔥 Tactical Insights
                      </span>
                      <span style={{ fontSize: '0.72rem', color: 'var(--text-muted)', fontWeight: 600 }}>Live Feed</span>
                    </div>

                    <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                      {/* Sub-Card 1: Naman Dhir */}
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
                      </div>
                    </div>
                  </div>

                  <div style={{
                    paddingTop: '12px',
                    borderTop: '1px solid rgba(15, 23, 42, 0.06)',
                    display: 'flex',
                    justifyContent: 'space-between',
                    fontSize: '0.72rem',
                    color: 'var(--text-muted)'
                  }}>
                    <span>High-Pressure Performance & Consistency Engine</span>
                    <span style={{ fontWeight: 800, color: 'var(--rr-pink)' }}>200,999 Balls Ingested</span>
                  </div>
                </div>

                {/* Right Big Hero Card */}
                <div className="glass-card hero-card" style={{
                  padding: '36px 40px',
                  position: 'relative',
                  overflow: 'hidden',
                  background: 'linear-gradient(135deg, rgba(14, 54, 150, 0.94) 0%, rgba(230, 0, 126, 0.90) 100%)',
                  color: '#FFFFFF',
                  display: 'flex',
                  flexDirection: 'column',
                  justifyContent: 'space-between',
                  boxShadow: '0 20px 40px -10px rgba(230, 0, 126, 0.28)'
                }}>
                  <div style={{
                    position: 'absolute',
                    right: '-40px',
                    top: '-40px',
                    width: '300px',
                    height: '300px',
                    borderRadius: '50%',
                    background: 'radial-gradient(circle, rgba(255,255,255,0.2) 0%, transparent 70%)',
                    pointerEvents: 'none'
                  }} />

                  <div>
                    <div style={{ display: 'flex', gap: '8px', marginBottom: '14px' }}>
                      <span style={{
                        padding: '4px 12px',
                        borderRadius: '999px',
                        background: 'rgba(255, 255, 255, 0.2)',
                        backdropFilter: 'blur(10px)',
                        fontSize: '0.72rem',
                        fontWeight: 800,
                        letterSpacing: '0.08em'
                      }}>
                        TOP PRIORITY PICK
                      </span>
                      <span style={{
                        padding: '4px 12px',
                        borderRadius: '999px',
                        background: 'rgba(255, 255, 255, 0.12)',
                        backdropFilter: 'blur(10px)',
                        fontSize: '0.72rem',
                        fontWeight: 700
                      }}>
                        IPL 2027 AUCTION
                      </span>
                    </div>

                    <h2 style={{
                      margin: '0 0 10px 0',
                      fontSize: '2.1rem',
                      fontWeight: 900,
                      letterSpacing: '-0.03em',
                      color: '#FFFFFF'
                    }}>
                      Matheesha Pathirana
                    </h2>

                    <p style={{
                      margin: 0,
                      maxWidth: '560px',
                      fontSize: '0.92rem',
                      lineHeight: 1.55,
                      color: 'rgba(255, 255, 255, 0.88)',
                      fontWeight: 400
                    }}>
                      The ultimate high-tension death overs weapon. Unmatched 6.55 economy across 519 high-stress match balls with 53 wickets, shutting down 19th-over collapse risk for the Royals.
                    </p>
                  </div>

                  {/* Actions & Metrics Row */}
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

                    <div style={{ display: 'flex', gap: '16px', textAlign: 'right', alignItems: 'center' }}>
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
                    </div>
                  </div>
                </div>

              </div>

              {/* LOWER SECTION: Dynamic Carousel of Cards */}
              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '14px' }}>
                  <h3 style={{ margin: 0, fontSize: '1.1rem', fontWeight: 800, color: 'var(--text-primary)' }}>
                    Elite Clutch Prospects
                  </h3>
                  <div style={{ display: 'flex', gap: '8px' }}>
                    {[
                      { id: 'all', label: 'All' },
                      { id: 'bat', label: 'Batters' },
                      { id: 'bowl', label: 'Bowlers' }
                    ].map(f => (
                      <button
                        key={f.id}
                        onClick={() => setRoleFilter(f.id as any)}
                        style={{
                          padding: '4px 12px',
                          borderRadius: '999px',
                          fontSize: '0.72rem',
                          fontWeight: 700,
                          cursor: 'pointer',
                          border: 'none',
                          background: roleFilter === f.id ? 'var(--rr-pink)' : '#FFFFFF',
                          color: roleFilter === f.id ? '#FFFFFF' : 'var(--text-secondary)',
                          boxShadow: '0 1px 4px rgba(0,0,0,0.04)'
                        }}
                      >
                        {f.label}
                      </button>
                    ))}
                  </div>
                </div>

                {/* Dynamic Player Grid Based on Filter (Independent of Search Box) */}
                <div className="elite-clutch-grid">
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
                                color: b.rank === 1 ? 'var(--rr-pink)' : 'var(--rr-gold)',
                                whiteSpace: 'nowrap'
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
                                color: 'var(--rr-blue)',
                                whiteSpace: 'nowrap'
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
                      ))}
                    </>
                  )}
                </div>
              </div>

              {/* ========================================================================= */}
              {/* TOP 10 RANKINGS (10 BATTERS & 10 BOWLERS UNDER PRESSURE)                  */}
              {/* ========================================================================= */}
              <div style={{ marginTop: '28px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '12px' }}>
                  <div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '4px' }}>
                      <div style={{
                        width: '32px',
                        height: '32px',
                        borderRadius: '10px',
                        background: 'linear-gradient(135deg, var(--rr-pink) 0%, var(--rr-blue) 100%)',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        color: '#FFFFFF',
                        boxShadow: '0 2px 8px rgba(230, 0, 126, 0.25)'
                      }}>
                        <Trophy size={17} />
                      </div>
                      <h3 style={{ margin: 0, fontSize: '1.2rem', fontWeight: 900, color: 'var(--text-primary)', letterSpacing: '-0.02em' }}>
                        Top 10 Performers
                      </h3>
                    </div>
                    <p style={{ margin: 0, fontSize: '0.78rem', color: 'var(--text-secondary)' }}>
                      Rank 1 to 10 choices computed directly from all 6 CSV datasets.
                    </p>
                  </div>

                  {/* Phase & Role Filter Capsules */}
                  <div style={{ display: 'flex', alignItems: 'center', gap: '10px', flexWrap: 'wrap', width: '100%', justifyContent: 'space-between' }}>
                    {/* Phase Selector Capsules */}
                    <div style={{
                      display: 'inline-flex',
                      alignItems: 'center',
                      gap: '4px',
                      background: 'rgba(15, 23, 42, 0.05)',
                      padding: '4px',
                      borderRadius: '999px',
                      border: '1px solid rgba(15, 23, 42, 0.06)',
                      overflowX: 'auto',
                      flexWrap: 'nowrap',
                      maxWidth: '100%',
                      scrollbarWidth: 'none',
                      whiteSpace: 'nowrap',
                      WebkitOverflowScrolling: 'touch'
                    }}>
                      {[
                        { id: 'all', label: 'All Overs' },
                        { id: 'powerplay', label: '⚡ Powerplay' },
                        { id: 'middle', label: '💧 Middle' },
                        { id: 'death', label: '🎯 Death' }
                      ].map(ph => (
                        <button
                          key={ph.id}
                          onClick={() => setPhaseFilter(ph.id as any)}
                          style={{
                            padding: '6px 12px',
                            borderRadius: '999px',
                            fontSize: '0.72rem',
                            fontWeight: 700,
                            cursor: 'pointer',
                            border: 'none',
                            whiteSpace: 'nowrap',
                            flexShrink: 0,
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
                    <div style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: '3px',
                      background: 'rgba(15, 23, 42, 0.05)',
                      padding: '4px',
                      borderRadius: '999px',
                      border: '1px solid rgba(15, 23, 42, 0.06)',
                      whiteSpace: 'nowrap',
                      flexShrink: 0
                    }}>
                      {[
                        { id: 'bat', label: '🏏 Batters' },
                        { id: 'bowl', label: '🎯 Bowlers' }
                      ].map(tab => (
                        <button
                          key={tab.id}
                          onClick={() => setTableTab(tab.id as any)}
                          style={{
                            padding: '6px 13px',
                            borderRadius: '999px',
                            fontSize: '0.72rem',
                            fontWeight: 700,
                            cursor: 'pointer',
                            border: 'none',
                            whiteSpace: 'nowrap',
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
                  </div>
                </div>

                {/* Grid for Tables: 1-column single tab view */}
                <div style={{
                  display: 'grid',
                  gridTemplateColumns: 'minmax(0, 1fr)',
                  width: '100%',
                  minWidth: 0,
                  gap: '18px'
                }}>

                  {/* 1. TOP 10 BATTERS TABLE */}
                  {tableTab === 'bat' && (
                    <div className="glass-card" style={{ padding: '16px 14px', borderRadius: '20px', minWidth: 0, width: '100%', maxWidth: '100%', boxSizing: 'border-box' }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '14px', paddingBottom: '12px', borderBottom: '1px solid rgba(15, 23, 42, 0.06)' }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                          <span style={{ fontSize: '1.1rem' }}>🏏</span>
                          <div>
                            <h4 style={{ margin: 0, fontSize: '0.98rem', fontWeight: 800, color: 'var(--text-primary)' }}>
                              {phaseFilter === 'death' ? 'Top Death-Overs Finishers (#5–#7)' : 'Top 10 Batters Under Pressure'}
                            </h4>
                            <span style={{ fontSize: '0.68rem', color: phaseFilter === 'death' ? '#DC2626' : 'var(--text-muted)', fontWeight: phaseFilter === 'death' ? 700 : 500 }}>
                              {phaseFilter === 'death' ? `🎯 Phase-Calibrated: Min ${activeCalib.minDeathBalls} Death Deliveries (Sorted by Death Clutch)` : `Min ${activeCalib.minBatBalls} Pressure Balls · Sorted by Clutch Rating`}
                            </span>
                          </div>
                        </div>
                        <span style={{
                          fontSize: '0.65rem',
                          fontWeight: 800,
                          padding: '3px 8px',
                          borderRadius: '999px',
                          background: 'var(--rr-pink-light)',
                          color: 'var(--rr-pink)',
                          whiteSpace: 'nowrap'
                        }}>
                          RANKS 1 TO 10
                        </span>
                      </div>

                      <div className="table-responsive-wrapper">
                        <table style={{ width: '100%', minWidth: '600px', borderCollapse: 'collapse', textAlign: 'left', fontSize: '0.78rem' }}>
                          <thead>
                            <tr style={{ borderBottom: '1px solid rgba(15, 23, 42, 0.08)', color: 'var(--text-muted)', fontSize: '0.68rem', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
                              <th style={{ padding: '8px 6px', width: '38px', minWidth: '38px', whiteSpace: 'nowrap' }}>Rank</th>
                              <th style={{ padding: '8px 10px', minWidth: '150px', whiteSpace: 'nowrap' }}>Batter</th>
                              <th style={{ padding: '8px 8px', textAlign: 'right', whiteSpace: 'nowrap' }}>Balls</th>
                              <th style={{ padding: '8px 8px', textAlign: 'right', whiteSpace: 'nowrap' }}>Pressure SR</th>
                              <th style={{ padding: '8px 8px', textAlign: 'right', whiteSpace: 'nowrap' }}>Pressure Boost</th>
                              <th style={{ padding: '8px 8px', textAlign: 'right', whiteSpace: 'nowrap' }}>Bnd %</th>
                              <th style={{ padding: '8px 8px', textAlign: 'right', whiteSpace: 'nowrap' }}>Dot %</th>
                              <th style={{ padding: '8px 8px', textAlign: 'right', whiteSpace: 'nowrap' }}>Consist %</th>
                              <th style={{ padding: '8px 10px', textAlign: 'right', whiteSpace: 'nowrap' }}>Clutch Score</th>
                            </tr>
                          </thead>
                          <tbody>
                            {displayedBatters.slice(0, 10).map((b: any) => {
                              const isTop1 = b.rank === 1;
                              const isTop2 = b.rank === 2;
                              const isTop3 = b.rank === 3;
                              return (
                                <tr
                                  key={b.name}
                                  style={{
                                    borderBottom: '1px solid rgba(15, 23, 42, 0.04)',
                                    transition: 'background 0.15s ease'
                                  }}
                                  onMouseEnter={(e) => (e.currentTarget.style.background = 'rgba(225, 29, 72, 0.02)')}
                                  onMouseLeave={(e) => (e.currentTarget.style.background = 'transparent')}
                                >
                                  {/* Rank Badge */}
                                  <td style={{ padding: '10px 6px', whiteSpace: 'nowrap' }}>
                                    <span style={{
                                      display: 'inline-flex',
                                      alignItems: 'center',
                                      justifyContent: 'center',
                                      width: '24px',
                                      height: '24px',
                                      borderRadius: '50%',
                                      fontSize: '0.72rem',
                                      fontWeight: 900,
                                      color: (isTop1 || isTop2 || isTop3) ? '#FFFFFF' : 'var(--text-secondary)',
                                      background: isTop1
                                        ? 'linear-gradient(135deg, #F59E0B, #D97706)'
                                        : isTop2
                                        ? 'linear-gradient(135deg, #94A3B8, #64748B)'
                                        : isTop3
                                        ? 'linear-gradient(135deg, #B45309, #92400E)'
                                        : 'rgba(15, 23, 42, 0.05)',
                                      boxShadow: isTop1 ? '0 2px 6px rgba(245, 158, 11, 0.3)' : 'none'
                                    }}>
                                      {b.rank}
                                    </span>
                                  </td>

                                  {/* Player Name & Team */}
                                  <td style={{ padding: '10px 10px', whiteSpace: 'nowrap' }}>
                                    <div style={{ fontWeight: 800, color: 'var(--text-primary)', display: 'flex', alignItems: 'center', gap: '6px', whiteSpace: 'nowrap' }}>
                                      <span style={{ whiteSpace: 'nowrap' }}>{b.name}</span>
                                      <button
                                        onClick={() => togglePlayerInShortlist(b.name)}
                                        style={{
                                          border: 'none',
                                          background: 'transparent',
                                          cursor: 'pointer',
                                          padding: '2px',
                                          display: 'inline-flex',
                                          alignItems: 'center',
                                          color: coachShortlist.includes(b.name) ? 'var(--rr-pink)' : 'rgba(15,23,42,0.25)'
                                        }}
                                        title={coachShortlist.includes(b.name) ? 'Remove from Coach Shortlist' : 'Add to Coach Shortlist'}
                                      >
                                        <Bookmark size={12} fill={coachShortlist.includes(b.name) ? 'currentColor' : 'none'} />
                                      </button>
                                      {isTop1 && (
                                        <span style={{ fontSize: '0.6rem', padding: '1px 5px', borderRadius: '4px', background: 'var(--rr-pink-light)', color: 'var(--rr-pink)', fontWeight: 800, whiteSpace: 'nowrap' }}>
                                          #1 LOCK
                                        </span>
                                      )}
                                    </div>
                                    <div style={{ fontSize: '0.68rem', color: 'var(--text-muted)', whiteSpace: 'nowrap' }}>{b.team}</div>
                                  </td>

                                  {/* Balls Faced */}
                                  <td style={{ padding: '10px 8px', textAlign: 'right', fontFamily: 'JetBrains Mono, monospace', color: 'var(--text-secondary)', whiteSpace: 'nowrap' }}>
                                    {b.balls}
                                  </td>

                                  {/* Pressure SR */}
                                  <td style={{ padding: '10px 8px', textAlign: 'right', fontFamily: 'JetBrains Mono, monospace', fontWeight: 800, color: 'var(--rr-pink)', whiteSpace: 'nowrap' }}>
                                    {b.strikeRate.toFixed(1)}
                                  </td>

                                  {/* SR Delta */}
                                  <td style={{ padding: '10px 8px', textAlign: 'right', fontFamily: 'JetBrains Mono, monospace', fontWeight: 700, color: '#10B981', whiteSpace: 'nowrap' }}>
                                    +{b.srDelta.toFixed(1)}
                                  </td>

                                  {/* Boundary % */}
                                  <td style={{ padding: '10px 8px', textAlign: 'right', fontFamily: 'JetBrains Mono, monospace', fontWeight: 700, color: '#8B5CF6', whiteSpace: 'nowrap' }}>
                                    {b.boundaryPct !== undefined ? `${b.boundaryPct.toFixed(1)}%` : '-'}
                                  </td>

                                  {/* Dot % */}
                                  <td style={{ padding: '10px 8px', textAlign: 'right', fontFamily: 'JetBrains Mono, monospace', fontWeight: 600, color: 'var(--text-muted)', whiteSpace: 'nowrap' }}>
                                    {b.dotPct !== undefined ? `${b.dotPct.toFixed(1)}%` : '-'}
                                  </td>

                                  {/* Consistency % */}
                                  <td style={{ padding: '10px 8px', textAlign: 'right', fontFamily: 'JetBrains Mono, monospace', fontWeight: 800, color: 'var(--rr-blue)', whiteSpace: 'nowrap' }}>
                                    {b.consistencyPct !== undefined ? `${b.consistencyPct.toFixed(1)}%` : '-'}
                                  </td>

                                  {/* Clutch Score */}
                                  <td style={{ padding: '10px 10px', textAlign: 'right', fontFamily: 'JetBrains Mono, monospace', fontWeight: 900, color: 'var(--text-primary)', fontSize: '0.88rem', whiteSpace: 'nowrap' }}>
                                    {b.clutchScore.toFixed(1)}
                                  </td>
                                </tr>
                              );
                            })}
                          </tbody>
                        </table>
                      </div>
                    </div>
                  )}

                  {/* 2. TOP 10 BOWLERS TABLE */}
                  {tableTab === 'bowl' && (
                    <div className="glass-card" style={{ padding: '16px 14px', borderRadius: '20px', minWidth: 0, width: '100%', maxWidth: '100%', boxSizing: 'border-box' }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '14px', paddingBottom: '12px', borderBottom: '1px solid rgba(15, 23, 42, 0.06)' }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                          <span style={{ fontSize: '1.1rem' }}>🎯</span>
                          <div>
                            <h4 style={{ margin: 0, fontSize: '0.98rem', fontWeight: 800, color: 'var(--text-primary)' }}>
                              Top 10 Bowlers Under Pressure
                            </h4>
                            <span style={{ fontSize: '0.68rem', color: 'var(--text-muted)' }}>
                              Min {activeCalib.minBowlBalls} Pressure Balls · Sorted by Clutch Suppression Score
                            </span>
                          </div>
                        </div>
                        <span style={{
                          fontSize: '0.65rem',
                          fontWeight: 800,
                          padding: '3px 8px',
                          borderRadius: '999px',
                          background: 'var(--rr-blue-light)',
                          color: 'var(--rr-blue)',
                          whiteSpace: 'nowrap'
                        }}>
                          RANKS 1 TO 10
                        </span>
                      </div>

                      <div className="table-responsive-wrapper">
                        <table style={{ width: '100%', minWidth: '600px', borderCollapse: 'collapse', textAlign: 'left', fontSize: '0.78rem' }}>
                          <thead>
                            <tr style={{ borderBottom: '1px solid rgba(15, 23, 42, 0.08)', color: 'var(--text-muted)', fontSize: '0.68rem', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
                              <th style={{ padding: '8px 6px', width: '38px', minWidth: '38px', whiteSpace: 'nowrap' }}>Rank</th>
                              <th style={{ padding: '8px 10px', minWidth: '150px', whiteSpace: 'nowrap' }}>Bowler</th>
                              <th style={{ padding: '8px 8px', textAlign: 'right', whiteSpace: 'nowrap' }}>Balls</th>
                              <th style={{ padding: '8px 8px', textAlign: 'right', whiteSpace: 'nowrap' }}>Wickets</th>
                              <th style={{ padding: '8px 8px', textAlign: 'right', whiteSpace: 'nowrap' }}>Pressure Econ</th>
                              <th style={{ padding: '8px 8px', textAlign: 'right', whiteSpace: 'nowrap' }}>Dot %</th>
                              <th style={{ padding: '8px 8px', textAlign: 'right', whiteSpace: 'nowrap' }}>Consist %</th>
                              <th style={{ padding: '8px 10px', textAlign: 'right', whiteSpace: 'nowrap' }}>Clutch Score</th>
                            </tr>
                          </thead>
                          <tbody>
                            {displayedBowlers.slice(0, 10).map((bw) => {
                              const isTop1 = bw.rank === 1;
                              const isTop2 = bw.rank === 2;
                              const isTop3 = bw.rank === 3;
                              return (
                                <tr
                                  key={bw.name}
                                  style={{
                                    borderBottom: '1px solid rgba(15, 23, 42, 0.04)',
                                    transition: 'background 0.15s ease'
                                  }}
                                  onMouseEnter={(e) => (e.currentTarget.style.background = 'rgba(0, 102, 204, 0.02)')}
                                  onMouseLeave={(e) => (e.currentTarget.style.background = 'transparent')}
                                >
                                  {/* Rank Badge */}
                                  <td style={{ padding: '10px 6px', whiteSpace: 'nowrap' }}>
                                    <span style={{
                                      display: 'inline-flex',
                                      alignItems: 'center',
                                      justifyContent: 'center',
                                      width: '24px',
                                      height: '24px',
                                      borderRadius: '50%',
                                      fontSize: '0.72rem',
                                      fontWeight: 900,
                                      color: (isTop1 || isTop2 || isTop3) ? '#FFFFFF' : 'var(--text-secondary)',
                                      background: isTop1
                                        ? 'linear-gradient(135deg, #F59E0B, #D97706)'
                                        : isTop2
                                        ? 'linear-gradient(135deg, #94A3B8, #64748B)'
                                        : isTop3
                                        ? 'linear-gradient(135deg, #B45309, #92400E)'
                                        : 'rgba(15, 23, 42, 0.05)',
                                      boxShadow: isTop1 ? '0 2px 6px rgba(245, 158, 11, 0.3)' : 'none'
                                    }}>
                                      {bw.rank}
                                    </span>
                                  </td>

                                  {/* Bowler Name & Team */}
                                  <td style={{ padding: '10px 10px', whiteSpace: 'nowrap' }}>
                                    <div style={{ fontWeight: 800, color: 'var(--text-primary)', display: 'flex', alignItems: 'center', gap: '6px', whiteSpace: 'nowrap' }}>
                                      <span style={{ whiteSpace: 'nowrap' }}>{bw.name}</span>
                                      <button
                                        onClick={() => togglePlayerInShortlist(bw.name)}
                                        style={{
                                          border: 'none',
                                          background: 'transparent',
                                          cursor: 'pointer',
                                          padding: '2px',
                                          display: 'inline-flex',
                                          alignItems: 'center',
                                          color: coachShortlist.includes(bw.name) ? 'var(--rr-blue)' : 'rgba(15,23,42,0.25)'
                                        }}
                                        title={coachShortlist.includes(bw.name) ? 'Remove from Coach Shortlist' : 'Add to Coach Shortlist'}
                                      >
                                        <Bookmark size={12} fill={coachShortlist.includes(bw.name) ? 'currentColor' : 'none'} />
                                      </button>
                                      {isTop1 && (
                                        <span style={{ fontSize: '0.6rem', padding: '1px 5px', borderRadius: '4px', background: 'var(--rr-blue-light)', color: 'var(--rr-blue)', fontWeight: 800, whiteSpace: 'nowrap' }}>
                                          #1 LEADER
                                        </span>
                                      )}
                                    </div>
                                    <div style={{ fontSize: '0.68rem', color: 'var(--text-muted)', whiteSpace: 'nowrap' }}>{bw.team}</div>
                                  </td>

                                  {/* Balls Bowled */}
                                  <td style={{ padding: '10px 8px', textAlign: 'right', fontFamily: 'JetBrains Mono, monospace', color: 'var(--text-secondary)', whiteSpace: 'nowrap' }}>
                                    {bw.balls}
                                  </td>

                                  {/* Wickets */}
                                  <td style={{ padding: '10px 8px', textAlign: 'right', fontFamily: 'JetBrains Mono, monospace', fontWeight: 800, color: 'var(--rr-pink)', whiteSpace: 'nowrap' }}>
                                    {bw.wickets}
                                  </td>

                                  {/* Pressure Economy & Delta */}
                                  <td style={{ padding: '10px 8px', textAlign: 'right', fontFamily: 'JetBrains Mono, monospace', fontWeight: 700, color: bw.economy <= 7.5 ? '#10B981' : 'var(--text-primary)', whiteSpace: 'nowrap' }}>
                                    {bw.economy.toFixed(2)}
                                  </td>

                                  {/* Dot % */}
                                  <td style={{ padding: '10px 8px', textAlign: 'right', fontFamily: 'JetBrains Mono, monospace', fontWeight: 700, color: 'var(--rr-blue)', whiteSpace: 'nowrap' }}>
                                    {bw.dotPct !== undefined ? `${bw.dotPct.toFixed(1)}%` : '-'}
                                  </td>

                                  {/* Consistency % */}
                                  <td style={{ padding: '10px 8px', textAlign: 'right', fontFamily: 'JetBrains Mono, monospace', fontWeight: 800, color: '#10B981', whiteSpace: 'nowrap' }}>
                                    {bw.consistencyPct !== undefined ? `${bw.consistencyPct.toFixed(1)}%` : '-'}
                                  </td>

                                  {/* Clutch Score */}
                                  <td style={{ padding: '10px 10px', textAlign: 'right', fontFamily: 'JetBrains Mono, monospace', fontWeight: 900, color: 'var(--text-primary)', fontSize: '0.88rem', whiteSpace: 'nowrap' }}>
                                    {bw.clutchScore.toFixed(1)}
                                  </td>
                                </tr>
                              );
                            })}
                          </tbody>
                        </table>
                      </div>
                    </div>
                  )}

                </div>
              </div>

            </div>
          )}

          {/* ========================================================================= */}
          {/* PAGE 2: MATRIX COMPARISON                                                 */}
          {/* ========================================================================= */}
          {activePage === 'matrix' && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '16px', flex: 1, overflowY: 'auto' }}>
              
              {/* Role Toggle Capsules */}
              <div style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                flexWrap: 'wrap',
                gap: '10px',
                background: '#FFFFFF',
                borderRadius: '16px',
                padding: '10px 18px',
                border: '1px solid rgba(15, 23, 42, 0.06)',
                boxShadow: '0 2px 8px rgba(0,0,0,0.02)'
              }}>
                <div style={{ fontSize: '0.92rem', fontWeight: 800, color: 'var(--text-primary)' }}>
                  Compare Top Players
                </div>

                {/* 2 Capsules for Batsmen and Bowlers */}
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
                      padding: '6px 14px',
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
                    Batsmen
                  </button>
                  <button
                    onClick={() => setCompareRole('bowl')}
                    style={{
                      padding: '6px 14px',
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
                    Bowlers
                  </button>
                </div>
              </div>

              {/* Selection Dropdowns */}
              {compareRole === 'bat' ? (
                <div className="two-col-grid" style={{ gap: '16px' }}>
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
                          #{b.rank} {b.name} ({b.team})
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
                          #{b.rank} {b.name} ({b.team})
                        </option>
                      ))}
                    </select>
                  </div>
                </div>
              ) : (
                <div className="two-col-grid" style={{ gap: '16px' }}>
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
                          #{bw.rank} {bw.name} ({bw.team})
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
                          #{bw.rank} {bw.name} ({bw.team})
                        </option>
                      ))}
                    </select>
                  </div>
                </div>
              )}

              {/* BATTER COMPARISON VIEW */}
              {compareRole === 'bat' && p1 && p2 && (
                <>
                  <div className="two-col-grid" style={{ gap: '16px' }}>
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

                      <div className="four-col-stat-grid" style={{ gap: '10px', background: 'rgba(15, 23, 42, 0.03)', padding: '12px 14px', borderRadius: '14px', marginBottom: '14px' }}>
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

                      <div className="four-col-stat-grid" style={{ gap: '10px', background: 'rgba(15, 23, 42, 0.03)', padding: '12px 14px', borderRadius: '14px', marginBottom: '14px' }}>
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

                  {/* Tactical Phase Comparison for Batters */}
                  <div className="glass-card" style={{ padding: '20px 24px' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '14px' }}>
                      <h4 style={{ margin: 0, fontSize: '0.92rem', fontWeight: 800, color: 'var(--text-primary)' }}>
                        ⚡ Phase-by-Phase Strike Rate & Boundary Breakdown
                      </h4>
                      <span style={{ fontSize: '0.68rem', fontWeight: 800, color: 'var(--rr-pink)', background: 'var(--rr-pink-light)', padding: '2px 10px', borderRadius: '999px' }}>
                        TACTICAL AUDIT
                      </span>
                    </div>

                    <div className="three-col-grid" style={{ gap: '12px' }}>
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

                  {/* Direct Proportion Meters for Batters */}
                  <div className="glass-card" style={{ padding: '20px 24px' }}>
                    <h4 style={{ margin: '0 0 14px 0', fontSize: '0.92rem', fontWeight: 800, color: 'var(--text-primary)' }}>Direct Metric Comparison</h4>
                    {[
                      { label: 'Pressure Strike Rate', v1: p1.pSR, v2: p2.pSR },
                      { label: 'Pressure Boost vs Baseline', v1: p1.deltaSR, v2: p2.deltaSR },
                      { label: 'Match Consistency Rate', v1: p1.consistencyPct ?? 80, v2: p2.consistencyPct ?? 80 },
                      { label: 'Boundary %', v1: p1.bndPct, v2: p2.bndPct },
                      { label: 'Overall Clutch Rating', v1: p1.clutchScore, v2: p2.clutchScore }
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
                  <div className="two-col-grid" style={{ gap: '16px' }}>
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

                      <div className="four-col-stat-grid" style={{ gap: '10px', background: 'rgba(15, 23, 42, 0.03)', padding: '12px 14px', borderRadius: '14px', marginBottom: '14px' }}>
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

                      <div className="four-col-stat-grid" style={{ gap: '10px', background: 'rgba(15, 23, 42, 0.03)', padding: '12px 14px', borderRadius: '14px', marginBottom: '14px' }}>
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

                  {/* Tactical Phase Comparison for Bowlers */}
                  <div className="glass-card" style={{ padding: '20px 24px' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '14px' }}>
                      <h4 style={{ margin: 0, fontSize: '0.92rem', fontWeight: 800, color: 'var(--text-primary)' }}>
                        🎯 Phase-by-Phase Economy & Wicket Suppression Breakdown
                      </h4>
                      <span style={{ fontSize: '0.68rem', fontWeight: 800, color: 'var(--rr-blue)', background: 'var(--rr-blue-light)', padding: '2px 10px', borderRadius: '999px' }}>
                        TACTICAL AUDIT
                      </span>
                    </div>

                    <div className="three-col-grid" style={{ gap: '12px' }}>
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

                  {/* Direct Proportion Meters for Bowlers */}
                  <div className="glass-card" style={{ padding: '20px 24px' }}>
                    <h4 style={{ margin: '0 0 14px 0', fontSize: '0.92rem', fontWeight: 800, color: 'var(--text-primary)' }}>Direct Metric Comparison</h4>
                    {[
                      { label: 'Pressure Economy (Lower is Better)', v1: bw1.pEcon, v2: bw2.pEcon, invert: true },
                      { label: 'Pressure Wickets Taken', v1: bw1.pWkts, v2: bw2.pWkts },
                      { label: 'Match Consistency Rate', v1: bw1.consistencyPct ?? 75, v2: bw2.consistencyPct ?? 75 },
                      { label: 'Dot Ball % under Pressure', v1: bw1.dotPct, v2: bw2.dotPct },
                      { label: 'Overall Clutch Rating', v1: bw1.clutchScore, v2: bw2.clutchScore }
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

          {/* PAGE 3: WAR ROOM 2027 (SOLVING THE 4 SQUAD CONSTRUCTION FLAWS)             */}
          {/* ========================================================================= */}
          {activePage === 'auction' && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '16px', flex: 1, overflowY: 'auto' }}>
              
              {/* Section Header Notice */}
              <div style={{
                background: '#FFFFFF',
                borderRadius: '16px',
                padding: '14px 20px',
                border: '1px solid rgba(15, 23, 42, 0.06)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                boxShadow: '0 2px 8px rgba(0,0,0,0.02)'
              }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                  <span style={{ fontSize: '1.2rem' }}>🎯</span>
                  <div>
                    <div style={{ fontSize: '0.85rem', fontWeight: 800, color: 'var(--text-primary)' }}>
                      Core Squad Construction Invariants & 2027 Auction Fixes
                    </div>
                    <div style={{ fontSize: '0.74rem', color: 'var(--text-secondary)' }}>
                      Solving the 4 recurring squad construction vulnerabilities in Rajasthan Royals IPL auction history.
                    </div>
                  </div>
                </div>
              </div>

              {/* 4 Expert Flaws Grid with Actionable Target Plans */}
              <div className="two-col-grid" style={{ gap: '16px' }}>
                
                {/* Flaw 1 */}
                <div className="glass-card" style={{ padding: '20px' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
                    <span style={{
                      fontSize: '0.7rem',
                      fontWeight: 800,
                      padding: '2px 8px',
                      borderRadius: '6px',
                      background: '#FEE2E2',
                      color: '#DC2626'
                    }}>
                      FLAW #1
                    </span>
                    <h4 style={{ margin: 0, fontSize: '0.95rem', fontWeight: 800, color: 'var(--text-primary)' }}>
                      The "Glass Cannon" Roster: Paper-Thin Bench
                    </h4>
                  </div>
                  <p style={{ margin: '0 0 12px 0', fontSize: '0.78rem', color: 'var(--text-secondary)', lineHeight: 1.5 }}>
                    <b>Observation:</b> RR historically spends 80–85% of their purse on the starting XI, starving the bench. Injuries in the second half of the tournament lead to the steepest performance drop-off in the league.
                  </p>
                  <div style={{ background: '#FFFFFF', padding: '10px 14px', borderRadius: '12px', border: '1px solid rgba(15,23,42,0.06)' }}>
                    <div style={{ fontSize: '0.68rem', fontWeight: 700, color: 'var(--rr-pink)', textTransform: 'uppercase' }}>War Room Solution & Targets:</div>
                    <div style={{ fontSize: '0.8rem', color: 'var(--text-primary)', marginTop: '2px' }}>
                      Target verified 140+ ball Indian clutch specialists: <b>Naman Dhir</b> (Rank #1 Batter, 395 balls, 80.0% consistency, &lt; ₹4 Cr) and <b>Shashank Singh</b> (Rank #5, 535 balls, 159.6 SR) to guarantee battle-tested bench depth.
                    </div>
                  </div>
                </div>

                {/* Flaw 2 */}
                <div className="glass-card" style={{ padding: '20px' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
                    <span style={{
                      fontSize: '0.7rem',
                      fontWeight: 800,
                      padding: '2px 8px',
                      borderRadius: '6px',
                      background: '#FEF3C7',
                      color: '#B45309'
                    }}>
                      FLAW #2
                    </span>
                    <h4 style={{ margin: 0, fontSize: '0.95rem', fontWeight: 800, color: 'var(--text-primary)' }}>
                      Middle-Overs Spin Enforcer Vacuum
                    </h4>
                  </div>
                  <p style={{ margin: '0 0 12px 0', fontSize: '0.78rem', color: 'var(--text-secondary)', lineHeight: 1.5 }}>
                    <b>Observation:</b> Losing 2 early wickets bogs down RR against wrist spin in overs 7–15 (&lt;7.5 RPO). Lacks a batter who attacks without eating 15 set-up balls.
                  </p>
                  <div style={{ background: '#FFFFFF', padding: '10px 14px', borderRadius: '12px', border: '1px solid rgba(15,23,42,0.06)' }}>
                    <div style={{ fontSize: '0.68rem', fontWeight: 700, color: 'var(--rr-blue)', textTransform: 'uppercase' }}>War Room Solution & Targets:</div>
                    <div style={{ fontSize: '0.8rem', color: 'var(--text-primary)', marginTop: '2px' }}>
                      Acquire 100% consistency qualified enforcers: <b>Phil Salt</b> (Rank #4, 223 balls, 177.1 SR, +15.5 boost) and <b>Sai Sudharsan</b> (Rank #3, 498 balls, 81.0% consistency, 162.0 SR) to sustain high-tempo strike rotation against spin without dot-ball stall.
                    </div>
                  </div>
                </div>

                {/* Flaw 3 */}
                <div className="glass-card" style={{ padding: '20px' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
                    <span style={{
                      fontSize: '0.7rem',
                      fontWeight: 800,
                      padding: '2px 8px',
                      borderRadius: '6px',
                      background: '#DBEAFE',
                      color: '#1D4ED8'
                    }}>
                      FLAW #3
                    </span>
                    <h4 style={{ margin: 0, fontSize: '0.95rem', fontWeight: 800, color: 'var(--text-primary)' }}>
                      Overseas Slot Bottleneck & Death Bowling
                    </h4>
                  </div>
                  <p style={{ margin: '0 0 12px 0', fontSize: '0.78rem', color: 'var(--text-secondary)', lineHeight: 1.5 }}>
                    <b>Observation:</b> RR locks 3 overseas slots into top-order bats & opening swing. Runs out of slots for a death specialist, resulting in 19th-over collapses.
                  </p>
                  <div style={{ background: '#FFFFFF', padding: '10px 14px', borderRadius: '12px', border: '1px solid rgba(15,23,42,0.06)' }}>
                    <div style={{ fontSize: '0.68rem', fontWeight: 700, color: '#059669', textTransform: 'uppercase' }}>War Room Solution & Targets:</div>
                    <div style={{ fontSize: '0.8rem', color: 'var(--text-primary)', marginTop: '2px' }}>
                      Target the top two 140+ ball death masters: <b>Arshdeep Singh</b> (Rank #1 Bowler, 1,807 balls, 81.1% consistency) and <b>Matheesha Pathirana</b> (Rank #3 Bowler, 919 balls, 6.83 econ, 93.5% consistency) to permanently fix RR's 19th-over vulnerability.
                    </div>
                  </div>
                </div>

                {/* Flaw 4 */}
                <div className="glass-card" style={{ padding: '20px' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
                    <span style={{
                      fontSize: '0.7rem',
                      fontWeight: 800,
                      padding: '2px 8px',
                      borderRadius: '6px',
                      background: '#F3E8FF',
                      color: '#7E22CE'
                    }}>
                      FLAW #4
                    </span>
                    <h4 style={{ margin: 0, fontSize: '0.95rem', fontWeight: 800, color: 'var(--text-primary)' }}>
                      Absence of Genuine All-Rounder Buffer
                    </h4>
                  </div>
                  <p style={{ margin: '0 0 12px 0', fontSize: '0.78rem', color: 'var(--text-secondary)', lineHeight: 1.5 }}>
                    <b>Observation:</b> RR plays rigid single-skill specialists—batters who don't bowl and bowlers who don't bat. Limits in-game tactical adjustments when early wickets fall.
                  </p>
                  <div style={{ background: '#FFFFFF', padding: '10px 14px', borderRadius: '12px', border: '1px solid rgba(15,23,42,0.06)' }}>
                    <div style={{ fontSize: '0.68rem', fontWeight: 700, color: '#7E22CE', textTransform: 'uppercase' }}>War Room Solution & Targets:</div>
                    <div style={{ fontSize: '0.8rem', color: 'var(--text-primary)', marginTop: '2px' }}>
                      Invest in verified high-sample multi-utility assets: <b>Wanindu Hasaranga</b> (Rank #5 Bowler, 951 balls, 86.4% consistency, lower-order boundary power) and power finisher <b>Tim David</b> (Rank #9, 1,077 pressure balls, 170.6 SR) for dual-phase tactical flexibility.
                    </div>
                  </div>
                </div>

              </div>
            </div>
          )}

          {/* ========================================================================= */}
          {/* PAGE 4: COACHES PLAYBOOK (ALL 4 MATCH DIRECTIVES VISIBLE)                 */}
          {/* ========================================================================= */}
          {activePage === 'playbook' && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '16px', flex: 1, overflowY: 'auto' }}>
              <div className="two-col-grid" style={{ gap: '16px' }}>
                
                {/* Directive 1 */}
                <div className="glass-card" style={{ padding: '20px' }}>
                  <h4 style={{ margin: '0 0 8px 0', fontSize: '0.95rem', fontWeight: 800, color: 'var(--rr-pink)', display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <CheckCircle2 size={16} />
                    1. Middle-Overs Spin Counter (Overs 7–15)
                  </h4>
                  <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', lineHeight: 1.55, margin: 0 }}>
                    Opposition captains consistently deploy spin chokes against Rajasthan when early wickets fall in the powerplay.
                    <br/><br/>
                    <b>Tactical Warning & Advice:</b> Deploy designated 140+ ball positive-delta enforcers like <b>Phil Salt</b> (177.1 SR, 76.9% consistency) or <b>Sai Sudharsan</b> (81.0% consistency, 162.0 SR) with license to attack from ball one. Eliminating the 15-ball "set-up tax" ensures the required run rate never crosses 12.0 going into the death overs.
                  </p>
                </div>

                {/* Directive 2 */}
                <div className="glass-card" style={{ padding: '20px' }}>
                  <h4 style={{ margin: '0 0 8px 0', fontSize: '0.95rem', fontWeight: 800, color: 'var(--rr-blue)', display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <CheckCircle2 size={16} />
                    2. Death Bowling Isolation (Overs 17–20)
                  </h4>
                  <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', lineHeight: 1.55, margin: 0 }}>
                    Trent Boult secures world-class powerplay wickets, but defending in Jaipur requires specialists who do not rely on early swing.
                    <br/><br/>
                    <b>Tactical Warning & Advice:</b> Pair <b>Arshdeep Singh</b> (Rank #1 Bowler, 1,807 pressure balls, 81.1% consistency) with sling-yorker weapon <b>Matheesha Pathirana</b> (Rank #3, 6.83 econ, 93.5% consistency). Their combined 2,700+ pressure ball foundation provides unmatched boundary suppression and yorker precision at the death.
                  </p>
                </div>

                {/* Directive 3 */}
                <div className="glass-card" style={{ padding: '20px' }}>
                  <h4 style={{ margin: '0 0 8px 0', fontSize: '0.95rem', fontWeight: 800, color: '#059669', display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <CheckCircle2 size={16} />
                    3. Impact Player Tactical Deployment
                  </h4>
                  <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', lineHeight: 1.55, margin: 0 }}>
                    Under the Impact Player rule, teams with true batting depth dominate. RR must stop treating the 12th player as a late-game panic substitute.
                    <br/><br/>
                    <b>Tactical Warning & Advice:</b> Retain overseas batting flexibility by using <b>Naman Dhir</b> (Rank #1 Clutch Batter, 395 pressure balls, 179.0 SR, 80.0% consistency) or <b>Ashutosh Sharma</b> (367 balls, 65.2% consistency) as designated Impact finishers to extend batting depth down to #8, freeing the top order to attack fearlessly.
                  </p>
                </div>

                {/* Directive 4 */}
                <div className="glass-card" style={{ padding: '20px' }}>
                  <h4 style={{ margin: '0 0 8px 0', fontSize: '0.95rem', fontWeight: 800, color: '#7E22CE', display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <CheckCircle2 size={16} />
                    4. Playoff Composure Multiplier
                  </h4>
                  <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', lineHeight: 1.55, margin: 0 }}>
                    RR has repeatedly dominated early league stages only to stumble in high-pressure playoff Eliminators and Qualifiers.
                    <br/><br/>
                    <b>Tactical Warning & Advice:</b> Anchor high-stakes playoff games with proven 100% consistency rated leaders like <b>Faf du Plessis</b> (Rank #2 Batter, 277 balls, 165.3 SR, 78.6% consistency) and <b>Yashasvi Jaiswal</b> (173.0 SR, +23.8 boost, 30.1% boundary rate). Their elite surge under pressure eliminates mental dips in Qualifiers and Eliminators.
                  </p>
                </div>

              </div>
            </div>
          )}

          {/* ========================================================================= */}
          {/* PAGE 5: SETTINGS / METRICS CONFIG (DYNAMIC LIVE CALIBRATION)               */}
          {/* ========================================================================= */}
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
                        localStorage.setItem('rr_active_calib_v3', JSON.stringify(DEFAULT_CALIB));
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
                        localStorage.setItem('rr_active_calib_v3', JSON.stringify(pendingCalib));
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
              <div className="settings-grid">
                
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
                    max="1.00"
                    step="0.05"
                    value={pendingCalib.consistencyWeight}
                    onChange={(e) => setPendingCalib(prev => ({ ...prev, consistencyWeight: parseFloat(e.target.value) }))}
                    style={{ width: '100%', accentColor: '#10B981', cursor: 'pointer' }}
                  />
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.65rem', color: 'var(--text-muted)', marginTop: '4px' }}>
                    <span>0% (Raw Numbers)</span>
                    <span>50% (Balanced)</span>
                    <span>100% (Strict Max Consistency)</span>
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
                    <span>0.70x (Max High Boost)</span>
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
                    <span>14.0x (Strict Lockdown Max)</span>
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

                {/* 5. Min Death Specialist Balls Filter */}
                <div style={{ padding: '16px 20px', background: '#FFFFFF', borderRadius: '16px', border: '1px solid rgba(15,23,42,0.08)', boxShadow: '0 2px 6px rgba(0,0,0,0.02)' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                    <div style={{ fontWeight: 800, fontSize: '0.85rem', color: 'var(--text-primary)' }}>Death Finisher Filter (Overs 16–20)</div>
                    <span className="mono-num" style={{ fontWeight: 900, color: '#DC2626', fontSize: '1.05rem' }}>{pendingCalib.minDeathBalls} Death Balls</span>
                  </div>
                  <div style={{ fontSize: '0.72rem', color: 'var(--text-secondary)', marginBottom: '12px' }}>
                    Calibrated specifically for #5–#7 finishers who face fewer balls per game (~10-15b). 40 death balls represents ~7 closing finishes.
                  </div>
                  <input
                    type="range"
                    min="20"
                    max="80"
                    step="5"
                    value={pendingCalib.minDeathBalls}
                    onChange={(e) => setPendingCalib(prev => ({ ...prev, minDeathBalls: parseInt(e.target.value) }))}
                    style={{ width: '100%', accentColor: '#DC2626', cursor: 'pointer' }}
                  />
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.65rem', color: 'var(--text-muted)', marginTop: '4px' }}>
                    <span>20b (Broad Pool)</span>
                    <span>40b (Standard Finisher Baseline)</span>
                    <span>80b (High Volume Only)</span>
                  </div>
                </div>

              </div>
            </div>
          )}

        </main>
      </div>

      {/* ========================================================================= */}
      {/* 3. DETERMINISTIC ROYALS SCOUT BOT (ZERO AI, 100% INDEX-BASED CHAT DRAWER)  */}
      {/* ========================================================================= */}
      {isBotOpen && (
        <>
          <div
            onClick={() => setIsBotOpen(false)}
            style={{
              position: 'fixed',
              inset: 0,
              background: 'rgba(15, 23, 42, 0.45)',
              backdropFilter: 'blur(3px)',
              WebkitBackdropFilter: 'blur(3px)',
              zIndex: 999998
            }}
          />
          <div style={{
            position: 'fixed',
            top: 0,
            right: 0,
            bottom: 0,
            width: 'min(420px, 100vw)',
            maxWidth: '100vw',
            background: 'rgba(255, 255, 255, 0.98)',
            backdropFilter: 'blur(30px)',
            WebkitBackdropFilter: 'blur(30px)',
            borderLeft: '1px solid rgba(15, 23, 42, 0.1)',
            boxShadow: '-15px 0 40px rgba(15, 23, 42, 0.16)',
            zIndex: 999999,
            display: 'flex',
            flexDirection: 'column'
          }}>
          {/* Bot Header */}
          <div style={{
            padding: '16px 20px',
            borderBottom: '1px solid rgba(15, 23, 42, 0.08)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            background: '#FFFFFF'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <div style={{
                width: '34px',
                height: '34px',
                borderRadius: '10px',
                background: 'linear-gradient(135deg, var(--rr-pink) 0%, var(--rr-blue) 100%)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: '#FFF'
              }}>
                <Bot size={18} />
              </div>
              <div>
                <div style={{ fontWeight: 800, fontSize: '0.9rem', color: 'var(--text-primary)' }}>
                  Royals Scout Engine
                </div>
                <div style={{ fontSize: '0.68rem', color: '#10B981', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '4px' }}>
                  <span style={{ width: '5px', height: '5px', borderRadius: '50%', background: '#10B981' }} />
                  Active · Ready
                </div>
              </div>


            </div>

            <button
              onClick={() => setIsBotOpen(false)}
              style={{
                width: '30px',
                height: '30px',
                borderRadius: '50%',
                border: 'none',
                background: 'rgba(15, 23, 42, 0.05)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                cursor: 'pointer',
                color: 'var(--text-secondary)'
              }}
            >
              <X size={16} />
            </button>
          </div>

          {/* Chat Messages Body */}
          <div style={{ flex: 1, padding: '16px', overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '14px' }}>
            {chatMessages.map(msg => (
              <div
                key={msg.id}
                style={{
                  alignSelf: msg.sender === 'user' ? 'flex-end' : 'flex-start',
                  maxWidth: msg.coachAudit || msg.comparison ? '96%' : '88%',
                  display: 'flex',
                  gap: '8px',
                  flexDirection: msg.sender === 'user' ? 'row-reverse' : 'row'
                }}
              >
                <div style={{
                  width: '26px',
                  height: '26px',
                  borderRadius: '50%',
                  background: msg.sender === 'user' ? '#0F172A' : 'var(--rr-pink-light)',
                  color: msg.sender === 'user' ? '#FFFFFF' : 'var(--rr-pink)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  flexShrink: 0,
                  fontSize: '0.7rem'
                }}>
                  {msg.sender === 'user' ? <UserIcon size={13} /> : <Bot size={13} />}
                </div>

                <div style={{
                  padding: '12px 14px',
                  borderRadius: '16px',
                  background: msg.sender === 'user' ? '#0F172A' : '#FFFFFF',
                  color: msg.sender === 'user' ? '#FFFFFF' : 'var(--text-primary)',
                  fontSize: '0.8rem',
                  lineHeight: 1.5,
                  boxShadow: '0 2px 8px rgba(0,0,0,0.04)',
                  border: msg.sender === 'user' ? 'none' : '1px solid rgba(15, 23, 42, 0.08)',
                  width: '100%'
                }}>
                  {msg.verdict && msg.verdict !== 'INFO' && !msg.coachAudit && (
                    <div style={{
                      display: 'inline-block',
                      fontSize: '0.65rem',
                      fontWeight: 800,
                      padding: '2px 8px',
                      borderRadius: '6px',
                      marginBottom: '6px',
                      background: msg.verdict === 'MUST BUY' ? '#ECFDF5' : '#FEF3C7',
                      color: msg.verdict === 'MUST BUY' ? '#059669' : '#B45309'
                    }}>
                      VERDICT: {msg.verdict}
                    </div>
                  )}

                  <div>{msg.text}</div>

                  {/* Standard key-value metrics */}
                  {msg.metrics && (
                    <div style={{ marginTop: '10px', paddingTop: '8px', borderTop: '1px solid rgba(15, 23, 42, 0.06)', display: 'flex', flexDirection: 'column', gap: '4px' }}>
                      {msg.metrics.map((m, idx) => (
                        <div key={idx} style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.7rem' }}>
                          <span style={{ color: 'var(--text-muted)' }}>{m.label}:</span>
                          <span className="mono-num" style={{ fontWeight: 700, color: 'var(--rr-blue)' }}>{m.value}</span>
                        </div>
                      ))}
                    </div>
                  )}

                  {/* RICH HEAD-TO-HEAD COMPARISON CARD */}
                  {msg.comparison && (
                    <div style={{
                      marginTop: '12px',
                      padding: '12px',
                      borderRadius: '12px',
                      background: '#F8FAFC',
                      border: '1px solid rgba(15, 23, 42, 0.08)'
                    }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px', paddingBottom: '8px', borderBottom: '1px solid rgba(15, 23, 42, 0.06)' }}>
                        <span style={{ fontWeight: 800, fontSize: '0.75rem', color: 'var(--text-primary)' }}>
                          📊 Head-to-Head Breakdown
                        </span>
                        <span style={{
                          fontSize: '0.65rem',
                          fontWeight: 800,
                          padding: '2px 8px',
                          borderRadius: '999px',
                          background: 'var(--rr-pink-light)',
                          color: 'var(--rr-pink)'
                        }}>
                          WINNER: {msg.comparison.verdictWinner}
                        </span>
                      </div>

                      <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
                        {msg.comparison.metrics.map((m, idx) => (
                          <div key={idx} style={{ display: 'grid', gridTemplateColumns: '1fr 70px 70px', gap: '6px', alignItems: 'center', fontSize: '0.68rem' }}>
                            <span style={{ color: 'var(--text-muted)' }}>{m.label}</span>
                            <span style={{
                              textAlign: 'right',
                              fontWeight: m.winner === 1 ? 800 : 500,
                              color: m.winner === 1 ? '#059669' : 'var(--text-primary)',
                              fontFamily: 'JetBrains Mono, monospace'
                            }}>
                              {m.v1} {m.winner === 1 && '✓'}
                            </span>
                            <span style={{
                              textAlign: 'right',
                              fontWeight: m.winner === 2 ? 800 : 500,
                              color: m.winner === 2 ? '#059669' : 'var(--text-primary)',
                              fontFamily: 'JetBrains Mono, monospace'
                            }}>
                              {m.v2} {m.winner === 2 && '✓'}
                            </span>
                          </div>
                        ))}
                      </div>

                      <button
                        onClick={() => {
                          setSelectedB1(msg.comparison!.p1.name);
                          setSelectedB2(msg.comparison!.p2.name);
                          setActivePage('matrix');
                          setIsBotOpen(false);
                        }}
                        style={{
                          marginTop: '10px',
                          width: '100%',
                          padding: '6px 10px',
                          borderRadius: '8px',
                          background: '#FFFFFF',
                          border: '1px solid rgba(15, 23, 42, 0.12)',
                          color: 'var(--rr-blue)',
                          fontSize: '0.72rem',
                          fontWeight: 700,
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          gap: '6px',
                          cursor: 'pointer'
                        }}
                      >
                        <Scale size={13} />
                        Compare on Matrix Radar
                      </button>
                    </div>
                  )}

                  {/* RICH COACH SHORTLIST AUDIT REPORT CARD */}
                  {msg.coachAudit && (
                    <div style={{
                      marginTop: '12px',
                      padding: '14px',
                      borderRadius: '14px',
                      background: '#F8FAFC',
                      border: '1px solid rgba(15, 23, 42, 0.1)',
                      display: 'flex',
                      flexDirection: 'column',
                      gap: '12px'
                    }}>
                      {/* Overall Grade Banner */}
                      <div style={{
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'space-between',
                        padding: '10px 12px',
                        borderRadius: '10px',
                        background: msg.coachAudit.grade.startsWith('A')
                          ? 'linear-gradient(135deg, #059669, #10B981)'
                          : msg.coachAudit.grade.startsWith('B')
                          ? 'linear-gradient(135deg, #2563EB, #3B82F6)'
                          : 'linear-gradient(135deg, #D97706, #F59E0B)',
                        color: '#FFFFFF'
                      }}>
                        <div>
                          <div style={{ fontSize: '0.65rem', fontWeight: 700, opacity: 0.9 }}>COACH SQUAD AUDIT</div>
                          <div style={{ fontSize: '0.95rem', fontWeight: 900 }}>GRADE {msg.coachAudit.grade}</div>
                        </div>
                        <div style={{ textAlign: 'right', fontSize: '0.68rem', fontWeight: 700 }}>
                          <div>{msg.coachAudit.buyCount} Buys · {msg.coachAudit.monitorCount} Monitor</div>
                          <div style={{ opacity: 0.85 }}>{msg.coachAudit.avoidCount} Red Flag(s)</div>
                        </div>
                      </div>

                      {/* Individual Target Roster */}
                      <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                        <div style={{ fontSize: '0.7rem', fontWeight: 800, color: 'var(--text-primary)' }}>
                          Shortlisted Players Viability:
                        </div>
                        {msg.coachAudit.players.map((item, idx) => (
                          <div
                            key={idx}
                            style={{
                              padding: '8px 10px',
                              borderRadius: '8px',
                              background: '#FFFFFF',
                              border: '1px solid rgba(15, 23, 42, 0.05)',
                              display: 'flex',
                              flexDirection: 'column',
                              gap: '4px'
                            }}
                          >
                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                              <span style={{ fontWeight: 800, fontSize: '0.78rem', color: 'var(--text-primary)' }}>
                                {item.player.name}
                              </span>
                              <span style={{
                                fontSize: '0.62rem',
                                fontWeight: 800,
                                padding: '2px 6px',
                                borderRadius: '4px',
                                background: item.verdict === 'MUST BUY' ? '#ECFDF5' : item.verdict === 'CONSIDER / VALUE' ? '#EFF6FF' : '#FEF2F2',
                                color: item.verdict === 'MUST BUY' ? '#059669' : item.verdict === 'CONSIDER / VALUE' ? '#2563EB' : '#DC2626'
                              }}>
                                {item.verdict}
                              </span>
                            </div>
                            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.66rem', color: 'var(--text-muted)' }}>
                              <span>{item.player.team} · {item.roleFit}</span>
                              <span className="mono-num" style={{ fontWeight: 700, color: 'var(--text-primary)' }}>{item.keyMetric}</span>
                            </div>
                            {item.redFlag && (
                              <div style={{ fontSize: '0.64rem', color: '#DC2626', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '4px' }}>
                                <AlertTriangle size={11} /> {item.redFlag}
                              </div>
                            )}
                          </div>
                        ))}
                      </div>

                      {/* RR Squad Gap Checklist */}
                      <div style={{
                        padding: '10px',
                        borderRadius: '8px',
                        background: '#FFFFFF',
                        border: '1px solid rgba(15, 23, 42, 0.05)',
                        fontSize: '0.68rem',
                        display: 'flex',
                        flexDirection: 'column',
                        gap: '4px'
                      }}>
                        <div style={{ fontWeight: 800, color: 'var(--text-primary)', marginBottom: '2px' }}>
                          👑 Rajasthan Royals Tactical Gaps:
                        </div>
                        <div style={{ color: msg.coachAudit.gapCheck.deathBowlingCovered ? '#059669' : '#D97706' }}>
                          {msg.coachAudit.gapCheck.deathDetail}
                        </div>
                        <div style={{ color: msg.coachAudit.gapCheck.spinSurgeCovered ? '#059669' : '#D97706' }}>
                          {msg.coachAudit.gapCheck.spinDetail}
                        </div>
                        <div style={{ color: msg.coachAudit.gapCheck.finishingDepthCovered ? '#059669' : '#D97706' }}>
                          {msg.coachAudit.gapCheck.finishDetail}
                        </div>
                      </div>

                      {/* Recommended Swaps */}
                      {msg.coachAudit.recommendedSwaps.length > 0 && (
                        <div style={{
                          padding: '10px',
                          borderRadius: '8px',
                          background: '#FFFBEB',
                          border: '1px solid #FDE68A',
                          fontSize: '0.68rem'
                        }}>
                          <div style={{ fontWeight: 800, color: '#92400E', marginBottom: '4px' }}>
                            ⚡ Data-Backed Swap Suggestions:
                          </div>
                          {msg.coachAudit.recommendedSwaps.map((sw, idx) => (
                            <div key={idx} style={{ color: '#78350F', lineHeight: 1.4 }}>
                              • {sw.reason}
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  )}

                </div>
              </div>


            ))}
            <div ref={chatEndRef} />
          </div>

          {/* Quick Prompt Pills for Instant Discovery */}
          <div style={{
            padding: '8px 14px',
            borderTop: '1px solid rgba(15, 23, 42, 0.06)',
            background: '#F8FAFC',
            display: 'flex',
            gap: '6px',
            overflowX: 'auto',
            whiteSpace: 'nowrap'
          }}>
            {[
              { label: `📋 Audit Shortlist (${coachShortlist.length})`, query: 'audit coach shortlist' },
              { label: '⚡ Bumrah vs Pathirana', query: 'Bumrah vs Pathirana' },
              { label: '🏏 Salt vs Klaasen', query: 'Phil Salt vs Heinrich Klaasen' },
              { label: '🔥 Solve RR Death Overs', query: 'how to solve death bowling for RR' },
              { label: '💎 Best All-Rounder', query: 'best all rounder' }
            ].map((pill, idx) => (
              <button
                key={idx}
                onClick={() => handleSendMessage(pill.query)}
                style={{
                  padding: '4px 10px',
                  borderRadius: '999px',
                  fontSize: '0.68rem',
                  fontWeight: 700,
                  border: '1px solid rgba(15, 23, 42, 0.1)',
                  background: '#FFFFFF',
                  color: 'var(--text-secondary)',
                  cursor: 'pointer',
                  flexShrink: 0
                }}
              >
                {pill.label}
              </button>
            ))}
          </div>

          {/* Chat Input Field */}
          <div style={{ padding: '14px 16px', borderTop: '1px solid rgba(15, 23, 42, 0.08)', background: '#FFFFFF' }}>
            <form
              onSubmit={(e) => {
                e.preventDefault();
                handleSendMessage();
              }}
              style={{ display: 'flex', gap: '8px', alignItems: 'center' }}
            >
              <input
                type="text"
                value={chatInput}
                onChange={(e) => setChatInput(e.target.value)}
                placeholder="Ask e.g. audit coach shortlist, Salt vs Dube..."
                style={{
                  flex: 1,
                  padding: '10px 14px',
                  borderRadius: '999px',
                  border: '1px solid rgba(15, 23, 42, 0.12)',
                  outline: 'none',
                  fontSize: '0.82rem',
                  color: 'var(--text-primary)',
                  background: '#F8FAFC'
                }}
              />
              <button
                type="submit"
                style={{
                  width: '36px',
                  height: '36px',
                  borderRadius: '50%',
                  background: 'var(--rr-pink)',
                  color: '#FFFFFF',
                  border: 'none',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  cursor: 'pointer',
                  boxShadow: '0 2px 8px rgba(230, 0, 126, 0.3)'
                }}
              >
                <Send size={15} />
              </button>
            </form>
          </div>

        </div>
        </>
      )}

      {/* ========================================================================= */}
      {/* 4. COACH TARGET SHORTLIST DRAWER / MODAL                                   */}
      {/* ========================================================================= */}
      {isShortlistOpen && (
        <>
          <div
            onClick={() => setIsShortlistOpen(false)}
            style={{
              position: 'fixed',
              inset: 0,
              background: 'rgba(15, 23, 42, 0.45)',
              backdropFilter: 'blur(3px)',
              WebkitBackdropFilter: 'blur(3px)',
              zIndex: 999998
            }}
          />
          <div style={{
            position: 'fixed',
            top: 0,
            right: 0,
            bottom: 0,
            width: 'min(420px, 100vw)',
            maxWidth: '100vw',
            background: '#FFFFFF',
            borderLeft: '1px solid rgba(15, 23, 42, 0.1)',
            boxShadow: '-15px 0 40px rgba(15, 23, 42, 0.16)',
            zIndex: 999999,
            display: 'flex',
            flexDirection: 'column'
          }}>
          {/* Header */}
          <div style={{
            padding: '16px 20px',
            borderBottom: '1px solid rgba(15, 23, 42, 0.08)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            background: 'var(--rr-blue)',
            color: '#FFFFFF'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <ClipboardList size={20} />
              <div>
                <div style={{ fontWeight: 800, fontSize: '0.95rem' }}>Coach Target Shortlist</div>
                <div style={{ fontSize: '0.68rem', opacity: 0.85 }}>{coachShortlist.length} Players (Unlimited Roster)</div>
              </div>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              {coachShortlist.length > 0 && (
                <button
                  onClick={() => setCoachShortlist([])}
                  style={{
                    padding: '3px 8px',
                    borderRadius: '6px',
                    border: '1px solid rgba(255,255,255,0.3)',
                    background: 'transparent',
                    color: '#FFFFFF',
                    fontSize: '0.65rem',
                    fontWeight: 700,
                    cursor: 'pointer'
                  }}
                  title="Clear all players"
                >
                  Clear All
                </button>
              )}
              <button
                onClick={() => setIsShortlistOpen(false)}
                style={{
                  width: '30px',
                  height: '30px',
                  borderRadius: '50%',
                  border: 'none',
                  background: 'rgba(255,255,255,0.15)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  cursor: 'pointer',
                  color: '#FFFFFF'
                }}
              >
                <X size={16} />
              </button>
            </div>
          </div>

          {/* Shortlist Content */}
          <div style={{ flex: 1, padding: '16px', overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '12px' }}>
            <p style={{ margin: 0, fontSize: '0.75rem', color: 'var(--text-secondary)' }}>
              Add any number of player targets submitted by coaches (no limit). The Royals Scout Engine will audit each candidate's clutch viability and collective squad fit.
            </p>

            {/* Quick Add Form with Autocomplete */}
            <form
              onSubmit={(e) => {
                e.preventDefault();
                addCustomPlayerToShortlist(shortlistInput);
              }}
              style={{ display: 'flex', gap: '8px' }}
            >
              <input
                type="text"
                list="registered-players-list"
                value={shortlistInput}
                onChange={(e) => setShortlistInput(e.target.value)}
                placeholder="Type or select any player..."
                style={{
                  flex: 1,
                  padding: '8px 12px',
                  borderRadius: '8px',
                  border: '1px solid rgba(15, 23, 42, 0.15)',
                  fontSize: '0.8rem',
                  outline: 'none'
                }}
              />
              <datalist id="registered-players-list">
                {Object.values(clutchData.players as any).map((p: any) => (
                  <option key={p.name} value={p.name} />
                ))}
              </datalist>
              <button
                type="submit"
                style={{
                  padding: '8px 14px',
                  borderRadius: '8px',
                  background: 'var(--rr-blue)',
                  color: '#FFFFFF',
                  border: 'none',
                  fontSize: '0.75rem',
                  fontWeight: 700,
                  cursor: 'pointer'
                }}
              >
                <Plus size={14} />
              </button>
            </form>

            {/* Roster of Shortlisted Players */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', marginTop: '6px' }}>
              {coachShortlist.map((name, idx) => {
                const p = findBestPlayerMatch(name, clutchData.players as any);
                return (
                  <div
                    key={idx}
                    style={{
                      padding: '10px 12px',
                      borderRadius: '10px',
                      background: '#F8FAFC',
                      border: '1px solid rgba(15, 23, 42, 0.08)',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between'
                    }}
                  >
                    <div>
                      <div style={{ fontWeight: 800, fontSize: '0.82rem', color: 'var(--text-primary)' }}>
                        {name}
                      </div>
                      <div style={{ fontSize: '0.68rem', color: 'var(--text-muted)' }}>
                        {p ? `${p.team} · ${p.role} · Clutch: ${p.clutchScore.toFixed(1)}` : 'Custom target candidate'}
                      </div>
                    </div>
                    <button
                      onClick={() => togglePlayerInShortlist(name)}
                      style={{
                        background: 'transparent',
                        border: 'none',
                        color: 'var(--text-muted)',
                        cursor: 'pointer',
                        padding: '4px'
                      }}
                      title="Remove from shortlist"
                    >
                      <Trash2 size={15} color="#DC2626" />
                    </button>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Action Footer */}
          <div style={{ padding: '16px', borderTop: '1px solid rgba(15, 23, 42, 0.08)', background: '#FFFFFF' }}>
            <button
              onClick={() => triggerCoachAudit()}
              style={{
                width: '100%',
                padding: '12px',
                borderRadius: '12px',
                background: 'linear-gradient(135deg, var(--rr-pink) 0%, var(--rr-blue) 100%)',
                color: '#FFFFFF',
                border: 'none',
                fontWeight: 800,
                fontSize: '0.85rem',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '8px',
                boxShadow: '0 4px 14px rgba(230, 0, 126, 0.3)'
              }}
            >
              <Sparkles size={16} />
              Run Royals Scout Audit on Shortlist
            </button>
          </div>
        </div>
        </>
      )}

      {/* 4. GLOBAL PLAYER PERFORMANCE DEEP-DIVE MODAL */}
      {selectedPlayerModal && (
        <div style={{
          position: 'fixed',
          inset: 0,
          background: 'rgba(15, 23, 42, 0.65)',
          backdropFilter: 'blur(8px)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 1000000,
          padding: '12px'
        }}>
          <div style={{
            width: '100%',
            maxWidth: '560px',
            background: '#FFFFFF',
            borderRadius: '20px',
            border: '1px solid rgba(255, 255, 255, 0.8)',
            boxShadow: '0 30px 60px -12px rgba(15, 23, 42, 0.25)',
            overflow: 'hidden',
            display: 'flex',
            flexDirection: 'column',
            maxHeight: '90vh'
          }}>
            {/* Modal Header */}
            <div style={{
              padding: '16px 20px',
              background: 'linear-gradient(135deg, #0E3696 0%, #1E293B 100%)',
              color: '#FFFFFF',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              flexShrink: 0
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                <div style={{
                  width: '40px',
                  height: '40px',
                  borderRadius: '10px',
                  background: 'rgba(255,255,255,0.12)',
                  border: '1px solid rgba(255,255,255,0.2)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontSize: '1.2rem'
                }}>
                  {selectedPlayerModal.role.toLowerCase().includes('bowl') ? '🎯' : '🏏'}
                </div>
                <div>
                  <div style={{ fontSize: '1.15rem', fontWeight: 900, letterSpacing: '-0.02em' }}>
                    {selectedPlayerModal.name}
                  </div>
                  <div style={{ fontSize: '0.75rem', color: '#94A3B8', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '6px', marginTop: '2px' }}>
                    <span>{selectedPlayerModal.team || 'Tournament Player'}</span>
                    <span>•</span>
                    <span style={{ color: '#F472B6', fontWeight: 700 }}>{selectedPlayerModal.role}</span>
                  </div>
                </div>
              </div>
              <button
                onClick={() => setSelectedPlayerModal(null)}
                style={{
                  background: 'rgba(255,255,255,0.12)',
                  border: 'none',
                  borderRadius: '50%',
                  width: '32px',
                  height: '32px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  color: '#FFFFFF',
                  cursor: 'pointer'
                }}
              >
                <X size={18} />
              </button>
            </div>

            {/* Modal Body */}
            <div style={{ padding: '16px 18px', display: 'flex', flexDirection: 'column', gap: '14px', overflowY: 'auto' }}>
              
              {/* Score & Verdict Banner */}
              {(() => {
                const pConsist = selectedPlayerModal.bowling?.consistency_pct ?? selectedPlayerModal.batting?.consistency_pct ?? selectedPlayerModal.consistencyPct ?? 50.0;
                return (
                  <div style={{
                    display: 'grid',
                    gridTemplateColumns: 'repeat(3, 1fr)',
                    gap: '10px',
                    padding: '14px 16px',
                    borderRadius: '16px',
                    background: '#F8FAFC',
                    border: '1px solid rgba(15, 23, 42, 0.06)'
                  }}>
                    <div>
                      <div style={{ fontSize: '0.66rem', fontWeight: 800, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
                        Clutch Score
                      </div>
                      <div style={{ fontSize: '1.75rem', fontWeight: 900, color: selectedPlayerModal.clutchScore >= 100 ? '#15803D' : selectedPlayerModal.clutchScore >= 70 ? 'var(--rr-blue)' : '#64748B', lineHeight: 1.1, marginTop: '2px' }}>
                        {selectedPlayerModal.clutchScore.toFixed(1)}
                      </div>
                    </div>

                    <div>
                      <div style={{ fontSize: '0.66rem', fontWeight: 800, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
                        Consistency
                      </div>
                      <div style={{ fontSize: '1.75rem', fontWeight: 900, color: pConsist >= 75 ? '#15803D' : pConsist >= 60 ? 'var(--rr-blue)' : '#D97706', lineHeight: 1.1, marginTop: '2px' }}>
                        {pConsist.toFixed(0)}%
                      </div>
                    </div>

                    <div style={{ display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'flex-start' }}>
                      <div style={{ fontSize: '0.66rem', fontWeight: 800, color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: '4px', letterSpacing: '0.04em' }}>
                        Scout Verdict
                      </div>
                      <span style={{
                        padding: '4px 10px',
                        borderRadius: '999px',
                        fontSize: '0.72rem',
                        fontWeight: 900,
                        letterSpacing: '0.03em',
                        whiteSpace: 'nowrap',
                        background: selectedPlayerModal.verdictClass === 'buy' ? 'rgba(21, 128, 61, 0.12)' : selectedPlayerModal.verdictClass === 'monitor' ? 'rgba(14, 54, 150, 0.12)' : 'rgba(100, 116, 139, 0.12)',
                        color: selectedPlayerModal.verdictClass === 'buy' ? '#15803D' : selectedPlayerModal.verdictClass === 'monitor' ? 'var(--rr-blue)' : '#475569',
                        border: selectedPlayerModal.verdictClass === 'buy' ? '1px solid rgba(21, 128, 61, 0.3)' : selectedPlayerModal.verdictClass === 'monitor' ? '1px solid rgba(14, 54, 150, 0.25)' : '1px solid rgba(100, 116, 139, 0.25)'
                      }}>
                        {selectedPlayerModal.verdict}
                      </span>
                    </div>
                  </div>
                );
              })()}

              {/* Phase Breakdown in Modal */}
              {selectedPlayerModal.phases && (
                <div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                    <div style={{ fontSize: '0.8rem', fontWeight: 800, color: 'var(--text-primary)' }}>
                      Phase Splits
                    </div>
                  </div>

                  {(() => {
                    const isBowler = selectedPlayerModal.role.toLowerCase().includes('bowl') || (!selectedPlayerModal.batting && selectedPlayerModal.bowling);
                    const batPh = selectedPlayerModal.phases?.batting;
                    const bowlPh = selectedPlayerModal.phases?.bowling;

                    return (
                      <div className="modal-phase-grid">
                        {/* Powerplay Card */}
                        <div style={{ background: '#F8FAFC', padding: '10px 12px', borderRadius: '12px', border: '1px solid rgba(15,23,42,0.06)' }}>
                          <div style={{ fontSize: '0.64rem', fontWeight: 800, color: 'var(--rr-pink)', textTransform: 'uppercase', marginBottom: '2px' }}>
                            Powerplay (1–6)
                          </div>
                          {isBowler ? (
                            bowlPh?.powerplay && bowlPh.powerplay.balls > 0 ? (
                              <div>
                                <div className="mono-num" style={{ fontSize: '1.15rem', fontWeight: 900, color: 'var(--text-primary)' }}>
                                  {bowlPh.powerplay.econ.toFixed(2)} Econ
                                </div>
                                <div style={{ fontSize: '0.65rem', color: 'var(--text-secondary)', marginTop: '2px' }}>
                                  {bowlPh.powerplay.wkts}w · {bowlPh.powerplay.balls}b · {bowlPh.powerplay.dotPct}% dots
                                </div>
                              </div>
                            ) : (
                              <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', fontStyle: 'italic', marginTop: '4px' }}>No deliveries</div>
                            )
                          ) : (
                            batPh?.powerplay && batPh.powerplay.balls > 0 ? (
                              <div>
                                <div className="mono-num" style={{ fontSize: '1.15rem', fontWeight: 900, color: 'var(--text-primary)' }}>
                                  {batPh.powerplay.sr.toFixed(1)} SR
                                </div>
                                <div style={{ fontSize: '0.65rem', color: 'var(--text-secondary)', marginTop: '2px' }}>
                                  {batPh.powerplay.runs}r · {batPh.powerplay.balls}b · {batPh.powerplay.bdryPct}% bdry
                                </div>
                              </div>
                            ) : (
                              <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', fontStyle: 'italic', marginTop: '4px' }}>No deliveries</div>
                            )
                          )}
                        </div>

                        {/* Middle Overs Card */}
                        <div style={{ background: '#F8FAFC', padding: '10px 12px', borderRadius: '12px', border: '1px solid rgba(15,23,42,0.06)' }}>
                          <div style={{ fontSize: '0.64rem', fontWeight: 800, color: 'var(--rr-blue)', textTransform: 'uppercase', marginBottom: '2px' }}>
                            Middle (7–15)
                          </div>
                          {isBowler ? (
                            bowlPh?.middle && bowlPh.middle.balls > 0 ? (
                              <div>
                                <div className="mono-num" style={{ fontSize: '1.15rem', fontWeight: 900, color: 'var(--text-primary)' }}>
                                  {bowlPh.middle.econ.toFixed(2)} Econ
                                </div>
                                <div style={{ fontSize: '0.65rem', color: 'var(--text-secondary)', marginTop: '2px' }}>
                                  {bowlPh.middle.wkts}w · {bowlPh.middle.balls}b · {bowlPh.middle.dotPct}% dots
                                </div>
                              </div>
                            ) : (
                              <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', fontStyle: 'italic', marginTop: '4px' }}>No deliveries</div>
                            )
                          ) : (
                            batPh?.middle && batPh.middle.balls > 0 ? (
                              <div>
                                <div className="mono-num" style={{ fontSize: '1.15rem', fontWeight: 900, color: 'var(--text-primary)' }}>
                                  {batPh.middle.sr.toFixed(1)} SR
                                </div>
                                <div style={{ fontSize: '0.65rem', color: 'var(--text-secondary)', marginTop: '2px' }}>
                                  {batPh.middle.runs}r · {batPh.middle.balls}b · {batPh.middle.bdryPct}% bdry
                                </div>
                              </div>
                            ) : (
                              <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', fontStyle: 'italic', marginTop: '4px' }}>No deliveries</div>
                            )
                          )}
                        </div>

                        {/* Death Overs Card */}
                        <div style={{ background: '#F8FAFC', padding: '10px 12px', borderRadius: '12px', border: '1px solid rgba(15,23,42,0.06)' }}>
                          <div style={{ fontSize: '0.64rem', fontWeight: 800, color: '#DC2626', textTransform: 'uppercase', marginBottom: '2px' }}>
                            Death (16–20)
                          </div>
                          {isBowler ? (
                            bowlPh?.death && bowlPh.death.balls > 0 ? (
                              <div>
                                <div className="mono-num" style={{ fontSize: '1.15rem', fontWeight: 900, color: 'var(--text-primary)' }}>
                                  {bowlPh.death.econ.toFixed(2)} Econ
                                </div>
                                <div style={{ fontSize: '0.65rem', color: 'var(--text-secondary)', marginTop: '2px' }}>
                                  {bowlPh.death.wkts}w · {bowlPh.death.balls}b · {bowlPh.death.dotPct}% dots
                                </div>
                              </div>
                            ) : (
                              <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', fontStyle: 'italic', marginTop: '4px' }}>No deliveries</div>
                            )
                          ) : (
                            batPh?.death && batPh.death.balls > 0 ? (
                              <div>
                                <div className="mono-num" style={{ fontSize: '1.15rem', fontWeight: 900, color: 'var(--text-primary)' }}>
                                  {batPh.death.sr.toFixed(1)} SR
                                </div>
                                <div style={{ fontSize: '0.65rem', color: 'var(--text-secondary)', marginTop: '2px' }}>
                                  {batPh.death.runs}r · {batPh.death.balls}b · {batPh.death.bdryPct}% bdry
                                </div>
                              </div>
                            ) : (
                              <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', fontStyle: 'italic', marginTop: '4px' }}>No deliveries</div>
                            )
                          )}
                        </div>
                      </div>
                    );
                  })()}
                </div>
              )}

              {/* Performance Metrics Breakdown */}
              <div>
                <div style={{ fontSize: '0.8rem', fontWeight: 800, color: 'var(--text-primary)', marginBottom: '8px' }}>
                  Pressure Metrics
                </div>
                
                {/* Bowler Metrics */}
                {selectedPlayerModal.bowling && (
                  <div className="modal-stat-grid">
                    <div style={{ padding: '10px 8px', borderRadius: '12px', background: '#F8FAFC', border: '1px solid rgba(15, 23, 42, 0.05)', textAlign: 'center' }}>
                      <div style={{ fontSize: '0.64rem', color: 'var(--text-muted)', fontWeight: 700 }}>Pressure Econ</div>
                      <div style={{ fontSize: '1.05rem', fontWeight: 800, color: 'var(--text-primary)', marginTop: '2px' }}>{selectedPlayerModal.bowling.p_econ.toFixed(2)}</div>
                    </div>
                    <div style={{ padding: '10px 8px', borderRadius: '12px', background: '#F8FAFC', border: '1px solid rgba(15, 23, 42, 0.05)', textAlign: 'center' }}>
                      <div style={{ fontSize: '0.64rem', color: 'var(--text-muted)', fontWeight: 700 }}>Econ Delta</div>
                      <div style={{ fontSize: '1.05rem', fontWeight: 800, color: selectedPlayerModal.bowling.econ_delta <= 0.5 ? '#15803D' : '#DC2626', marginTop: '2px' }}>
                        {selectedPlayerModal.bowling.econ_delta > 0 ? '+' : ''}{selectedPlayerModal.bowling.econ_delta.toFixed(2)}
                      </div>
                    </div>
                    <div style={{ padding: '10px 8px', borderRadius: '12px', background: '#F8FAFC', border: '1px solid rgba(15, 23, 42, 0.05)', textAlign: 'center' }}>
                      <div style={{ fontSize: '0.64rem', color: 'var(--text-muted)', fontWeight: 700 }}>Consistency</div>
                      <div style={{ fontSize: '1.05rem', fontWeight: 800, color: '#10B981', marginTop: '2px' }}>
                        {selectedPlayerModal.bowling.consistency_pct !== undefined ? `${selectedPlayerModal.bowling.consistency_pct.toFixed(0)}%` : '75%'}
                      </div>
                    </div>
                    <div style={{ padding: '10px 8px', borderRadius: '12px', background: '#F8FAFC', border: '1px solid rgba(15, 23, 42, 0.05)', textAlign: 'center' }}>
                      <div style={{ fontSize: '0.64rem', color: 'var(--text-muted)', fontWeight: 700 }}>Wickets</div>
                      <div style={{ fontSize: '1.05rem', fontWeight: 800, color: 'var(--text-primary)', marginTop: '2px' }}>{selectedPlayerModal.bowling.p_wkts}</div>
                      <div style={{ fontSize: '0.6rem', color: 'var(--text-muted)' }}>{selectedPlayerModal.bowling.p_balls}b</div>
                    </div>
                    <div style={{ padding: '10px 8px', borderRadius: '12px', background: '#F8FAFC', border: '1px solid rgba(15, 23, 42, 0.05)', textAlign: 'center' }}>
                      <div style={{ fontSize: '0.64rem', color: 'var(--text-muted)', fontWeight: 700 }}>Dot Ball %</div>
                      <div style={{ fontSize: '1.05rem', fontWeight: 800, color: 'var(--text-primary)', marginTop: '2px' }}>{selectedPlayerModal.bowling.p_dot_pct.toFixed(1)}%</div>
                    </div>
                  </div>
                )}

                {/* Batter Metrics */}
                {selectedPlayerModal.batting && (
                  <div className="modal-stat-grid" style={{ marginTop: selectedPlayerModal.bowling ? '8px' : 0 }}>
                    <div style={{ padding: '10px 8px', borderRadius: '12px', background: '#F8FAFC', border: '1px solid rgba(15, 23, 42, 0.05)', textAlign: 'center' }}>
                      <div style={{ fontSize: '0.64rem', color: 'var(--text-muted)', fontWeight: 700 }}>Pressure SR</div>
                      <div style={{ fontSize: '1.05rem', fontWeight: 800, color: 'var(--text-primary)', marginTop: '2px' }}>{selectedPlayerModal.batting.p_sr.toFixed(1)}</div>
                    </div>
                    <div style={{ padding: '10px 8px', borderRadius: '12px', background: '#F8FAFC', border: '1px solid rgba(15, 23, 42, 0.05)', textAlign: 'center' }}>
                      <div style={{ fontSize: '0.64rem', color: 'var(--text-muted)', fontWeight: 700 }}>SR Delta</div>
                      <div style={{ fontSize: '1.05rem', fontWeight: 800, color: selectedPlayerModal.batting.sr_delta > 0 ? '#10B981' : '#DC2626', marginTop: '2px' }}>
                        {selectedPlayerModal.batting.sr_delta > 0 ? '+' : ''}{selectedPlayerModal.batting.sr_delta.toFixed(1)}
                      </div>
                    </div>
                    <div style={{ padding: '10px 8px', borderRadius: '12px', background: '#F8FAFC', border: '1px solid rgba(15, 23, 42, 0.05)', textAlign: 'center' }}>
                      <div style={{ fontSize: '0.64rem', color: 'var(--text-muted)', fontWeight: 700 }}>Consistency</div>
                      <div style={{ fontSize: '1.05rem', fontWeight: 800, color: 'var(--rr-blue)', marginTop: '2px' }}>
                        {selectedPlayerModal.batting.consistency_pct !== undefined ? `${selectedPlayerModal.batting.consistency_pct.toFixed(0)}%` : '80%'}
                      </div>
                    </div>
                    <div style={{ padding: '10px 8px', borderRadius: '12px', background: '#F8FAFC', border: '1px solid rgba(15, 23, 42, 0.05)', textAlign: 'center' }}>
                      <div style={{ fontSize: '0.64rem', color: 'var(--text-muted)', fontWeight: 700 }}>Boundary %</div>
                      <div style={{ fontSize: '1.05rem', fontWeight: 800, color: 'var(--text-primary)', marginTop: '2px' }}>{selectedPlayerModal.batting.p_bdry_pct.toFixed(1)}%</div>
                      <div style={{ fontSize: '0.6rem', color: 'var(--text-muted)' }}>{selectedPlayerModal.batting.p_balls}b</div>
                    </div>
                    <div style={{ padding: '10px 8px', borderRadius: '12px', background: '#F8FAFC', border: '1px solid rgba(15, 23, 42, 0.05)', textAlign: 'center' }}>
                      <div style={{ fontSize: '0.64rem', color: 'var(--text-muted)', fontWeight: 700 }}>Dot Ball %</div>
                      <div style={{ fontSize: '1.05rem', fontWeight: 800, color: 'var(--text-primary)', marginTop: '2px' }}>{selectedPlayerModal.batting.p_dot_pct.toFixed(1)}%</div>
                    </div>
                  </div>
                )}
              </div>

              {/* Tactical Summary */}
              {selectedPlayerModal.summary && (
                <div style={{
                  padding: '14px 16px',
                  borderRadius: '12px',
                  background: '#FFF5F9',
                  border: '1px solid rgba(230, 0, 126, 0.15)',
                  fontSize: '0.8rem',
                  lineHeight: 1.5,
                  color: 'var(--text-secondary)'
                }}>
                  <span style={{ fontWeight: 800, color: 'var(--rr-pink)' }}>Scout Intelligence: </span>
                  {selectedPlayerModal.summary}
                </div>
              )}

              {/* Action Buttons */}
              <div style={{ display: 'flex', gap: '10px', marginTop: '6px' }}>
                <button
                  onClick={() => togglePlayerInShortlist(selectedPlayerModal.name)}
                  style={{
                    flex: 1,
                    padding: '12px',
                    borderRadius: '12px',
                    background: coachShortlist.includes(selectedPlayerModal.name) ? 'rgba(220, 38, 38, 0.08)' : 'var(--rr-blue)',
                    color: coachShortlist.includes(selectedPlayerModal.name) ? '#DC2626' : '#FFFFFF',
                    border: coachShortlist.includes(selectedPlayerModal.name) ? '1px solid rgba(220, 38, 38, 0.2)' : 'none',
                    fontWeight: 800,
                    fontSize: '0.82rem',
                    cursor: 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    gap: '6px'
                  }}
                >
                  <ClipboardList size={16} />
                  {coachShortlist.includes(selectedPlayerModal.name) ? 'Remove from Coach Shortlist' : 'Add to Coach Shortlist'}
                </button>
                <button
                  onClick={() => setSelectedPlayerModal(null)}
                  style={{
                    padding: '12px 20px',
                    borderRadius: '12px',
                    background: '#F1F5F9',
                    color: 'var(--text-primary)',
                    border: '1px solid rgba(15, 23, 42, 0.08)',
                    fontWeight: 700,
                    fontSize: '0.82rem',
                    cursor: 'pointer'
                  }}
                >
                  Close
                </button>
              </div>

            </div>
          </div>
        </div>
      )}

      {/* FLOATING MOBILE & TABLET BOTTOM NAVIGATION DOCK (FIXED TO VIEWPORT / ZERO DRIFT ON SCROLL) */}
      {!(isBotOpen || isShortlistOpen || selectedPlayerModal) && (
        <nav className="mobile-floating-nav" aria-label="Mobile Navigation">
          <div className="mobile-nav-pill">
            {dockNavItems.map(item => {
              const Icon = item.icon;
              const isActive = activePage === item.id;
              return (
                <button
                  key={item.id}
                  onClick={() => {
                    setActivePage(item.id as any);
                    window.scrollTo({ top: 0, behavior: 'smooth' });
                  }}
                  className={`mobile-nav-btn ${isActive ? 'active' : ''}`}
                  aria-label={item.label}
                  title={item.label}
                >
                  <Icon size={20} strokeWidth={isActive ? 2.4 : 1.9} />
                </button>
              );
            })}
          </div>
        </nav>
      )}

    </div>
  );
}
