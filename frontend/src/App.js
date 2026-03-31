import React, { useState, useEffect, useRef, useCallback } from 'react';
import { useSearchParams } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Copy, Check, ArrowRight, Zap, Target, MessageCircle,
  AlertTriangle, Lightbulb, Skull, Sparkles, ChevronLeft,
  ChevronRight, Clock, ClipboardCheck, RotateCcw, Trophy, Crown,
  ChevronDown, Shield, TrendingUp, Crosshair, BarChart3, Rocket,
  Swords, Send
} from 'lucide-react';
import './App.css';

const API_URL = process.env.REACT_APP_BACKEND_URL;
const HISTORY_KEY = 'noflop_history';

const CONTEXT_FIELDS = [
  { key: 'target_user', label: 'Target User (ICP)', placeholder: 'Who exactly is this for? Be specific.', type: 'text' },
  { key: 'problem', label: 'Problem', placeholder: 'What problem does this solve?', type: 'text' },
  { key: 'current_behavior', label: 'Current Behavior', placeholder: 'How do users solve this today?', type: 'text' },
  { key: 'trigger_moment', label: 'Trigger Moment', placeholder: 'When exactly does the problem occur?', type: 'text' },
  { key: 'frequency', label: 'Frequency', placeholder: '', type: 'select', options: ['', 'Daily', 'Weekly', 'Monthly', 'Rarely'] },
  { key: 'pain_level', label: 'Pain Level', placeholder: '', type: 'select', options: ['', 'Low', 'Medium', 'High', 'Critical'] },
  { key: 'existing_alternatives', label: 'Existing Alternatives', placeholder: 'What tools/products exist today?', type: 'text' },
  { key: 'monetization_idea', label: 'Monetization Idea', placeholder: 'How will you make money?', type: 'text' },
  { key: 'willingness_to_pay', label: 'Willingness to Pay', placeholder: '', type: 'select', options: ['', 'Yes', 'No', 'Unsure'] },
  { key: 'why_now', label: 'Why Now?', placeholder: 'Why is now the right time for this?', type: 'text' },
  { key: 'unfair_advantage', label: 'Unfair Advantage', placeholder: 'What makes you/your team uniquely suited?', type: 'text' },
  { key: 'mvp_plan', label: 'MVP Plan', placeholder: 'What does v1 look like?', type: 'text' },
  { key: 'time_to_build', label: 'Time to Build', placeholder: '', type: 'select', options: ['', '1 week', '2-4 weeks', '1-3 months', '3-6 months', '6+ months'] },
  { key: 'failure_risk', label: 'Failure Risk', placeholder: 'Why might this fail?', type: 'text' },
];

const DIMENSION_META = {
  problem: { label: 'Problem', icon: AlertTriangle, color: '#EF4444' },
  market: { label: 'Market', icon: TrendingUp, color: '#6366F1' },
  icp: { label: 'ICP', icon: Crosshair, color: '#8B5CF6' },
  behavior: { label: 'Behavior', icon: Target, color: '#F59E0B' },
  feasibility: { label: 'Feasibility', icon: Rocket, color: '#22C55E' },
  monetization: { label: 'Monetization', icon: BarChart3, color: '#10B981' },
  advantage: { label: 'Advantage', icon: Shield, color: '#3B82F6' },
  execution: { label: 'Execution', icon: Zap, color: '#F97316' },
  risk: { label: 'Risk', icon: Skull, color: '#DC2626' },
};

function getHistory() {
  try { return JSON.parse(localStorage.getItem(HISTORY_KEY) || '[]'); } catch { return []; }
}

function saveToHistory(result) {
  const history = getHistory();
  const id = result.result_id || result.id;
  if (history.find(h => h.id === id)) return;
  history.unshift({ id, idea: result.idea, signal: result.signal, score: result.score, verdict: result.verdict, created_at: result.created_at });
  if (history.length > 50) history.pop();
  localStorage.setItem(HISTORY_KEY, JSON.stringify(history));
}

const emptyContext = () => CONTEXT_FIELDS.reduce((a, f) => ({ ...a, [f.key]: '' }), {});

