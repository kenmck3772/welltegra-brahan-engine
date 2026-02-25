-- WellTegra Brahan Forensic Engine
-- Database Schema for PostgreSQL

-- Wells table
CREATE TABLE wells (
    well_id VARCHAR(100) PRIMARY KEY,
    name VARCHAR(200),
    field VARCHAR(100),
    company VARCHAR(200),
    uwi VARCHAR(50),
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Risk scores table
CREATE TABLE risk_scores (
    id SERIAL PRIMARY KEY,
    well_id VARCHAR(100) REFERENCES wells(well_id),
    score INTEGER,
    level VARCHAR(20),
    factors TEXT[],
    scanned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Fraud flags table
CREATE TABLE fraud_flags (
    id SERIAL PRIMARY KEY,
    well_id VARCHAR(100) REFERENCES wells(well_id),
    file_name VARCHAR(500),
    flag_code VARCHAR(10),
    flag_type VARCHAR(100),
    severity VARCHAR(20),
    detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Ghost fish table
CREATE TABLE ghost_fish (
    id SERIAL PRIMARY KEY,
    well_id VARCHAR(100) REFERENCES wells(well_id),
    file_name VARCHAR(500),
    item_type VARCHAR(100),
    depth DECIMAL(10, 2),
    status VARCHAR(50),
    detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Barriers table
CREATE TABLE barriers (
    id SERIAL PRIMARY KEY,
    well_id VARCHAR(100) REFERENCES wells(well_id),
    barrier_type VARCHAR(100),
    top_depth DECIMAL(10, 2),
    bottom_depth DECIMAL(10, 2),
    verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Scan history table
CREATE TABLE scan_history (
    id SERIAL PRIMARY KEY,
    scan_id VARCHAR(100) UNIQUE,
    scan_type VARCHAR(50),
    files_scanned INTEGER,
    wells_analyzed INTEGER,
    fraud_flags INTEGER,
    ghost_fish INTEGER,
    compliance_score DECIMAL(5, 2),
    scanned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    duration_seconds INTEGER
);

-- Predictions table
CREATE TABLE predictions (
    id SERIAL PRIMARY KEY,
    well_id VARCHAR(100) REFERENCES wells(well_id),
    failure_probability DECIMAL(5, 2),
    confidence VARCHAR(20),
    model_version VARCHAR(20),
    predicted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Audit trail table
CREATE TABLE audit_trail (
    id SERIAL PRIMARY KEY,
    entity_type VARCHAR(50),
    entity_id VARCHAR(100),
    action VARCHAR(50),
    old_value JSONB,
    new_value JSONB,
    user_id VARCHAR(100),
    action_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX idx_risk_well ON risk_scores(well_id);
CREATE INDEX idx_fraud_well ON fraud_flags(well_id);
CREATE INDEX idx_ghost_well ON ghost_fish(well_id);
CREATE INDEX idx_barriers_well ON barriers(well_id);
CREATE INDEX idx_predictions_well ON predictions(well_id);
CREATE INDEX idx_scan_history_date ON scan_history(scanned_at);

-- Views
CREATE VIEW vw_well_summary AS
SELECT 
    w.well_id,
    w.name,
    w.field,
    rs.score AS risk_score,
    rs.level AS risk_level,
    (SELECT COUNT(*) FROM fraud_flags ff WHERE ff.well_id = w.well_id) AS fraud_count,
    (SELECT COUNT(*) FROM ghost_fish gf WHERE gf.well_id = w.well_id) AS ghost_fish_count,
    p.failure_probability
FROM wells w
LEFT JOIN risk_scores rs ON w.well_id = rs.well_id
LEFT JOIN predictions p ON w.well_id = p.well_id
ORDER BY rs.score DESC;

-- Functions
CREATE OR REPLACE FUNCTION update_timestamp()
RETURNS TRIGGER AS $$ BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
 $$ LANGUAGE plpgsql;

-- Triggers
CREATE TRIGGER wells_update_timestamp
BEFORE UPDATE ON wells
FOR EACH ROW
EXECUTE FUNCTION update_timestamp();
