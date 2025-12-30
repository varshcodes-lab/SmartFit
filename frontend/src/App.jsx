import { useEffect, useState } from "react";
import "./App.css";

const BASE_URL = "https://smartfit-70dv.onrender.com";
const USER_ID = "demo_user";

function App() {
  const [file, setFile] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const [exercise, setExercise] = useState("squat");
  const [mode, setMode] = useState("image");

  const [jobId, setJobId] = useState(null);
  const [status, setStatus] = useState(null);


  useEffect(() => {
    if (!jobId) return;

    const interval = setInterval(async () => {
      try {
        const res = await fetch(`${BASE_URL}/tf/video-status/${jobId}`);
        const data = await res.json();

        setStatus(data.status);

        if (data.status === "completed") {
          const resultRes = await fetch(
            `${BASE_URL}/tf/video-result/${jobId}`
          );
          const resultData = await resultRes.json();
          setResult(resultData.result);
          setLoading(false);
          clearInterval(interval);
        }

        if (data.status === "failed") {
          alert("Video analysis failed");
          setLoading(false);
          clearInterval(interval);
        }
      } catch (err) {
        console.error("Polling error:", err);
        setLoading(false);
        clearInterval(interval);
      }
    }, 2000);

    return () => clearInterval(interval);
  }, [jobId]);

 
  const handleAnalyze = async () => {
    if (!file) {
      alert("Please select a file");
      return;
    }

    if (loading) return;

    setLoading(true);
    setResult(null);
    setJobId(null);
    setStatus(null);

    const formData = new FormData();
    formData.append("file", file);

    const endpoint =
      mode === "image"
        ? `${BASE_URL}/tf/analyze-image?exercise=${exercise}&user_id=${USER_ID}`
        : `${BASE_URL}/tf/analyze-video?exercise=${exercise}&user_id=${USER_ID}`;

    try {
      const res = await fetch(endpoint, {
        method: "POST",
        body: formData,
      });

      
      const data = await res.json();
      console.log("BACKEND RESPONSE:", data);

      if (!res.ok) {
        alert(data.detail || "Backend error");
        setLoading(false);
        return;
      }

      if (mode === "image") {
        setResult(data.result || data.workout);
        setLoading(false);
      } else {
        setJobId(data.job_id);
      }
    } catch (err) {
      console.error("FRONTEND ERROR:", err);
      alert("Frontend failed to read backend response");
      setLoading(false);
    }
  };

  return (
    <div className="container">
      <h1>🏋️ SmartFit Exercise Analyzer</h1>

      <label><b>Mode:</b></label>
      <select value={mode} onChange={(e) => setMode(e.target.value)}>
        <option value="image">Image</option>
        <option value="video">Video</option>
      </select>

      <br /><br />

      <label><b>Exercise:</b></label>
      <select value={exercise} onChange={(e) => setExercise(e.target.value)}>
        <option value="squat">Squat</option>
        <option value="pushup">Push-up</option>
        <option value="pullup">Pull-up</option>
      </select>

      <br /><br />

      <input
        type="file"
        accept={mode === "image" ? "image/*" : "video/*"}
        onChange={(e) => setFile(e.target.files[0])}
      />

      <br /><br />

      <button onClick={handleAnalyze} disabled={loading}>
        {loading ? "Analyzing..." : `Analyze ${mode}`}
      </button>

      {loading && mode === "video" && (
        <p>⏳ Video processing... {status || "starting"}</p>
      )}

      {result && (
        <div className="result">
          <h2>📊 Result</h2>

          <p><b>Exercise:</b> {result.exercise}</p>
          <p><b>Score:</b> {result.score}</p>
          <p><b>Reps:</b> {result.reps}</p>
          <p><b>Feedback:</b> {result.feedback}</p>

          {result.image && (
            <img
              src={`data:image/jpeg;base64,${result.image}`}
              alt="Pose Skeleton"
              className="pose-image"
            />
          )}
        </div>
      )}
    </div>
  );
}

export default App;
