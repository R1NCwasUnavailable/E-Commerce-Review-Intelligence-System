import { useState } from 'react';
import axios from 'axios';
import { Send, Cpu, CheckCircle2, AlertCircle, Edit2, Check } from 'lucide-react';

const API_URL = 'http://localhost:8000/api';

interface ReviewResult {
  id?: string;
  text: string;
  sentiment: string;
  score: number;
  aspects: Record<string, string>;
}

export default function Analyze() {
  const [text, setText] = useState('');
  const [results, setResults] = useState<ReviewResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [editingId, setEditingId] = useState<string | null>(null);
  const [correctedSentiment, setCorrectedSentiment] = useState<string>('');

  const handleAnalyze = async () => {
    if (!text.trim()) return;
    
    setLoading(true);
    setError('');
    
    try {
      // Check if it's bulk (e.g. separated by newlines)
      const lines = text.split('\n').filter(line => line.trim().length > 0);
      
      let res;
      if (lines.length > 1) {
        res = await axios.post(`${API_URL}/analyze/bulk`, { reviews: lines });
        setResults([...res.data.reverse(), ...results]);
      } else {
        res = await axios.post(`${API_URL}/analyze`, { text: lines[0] });
        setResults([res.data, ...results]);
      }
      
      setText('');
    } catch (err) {
      setError('Failed to analyze review(s). Please ensure backend is running.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleFeedback = async (id: string) => {
    if (!id || !correctedSentiment) return;
    try {
      await axios.post(`${API_URL}/feedback`, {
        review_id: id,
        corrected_sentiment: correctedSentiment
      });
      // Update local state
      setResults(results.map(r => r.id === id ? { ...r, sentiment: correctedSentiment } : r));
      setEditingId(null);
    } catch (err) {
      console.error('Failed to submit feedback', err);
    }
  };

  const startEditing = (result: ReviewResult) => {
    if (!result.id) return;
    setEditingId(result.id);
    setCorrectedSentiment(result.sentiment);
  };



  return (
    <div className="fade-in">
      <div className="page-header slide-up" style={{ animationDelay: '0.1s' }}>
        <h1 className="page-title">Analyze Reviews</h1>
      </div>

      <div className="grid-2 slide-up" style={{ animationDelay: '0.2s', alignItems: 'start' }}>
        {/* Input Section */}
        <div className="glass-card">
          <h3 style={{ marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <Cpu size={20} color="var(--accent-primary)" /> AI Processing
          </h3>
          <p style={{ color: 'var(--text-secondary)', marginBottom: '1.5rem', fontSize: '0.9rem' }}>
            Enter a single review, or multiple reviews separated by newlines to process them in bulk.
          </p>
          
          <div className="input-group">
            <textarea
              className="textarea-input"
              rows={6}
              placeholder="e.g. The battery life is amazing but the camera is quite bad in low light."
              value={text}
              onChange={(e) => setText(e.target.value)}
            />
          </div>
          
          {error && (
            <div style={{ color: 'var(--danger)', marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.9rem' }}>
              <AlertCircle size={16} /> {error}
            </div>
          )}

          <button 
            className="btn btn-primary" 
            onClick={handleAnalyze} 
            disabled={loading || !text.trim()}
            style={{ width: '100%' }}
          >
            {loading ? (
              <><div className="loader" style={{ width: '16px', height: '16px', borderWidth: '2px' }}></div> Processing...</>
            ) : (
              <><Send size={18} /> Analyze Sentiment & Aspects</>
            )}
          </button>
        </div>

        {/* Results Section */}
        <div className="glass-card" style={{ maxHeight: 'calc(100vh - 150px)', display: 'flex', flexDirection: 'column' }}>
          <h3 style={{ marginBottom: '1.5rem' }}>Recent Analysis (Data Flywheel)</h3>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.8rem', marginBottom: '1rem' }}>
            Flag incorrect predictions to improve future model fine-tuning.
          </p>
          
          <div style={{ overflowY: 'auto', flex: 1, paddingRight: '0.5rem' }}>
            {results.length === 0 ? (
              <div style={{ textAlign: 'center', color: 'var(--text-secondary)', padding: '3rem 0' }}>
                <CheckCircle2 size={48} style={{ margin: '0 auto 1rem', opacity: 0.2 }} />
                <p>No results yet. Run an analysis!</p>
              </div>
            ) : (
              results.map((result, idx) => (
                <div key={idx} className="review-item fade-in" style={{ animationDelay: `${idx * 0.1}s` }}>
                  <div className="review-header">
                    {editingId === result.id ? (
                      <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
                        <select 
                          className="text-input" 
                          style={{ padding: '0.2rem 0.5rem', width: 'auto' }}
                          value={correctedSentiment} 
                          onChange={(e) => setCorrectedSentiment(e.target.value)}
                        >
                          <option value="positive">Positive</option>
                          <option value="negative">Negative</option>
                          <option value="neutral">Neutral</option>
                        </select>
                        <button className="btn btn-primary" style={{ padding: '0.2rem 0.5rem' }} onClick={() => handleFeedback(result.id!)}>
                          <Check size={14} /> Save
                        </button>
                      </div>
                    ) : (
                      <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
                        <span className={`badge badge-${result.sentiment.toLowerCase()}`}>
                          {result.sentiment.toUpperCase()}
                        </span>
                        {result.id && (
                          <button onClick={() => startEditing(result)} style={{ background: 'none', border: 'none', color: 'var(--text-secondary)', cursor: 'pointer' }} title="Correct this prediction">
                            <Edit2 size={14} />
                          </button>
                        )}
                      </div>
                    )}
                    <span style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
                      Score: {(result.score * 100).toFixed(1)}%
                    </span>
                  </div>
                  <p className="review-text">{result.text}</p>
                  
                  {Object.keys(result.aspects).length > 0 && (
                    <div style={{ marginTop: '1rem' }}>
                      <span style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', display: 'block', marginBottom: '0.5rem' }}>Aspects Detected:</span>
                      <div className="aspect-tags">
                        {Object.entries(result.aspects).map(([aspect, sent]) => (
                          <span key={aspect} className={`badge badge-${sent.toLowerCase()}`} style={{ fontSize: '0.75rem', padding: '0.1rem 0.5rem' }}>
                            {aspect}: {sent}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
