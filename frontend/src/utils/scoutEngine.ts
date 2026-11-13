/**
 * Royals Scout Engine & Coach Shortlist Auditor
 * Deterministic, rule-and-index-based analytical intelligence engine
 * Powered by Rajasthan Royals 200,999-delivery MTGI Clutch Index.
 */

export interface PlayerStat {
  name: string;
  team: string;
  role: string;
  clutchScore: number;
  consistencyPct?: number;
  verdict: string;
  verdictClass: 'buy' | 'monitor' | 'pass';
  summary: string;
  batting?: {
    p_balls: number;
    p_runs: number;
    p_sr: number;
    n_sr: number;
    sr_delta: number;
    p_dot_pct: number;
    p_bdry_pct: number;
    consistency_pct?: number;
    clutch_score: number;
  } | null;
  bowling?: {
    p_balls: number;
    p_runs: number;
    p_econ: number;
    n_econ: number;
    econ_delta: number;
    p_wkts: number;
    p_dot_pct: number;
    consistency_pct?: number;
    clutch_score: number;
  } | null;
  phases?: {
    batting?: {
      powerplay?: { balls: number; runs: number; sr: number; dotPct: number; bdryPct: number };
      middle?: { balls: number; runs: number; sr: number; dotPct: number; bdryPct: number };
      death?: { balls: number; runs: number; sr: number; dotPct: number; bdryPct: number };
    };
    bowling?: {
      powerplay?: { balls: number; runs: number; wkts: number; econ: number; dotPct: number };
      middle?: { balls: number; runs: number; wkts: number; econ: number; dotPct: number };
      death?: { balls: number; runs: number; wkts: number; econ: number; dotPct: number };
    };
  };
}

export interface ComparisonResult {
  p1: PlayerStat;
  p2: PlayerStat;
  category: 'BATTER' | 'BOWLER' | 'ALL_ROUNDER';
  metrics: {
    label: string;
    v1: string | number;
    v2: string | number;
    winner: 1 | 2 | 0;
  }[];
  verdictWinner: string;
  rationale: string;
}

export interface CoachShortlistAudit {
  grade: 'A+' | 'A' | 'B+' | 'B' | 'C' | 'D';
  totalPlayers: number;
  buyCount: number;
  monitorCount: number;
  avoidCount: number;
  players: {
    player: PlayerStat;
    verdict: 'MUST BUY' | 'CONSIDER / VALUE' | 'AVOID / TRAP PICK';
    verdictClass: 'buy' | 'monitor' | 'pass';
    roleFit: string;
    keyMetric: string;
    redFlag?: string;
  }[];
  gapCheck: {
    deathBowlingCovered: boolean;
    spinSurgeCovered: boolean;
    finishingDepthCovered: boolean;
    deathDetail: string;
    spinDetail: string;
    finishDetail: string;
  };
  executiveSummary: string;
  recommendedSwaps: {
    dropPlayer: string;
    suggestedAdd: string;
    reason: string;
  }[];
}

// Clean and normalize strings for matching
export function cleanToken(s: string): string {
  return s.toLowerCase().replace(/[^a-z0-9]/g, '');
}

// Calculate similarity score between 0 and 1
export function stringSimilarity(s1: string, s2: string): number {
  const a = cleanToken(s1);
  const b = cleanToken(s2);
  if (a === b) return 1.0;
  if (!a || !b) return 0.0;
  if (a.includes(b) || b.includes(a)) return 0.85;

  const longer = a.length > b.length ? a : b;
  const shorter = a.length > b.length ? b : a;
  let matches = 0;
  for (let i = 0; i < shorter.length; i++) {
    if (longer.includes(shorter[i])) matches++;
  }
  return matches / longer.length;
}

// Resolve any player name from query against dataset.players
export function findBestPlayerMatch(queryName: string, playersMap: Record<string, PlayerStat>): PlayerStat | null {
  const qClean = cleanToken(queryName);
  if (!qClean || qClean.length < 3) return null;

  // 1. Direct dictionary key match
  if (playersMap[qClean]) return playersMap[qClean];

  // 2. Direct name match in lowercase
  const keys = Object.keys(playersMap);
  const exactKey = keys.find(k => k === qClean || cleanToken(playersMap[k].name) === qClean);
  if (exactKey) return playersMap[exactKey];

  // 3. Substring match
  const subKey = keys.find(k => k.includes(qClean) || qClean.includes(k));
  if (subKey) return playersMap[subKey];

  // 4. Fuzzy similarity lookup
  let bestScore = 0;
  let bestMatch: PlayerStat | null = null;
  for (const k of keys) {
    const score = stringSimilarity(qClean, k);
    if (score > bestScore && score >= 0.70) {
      bestScore = score;
      bestMatch = playersMap[k];
    }
  }

  return bestMatch;
}

