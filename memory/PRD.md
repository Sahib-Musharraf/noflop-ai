# Noflop.ai - PRD

## Problem Statement
Build a single-page startup idea validation app called Noflop.ai with a 9-dimension structured scoring engine. Uses Claude Sonnet 4.5 for brutally honest evaluation across Problem, Market, ICP, Behavior, Feasibility, Monetization, Advantage, Execution, and Risk dimensions.

## Architecture
- **Frontend**: React 18 with Framer Motion, react-router-dom
- **Backend**: FastAPI (Python) with pymongo
- **Database**: MongoDB (results storage for shareable links)
- **AI**: Claude Sonnet 4.5 via emergentintegrations (Emergent LLM Key)
- **Local Storage**: Idea history sidebar

## What's Been Implemented

### Iteration 1-3 (Jan 30, 2026)
- [x] Hero section, dark theme, indigo accent
- [x] Basic idea validation flow with Claude Sonnet 4.5
- [x] Signal/Score/Brutal Truth/User Questions result cards
- [x] Differentiation Angles, Similar Failures cards
- [x] Idea History Sidebar (localStorage)
- [x] Recommendation Engine with Validate This buttons
- [x] Copy Result + Copy Link buttons
- [x] Leaderboard with crown icons for top 3
- [x] Shareable result links (?r={id})

### Iteration 4 (Jan 30, 2026) — MAJOR UPGRADE
- [x] **9-Dimension Scoring Engine**: Problem, Market, ICP, Behavior, Feasibility, Monetization, Advantage, Execution, Risk — each scored 0-10
- [x] **Weighted Final Score**: Calculated per formula with proper weights
- [x] **Deep Analysis Mode**: Expandable form with 14 optional context fields (target user, problem, current behavior, trigger moment, frequency, pain level, existing alternatives, monetization idea, willingness to pay, why now, unfair advantage, MVP plan, time to build, failure risk)
- [x] **Animated Breakdown Bars**: Color-coded per dimension with animated fill
- [x] **Strengths + Risks**: Side-by-side cards with green/red bullet indicators
- [x] **Critical Insights**: Highlighted must-know items
- [x] **Actionable Suggestions**: Numbered next steps
- [x] **Verdict System**: Build / Refine / Avoid (replacing BUILD IT / KILL IT / PIVOT IT)
- [x] **Backward Compatibility**: All existing features preserved (sidebar, leaderboard, share, pivots)
- [x] Testing: Backend 100%, Frontend 100%, Integration blocked only by API budget limit

## Backlog
- P1: Rate limiting
- P1: OG meta tags for social sharing
- P2: Compare two ideas side-by-side
- P3: Export as PDF/image

## Next Tasks
- Add balance to Emergent LLM key (budget exceeded from testing)
- Social share buttons
