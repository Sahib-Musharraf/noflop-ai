# Noflop.ai - PRD

## Problem Statement
Build a single-page startup idea validation app called Noflop.ai with the tagline "Don't let your idea flop." The app uses AI (Claude Sonnet 4.5) to provide brutally honest feedback on startup ideas with structured sections. Additional features: shareable result links, idea history sidebar, recommendation engine, copy result.

## Architecture
- **Frontend**: React 18 with Framer Motion, react-router-dom
- **Backend**: FastAPI (Python) with pymongo
- **Database**: MongoDB (for storing results for shareable links)
- **AI**: Claude Sonnet 4.5 via emergentintegrations library (Emergent LLM Key)
- **Local Storage**: Idea history sidebar (no backend needed)

## User Personas
- Startup founders validating ideas before building
- Indie hackers looking for honest feedback
- VCs/advisors sharing quick idea assessments

## Core Requirements
- Single page app, no auth required
- AI-powered idea validation with structured output
- Dark theme (#0A0A0A bg, indigo accent)
- Shareable result links via URL params (?r={id})
- Mobile responsive

## What's Been Implemented

### Iteration 1 (Jan 30, 2026)
- [x] Hero section matching reference design (42% stat, pills, badge)
- [x] Textarea input with character count, Ctrl+Enter shortcut
- [x] Claude Sonnet 4.5 integration for brutal idea validation
- [x] Result cards: Signal badge, Score, Brutal Truth (3 sections), User Questions (3)
- [x] MongoDB storage for results with unique IDs
- [x] Shareable link generation and loading
- [x] Loading state with spinner animation
- [x] Error handling for short inputs
- [x] Mobile responsive design
- [x] Copy to clipboard for share links

### Iteration 2 (Jan 30, 2026)
- [x] **Differentiation Angle** card: 2-3 specific ways to make idea different from competition
- [x] **Similar Ideas That Flopped** card: 1-2 real startups that tried similar and failed with reasons
- [x] **Idea History Sidebar**: localStorage-based left sidebar with verdict badges, scores, click to reload
- [x] **Recommendation Engine**: "You might want to build this instead" with 3 pivot ideas + Validate This buttons
- [x] **Copy Result Button**: Formatted verdict, score, key points with noflop.ai branding
- [x] All E2E testing passed (100% backend, frontend, integration)

### Iteration 3 (Jan 30, 2026)
- [x] **Leaderboard**: Top-scored ideas ranked by score, crown icons for top 3, current result highlighted, refreshes after each validation
- [x] All E2E testing passed (100% backend, frontend, integration)

## Backlog
- P1: Rate limiting to prevent abuse
- P1: Social share (Twitter/LinkedIn) with OG meta tags
- P2: "Compare two ideas" side-by-side mode
- P2: Clear history button in sidebar
- P3: Export result as PDF/image
- P3: Analytics dashboard (most common signals, avg scores)

## Next Tasks
- Add OG meta tags for better social sharing preview
- Add rate limiting middleware
- Social share buttons (Twitter/LinkedIn)
