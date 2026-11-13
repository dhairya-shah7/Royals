# 🏆 Rajasthan Royals · SupeRR Selector (Season 2)
### *A Multi-Dimensional Clutch Index & Target Acquisition Engine for IPL 2027*

This repository contains the complete analytical framework, statistical models, interactive scout platform, and official methodology report submitted for **Rajasthan Royals SupeRR Selector Season 2**.

---

## 📌 Executive Summary
T20 analytics routinely misclassifies death-over volume as genuine situational temperament. By evaluating **201,173 deliveries** from 2008 to 2024 across 793 registered players, this project formulates an empirical **Clutch Index ($C_i$)** that isolates player performance under objectively verified leverage.

### Key Innovations:
1. **Dynamic Leverage Filtering:** Quantifies pressure deliveries across all match phases ($N = 82,625$, 41.1% of tournament history) rather than relying solely on death-over proxies.
2. **Empirical Bayes Shrinkage:** Solves the small-sample distortion problem ($N_0 = 120$ for batters, $N_0 = 90$ for bowlers) to separate sustainable baseline skill from random variance.
3. **Multi-Objective Value Function:** Evaluates auction targets across Scarcity, Role Match, Reliability, and Value for Money ($V_i \in [0, 100]$).
4. **Live Interactive Scout Engine:** High-performance React + TypeScript single-page application with real-time head-to-head comparisons, dynamic parameter tuning, and coach target shortlisting.

---

## 📂 Repository Structure
```
├── Royals_SupeRR_Selector_Season_2_Methodology_Report.pdf  # Official 5-Page Submission Report
├── frontend/                                              # Interactive Scout Engine SPA
│   ├── src/                                               # React 19 + TypeScript source
│   │   ├── App.tsx                                        # Main platform interface & scout engine
│   │   ├── data/clutch_index.json                         # Pre-computed Bayesian ratings (793 players)
│   │   └── utils/scoutEngine.ts                           # Algorithmic search, comparison & audit engine
│   ├── public/                                            # Static assets & PDF report
│   └── package.json                                       # Frontend dependencies
├── build_deliverable_pdf.py                               # PyMuPDF compilation engine for official PDF
├── generate_full_clutch_data.py                           # Full tournament clutch computation pipeline
├── generate_report_charts.py                              # Matplotlib statistical visualization generator
└── README.md
```

---

## ⚡ Interactive Scout Engine (Frontend)
The web application is built with **React 19, TypeScript, and Vite**, featuring:
- **Leaderboards:** Instant ranking across Batters, Bowlers, and All-Rounders with phase filters (Powerplay, Middle, Death).
- **Matrix Compare:** Direct head-to-head radar comparisons of clutch metrics, boundary percentage, dot ball containment, and delta performance.
- **War Room 2027:** Targeted solutions addressing RR's four core structural weaknesses (Overseas Yorker Specialist, Indian Pace Anchor, Middle-Overs Spin Enforcer, Counter-Attacking Finisher).
- **Coach's Playbook:** Actionable match-phase tactical directives derived from empirical leverage thresholds.
- **Direct PDF Access:** In-app access to the full methodology dossier via the top navigation bar.

### Running Locally:
```bash
cd frontend
npm install
npm run dev
```

---

## 📄 Official Methodology Report
The full 5-page submission document is available in the root directory:
👉 **[Royals_SupeRR_Selector_Season_2_Methodology_Report.pdf](./Royals_SupeRR_Selector_Season_2_Methodology_Report.pdf)**

---
*Created for Rajasthan Royals SupeRR Selector Season 2.*
