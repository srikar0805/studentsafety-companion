import { useState, useEffect } from 'react';
import { Newspaper, ChevronDown, ChevronUp, MapPin, ExternalLink, TrendingUp, TrendingDown, Minus } from 'lucide-react';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

interface NewsArticle {
    id: string;
    title: string;
    source: string;
    url: string;
    published_date: string;
    summary: string;
    sentiment_score: number;
    lat: number | null;
    lon: number | null;
    categories: string;
}

interface NewsPanelProps {
    onArticleClick?: (lat: number, lon: number, title: string) => void;
    compact?: boolean;  // Show icon-only mode for mobile
}

const categoryStyles: Record<string, { bg: string; text: string }> = {
    crime: { bg: 'rgba(239, 68, 68, 0.15)', text: '#ef4444' },
    safety: { bg: 'rgba(34, 197, 94, 0.15)', text: '#22c55e' },
    policy: { bg: 'rgba(59, 130, 246, 0.15)', text: '#3b82f6' },
    protest: { bg: 'rgba(249, 115, 22, 0.15)', text: '#f97316' },
    general: { bg: 'rgba(107, 114, 128, 0.15)', text: '#6b7280' },
};

function SentimentIcon({ score }: { score: number }) {
    if (score > 0.2) return <TrendingUp size={12} color="#22c55e" />;
    if (score < -0.2) return <TrendingDown size={12} color="#ef4444" />;
    return <Minus size={12} color="#6b7280" />;
}

function SentimentBadge({ score }: { score: number }) {
    let color = '#6b7280';
    let bg = 'rgba(107, 114, 128, 0.15)';
    let label = 'Neutral';

    if (score > 0.2) {
        color = '#22c55e';
        bg = 'rgba(34, 197, 94, 0.15)';
        label = 'Positive';
    } else if (score < -0.2) {
        color = '#ef4444';
        bg = 'rgba(239, 68, 68, 0.15)';
        label = 'Negative';
    }

    return (
        <span style={{
            fontSize: '10px',
            padding: '2px 6px',
            borderRadius: '9999px',
            fontWeight: 600,
            color,
            backgroundColor: bg,
            display: 'inline-flex',
            alignItems: 'center',
            gap: '3px',
        }}>
            <SentimentIcon score={score} />
            {label}
        </span>
    );
}