function App() {
  const [idea, setIdea] = useState('');
  const [context, setContext] = useState(emptyContext);
  const [showContext, setShowContext] = useState(false);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [copied, setCopied] = useState(false);
  const [resultCopied, setResultCopied] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [history, setHistory] = useState(getHistory);
  const [searchParams] = useSearchParams();
  const resultRef = useRef(null);
  const [leaderboard, setLeaderboard] = useState([]);
  const [challengeOpen, setChallengeOpen] = useState(false);
  const [counterArg, setCounterArg] = useState('');
  const [challengeResult, setChallengeResult] = useState(null);
  const [challengeLoading, setChallengeLoading] = useState(false);

  const fetchLeaderboard = async () => {
    try {
      const res = await fetch(`${API_URL}/api/leaderboard`);
      if (res.ok) { const data = await res.json(); setLeaderboard(data.leaderboard || []); }
    } catch {}
  };

  useEffect(() => { fetchLeaderboard(); }, []);

  useEffect(() => {
    const rid = searchParams.get('r');
    if (rid) fetchResult(rid);
  }, [searchParams]);

  const fetchResult = async (id) => {
    setLoading(true); setError('');
    try {
      const res = await fetch(`${API_URL}/api/result/${id}`);
      if (!res.ok) throw new Error('Result not found');
      const data = await res.json();
      setResult(data); setIdea(data.idea);
      if (data.context_fields) setContext(prev => ({ ...prev, ...data.context_fields }));
      saveToHistory(data); setHistory(getHistory());
    } catch { setError('This result link has expired or doesn\'t exist.'); }
    finally { setLoading(false); }
  };

  const handleSubmit = useCallback(async (overrideIdea) => {
    const text = (overrideIdea || idea).trim();
    if (!text || text.length < 10) { setError('Come on. Give us at least a couple sentences to tear apart.'); return; }
    setLoading(true); setError(''); setResult(null);
    setChallengeOpen(false); setChallengeResult(null); setCounterArg('');
    try {
      const body = { idea: text, ...context };
      const res = await fetch(`${API_URL}/api/validate`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body),
      });
      if (!res.ok) { const e = await res.json().catch(() => ({})); throw new Error(e.detail || 'Something broke.'); }
      const data = await res.json();
      setResult(data); saveToHistory(data); setHistory(getHistory()); fetchLeaderboard();
      setTimeout(() => { resultRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' }); }, 300);
    } catch (err) { setError(err.message); }
    finally { setLoading(false); }
  }, [idea, context]);

  const handleValidatePivot = (pivotIdea) => {
    setIdea(pivotIdea); setContext(emptyContext()); setResult(null);
    window.scrollTo({ top: 0, behavior: 'smooth' });
    setTimeout(() => handleSubmit(pivotIdea), 100);
  };

  const loadHistoryItem = (item) => { setSidebarOpen(false); fetchResult(item.id); };

  const copyShareLink = () => {
    if (!result) return;
    const id = result.result_id || result.id;
    navigator.clipboard.writeText(`${window.location.origin}?r=${id}`);
    setCopied(true); setTimeout(() => setCopied(false), 2000);
  };

  const copyResultText = () => {
    if (!result) return;
    const bd = result.breakdown || {};
    const lines = [
      `${result.verdict || result.signal} — ${result.score}/10`,
      '', result.verdict_reason || result.signal_reason, '',
      'BREAKDOWN:',
      ...Object.entries(bd).map(([k, v]) => `  ${k}: ${v}/10`),
      '', 'STRENGTHS:',
      ...(result.strengths || []).map(s => `- ${s}`),
      '', 'RISKS:',
      ...(result.risks || []).map(r => `- ${r}`),
      '', 'CRITICAL INSIGHTS:',
      ...(result.critical_insights || []).map(c => `- ${c}`),
      '', 'ACTIONABLE SUGGESTIONS:',
      ...(result.actionable_suggestions || []).map(a => `- ${a}`),
      '', '---', 'Validated on noflop.ai — No glaze. No hype. Just signal.',
    ];
    navigator.clipboard.writeText(lines.join('\n'));
    setResultCopied(true); setTimeout(() => setResultCopied(false), 2000);
  };

  const handleChallenge = async () => {
    if (!counterArg.trim() || counterArg.trim().length < 10) return;
    const rid = result?.result_id || result?.id;
    if (!rid) return;
    setChallengeLoading(true); setChallengeResult(null);
    try {
      const res = await fetch(`${API_URL}/api/challenge`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ result_id: rid, counter_argument: counterArg.trim() }),
      });
      if (!res.ok) { const e = await res.json().catch(() => ({})); throw new Error(e.detail || 'Challenge failed.'); }
      const data = await res.json();
      setChallengeResult(data);
    } catch (err) { setChallengeResult({ counter_status: 'ERROR', reasoning: err.message }); }
    finally { setChallengeLoading(false); }
  };

  const handleKeyDown = (e) => { if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) handleSubmit(); };

  const getVerdictStyle = (v) => {
    if (!v) return {};
    const s = (v || '').toUpperCase();
    if (s === 'BUILD' || s.includes('BUILD')) return { color: 'var(--green)', bg: 'var(--green-dim)', border: 'var(--green-border)' };
    if (s === 'AVOID' || s.includes('KILL')) return { color: 'var(--red)', bg: 'var(--red-dim)', border: 'var(--red-border)' };
    return { color: 'var(--yellow)', bg: 'var(--yellow-dim)', border: 'var(--yellow-border)' };
  };

  const getSignalColorForItem = (signal) => {
    if (!signal) return 'var(--text-muted)';
    const s = signal.toUpperCase();
    if (s.includes('BUILD')) return 'var(--green)';
    if (s.includes('KILL') || s.includes('AVOID')) return 'var(--red)';
    return 'var(--yellow)';
  };

  const filledCount = Object.values(context).filter(v => v && v.trim()).length;
  const verdictDisplay = result?.verdict || (result?.signal?.includes('BUILD') ? 'Build' : result?.signal?.includes('KILL') ? 'Avoid' : 'Refine');
  const vs = getVerdictStyle(verdictDisplay);

  return (
    <div className="app-layout">
      {/* Sidebar */}
      <aside className={`sidebar ${sidebarOpen ? 'sidebar-open' : ''}`} data-testid="idea-sidebar">
        <div className="sidebar-header"><Clock size={14} /><span>Your Ideas</span></div>
        <div className="sidebar-list" data-testid="sidebar-list">
          {history.length === 0 ? (
            <div className="sidebar-empty">No ideas validated yet.</div>
          ) : history.map((item) => (
            <button key={item.id} className="sidebar-item" onClick={() => loadHistoryItem(item)} data-testid={`history-item-${item.id}`}>
              <div className="sidebar-item-top">
                <span className="sidebar-signal" style={{ color: getSignalColorForItem(item.signal) }}>{item.verdict || item.signal}</span>
                <span className="sidebar-score">{item.score}/10</span>
              </div>
              <p className="sidebar-idea">{item.idea}</p>
            </button>
          ))}
        </div>
      </aside>
      <button className={`sidebar-toggle ${sidebarOpen ? 'sidebar-toggle-open' : ''}`} onClick={() => setSidebarOpen(!sidebarOpen)} data-testid="sidebar-toggle">
        {sidebarOpen ? <ChevronLeft size={16} /> : <ChevronRight size={16} />}
        {!sidebarOpen && history.length > 0 && <span className="sidebar-count">{history.length}</span>}
      </button>
      {sidebarOpen && <div className="sidebar-overlay" onClick={() => setSidebarOpen(false)} />}

      <div className="app-main">
        {/* Nav */}
        <nav className="nav" data-testid="nav-bar">
          <div className="nav-logo" data-testid="nav-logo">noflop.ai</div>
          <div className="nav-tagline">No glaze. No hype. Just signal.</div>
        </nav>

        {/* Hero */}
        <section className="hero" data-testid="hero-section">
          <div className="hero-content">
            <div className="hero-left">
              <motion.div className="hero-badge" initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }} data-testid="hero-badge">
                <span className="badge-dot" />BRUTAL IDEA VALIDATION
              </motion.div>
              <motion.h1 className="hero-heading" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3, duration: 0.6 }} data-testid="hero-heading">
                Don't let your<br /><span className="accent-text">idea flop.</span>
              </motion.h1>
              <motion.p className="hero-sub" initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.5 }} data-testid="hero-subheading">
                An AI-powered idea validation tool for builders and founders. Brutal honesty. No sugarcoating. Real signal — in 30 seconds.
              </motion.p>
              <motion.div className="hero-pills" initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.7 }} data-testid="hero-pills">
                <span className="pill pill-green">BUILD</span>
                <span className="pill pill-red">AVOID</span>
                <span className="pill pill-yellow">REFINE</span>
                <span className="pill pill-outline">9-DIMENSION SCORING</span>
              </motion.div>
            </div>
            <motion.div className="hero-right" initial={{ opacity: 0, scale: 0.8 }} animate={{ opacity: 1, scale: 1 }} transition={{ delay: 0.4, duration: 0.8 }} data-testid="hero-stat">
              <span className="stat-number">42%</span>
            </motion.div>
          </div>
        </section>

        {/* Input Section */}
        <section className="input-section" data-testid="input-section">
          <div className="input-wrapper">
            <div className="input-header">
              <h2 className="input-title">Your idea gets one shot. Make it count.</h2>
              <p className="input-subtitle">Built for builders who want truth, not therapy.</p>
            </div>

            <div className="textarea-container">
              <textarea data-testid="idea-textarea" className="idea-input" placeholder="Describe your idea in 2-3 sentences. We will not be nice about it." value={idea} onChange={(e) => setIdea(e.target.value)} onKeyDown={handleKeyDown} maxLength={1000} rows={4} />
              <div className="textarea-footer">
                <span className="char-count">{idea.length}/1000</span>
                <span className="kbd-hint">Ctrl+Enter to submit</span>
              </div>
            </div>

            {/* Expandable Context Fields */}
            <button className="context-toggle" onClick={() => setShowContext(!showContext)} data-testid="context-toggle">
              <ChevronDown size={14} className={`context-chevron ${showContext ? 'context-chevron-open' : ''}`} />
              Deep Analysis Mode {filledCount > 0 && <span className="context-filled">{filledCount} field{filledCount > 1 ? 's' : ''} filled</span>}
              <span className="context-hint">{showContext ? 'Collapse' : 'More context = better analysis'}</span>
            </button>

            <AnimatePresence>
              {showContext && (
                <motion.div className="context-fields" initial={{ height: 0, opacity: 0 }} animate={{ height: 'auto', opacity: 1 }} exit={{ height: 0, opacity: 0 }} transition={{ duration: 0.3 }} data-testid="context-fields">
                  <div className="context-grid">
                    {CONTEXT_FIELDS.map(f => (
                      <div key={f.key} className={`context-field ${f.type === 'text' && (f.key === 'problem' || f.key === 'mvp_plan') ? 'context-field-wide' : ''}`}>
                        <label className="context-label">{f.label}</label>
                        {f.type === 'select' ? (
                          <select data-testid={`field-${f.key}`} className="context-select" value={context[f.key]} onChange={e => setContext(p => ({ ...p, [f.key]: e.target.value }))}>
                            {f.options.map(o => <option key={o} value={o}>{o || `Select ${f.label}`}</option>)}
                          </select>
                        ) : (
                          <input data-testid={`field-${f.key}`} className="context-input" placeholder={f.placeholder} value={context[f.key]} onChange={e => setContext(p => ({ ...p, [f.key]: e.target.value }))} />
                        )}
                      </div>
                    ))}
                  </div>
                </motion.div>
              )}
            </AnimatePresence>

            <AnimatePresence>
              {error && (
                <motion.div className="error-msg" initial={{ opacity: 0, y: -5 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }} data-testid="error-message">
                  <AlertTriangle size={14} /> {error}
                </motion.div>
              )}
            </AnimatePresence>

            <button data-testid="submit-button" className="submit-btn" onClick={() => handleSubmit()} disabled={loading || !idea.trim()}>
              {loading ? (
                <span className="loading-text"><span className="spinner" />Running your idea through the reality check...</span>
              ) : (<>Be Brutal <ArrowRight size={18} /></>)}
            </button>
          </div>
        </section>

        {/* Result */}
        <AnimatePresence>
          {result && (
            <motion.section ref={resultRef} className="result-section" initial={{ opacity: 0, y: 40 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: 40 }} transition={{ duration: 0.5 }} data-testid="result-section">
              <div className="result-wrapper">

                {/* Verdict + Score Header */}
                <div className="result-card verdict-card" data-testid="verdict-card">
                  <div className="verdict-top">
                    <div>
                      <div className="card-label"><Zap size={14} /> VERDICT</div>
                      <div className="signal-badge" style={{ color: vs.color, background: vs.bg, borderColor: vs.border }} data-testid="signal-badge">
                        {verdictDisplay.toUpperCase()}
                      </div>
                    </div>
                    <div className="verdict-score-block">
                      <div className="card-label"><Target size={14} /> SCORE</div>
                      <div className="score-display">
                        <span className="score-number" style={{ color: vs.color }} data-testid="score-number">{result.score}</span>
                        <span className="score-total">/10</span>
                      </div>
                    </div>
                  </div>
                  <p className="signal-reason" data-testid="verdict-reason">{result.verdict_reason || result.signal_reason}</p>
                </div>

                {/* 9-Dimension Breakdown */}
                {result.breakdown && Object.keys(result.breakdown).length > 0 && (
                  <div className="result-card breakdown-card" data-testid="breakdown-card">
                    <div className="card-label"><BarChart3 size={14} /> 9-DIMENSION BREAKDOWN</div>
                    <div className="breakdown-grid">
                      {Object.entries(DIMENSION_META).map(([key, meta]) => {
                        const val = result.breakdown[key] ?? 0;
                        const Icon = meta.icon;
                        return (
                          <div key={key} className="breakdown-row" data-testid={`breakdown-${key}`}>
                            <div className="breakdown-label">
                              <Icon size={13} style={{ color: meta.color }} />
                              <span>{meta.label}</span>
                            </div>
                            <div className="breakdown-bar-wrap">
                              <motion.div className="breakdown-bar" initial={{ width: 0 }} animate={{ width: `${val * 10}%` }} transition={{ delay: 0.1, duration: 0.6 }} style={{ background: meta.color }} />
                            </div>
                            <span className="breakdown-val" style={{ color: meta.color }}>{val}</span>
                          </div>
                        );
                      })}
                    </div>
                  </div>
                )}

                {/* Strengths + Risks side by side */}
                <div className="two-col-row">
                  {result.strengths?.length > 0 && (
                    <div className="result-card strengths-card" data-testid="strengths-card">
                      <div className="card-label"><TrendingUp size={14} /> STRENGTHS</div>
                      <div className="bullet-list">
                        {result.strengths.map((s, i) => (
                          <div key={i} className="bullet-item bullet-green" data-testid={`strength-${i}`}><span className="bullet-dot green-dot" /><p>{s}</p></div>
                        ))}
                      </div>
                    </div>
                  )}
                  {result.risks?.length > 0 && (
                    <div className="result-card risks-card" data-testid="risks-card">
                      <div className="card-label"><AlertTriangle size={14} /> RISKS</div>
                      <div className="bullet-list">
                        {result.risks.map((r, i) => (
                          <div key={i} className="bullet-item bullet-red" data-testid={`risk-${i}`}><span className="bullet-dot red-dot" /><p>{r}</p></div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>

                {/* Critical Insights */}
                {result.critical_insights?.length > 0 && (
                  <div className="result-card insights-card" data-testid="insights-card">
                    <div className="card-label"><Crosshair size={14} /> CRITICAL INSIGHTS</div>
                    <div className="insights-list">
                      {result.critical_insights.map((c, i) => (
                        <div key={i} className="insight-item" data-testid={`insight-${i}`}><span className="insight-marker">!</span><p>{c}</p></div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Actionable Suggestions */}
                {result.actionable_suggestions?.length > 0 && (
                  <div className="result-card suggestions-card" data-testid="suggestions-card">
                    <div className="card-label"><Rocket size={14} /> ACTIONABLE SUGGESTIONS</div>
                    <div className="questions-list">
                      {result.actionable_suggestions.map((a, i) => (
                        <div key={i} className="question-item" data-testid={`suggestion-${i}`}><span className="question-num">{i + 1}</span><p>{a}</p></div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Differentiation Angle */}
                {result.differentiation_angles?.length > 0 && (
                  <div className="result-card diff-card" data-testid="differentiation-card">
                    <div className="card-label"><Lightbulb size={14} /> DIFFERENTIATION ANGLE</div>
                    <div className="diff-list">
                      {result.differentiation_angles.map((angle, i) => (
                        <div key={i} className="diff-item" data-testid={`diff-angle-${i}`}><span className="diff-num">{i + 1}</span><p>{angle}</p></div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Similar Failures */}
                {result.similar_failures?.length > 0 && (
                  <div className="result-card failures-card" data-testid="similar-failures-card">
                    <div className="card-label"><Skull size={14} /> SIMILAR IDEAS THAT FLOPPED</div>
                    <div className="failures-list">
                      {result.similar_failures.map((f, i) => (
                        <div key={i} className="failure-item" data-testid={`failure-${i}`}><span className="failure-name">{f.name}</span><p>{f.reason}</p></div>
                      ))}
                    </div>
                  </div>
                )}

                {/* User Questions */}
                {result.user_questions?.length > 0 && (
                  <div className="result-card questions-card" data-testid="questions-card">
                    <div className="card-label"><MessageCircle size={14} /> WHAT TO ASK REAL USERS</div>
                    <div className="questions-list">
                      {result.user_questions.map((q, i) => (
                        <div key={i} className="question-item" data-testid={`question-${i}`}><span className="question-num">{i + 1}</span><p>{q}</p></div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Share */}
                <div className="share-bar" data-testid="share-bar">
                  <button className="share-btn" onClick={copyShareLink} data-testid="copy-link-button">
                    {copied ? <Check size={16} /> : <Copy size={16} />}{copied ? 'Link copied!' : 'Copy shareable link'}
                  </button>
                  <button className="share-btn result-copy-btn" onClick={copyResultText} data-testid="copy-result-button">
                    {resultCopied ? <Check size={16} /> : <ClipboardCheck size={16} />}{resultCopied ? 'Result copied!' : 'Copy result'}
                  </button>
                  <button className="retry-btn" onClick={() => { setResult(null); setIdea(''); setContext(emptyContext()); setChallengeOpen(false); setChallengeResult(null); setCounterArg(''); window.scrollTo({ top: 0, behavior: 'smooth' }); }} data-testid="try-another-button">
                    <RotateCcw size={14} /> New idea
                  </button>
                </div>

                {/* Challenge the Verdict */}
                <div className="challenge-section" data-testid="challenge-section">
                  {!challengeOpen && !challengeResult && (
                    <button className="challenge-toggle-btn" onClick={() => setChallengeOpen(true)} data-testid="challenge-toggle-btn">
                      <Swords size={16} /> Challenge the Verdict
                    </button>
                  )}

                  <AnimatePresence>
                    {challengeOpen && !challengeResult && (
                      <motion.div className="challenge-form" initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: 'auto' }} exit={{ opacity: 0, height: 0 }} transition={{ duration: 0.3 }} data-testid="challenge-form">
                        <div className="challenge-form-header">
                          <Swords size={14} />
                          <span>Think we got it wrong? Make your case.</span>
                        </div>
                        <textarea
                          className="challenge-textarea"
                          placeholder="Type your counter-argument. Be specific — vague cope gets rejected."
                          value={counterArg}
                          onChange={e => setCounterArg(e.target.value)}
                          maxLength={1000}
                          rows={3}
                          data-testid="challenge-textarea"
                        />
                        <div className="challenge-actions">
                          <button className="challenge-submit-btn" onClick={handleChallenge} disabled={challengeLoading || counterArg.trim().length < 10} data-testid="challenge-submit-btn">
                            {challengeLoading ? (<span className="loading-text"><span className="spinner" />Evaluating your counter...</span>) : (<><Send size={14} /> Submit Counter</>)}
                          </button>
                          <button className="challenge-cancel-btn" onClick={() => { setChallengeOpen(false); setCounterArg(''); }} data-testid="challenge-cancel-btn">Cancel</button>
                        </div>
                      </motion.div>
                    )}
                  </AnimatePresence>

                  <AnimatePresence>
                    {challengeResult && challengeResult.counter_status !== 'ERROR' && (
                      <motion.div className="challenge-result" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }} transition={{ duration: 0.4 }} data-testid="challenge-result">
                        <div className={`challenge-badge ${challengeResult.counter_status === 'ACCEPTED' ? 'challenge-accepted' : 'challenge-rejected'}`} data-testid="challenge-badge">
                          {challengeResult.counter_status === 'ACCEPTED' ? 'COUNTER ACCEPTED' : 'COUNTER REJECTED'}
                        </div>
                        <p className="challenge-reasoning" data-testid="challenge-reasoning">{challengeResult.reasoning}</p>
                        <button className="challenge-retry-btn" onClick={() => { setChallengeResult(null); setChallengeOpen(true); setCounterArg(''); }} data-testid="challenge-retry-btn">
                          <Swords size={13} /> Challenge Again
                        </button>
                      </motion.div>
                    )}
                  </AnimatePresence>
                </div>

                {/* Pivot Suggestions */}
                {result.pivot_suggestions?.length > 0 && (
                  <motion.div className="pivot-section" initial={{ opacity: 0, y: 30 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }} data-testid="pivot-section">
                    <div className="pivot-header"><Sparkles size={16} /><h3>You might want to build this instead</h3></div>
                    <div className="pivot-grid">
                      {result.pivot_suggestions.map((p, i) => (
                        <div key={i} className="pivot-card" data-testid={`pivot-card-${i}`}>
                          <p className="pivot-idea">{p.idea}</p>
                          <p className="pivot-why">{p.why}</p>
                          <button className="pivot-validate-btn" onClick={() => handleValidatePivot(p.idea)} disabled={loading} data-testid={`validate-pivot-${i}`}>
                            <Zap size={13} /> Validate This
                          </button>
                        </div>
                      ))}
                    </div>
                  </motion.div>
                )}
              </div>
            </motion.section>
          )}
        </AnimatePresence>

        {/* Leaderboard */}
        {leaderboard.length > 0 && (
          <section className="leaderboard-section" data-testid="leaderboard-section">
            <div className="leaderboard-wrapper">
              <div className="leaderboard-header"><Trophy size={18} /><h2>Leaderboard</h2><span className="leaderboard-subtitle">Top-scored ideas. Can you beat them?</span></div>
              <div className="leaderboard-table" data-testid="leaderboard-table">
                {leaderboard.map((item) => {
                  const rid = result?.result_id || result?.id;
                  const isActive = rid === item.id;
                  return (
                    <motion.div key={item.id} className={`lb-row ${isActive ? 'lb-row-active' : ''}`} initial={{ opacity: 0, x: -10 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: item.rank * 0.03 }} data-testid={`lb-row-${item.rank}`}>
                      <div className="lb-rank">{item.rank <= 3 ? <Crown size={14} className={`lb-crown lb-crown-${item.rank}`} /> : <span>{item.rank}</span>}</div>
                      <div className="lb-content"><p className="lb-idea">{item.idea_preview}</p><p className="lb-reason">{item.signal_reason}</p></div>
                      <div className="lb-meta">
                        <span className="lb-signal" style={{ color: getSignalColorForItem(item.signal) }}>{item.verdict || item.signal}</span>
                        <span className="lb-score" style={{ color: getSignalColorForItem(item.signal) }}>{item.score}<span className="lb-score-total">/10</span></span>
                      </div>
                    </motion.div>
                  );
                })}
              </div>
            </div>
          </section>
        )}

        <footer className="footer" data-testid="footer"><p>noflop.ai — No glaze. No hype. Just signal.</p></footer>
      </div>
    </div>
  );
}

export default App;