// Search all players in the dataset matching query
export function searchPlayers(queryName: string, playersMap: Record<string, PlayerStat>, limit: number = 8): PlayerStat[] {
  const q = queryName.trim().toLowerCase();
  if (!q || q.length < 2) return [];

  const qClean = cleanToken(q);
  const qTokens = q.split(/\s+/).filter(Boolean);
  const all = Object.values(playersMap);

  const matched = all.filter(p => {
    const pName = p.name.toLowerCase();
    const pClean = cleanToken(p.name);
    const pTeam = (p.team || '').toLowerCase();
    const pRole = (p.role || '').toLowerCase();
    
    // Check if clean name matches or if all search tokens match name/team/role
    if (pClean.includes(qClean) || qClean.includes(pClean)) return true;
    return qTokens.every(tok => pName.includes(tok) || pTeam.includes(tok) || pRole.includes(tok));
  });

  return matched.sort((a, b) => {
    const aClean = cleanToken(a.name);
    const bClean = cleanToken(b.name);
    const aExact = aClean === qClean;
    const bExact = bClean === qClean;
    if (aExact && !bExact) return -1;
    if (!aExact && bExact) return 1;

    const aStarts = a.name.toLowerCase().startsWith(q);
    const bStarts = b.name.toLowerCase().startsWith(q);
    if (aStarts && !bStarts) return -1;
    if (!aStarts && bStarts) return 1;

    return (b.clutchScore || 0) - (a.clutchScore || 0);
  }).slice(0, limit);
}

