-- Create weather_history table
CREATE TABLE IF NOT EXISTS weather_history (
    id SERIAL PRIMARY KEY,
    city VARCHAR(100) NOT NULL,
    temperature FLOAT NOT NULL,
    humidity INTEGER,
    description VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create an index on city for faster queries
CREATE INDEX IF NOT EXISTS idx_city ON weather_history(city);

-- Create an index on created_at for faster date range queries
CREATE INDEX IF NOT EXISTS idx_created_at ON weather_history(created_at);
