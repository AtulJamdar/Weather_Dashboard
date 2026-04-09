import React, { useState } from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid
} from "recharts";

function App() {
  const [city, setCity] = useState("");
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [history, setHistory] = useState([]);

  const fetchWeather = async () => {
    if (!city.trim()) {
      setError("Please enter a city name.");
      return;
    }

    setLoading(true);
    setError("");
    setData(null);

    try {
      // Calling your Java Backend on Port 8080
      const res = await fetch(
        `https://weather-dashboard-1-tnkh.onrender.com/api/weather/${encodeURIComponent(city.trim())}`
      );

      if (!res.ok) {
        throw new Error("Failed to fetch data from server.");
      }

      const result = await res.json();

      if (result.status === "error") {
        setError(result.message || "Unable to fetch weather.");
      } else {
        setData(result);
        fetchHistory(); // Fetch history after getting weather
      }
    } catch (err) {
      console.error(err);
      setError("Backend not reachable. Ensure Java (8080) and Python (8000) are running.");
    } finally {
      setLoading(false);
    }
  };

  const fetchHistory = async () => {
    try {
      const res = await fetch(`https://weather-dashboard-1-tnkh.onrender.com/api/history/${city}`);
      const responseData = await res.json();
      
      // Check if response is an array (valid history data)
      if (Array.isArray(responseData)) {
        setHistory(responseData);
      } else if (responseData.error) {
        console.warn("History error:", responseData.error);
        setHistory([]);  // Set empty array so chart won't show
      } else {
        setHistory([]);
      }
    } catch (err) {
      console.error("Failed to fetch history:", err);
      setHistory([]);
    }
  };

  return (
    <div style={styles.container}>
      <h1 style={styles.title}>Weather Dashboard</h1>

      <div style={styles.searchBox}>
        <input
          type="text"
          placeholder="Enter city name (e.g. Pune)"
          value={city}
          onChange={(e) => setCity(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && fetchWeather()}
          style={styles.input}
        />

        <button onClick={fetchWeather} style={styles.button} disabled={loading}>
          {loading ? "Loading..." : "Get Weather"}
        </button>
      </div>

      {error && <div style={styles.errorCard}>{error}</div>}

      {data && (
        <div style={styles.weatherCard}>
          <h2 style={styles.cityTitle}>{data.city}</h2>
          
          <div style={styles.infoGrid}>
            <p><strong>Temperature:</strong> {data.temperature}</p>
            <p><strong>Humidity:</strong> {data.humidity}</p>
            <p><strong>Condition:</strong> {data.condition}</p>
          </div>

          <div style={styles.aiBox}>
            <strong style={styles.aiLabel}>✨ AI Insight:</strong>
            <p style={styles.aiText}>{data.ai_insight || "No summary available."}</p>
          </div>

          <div style={styles.chartContainer}>
            <h3 style={styles.chartTitle}>📊 Temperature History (Last 24 Hours)</h3>
            {history && history.length > 0 ? (
              <>
                <LineChart width={600} height={300} data={history}>
                  <XAxis 
                    dataKey="time" 
                    tick={{ fontSize: 12 }}
                    angle={-45}
                    textAnchor="end"
                    height={100}
                  />
                  <YAxis label={{ value: 'Temperature (°C)', angle: -90, position: 'insideLeft' }} />
                  <Tooltip 
                    formatter={(value) => `${value}°C`}
                    labelFormatter={(label) => `Time: ${label}`}
                  />
                  <CartesianGrid stroke="#ccc" />
                  <Line 
                    type="monotone" 
                    dataKey="temp" 
                    stroke="#2563eb" 
                    strokeWidth={2}
                    dot={{ fill: '#2563eb', r: 4 }}
                  />
                </LineChart>
                <p style={styles.chartNote}>Chart shows temperature variations across time periods</p>
              </>
            ) : (
              <div style={styles.noChartData}>
                <p>Loading chart data...</p>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

// Inline Styles
const styles = {
  container: {
    maxWidth: "600px",
    margin: "50px auto",
    fontFamily: "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif",
    padding: "20px",
    backgroundColor: "#f4f7fe",
    borderRadius: "15px",
  },
  title: {
    textAlign: "center",
    color: "#1e293b",
    marginBottom: "30px",
  },
  searchBox: {
    display: "flex",
    gap: "10px",
    marginBottom: "25px",
  },
  input: {
    flex: 1,
    padding: "14px",
    borderRadius: "10px",
    border: "1px solid #cbd5e1",
    fontSize: "16px",
    outline: "none",
  },
  button: {
    padding: "14px 24px",
    borderRadius: "10px",
    border: "none",
    background: "#2563eb",
    color: "white",
    fontSize: "16px",
    fontWeight: "bold",
    cursor: "pointer",
    transition: "background 0.2s",
  },
  errorCard: {
    padding: "15px",
    borderRadius: "10px",
    background: "#fee2e2",
    color: "#b91c1c",
    marginBottom: "20px",
    border: "1px solid #fecaca",
  },
  weatherCard: {
    padding: "25px",
    borderRadius: "15px",
    background: "white",
    boxShadow: "0 10px 15px -3px rgba(0, 0, 0, 0.1)",
  },
  cityTitle: {
    marginTop: 0,
    color: "#1e293b",
    borderBottom: "2px solid #e2e8f0",
    paddingBottom: "10px",
  },
  infoGrid: {
    display: "grid",
    gridTemplateColumns: "1fr 1fr",
    gap: "10px",
    margin: "20px 0",
  },
  aiBox: {
    marginTop: "20px",
    padding: "15px",
    borderRadius: "10px",
    background: "#eff6ff",
    borderLeft: "4px solid #3b82f6",
  },
  aiLabel: {
    color: "#1e40af",
    display: "block",
    marginBottom: "5px",
  },
  aiText: {
    margin: 0,
    color: "#334155",
    lineHeight: "1.5",
  },
  chartContainer: {
    marginTop: "30px",
    textAlign: "center",
    padding: "20px",
    borderRadius: "10px",
    background: "#f0f9ff",
    border: "1px solid #bfdbfe",
  },
  chartTitle: {
    color: "#1e40af",
    marginTop: 0,
    marginBottom: "15px",
  },
  chartNote: {
    color: "#64748b",
    fontSize: "13px",
    marginTop: "10px",
    fontStyle: "italic",
  },
  noChartData: {
    padding: "40px 20px",
    color: "#64748b",
    fontSize: "14px",
  },
};

export default App;