// Head-to-Head Player Comparison Logic
export function compareTwoPlayers(p1Name: string, p2Name: string, playersMap: Record<string, PlayerStat>): ComparisonResult | null {
  const p1 = findBestPlayerMatch(p1Name, playersMap);
  const p2 = findBestPlayerMatch(p2Name, playersMap);
  if (!p1 || !p2) return null;

  const isBowl = (p1.bowling !== null || p2.bowling !== null) && (p1.batting === null && p2.batting === null);
  const isAllRound = (p1.batting && p1.bowling) || (p2.batting && p2.bowling);
  const category = isAllRound ? 'ALL_ROUNDER' : isBowl ? 'BOWLER' : 'BATTER';

  const metrics: ComparisonResult['metrics'] = [];
  let p1Points = 0;
  let p2Points = 0;

  // Clutch Rating
  const s1 = p1.clutchScore || 0;
  const s2 = p2.clutchScore || 0;
  metrics.push({
    label: 'Clutch Score',
    v1: s1.toFixed(1),
    v2: s2.toFixed(1),
    winner: s1 > s2 ? 1 : s2 > s1 ? 2 : 0
  });
  if (s1 > s2) p1Points++; else if (s2 > s1) p2Points++;

  // Batting Metrics if relevant
  if (p1.batting || p2.batting) {
    const sr1 = p1.batting?.p_sr || 0;
    const sr2 = p2.batting?.p_sr || 0;
    metrics.push({
      label: 'Pressure Strike Rate',
      v1: sr1 ? `${sr1.toFixed(1)}` : 'N/A',
      v2: sr2 ? `${sr2.toFixed(1)}` : 'N/A',
      winner: sr1 > sr2 ? 1 : sr2 > sr1 ? 2 : 0
    });
    if (sr1 > sr2) p1Points++; else if (sr2 > sr1) p2Points++;

    const d1 = p1.batting?.sr_delta || 0;
    const d2 = p2.batting?.sr_delta || 0;
    metrics.push({
      label: 'Pressure Boost',
      v1: d1 ? `+${d1.toFixed(1)}` : 'N/A',
      v2: d2 ? `+${d2.toFixed(1)}` : 'N/A',
      winner: d1 > d2 ? 1 : d2 > d1 ? 2 : 0
    });
    if (d1 > d2) p1Points++; else if (d2 > d1) p2Points++;

    const bnd1 = p1.batting?.p_bdry_pct || 0;
    const bnd2 = p2.batting?.p_bdry_pct || 0;
    metrics.push({
      label: 'Boundary % Under Pressure',
      v1: bnd1 ? `${bnd1.toFixed(1)}%` : 'N/A',
      v2: bnd2 ? `${bnd2.toFixed(1)}%` : 'N/A',
      winner: bnd1 > bnd2 ? 1 : bnd2 > bnd1 ? 2 : 0
    });
    if (bnd1 > bnd2) p1Points++; else if (bnd2 > bnd1) p2Points++;
  }

  // Bowling Metrics if relevant
  if (p1.bowling || p2.bowling) {
    const ec1 = p1.bowling?.p_econ || 99;
    const ec2 = p2.bowling?.p_econ || 99;
    metrics.push({
      label: 'Pressure Economy (Lower is better)',
      v1: ec1 !== 99 ? ec1.toFixed(2) : 'N/A',
      v2: ec2 !== 99 ? ec2.toFixed(2) : 'N/A',
      winner: ec1 < ec2 ? 1 : ec2 < ec1 ? 2 : 0
    });
    if (ec1 < ec2) p1Points++; else if (ec2 < ec1) p2Points++;

    const wk1 = p1.bowling?.p_wkts || 0;
    const wk2 = p2.bowling?.p_wkts || 0;
    metrics.push({
      label: 'Pressure Wickets',
      v1: wk1,
      v2: wk2,
      winner: wk1 > wk2 ? 1 : wk2 > wk1 ? 2 : 0
    });
    if (wk1 > wk2) p1Points++; else if (wk2 > wk1) p2Points++;

    const dt1 = p1.bowling?.p_dot_pct || 0;
    const dt2 = p2.bowling?.p_dot_pct || 0;
    metrics.push({
      label: 'Dot Ball %',
      v1: dt1 ? `${dt1.toFixed(1)}%` : 'N/A',
      v2: dt2 ? `${dt2.toFixed(1)}%` : 'N/A',
      winner: dt1 > dt2 ? 1 : dt2 > dt1 ? 2 : 0
    });
    if (dt1 > dt2) p1Points++; else if (dt2 > dt1) p2Points++;
  }

  // Match Consistency Rate (Dual Engine Component)
  const c1 = p1.batting?.consistency_pct ?? p1.bowling?.consistency_pct ?? p1.consistencyPct ?? 50.0;
  const c2 = p2.batting?.consistency_pct ?? p2.bowling?.consistency_pct ?? p2.consistencyPct ?? 50.0;
  metrics.push({
    label: 'Match Consistency Rate (C_rate)',
    v1: `${c1.toFixed(1)}%`,
    v2: `${c2.toFixed(1)}%`,
    winner: c1 > c2 ? 1 : c2 > c1 ? 2 : 0
  });
  if (c1 > c2) p1Points++; else if (c2 > c1) p2Points++;

  const winner = p1Points > p2Points ? p1.name : p2Points > p1Points ? p2.name : 'TIE / CONTEXT DEPENDENT';
  const winnerPlayer = p1Points >= p2Points ? p1 : p2;
  const loserPlayer = p1Points >= p2Points ? p2 : p1;

  const rationale = `${winnerPlayer.name} edges out ${loserPlayer.name} with stronger execution across high-stress leverage deliveries (won ${Math.max(p1Points, p2Points)} of ${metrics.length} metrics).`;

  return {
    p1,
    p2,
    category,
    metrics,
    verdictWinner: winner,
    rationale
  };
}

