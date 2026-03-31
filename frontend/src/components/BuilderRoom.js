import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { MessageCircle, Send, Users, Clock } from 'lucide-react';

const ROOM_KEY = 'noflop_builder_room';

function getPosts() {
  try { return JSON.parse(localStorage.getItem(ROOM_KEY) || '[]'); } catch { return []; }
}

function timeAgo(dateStr) {
  const diff = Date.now() - new Date(dateStr).getTime();
  const mins = Math.floor(diff / 60000);
  if (mins < 1) return 'just now';
  if (mins < 60) return `${mins}m ago`;
  const hrs = Math.floor(mins / 60);
  if (hrs < 24) return `${hrs}h ago`;
  const days = Math.floor(hrs / 24);
  return `${days}d ago`;
}

function getVerdictClass(v) {
  if (!v) return '';
  const s = v.toUpperCase();
  if (s === 'BUILD' || s.includes('BUILD')) return 'br-verdict-build';
  if (s === 'AVOID' || s.includes('AVOID') || s.includes('KILL')) return 'br-verdict-avoid';
  return 'br-verdict-refine';
}

function BuilderRoom() {
  const [posts, setPosts] = useState(getPosts);
  const [replyOpen, setReplyOpen] = useState(null);
  const [replyName, setReplyName] = useState('');
  const [replyText, setReplyText] = useState('');

  useEffect(() => {
    const interval = setInterval(() => setPosts(getPosts()), 2000);
    return () => clearInterval(interval);
  }, []);

  const submitReply = (postId) => {
    if (!replyText.trim()) return;
    const updated = posts.map(p => {
      if (p.id === postId) {
        return {
          ...p,
          replies: [...(p.replies || []), {
            id: Date.now().toString(36),
            name: replyName.trim() || 'Anonymous',
            text: replyText.trim(),
            created_at: new Date().toISOString(),
          }]
        };
      }
      return p;
    });
    localStorage.setItem(ROOM_KEY, JSON.stringify(updated));
    setPosts(updated);
    setReplyOpen(null);
    setReplyName('');
    setReplyText('');
  };

  return (
    <section className="br-section" data-testid="builder-room-section">
      <div className="br-wrapper">
        <div className="br-header">
          <div className="br-title-row">
            <Users size={20} />
            <h1 className="br-title">The Builder Room</h1>
          </div>
          <p className="br-subtitle">Where builders share ideas and give each other real feedback. Not a LinkedIn comment section.</p>
          <div className="br-stats">
            <span className="br-stat">{posts.length} idea{posts.length !== 1 ? 's' : ''} shared</span>
            <span className="br-stat">{posts.reduce((a, p) => a + (p.replies?.length || 0), 0)} replies</span>
          </div>
        </div>

        {posts.length === 0 ? (
          <div className="br-empty" data-testid="builder-room-empty">
            <p>No ideas shared yet. Validate an idea and be the first to share.</p>
          </div>
        ) : (
          <div className="br-feed" data-testid="builder-room-feed">
            {posts.map((post, idx) => (
              <motion.div
                key={post.id}
                className="br-card"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: idx * 0.05 }}
                data-testid={`br-post-${post.id}`}
              >
                <div className="br-card-top">
                  <span className={`br-verdict ${getVerdictClass(post.verdict)}`} data-testid={`br-verdict-${post.id}`}>
                    {(post.verdict || 'Refine').toUpperCase()}
                  </span>
                  <span className="br-card-score" data-testid={`br-score-${post.id}`}>{post.score}/10</span>
                </div>

                <p className="br-card-idea" data-testid={`br-idea-${post.id}`}>{post.idea}</p>

                <div className="br-card-meta">
                  <span className="br-card-author">{post.name || 'Anonymous'}</span>
                  <span className="br-card-time"><Clock size={11} /> {timeAgo(post.created_at)}</span>
                </div>

                {/* Replies */}
                {post.replies?.length > 0 && (
                  <div className="br-replies" data-testid={`br-replies-${post.id}`}>
                    {post.replies.map(r => (
                      <div key={r.id} className="br-reply">
                        <div className="br-reply-meta">
                          <span className="br-reply-name">{r.name}</span>
                          <span className="br-reply-time">{timeAgo(r.created_at)}</span>
                        </div>
                        <p className="br-reply-text">{r.text}</p>
                      </div>
                    ))}
                  </div>
                )}

                {/* Reply Button / Form */}
                {replyOpen === post.id ? (
                  <motion.div className="br-reply-form" initial={{ opacity: 0 }} animate={{ opacity: 1 }} data-testid={`br-reply-form-${post.id}`}>
                    <input
                      className="br-reply-name-input"
                      placeholder="Your name (optional)"
                      value={replyName}
                      onChange={e => setReplyName(e.target.value)}
                      maxLength={40}
                      data-testid={`br-reply-name-${post.id}`}
                    />
                    <textarea
                      className="br-reply-textarea"
                      placeholder="Give real feedback. Not platitudes."
                      value={replyText}
                      onChange={e => setReplyText(e.target.value)}
                      maxLength={500}
                      rows={2}
                      data-testid={`br-reply-text-${post.id}`}
                    />
                    <div className="br-reply-actions">
                      <button className="br-reply-submit" onClick={() => submitReply(post.id)} disabled={!replyText.trim()} data-testid={`br-reply-submit-${post.id}`}>
                        <Send size={12} /> Reply
                      </button>
                      <button className="br-reply-cancel" onClick={() => { setReplyOpen(null); setReplyName(''); setReplyText(''); }}>Cancel</button>
                    </div>
                  </motion.div>
                ) : (
                  <button className="br-reply-btn" onClick={() => setReplyOpen(post.id)} data-testid={`br-reply-btn-${post.id}`}>
                    <MessageCircle size={13} /> Reply {post.replies?.length > 0 && `(${post.replies.length})`}
                  </button>
                )}
              </motion.div>
            ))}
          </div>
        )}
      </div>
    </section>
  );
}

export default BuilderRoom;
