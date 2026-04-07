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
        `http://localhost:8080/api/weather/${encodeURIComponent(city.trim())}`
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
      const res = await fetch(`http://localhost:8080/api/history/${encodeURIComponent(city.trim())}`);
      const data = await res.json();
      setHistory(data);
    } catch (err) {
      console.error("Failed to fetch history:", err);
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

          {history.length > 0 && (
            <div style={styles.chartContainer}>
              <h3>Temperature History (Last 24 Hours)</h3>
              <LineChart width={600} height={300} data={history}>
                <XAxis dataKey="time" />
                <YAxis />
                <Tooltip />
                <CartesianGrid stroke="#ccc" />
                <Line type="monotone" dataKey="temp" stroke="#2563eb" />
              </LineChart>
            </div>
          )}
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
  },
};

export default App;