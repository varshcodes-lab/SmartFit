import React, { useState } from "react";

const API_URL = "http://127.0.0.1:8000/tf/analyze-image";

export default function SquatAnalyzer() {
  const [file, setFile] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleUpload = async () => {
    if (!file) return alert("Please upload an image");

    const formData = new FormData();
    formData.append("file", file);
    formData.append("exercise", "pushup");

    setLoading(true);
    try {
      const res = await fetch(API_URL, {
        method: "POST",
        body: formData,
      });

      const data = await res.json();
      setResult(data.result);
    } catch (err) {
      alert("Error analyzing image");
      console.error(err);
    }
    setLoading(false);
  };

  const feedbackColor =
    result?.form === "Good Squat"
      ? "#22c55e"
      : result?.form === "Shallow Squat"
      ? "#facc15"
      : "#ef4444";

  return (
    <div style={styles.container}>
      <h1>🏋️ Squat Form Analyzer</h1>

      <input
        type="file"
        accept="image/*"
        onChange={(e) => setFile(e.target.files[0])}
      />

      <button onClick={handleUpload} disabled={loading}>
        {loading ? "Analyzing..." : "Analyze Squat"}
      </button>

      {result && (
        <div style={styles.card}>
          <h2 style={{ color: feedbackColor }}>{result.form}</h2>

          <p>🦵 Knee Angle: <b>{result.knee_angle}°</b></p>
          <p>🦴 Hip Angle: <b>{result.hip_angle}°</b></p>

          <p>📊 Score</p>
          <div style={styles.progressBar}>
            <div
              style={{
                ...styles.progressFill,
                width: `${result.score}%`,
                backgroundColor: feedbackColor,
              }}
            />
          </div>
          <p><b>{result.score}%</b></p>

          <p>💬 {result.feedback}</p>

          <img
            src={`data:image/jpeg;base64,${result.image}`}
            alt="Skeleton"
            style={styles.image}
          />
        </div>
      )}
    </div>
  );
}

const styles = {
  container: {
    maxWidth: "500px",
    margin: "40px auto",
    textAlign: "center",
    fontFamily: "sans-serif",
  },
  card: {
    marginTop: "20px",
    padding: "20px",
    borderRadius: "12px",
    boxShadow: "0 10px 25px rgba(0,0,0,0.15)",
  },
  image: {
    marginTop: "15px",
    width: "100%",
    borderRadius: "10px",
  },
  progressBar: {
    width: "100%",
    height: "10px",
    background: "#e5e7eb",
    borderRadius: "6px",
    overflow: "hidden",
  },
  progressFill: {
    height: "100%",
    transition: "width 0.4s ease",
  },
};
