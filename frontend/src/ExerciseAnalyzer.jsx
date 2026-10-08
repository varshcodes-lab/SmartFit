import { useState } from "react";

export default function ExerciseAnalyzer() {
  const [file, setFile] = useState(null);
  const [exercise, setExercise] = useState("squat");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async () => {
    if (!file) {
      alert("Please select an image");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);

    setLoading(true);
    setResult(null);

    try {
      const response = await fetch(
        `http://127.0.0.1:8000/tf/analyze-image?exercise=${exercise}`,
        {
          method: "POST",
          body: formData,
        }
      );

      const data = await response.json();
      setResult(data.result);
    } catch (err) {
      alert("Backend error");
    }

    setLoading(false);
  };

  return (
    <div style={{ maxWidth: 500, margin: "auto", padding: 20 }}>
      <h2>🏋️ SmartFit Exercise Analyzer</h2>

      <select
        value={exercise}
        onChange={(e) => setExercise(e.target.value)}
        style={{ width: "100%", marginBottom: 10 }}
      >
        <option value="squat">Squat</option>
        <option value="pushup">Push-up</option>
      </select>

      <input
        type="file"
        accept="image/*"
        onChange={(e) => setFile(e.target.files[0])}
      />

      <br /><br />

      <button onClick={handleSubmit}>
        Analyze
      </button>

      {loading && <p>Analyzing...</p>}

      {result && (
        <div style={{ marginTop: 20 }}>
          <h3>📊 Result</h3>

          <p><b>Exercise:</b> {result.exercise}</p>
          <p><b>Score:</b> {result.score}</p>
          <p><b>Form:</b> {result.form}</p>
          <p><b>Feedback:</b> {result.feedback}</p>

          {result.knee_angle && <p>Knee Angle: {result.knee_angle}°</p>}
          {result.hip_angle && <p>Hip Angle: {result.hip_angle}°</p>}
          {result.elbow_angle && <p>Elbow Angle: {result.elbow_angle}°</p>}
          {result.body_angle && <p>Body Angle: {result.body_angle}°</p>}

          {result.image && (
            <>
              <h4>🦴 Skeleton Output</h4>
              <img
                src={`data:image/jpeg;base64,${result.image}`}
                alt="Skeleton"
                style={{ width: "100%", border: "1px solid #ccc" }}
              />
            </>
          )}
        </div>
      )}
    </div>
  );
}
