import { useState, useEffect } from 'react';
import axios from 'axios';
import { BarChart, Bar, XAxis, YAxis, Tooltip as RechartsTooltip, ResponsiveContainer, Cell, PieChart, Pie } from 'recharts';
import { Activity, MessageSquare, TrendingUp, Sparkles } from 'lucide-react';

const API_URL = 'http://localhost:8000/api';

const COLORS = {
  positive: '#10b981',
  negative: '#ef4444',
  neutral: '#94a3b8'
};

interface Stats {
  total_reviews: number;
  sentiment_distribution: {
    positive: number;
    negative: number;
    neutral: number;
  };
}

interface AspectData {
  [key: string]: {
    positive: number;
    negative: number;
    neutral: number;
  };
}

export default function Dashboard() {
  const [stats, setStats] = useState<Stats | null>(null);
  const [summary, setSummary] = useState<string | null>(null);
  const [aspects, setAspects] = useState<AspectData>({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [statsRes, summaryRes, aspectsRes] = await Promise.all([
          axios.get(`${API_URL}/stats`).catch(() => ({ data: { total_reviews: 0, sentiment_distribution: { positive: 0, negative: 0, neutral: 0 } } })),
          axios.get(`${API_URL}/summary`).catch(() => ({ data: { summary: 'No data available' } })),
          axios.get(`${API_URL}/aspects`).catch(() => ({ data: {} }))
        ]);
        
        setStats(statsRes.data);
        setSummary(summaryRes.data.summary);
        setAspects(aspectsRes.data);
      } catch (error) {
        console.error("Failed to fetch data", error);
      } finally {
        setLoading(false);
      }
    };
    
    fetchData();
  }, []);

  if (loading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%' }}>
        <div className="loader"></div>
      </div>
    );
  }

  const sentimentData = stats ? [
    { name: 'Positive', value: stats.sentiment_distribution.positive || 0, color: COLORS.positive },
    { name: 'Neutral', value: stats.sentiment_distribution.neutral || 0, color: COLORS.neutral },
    { name: 'Negative', value: stats.sentiment_distribution.negative || 0, color: COLORS.negative }
  ] : [];

  const aspectData = Object.keys(aspects).map(key => {
    const total = aspects[key].positive + aspects[key].negative + aspects[key].neutral;
    const posScore = total > 0 ? (aspects[key].positive / total) * 100 : 0;
    return {
      name: key.charAt(0).toUpperCase() + key.slice(1),
      score: posScore,
      total
    };
  }).sort((a, b) => b.total - a.total).slice(0, 5); // top 5 aspects

  return (
    <div>
      <div className="page-header slide-up" style={{ animationDelay: '0.1s' }}>
        <h1 className="page-title">Intelligence Dashboard</h1>
        <div style={{ display: 'flex', gap: '1rem' }}>
          <span className="badge badge-positive" style={{ padding: '0.5rem 1rem' }}>
            <Activity size={16} /> Live Data
          </span>
        </div>
      </div>

      {/* Top Stats */}
      <div className="grid-4 slide-up" style={{ animationDelay: '0.2s', marginBottom: '2rem' }}>
        <div className="glass-card stat-card">
          <div className="stat-header">
            <span>Total Reviews</span>
            <MessageSquare size={20} color="var(--accent-primary)" />
          </div>
          <div className="stat-value">{stats?.total_reviews || 0}</div>
        </div>
        
        <div className="glass-card stat-card">
          <div className="stat-header">
            <span>Positive Ratio</span>
            <TrendingUp size={20} color="var(--success)" />
          </div>
          <div className="stat-value">
            {stats?.total_reviews ? 
              Math.round(((stats.sentiment_distribution.positive || 0) / stats.total_reviews) * 100) 
              : 0}%
          </div>
        </div>

        <div className="glass-card" style={{ gridColumn: 'span 2' }}>
          <div className="stat-header" style={{ marginBottom: '0.5rem' }}>
            <span style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <Sparkles size={18} color="var(--accent-secondary)" /> AI Summary (Recent)
            </span>
          </div>
          <p style={{ color: 'var(--text-primary)', lineHeight: 1.5, fontSize: '0.95rem' }}>
            {summary || 'No summary available. Analyze some reviews first!'}
          </p>
        </div>
      </div>

      <div className="grid-2 slide-up" style={{ animationDelay: '0.3s' }}>
        {/* Sentiment Chart */}
        <div className="glass-card">
          <h3 style={{ marginBottom: '1rem', color: 'var(--text-secondary)', fontWeight: 500 }}>Overall Sentiment</h3>
          <div className="chart-container">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={sentimentData}
                  cx="50%"
                  cy="50%"
                  innerRadius={80}
                  outerRadius={110}
                  paddingAngle={5}
                  dataKey="value"
                  stroke="none"
                >
                  {sentimentData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <RechartsTooltip 
                  contentStyle={{ backgroundColor: 'rgba(10, 10, 15, 0.9)', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '8px' }}
                  itemStyle={{ color: '#fff' }}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>
          <div style={{ display: 'flex', justifyContent: 'center', gap: '1.5rem', marginTop: '1rem' }}>
            {sentimentData.map(d => (
              <div key={d.name} style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <div style={{ width: '12px', height: '12px', borderRadius: '50%', backgroundColor: d.color }}></div>
                <span style={{ fontSize: '0.875rem' }}>{d.name}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Aspects Chart */}
        <div className="glass-card">
          <h3 style={{ marginBottom: '1rem', color: 'var(--text-secondary)', fontWeight: 500 }}>Top Aspects (Positivity %)</h3>
          {aspectData.length > 0 ? (
            <div className="chart-container">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={aspectData} layout="vertical" margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
                  <XAxis type="number" domain={[0, 100]} hide />
                  <YAxis dataKey="name" type="category" axisLine={false} tickLine={false} tick={{ fill: 'var(--text-secondary)' }} />
                  <RechartsTooltip 
                    cursor={{ fill: 'rgba(255,255,255,0.05)' }}
                    contentStyle={{ backgroundColor: 'rgba(10, 10, 15, 0.9)', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '8px' }}
                  />
                  <Bar dataKey="score" radius={[0, 4, 4, 0]}>
                    {aspectData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.score > 50 ? COLORS.positive : COLORS.negative} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          ) : (
            <div style={{ height: '300px', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--text-secondary)' }}>
              Not enough aspect data yet.
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
