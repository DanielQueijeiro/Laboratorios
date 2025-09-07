-- Crear tabla para análisis
CREATE TABLE IF NOT EXISTS analyses (
    id SERIAL PRIMARY KEY,
    text_hash VARCHAR(32) UNIQUE NOT NULL,
    text TEXT NOT NULL,
    sentiment VARCHAR(20) NOT NULL,
    polarity FLOAT NOT NULL,
    subjectivity FLOAT NOT NULL,
    worker_id VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Índices para mejor performance
CREATE INDEX idx_sentiment ON analyses(sentiment);
CREATE INDEX idx_worker ON analyses(worker_id);
CREATE INDEX idx_created ON analyses(created_at);

-- Vista para estadísticas rápidas
CREATE VIEW sentiment_stats AS
SELECT 
    sentiment,
    COUNT(*) as count,
    AVG(polarity) as avg_polarity,
    AVG(subjectivity) as avg_subjectivity
FROM analyses
GROUP BY sentiment;