// Coach's Shortlist Audit System
export function auditCoachShortlist(
  names: string[],
  playersMap: Record<string, PlayerStat>,
  dataset: any
): CoachShortlistAudit {
  const evaluatedPlayers: CoachShortlistAudit['players'] = [];
  let buyCount = 0;
  let monitorCount = 0;
  let avoidCount = 0;

  let hasDeathBowler = false;
  let hasSpinSurge = false;
  let hasFinisher = false;

  let deathDetail = "⚠️ No specialist with pressure economy < 8.2 found.";
  let spinDetail = "⚠️ No batter with positive surge delta against high tension found.";
  let finishDetail = "⚠️ No high-boundary finisher under pressure found.";

  names.forEach(rawName => {
    const p = findBestPlayerMatch(rawName, playersMap);
    if (!p) {
      evaluatedPlayers.push({
        player: {
          name: rawName,
          team: 'Unknown',
          role: 'Candidate',
          clutchScore: 0,
          verdict: 'NOT FOUND IN DATASET',
          verdictClass: 'pass',
          summary: 'Player did not register minimum 15 qualifying balls in 2022–2026 IPL/T20I dataset.'
        },
        verdict: 'AVOID / TRAP PICK',
        verdictClass: 'pass',
        roleFit: 'Unverified sample',
        keyMetric: '0 Balls in Dataset',
        redFlag: 'Insufficient pressure sample to substantiate an auction bid.'
      });
      avoidCount++;
      return;
    }

    // Determine primary role accurately (Bowler vs Batter vs All-Rounder)
    const batVol = p.batting?.p_balls || 0;
    const bowlVol = p.bowling?.p_balls || 0;
    const isBowler = p.role.toLowerCase().includes('bowl') || (p.bowling && (bowlVol >= batVol * 1.5 || batVol < 30 || p.bowling.p_wkts >= 15));
    const isAllRounder = p.role.toLowerCase().includes('all') || (p.batting && p.bowling && batVol >= 40 && bowlVol >= 40 && p.batting.p_sr >= 115);

    // Role-specific evaluation logic
    let verdict: CoachShortlistAudit['players'][0]['verdict'] = 'CONSIDER / VALUE';
    let redFlag: string | undefined;
    let roleFit = isAllRounder ? 'All-Rounder' : isBowler ? 'Bowler' : 'Batter';
    const consist = isBowler ? (p.bowling?.consistency_pct ?? p.consistencyPct ?? 50.0) : (p.batting?.consistency_pct ?? p.consistencyPct ?? 50.0);
    let keyMetric = `Clutch: ${p.clutchScore.toFixed(1)} · ${consist.toFixed(0)}% Consist`;

    if (isBowler && p.bowling) {
      keyMetric = `${p.bowling.p_econ.toFixed(2)} Econ · ${p.bowling.p_wkts} Wkts · ${consist.toFixed(0)}% Consist`;
      if (p.bowling.p_econ <= 8.5 && p.bowling.econ_delta <= 0.5 && p.bowling.p_balls >= 50 && consist >= 65) {
        verdict = 'MUST BUY';
        buyCount++;
      } else if (p.bowling.p_econ <= 9.2 && p.bowling.p_balls >= 30) {
        verdict = 'CONSIDER / VALUE';
        monitorCount++;
        if (consist < 55) {
          redFlag = `High match-to-match volatility: Delivers winning baseline in only ${consist.toFixed(0)}% of high-tension matches.`;
        }
      } else {
        verdict = 'AVOID / TRAP PICK';
        avoidCount++;
        redFlag = p.bowling.econ_delta > 0.6
          ? `Economy inflates by +${p.bowling.econ_delta.toFixed(2)} in death overs (${consist.toFixed(0)}% consistency).`
          : `High pressure economy (${p.bowling.p_econ.toFixed(2)} RPO) exceeds death limits.`;
      }

      if (p.bowling.p_econ <= 8.3 && p.bowling.p_balls >= 50) {
        hasDeathBowler = true;
        deathDetail = `✅ Covered by ${p.name} (${p.bowling.p_econ.toFixed(2)} Econ, ${p.bowling.p_wkts} Wkts, ${consist.toFixed(0)}% Consist)`;
      }
    } else if (isAllRounder && p.batting && p.bowling) {
      keyMetric = `${p.batting.p_sr.toFixed(1)} SR | ${p.bowling.p_econ.toFixed(2)} Econ · ${consist.toFixed(0)}% Consist`;
      if (p.batting.sr_delta > 0 && p.bowling.econ_delta <= 0.6 && consist >= 65) {
        verdict = 'MUST BUY';
        buyCount++;
      } else {
        verdict = 'CONSIDER / VALUE';
        monitorCount++;
      }
      if (p.bowling.p_econ <= 8.5) hasDeathBowler = true;
      if (p.batting.sr_delta >= 15) hasSpinSurge = true;
    } else if (p.batting) {
      keyMetric = `${p.batting.p_sr.toFixed(1)} SR (+${p.batting.sr_delta.toFixed(1)} Surge) · ${consist.toFixed(0)}% Consist`;
      if (p.batting.p_balls >= 60 && p.batting.sr_delta >= 15 && p.batting.p_sr >= 165 && consist >= 65) {
        verdict = 'MUST BUY';
        buyCount++;
      } else if (p.batting.p_balls >= 30 && p.batting.sr_delta >= 0) {
        verdict = 'CONSIDER / VALUE';
        monitorCount++;
        if (consist < 55) {
          redFlag = `Boom-or-bust risk: Delivers targeted crisis SR in only ${consist.toFixed(0)}% of pressure outings.`;
        }
      } else {
        verdict = 'AVOID / TRAP PICK';
        avoidCount++;
        redFlag = p.batting.sr_delta < 0
          ? `Strike rate plummets by ${Math.abs(p.batting.sr_delta).toFixed(1)} in crisis (${consist.toFixed(0)}% consistency).`
          : `High dot ball rate (${p.batting.p_dot_pct.toFixed(1)}%) freezes middle-overs chases.`;
      }

      if (p.batting.sr_delta >= 15 && p.batting.p_sr >= 170) {
        hasSpinSurge = true;
        spinDetail = `✅ Covered by ${p.name} (${p.batting.p_sr.toFixed(1)} SR, +${p.batting.sr_delta.toFixed(1)} Surge, ${consist.toFixed(0)}% Consist)`;
      }
      if (p.batting.p_bdry_pct >= 28 && p.batting.p_balls >= 60) {
        hasFinisher = true;
        finishDetail = `✅ Covered by ${p.name} (${p.batting.p_bdry_pct.toFixed(1)}% Boundaries, ${consist.toFixed(0)}% Consist)`;
      }
    } else {
      verdict = 'CONSIDER / VALUE';
      monitorCount++;
    }

    evaluatedPlayers.push({
      player: p,
      verdict,
      verdictClass: verdict === 'MUST BUY' ? 'buy' : verdict === 'CONSIDER / VALUE' ? 'monitor' : 'pass',
      roleFit,
      keyMetric,
      redFlag
    });
  });

  // Calculate Overall Grade
  const total = names.length || 1;
  const buyRatio = buyCount / total;
  let grade: CoachShortlistAudit['grade'] = 'B';
  if (buyRatio >= 0.8 && hasDeathBowler && (hasSpinSurge || hasFinisher)) grade = 'A+';
  else if (buyRatio >= 0.6 && (hasDeathBowler || hasSpinSurge)) grade = 'A';
  else if (buyRatio >= 0.5) grade = 'B+';
  else if (buyRatio >= 0.3) grade = 'B';
  else if (avoidCount >= 2) grade = 'C';
  else grade = 'D';

  // Generate Data-Backed Suggested Swaps for any Avoid players (Role-Aware)
  const recommendedSwaps: CoachShortlistAudit['recommendedSwaps'] = [];
  evaluatedPlayers.filter(ep => ep.verdict === 'AVOID / TRAP PICK').forEach(ep => {
    const isBowler = ep.roleFit === 'Bowler';
    const cleanNames = names.map(cleanToken);

    if (isBowler) {
      const topAlternativeObj = (dataset.topBowlers || []).find((bw: any) => !cleanNames.includes(cleanToken(bw.name)));
      const topAltName = topAlternativeObj ? topAlternativeObj.name : "Matheesha Pathirana";
      const altEcon = topAlternativeObj ? topAlternativeObj.economy : 6.52;
      const altWkts = topAlternativeObj ? topAlternativeObj.wickets : 53;
      recommendedSwaps.push({
        dropPlayer: ep.player.name,
        suggestedAdd: topAltName,
        reason: `Replace bowler ${ep.player.name} with ${topAltName} for elite death-overs suppression (${altEcon} pressure economy, ${altWkts} clutch wickets).`
      });
    } else {
      const topAlternativeObj = (dataset.topBatters || []).find((b: any) => !cleanNames.includes(cleanToken(b.name)));
      const topAltName = topAlternativeObj ? topAlternativeObj.name : "Naman Dhir";
      const altSR = topAlternativeObj ? topAlternativeObj.strikeRate : 211.1;
      const altSurge = topAlternativeObj ? topAlternativeObj.srDelta : 67.9;
      recommendedSwaps.push({
        dropPlayer: ep.player.name,
        suggestedAdd: topAltName,
        reason: `Replace batter ${ep.player.name} with ${topAltName} for explosive crisis acceleration (${altSR} SR, +${altSurge} surge delta).`
      });
    }
  });

  // Executive summary
  const executiveSummary = `${buyCount} of ${total} coach-shortlisted players are verified clutch assets. ${
    avoidCount > 0
      ? `Caution: ${avoidCount} player(s) suffer from negative tension deltas and should be avoided or replaced.`
      : 'Zero critical red flags detected across all shortlisted targets.'
  } Rajasthan Royals gap analysis: Death Bowling is ${hasDeathBowler ? 'SECURED' : 'UNRESOLVED'}, Middle-Overs Punch is ${hasSpinSurge ? 'STRONG' : 'NEEDS ATTENTION'}.`;

  return {
    grade,
    totalPlayers: total,
    buyCount,
    monitorCount,
    avoidCount,
    players: evaluatedPlayers,
    gapCheck: {
      deathBowlingCovered: hasDeathBowler,
      spinSurgeCovered: hasSpinSurge,
      finishingDepthCovered: hasFinisher,
      deathDetail,
      spinDetail,
      finishDetail
    },
    executiveSummary,
    recommendedSwaps
  };
}