export default function NewsPanel({ onArticleClick, compact = false }: NewsPanelProps) {
    const [isOpen, setIsOpen] = useState(false);
    const [articles, setArticles] = useState<NewsArticle[]>([]);
    const [sentimentData, setSentimentData] = useState<{ average: number; total_articles: number } | null>(null);
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        if (isOpen && articles.length === 0) {
            fetchNews();
        }
    }, [isOpen]);

    // Fetch sentiment data on mount for compact mode badge
    useEffect(() => {
        if (compact && !sentimentData) {
            fetch(`${API_BASE}/api/news/sentiment`)
                .then(r => r.json())
                .then(setSentimentData)
                .catch(err => console.error('Failed to fetch sentiment:', err));
        }
    }, [compact, sentimentData]);

    const fetchNews = async () => {
        setLoading(true);
        try {
            const [newsRes, sentimentRes] = await Promise.all([
                fetch(`${API_BASE}/api/news`).then(r => r.json()),
                fetch(`${API_BASE}/api/news/sentiment`).then(r => r.json()),
            ]);
            setArticles(newsRes);
            setSentimentData(sentimentRes);
        } catch (err) {
            console.error('Failed to fetch news:', err);
        } finally {
            setLoading(false);
        }
    };

    // Compact mode: Just show icon button when closed
    if (compact && !isOpen) {
        return (
            <button
                onClick={() => setIsOpen(true)}
                style={{
                    width: '48px',
                    height: '48px',
                    borderRadius: '12px',
                    background: 'rgba(15, 23, 42, 0.85)',
                    backdropFilter: 'blur(12px)',
                    border: '1px solid rgba(255, 255, 255, 0.08)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    cursor: 'pointer',
                    boxShadow: '0 4px 24px rgba(0, 0, 0, 0.3)',
                    position: 'relative',
                }}
            >
                <Newspaper size={22} color="#facc15" />
                {sentimentData && sentimentData.total_articles > 0 && (
                    <span style={{
                        position: 'absolute',
                        top: '-4px',
                        right: '-4px',
                        background: '#ef4444',
                        color: 'white',
                        fontSize: '10px',
                        fontWeight: 700,
                        borderRadius: '50%',
                        width: '18px',
                        height: '18px',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        border: '2px solid rgba(15, 23, 42, 1)',
                    }}>
                        {sentimentData.total_articles}
                    </span>
                )}
            </button>
        );
    }

    // When opened in compact mode, show full panel
    return (
        <div style={{
            background: 'rgba(15, 23, 42, 0.85)',
            backdropFilter: 'blur(12px)',
            borderRadius: '12px',
            border: '1px solid rgba(255, 255, 255, 0.08)',
            overflow: 'hidden',
            boxShadow: '0 4px 24px rgba(0, 0, 0, 0.3)',
            width: compact ? '280px' : 'auto',
        }}>
            {/* Header toggle */}
            <button
                onClick={() => setIsOpen(!isOpen)}
                style={{
                    width: '100%',
                    padding: '12px 14px',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    background: 'transparent',
                    border: 'none',
                    cursor: 'pointer',
                    color: '#e2e8f0',
                    transition: 'background 0.2s',
                }}
                onMouseEnter={e => (e.currentTarget.style.background = 'rgba(255,255,255,0.05)')}
                onMouseLeave={e => (e.currentTarget.style.background = 'transparent')}
            >
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <Newspaper size={18} color="#facc15" />
                    <span style={{ fontSize: '13px', fontWeight: 600 }}>Local Safety News</span>
                    {sentimentData && (
                        <span style={{ fontSize: '10px', color: '#94a3b8' }}>
                            {sentimentData.total_articles} articles
                        </span>
                    )}
                </div>
                {isOpen ? <ChevronUp size={16} color="#94a3b8" /> : <ChevronDown size={16} color="#94a3b8" />}
            </button>

            {/* Content */}
            {isOpen && (
                <div style={{ borderTop: '1px solid rgba(255, 255, 255, 0.06)' }}>
                    {/* Sentiment overview */}
                    {sentimentData && (
                        <div style={{
                            padding: '8px 14px',
                            background: 'rgba(255, 255, 255, 0.03)',
                            fontSize: '11px',
                            color: '#94a3b8',
                            display: 'flex',
                            alignItems: 'center',
                            gap: '8px',
                        }}>
                            <span>Overall sentiment:</span>
                            <SentimentBadge score={sentimentData.average} />
                        </div>
                    )}

                    {loading ? (
                        <div style={{ padding: '24px', textAlign: 'center', color: '#94a3b8', fontSize: '13px' }}>
                            <div style={{
                                width: '20px', height: '20px',
                                border: '2px solid #facc15',
                                borderTop: '2px solid transparent',
                                borderRadius: '50%',
                                animation: 'spin 1s linear infinite',
                                margin: '0 auto 8px',
                            }} />
                            Loading news...
                        </div>
                    ) : articles.length === 0 ? (
                        <div style={{ padding: '24px', textAlign: 'center', color: '#64748b', fontSize: '13px' }}>
                            No news articles available.
                        </div>
                    ) : (
                        <div style={{ maxHeight: '320px', overflowY: 'auto' }}>
                            {articles.map((article) => {
                                const catStyle = categoryStyles[article.categories] || categoryStyles.general;
                                return (
                                    <div
                                        key={article.id}
                                        onClick={() => {
                                            if (article.lat && article.lon && onArticleClick) {
                                                onArticleClick(article.lat, article.lon, article.title);
                                            }
                                        }}
                                        style={{
                                            padding: '12px 14px',
                                            borderBottom: '1px solid rgba(255, 255, 255, 0.04)',
                                            cursor: article.lat ? 'pointer' : 'default',
                                            transition: 'background 0.2s',
                                        }}
                                        onMouseEnter={e => (e.currentTarget.style.background = 'rgba(250, 204, 21, 0.05)')}
                                        onMouseLeave={e => (e.currentTarget.style.background = 'transparent')}
                                    >
                                        <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: '8px' }}>
                                            <h4 style={{
                                                fontSize: '12.5px',
                                                fontWeight: 600,
                                                color: '#e2e8f0',
                                                lineHeight: '1.4',
                                                flex: 1,
                                                margin: 0,
                                            }}>
                                                {article.title}
                                            </h4>
                                            <SentimentBadge score={article.sentiment_score} />
                                        </div>

                                        <p style={{
                                            fontSize: '11px',
                                            color: '#94a3b8',
                                            marginTop: '4px',
                                            lineHeight: '1.4',
                                            display: '-webkit-box',
                                            WebkitLineClamp: 2,
                                            WebkitBoxOrient: 'vertical',
                                            overflow: 'hidden',
                                        }}>
                                            {article.summary}
                                        </p>

                                        <div style={{
                                            display: 'flex',
                                            alignItems: 'center',
                                            justifyContent: 'space-between',
                                            marginTop: '6px',
                                            flexWrap: 'wrap',
                                            gap: '4px',
                                        }}>
                                            <div style={{ display: 'flex', alignItems: 'center', gap: '6px', flexWrap: 'wrap' }}>
                                                <span style={{ fontSize: '10px', color: '#64748b' }}>{article.source}</span>
                                                <span style={{ fontSize: '10px', color: '#475569' }}>•</span>
                                                <span style={{ fontSize: '10px', color: '#64748b' }}>{article.published_date}</span>
                                                <span style={{
                                                    fontSize: '10px',
                                                    padding: '1px 6px',
                                                    borderRadius: '9999px',
                                                    fontWeight: 600,
                                                    color: catStyle.text,
                                                    backgroundColor: catStyle.bg,
                                                }}>
                                                    {article.categories}
                                                </span>
                                            </div>

                                            <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                                                {article.lat && (
                                                    <span style={{ fontSize: '10px', color: '#facc15', display: 'flex', alignItems: 'center', gap: '2px' }}>
                                                        <MapPin size={10} /> Map
                                                    </span>
                                                )}
                                                {article.url && (
                                                    <a
                                                        href={article.url}
                                                        target="_blank"
                                                        rel="noopener noreferrer"
                                                        onClick={e => e.stopPropagation()}
                                                        style={{ fontSize: '10px', color: '#60a5fa', display: 'flex', alignItems: 'center', gap: '2px', textDecoration: 'none' }}
                                                    >
                                                        <ExternalLink size={10} /> Link
                                                    </a>
                                                )}
                                            </div>
                                        </div>
                                    </div>
                                );
                            })}
                        </div>
                    )}
                </div>
            )}
        </div>
    );
}
