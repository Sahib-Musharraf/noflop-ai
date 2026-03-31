import React, { useState, useEffect, useRef, useCallback } from 'react';
import { useSearchParams } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Copy, Check, ArrowRight, Zap, Target, MessageCircle,
  AlertTriangle, Lightbulb, Skull, Sparkles, ChevronLeft,
  ChevronRight, Clock, ClipboardCheck, RotateCcw, Trophy, Crown
} from 'lucide-react';
import './App.css';

const API_URL = process.env.REACT_APP_BACKEND_URL;
const HISTORY_KEY = 'noflop_history';

function getHistory() {
  try {
    return JSON.parse(localStorage.getItem(HISTORY_KEY) || '[]');
  } catch { return []; }
}

function saveToHistory(result) {
  const history = getHistory();
  const exists = history.find(h => h.id === result.id);
  if (exists) return;
  const entry = {
    id: result.id,
    idea: result.idea,
    signal: result.signal,
    score: result.score,
    created_at: result.created_at,
  };
  history.unshift(entry);
  if (history.length > 50) history.pop();
  localStorage.setItem(HISTORY_KEY, JSON.stringify(history));
}

function App() {
  const [idea, setIdea] = useState('');
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

  const fetchLeaderboard = async () => {
    try {
      const res = await fetch(`${API_URL}/api/leaderboard`);
      if (res.ok) {
        const data = await res.json();
        setLeaderboard(data.leaderboard || []);
      }
    } catch {}
  };

  useEffect(() => {
    fetchLeaderboard();
  }, []);

  useEffect(() => {
    const resultId = searchParams.get('r');
    if (resultId) {
      fetchResult(resultId);
    }
  }, [searchParams]);

  const fetchResult = async (id) => {
    setLoading(true);
    setError('');
    try {
      const res = await fetch(`${API_URL}/api/result/${id}`);
      if (!res.ok) throw new Error('Result not found');
      const data = await res.json();
      setResult(data);
      setIdea(data.idea);
      saveToHistory(data);
      setHistory(getHistory());
    } catch (err) {
      setError('This result link has expired or doesn\'t exist.');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = useCallback(async (overrideIdea) => {
    const text = (overrideIdea || idea).trim();
    if (!text || text.length < 10) {
      setError('Come on. Give us at least a couple sentences to tear apart.');
      return;
    }
    setLoading(true);
    setError('');
    setResult(null);

    try {
      const res = await fetch(`${API_URL}/api/validate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ idea: text }),
      });
      if (!res.ok) {
        const errData = await res.json().catch(() => ({}));
        throw new Error(errData.detail || 'Something broke. Even our validator has bad days.');
      }
      const data = await res.json();
      setResult(data);
      saveToHistory(data);
      setHistory(getHistory());
      fetchLeaderboard();
      setTimeout(() => {
        resultRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }, 300);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [idea]);

  const handleValidatePivot = (pivotIdea) => {
    setIdea(pivotIdea);
    setResult(null);
    window.scrollTo({ top: 0, behavior: 'smooth' });
    setTimeout(() => {
      handleSubmit(pivotIdea);
    }, 100);
  };

  const loadHistoryItem = async (item) => {
    setSidebarOpen(false);
    fetchResult(item.id);
  };

  const copyShareLink = () => {
    if (!result?.id) return;
    const shareUrl = `${window.location.origin}?r=${result.id}`;
    navigator.clipboard.writeText(shareUrl);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const copyResultText = () => {
    if (!result) return;
    const bt = result.brutal_truth || {};
    const lines = [
      `${result.signal} — ${result.score}/10`,
      ``,
      result.signal_reason,
      ``,
      `BRUTAL TRUTH:`,
      `- Market: ${bt.market_demand || ''}`,
      `- Timing: ${bt.timing_reality || ''}`,
      `- Competition: ${bt.competition_problem || ''}`,
      ``,
      `QUESTIONS TO ASK USERS:`,
      ...(result.user_questions || []).map((q, i) => `${i + 1}. ${q}`),
      ``,
      `———`,
      `Validated on noflop.ai — No glaze. No hype. Just signal.`,
    ];
    navigator.clipboard.writeText(lines.join('\n'));
    setResultCopied(true);
    setTimeout(() => setResultCopied(false), 2000);
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) {
      handleSubmit();
    }
  };

  const getSignalColor = (signal) => {
    if (!signal) return {};
    const s = signal.toUpperCase();
    if (s.includes('BUILD')) return { color: 'var(--green)', bg: 'var(--green-dim)', border: 'var(--green-border)' };
    if (s.includes('KILL')) return { color: 'var(--red)', bg: 'var(--red-dim)', border: 'var(--red-border)' };
    return { color: 'var(--yellow)', bg: 'var(--yellow-dim)', border: 'var(--yellow-border)' };
  };

  const getSignalColorForItem = (signal) => {
    if (!signal) return 'var(--text-muted)';
    const s = signal.toUpperCase();
    if (s.includes('BUILD')) return 'var(--green)';
    if (s.includes('KILL')) return 'var(--red)';
    return 'var(--yellow)';
  };

  return (
    <div className="app-layout">
      {/* Sidebar */}
      <aside className={`sidebar ${sidebarOpen ? 'sidebar-open' : ''}`} data-testid="idea-sidebar">
        <div className="sidebar-header">
          <Clock size={14} />
          <span>Your Ideas</span>
        </div>
        <div className="sidebar-list" data-testid="sidebar-list">
          {history.length === 0 ? (
            <div className="sidebar-empty">No ideas validated yet.</div>
          ) : (
            history.map((item) => (
              <button
                key={item.id}
                className="sidebar-item"
                onClick={() => loadHistoryItem(item)}
                data-testid={`history-item-${item.id}`}
              >
                <div className="sidebar-item-top">
                  <span
                    className="sidebar-signal"
                    style={{ color: getSignalColorForItem(item.signal) }}
                  >
                    {item.signal}
                  </span>
                  <span className="sidebar-score">{item.score}/10</span>
                </div>
                <p className="sidebar-idea">{item.idea}</p>
              </button>
            ))
          )}
        </div>
      </aside>

      {/* Sidebar Toggle */}
      <button
        className={`sidebar-toggle ${sidebarOpen ? 'sidebar-toggle-open' : ''}`}
        onClick={() => setSidebarOpen(!sidebarOpen)}
        data-testid="sidebar-toggle"
      >
        {sidebarOpen ? <ChevronLeft size={16} /> : <ChevronRight size={16} />}
        {!sidebarOpen && history.length > 0 && (
          <span className="sidebar-count">{history.length}</span>
        )}
      </button>

      {/* Overlay for mobile */}
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
              <motion.div
                className="hero-badge"
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.2 }}
                data-testid="hero-badge"
              >
                <span className="badge-dot" />
                BRUTAL IDEA VALIDATION
              </motion.div>

              <motion.h1
                className="hero-heading"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.3, duration: 0.6 }}
                data-testid="hero-heading"
              >
                Don't let your<br />
                <span className="accent-text">idea flop.</span>
              </motion.h1>

              <motion.p
                className="hero-sub"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.5 }}
                data-testid="hero-subheading"
              >
                An AI-powered idea validation tool for builders and founders.
                Brutal honesty. No sugarcoating. Real signal — in 30 seconds.
              </motion.p>

              <motion.div
                className="hero-pills"
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.7 }}
                data-testid="hero-pills"
              >
                <span className="pill pill-green">BUILD IT</span>
                <span className="pill pill-red">KILL IT</span>
                <span className="pill pill-yellow">PIVOT IT</span>
                <span className="pill pill-outline">30 SEC VALIDATION</span>
              </motion.div>
            </div>

            <motion.div
              className="hero-right"
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 0.4, duration: 0.8 }}
              data-testid="hero-stat"
            >
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
              <textarea
                data-testid="idea-textarea"
                className="idea-input"
                placeholder="Describe your idea in 2-3 sentences. We will not be nice about it."
                value={idea}
                onChange={(e) => setIdea(e.target.value)}
                onKeyDown={handleKeyDown}
                maxLength={1000}
                rows={4}
              />
              <div className="textarea-footer">
                <span className="char-count">{idea.length}/1000</span>
                <span className="kbd-hint">Ctrl+Enter to submit</span>
              </div>
            </div>

            <AnimatePresence>
              {error && (
                <motion.div
                  className="error-msg"
                  initial={{ opacity: 0, y: -5 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0 }}
                  data-testid="error-message"
                >
                  <AlertTriangle size={14} /> {error}
                </motion.div>
              )}
            </AnimatePresence>

            <button
              data-testid="submit-button"
              className="submit-btn"
              onClick={() => handleSubmit()}
              disabled={loading || !idea.trim()}
            >
              {loading ? (
                <span className="loading-text">
                  <span className="spinner" />
                  Running your idea through the reality check...
                </span>
              ) : (
                <>
                  Be Brutal <ArrowRight size={18} />
                </>
              )}
            </button>
          </div>
        </section>

        {/* Result */}
        <AnimatePresence>
          {result && (
            <motion.section
              ref={resultRef}
              className="result-section"
              initial={{ opacity: 0, y: 40 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: 40 }}
              transition={{ duration: 0.5 }}
              data-testid="result-section"
            >
              <div className="result-wrapper">
                {/* Signal */}
                <div className="result-card signal-card" data-testid="signal-card">
                  <div className="card-label">
                    <Zap size={14} /> SIGNAL
                  </div>
                  <div
                    className="signal-badge"
                    style={{
                      color: getSignalColor(result.signal).color,
                      background: getSignalColor(result.signal).bg,
                      borderColor: getSignalColor(result.signal).border,
                    }}
                    data-testid="signal-badge"
                  >
                    {result.signal}
                  </div>
                  <p className="signal-reason" data-testid="signal-reason">{result.signal_reason}</p>
                </div>

                {/* Score */}
                <div className="result-card score-card" data-testid="score-card">
                  <div className="card-label">
                    <Target size={14} /> SCORE
                  </div>
                  <div className="score-display">
                    <span
                      className="score-number"
                      style={{ color: getSignalColor(result.signal).color }}
                      data-testid="score-number"
                    >
                      {result.score}
                    </span>
                    <span className="score-total">/10</span>
                  </div>
                  <p className="score-reason" data-testid="score-reason">{result.score_reason}</p>
                </div>

                {/* Brutal Truth */}
                <div className="result-card truth-card" data-testid="brutal-truth-card">
                  <div className="card-label">
                    <AlertTriangle size={14} /> BRUTAL TRUTH
                  </div>
                  <div className="truth-list">
                    <div className="truth-item" data-testid="truth-market">
                      <span className="truth-tag">MARKET DEMAND</span>
                      <p>{result.brutal_truth?.market_demand}</p>
                    </div>
                    <div className="truth-item" data-testid="truth-timing">
                      <span className="truth-tag">TIMING REALITY</span>
                      <p>{result.brutal_truth?.timing_reality}</p>
                    </div>
                    <div className="truth-item" data-testid="truth-competition">
                      <span className="truth-tag">COMPETITION</span>
                      <p>{result.brutal_truth?.competition_problem}</p>
                    </div>
                  </div>
                </div>

                {/* Differentiation Angle — NEW */}
                {result.differentiation_angles?.length > 0 && (
                  <motion.div
                    className="result-card diff-card"
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.1 }}
                    data-testid="differentiation-card"
                  >
                    <div className="card-label">
                      <Lightbulb size={14} /> DIFFERENTIATION ANGLE
                    </div>
                    <div className="diff-list">
                      {result.differentiation_angles.map((angle, i) => (
                        <div key={i} className="diff-item" data-testid={`diff-angle-${i}`}>
                          <span className="diff-num">{i + 1}</span>
                          <p>{angle}</p>
                        </div>
                      ))}
                    </div>
                  </motion.div>
                )}

                {/* Similar Ideas That Flopped — NEW */}
                {result.similar_failures?.length > 0 && (
                  <motion.div
                    className="result-card failures-card"
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.15 }}
                    data-testid="similar-failures-card"
                  >
                    <div className="card-label">
                      <Skull size={14} /> SIMILAR IDEAS THAT FLOPPED
                    </div>
                    <div className="failures-list">
                      {result.similar_failures.map((f, i) => (
                        <div key={i} className="failure-item" data-testid={`failure-${i}`}>
                          <span className="failure-name">{f.name}</span>
                          <p>{f.reason}</p>
                        </div>
                      ))}
                    </div>
                  </motion.div>
                )}

                {/* User Questions */}
                <div className="result-card questions-card" data-testid="questions-card">
                  <div className="card-label">
                    <MessageCircle size={14} /> WHAT TO ASK REAL USERS
                  </div>
                  <div className="questions-list">
                    {result.user_questions?.map((q, i) => (
                      <div key={i} className="question-item" data-testid={`question-${i}`}>
                        <span className="question-num">{i + 1}</span>
                        <p>{q}</p>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Share */}
                <div className="share-bar" data-testid="share-bar">
                  <button
                    className="share-btn"
                    onClick={copyShareLink}
                    data-testid="copy-link-button"
                  >
                    {copied ? <Check size={16} /> : <Copy size={16} />}
                    {copied ? 'Link copied!' : 'Copy shareable link'}
                  </button>
                  <button
                    className="share-btn result-copy-btn"
                    onClick={copyResultText}
                    data-testid="copy-result-button"
                  >
                    {resultCopied ? <Check size={16} /> : <ClipboardCheck size={16} />}
                    {resultCopied ? 'Result copied!' : 'Copy result'}
                  </button>
                  <button
                    className="retry-btn"
                    onClick={() => { setResult(null); setIdea(''); window.scrollTo({ top: 0, behavior: 'smooth' }); }}
                    data-testid="try-another-button"
                  >
                    <RotateCcw size={14} /> New idea
                  </button>
                </div>

                {/* Recommendation Engine — NEW */}
                {result.pivot_suggestions?.length > 0 && (
                  <motion.div
                    className="pivot-section"
                    initial={{ opacity: 0, y: 30 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.2 }}
                    data-testid="pivot-section"
                  >
                    <div className="pivot-header">
                      <Sparkles size={16} />
                      <h3>You might want to build this instead</h3>
                    </div>
                    <div className="pivot-grid">
                      {result.pivot_suggestions.map((p, i) => (
                        <div key={i} className="pivot-card" data-testid={`pivot-card-${i}`}>
                          <p className="pivot-idea">{p.idea}</p>
                          <p className="pivot-why">{p.why}</p>
                          <button
                            className="pivot-validate-btn"
                            onClick={() => handleValidatePivot(p.idea)}
                            disabled={loading}
                            data-testid={`validate-pivot-${i}`}
                          >
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
              <div className="leaderboard-header">
                <Trophy size={18} />
                <h2>Leaderboard</h2>
                <span className="leaderboard-subtitle">Top-scored ideas. Can you beat them?</span>
              </div>
              <div className="leaderboard-table" data-testid="leaderboard-table">
                {leaderboard.map((item) => {
                  const isCurrentResult = result?.id === item.id;
                  return (
                    <motion.div
                      key={item.id}
                      className={`lb-row ${isCurrentResult ? 'lb-row-active' : ''}`}
                      initial={{ opacity: 0, x: -10 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: item.rank * 0.03 }}
                      data-testid={`lb-row-${item.rank}`}
                    >
                      <div className="lb-rank">
                        {item.rank <= 3 ? <Crown size={14} className={`lb-crown lb-crown-${item.rank}`} /> : <span>{item.rank}</span>}
                      </div>
                      <div className="lb-content">
                        <p className="lb-idea">{item.idea_preview}</p>
                        <p className="lb-reason">{item.signal_reason}</p>
                      </div>
                      <div className="lb-meta">
                        <span
                          className="lb-signal"
                          style={{ color: getSignalColorForItem(item.signal) }}
                        >
                          {item.signal}
                        </span>
                        <span className="lb-score" style={{ color: getSignalColorForItem(item.signal) }}>
                          {item.score}<span className="lb-score-total">/10</span>
                        </span>
                      </div>
                    </motion.div>
                  );
                })}
              </div>
            </div>
          </section>
        )}

        {/* Footer */}
        <footer className="footer" data-testid="footer">
          <p>noflop.ai — No glaze. No hype. Just signal.</p>
        </footer>
      </div>
    </div>
  );
}

export default App;
