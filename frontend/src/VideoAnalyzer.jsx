import { useState } from "react";

function VideoAnalyzer() {
  const [video, setVideo] = useState(null);
  const [exercise, setExercise] = useState("squat");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleAnalyze = async () => {
    if (!video) {
      alert("Please select a video");
      return;
    }

    const formData = new FormData();
    formData.append("file", video);

    setLoading(true);
    setResult(null);

    try {
      const response = await fetch(
        `http://127.0.0.1:8000/tf/analyze-video?exercise=${exercise}`,
        {
          method: "POST",
          body: formData,
        }
      );

      const data = await response.json();
      setResult(data);
    } catch (error) {
      alert("Backend error");
      console.error(error);
    }

    setLoading(false);
  };

  return (
    <div style={{ padding: "20px" }}>
      <h2>🎥 SmartFit Video Analyzer</h2>

      <select
        value={exercise}
        onChange={(e) => setExercise(e.target.value)}
      >
        <option value="squat">Squat</option>
        <option value="pushup">Push-up</option>
        <option value="pullup">Pull-up</option>
      </select>

      <br /><br />

      <input
        type="file"
        accept="video/*"
        onChange={(e) => setVideo(e.target.files[0])}
      />

      <br /><br />

      <button onClick={handleAnalyze}>
        Analyze Video
      </button>

      {loading && <p>Analyzing video...</p>}

      {result && (
        <div style={{ marginTop: "20px" }}>
          <h3>📊 Result</h3>
          <p><b>Exercise:</b> {result.exercise}</p>
          <p><b>Total Frames:</b> {result.frames}</p>

          <h4>📋 Data Preview</h4>
          <table border="1" cellPadding="6">
            <thead>
              <tr>
                <th>Frame</th>
                <th>Pose Detected</th>
                <th>Knee Angle</th>
              </tr>
            </thead>
            <tbody>
              {result.data_preview.map((row, index) => (
                <tr key={index}>
                  <td>{row.frame}</td>
                  <td>{row.pose_detected ? "Yes" : "No"}</td>
                  <td>{row.knee_angle ?? "-"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

export default VideoAnalyzer;
