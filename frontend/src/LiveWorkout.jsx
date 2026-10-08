import { useCallback, useEffect, useRef, useState } from "react";

const BASE_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";
const USER_ID = "demo_user";

const POSE_CONNECTIONS = [
  [11, 12], [11, 13], [13, 15], [12, 14], [14, 16],
  [11, 23], [12, 24], [23, 24], [23, 25], [25, 27],
  [24, 26], [26, 28], [27, 31], [28, 32],
];

function LiveWorkout() {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const captureRef = useRef(null);
  const streamRef = useRef(null);
  const socketRef = useRef(null);
  const frameTimerRef = useRef(null);

  const [exercise, setExercise] = useState("squat");
  const [running, setRunning] = useState(false);
  const [connecting, setConnecting] = useState(false);
  const [error, setError] = useState("");
  const [analysis, setAnalysis] = useState({
    reps: 0,
    score: 0,
    average_score: 0,
    feedback: "Start your workout to begin live analysis",
    state: "up",
    angles: {},
  });
  const [summary, setSummary] = useState(null);

  const wsUrl = `${BASE_URL.replace(/^http/, "ws")}/live/workout`;

  const drawPose = useCallback((landmarks) => {
    const canvas = canvasRef.current;
    const video = videoRef.current;
    if (!canvas || !video || !landmarks?.length) return;

    const width = video.clientWidth || 640;
    const height = video.clientHeight || 480;
    const scaleX = width / video.videoWidth;
    const scaleY = height / video.videoHeight;

    canvas.width = width;
    canvas.height = height;

    const ctx = canvas.getContext("2d");
    ctx.clearRect(0, 0, width, height);
    ctx.lineWidth = 3;
    ctx.strokeStyle = "#22c55e";
    ctx.fillStyle = "#ffffff";

    for (const [a, b] of POSE_CONNECTIONS) {
      const p1 = landmarks[a];
      const p2 = landmarks[b];
      if (!p1 || !p2 || p1.visibility < 0.35 || p2.visibility < 0.35) continue;
      ctx.beginPath();
      ctx.moveTo(p1.x * width, p1.y * height);
      ctx.lineTo(p2.x * width, p2.y * height);
      ctx.stroke();
    }

    for (const point of landmarks) {
      if (point.visibility < 0.35) continue;
      ctx.beginPath();
      ctx.arc(point.x * width, point.y * height, 4, 0, Math.PI * 2);
      ctx.fill();
    }
  }, []);

  const stopCamera = useCallback(() => {
    if (frameTimerRef.current) clearInterval(frameTimerRef.current);
    frameTimerRef.current = null;

    if (streamRef.current) {
      streamRef.current.getTracks().forEach((track) => track.stop());
      streamRef.current = null;
    }

    if (videoRef.current) videoRef.current.srcObject = null;
  }, []);

  const stopWorkout = useCallback(() => {
    if (socketRef.current?.readyState === WebSocket.OPEN) {
      socketRef.current.send(JSON.stringify({ type: "stop" }));
    }
    if (frameTimerRef.current) clearInterval(frameTimerRef.current);
    frameTimerRef.current = null;
    stopCamera();
    setRunning(false);
    setConnecting(false);
  }, [stopCamera]);

  const sendFrame = useCallback(() => {
    const video = videoRef.current;
    const capture = captureRef.current;
    const socket = socketRef.current;
    if (!video || !capture || !socket || socket.readyState !== WebSocket.OPEN) return;
    if (video.readyState < 2) return;

    const maxWidth = 640;
    const ratio = Math.min(1, maxWidth / video.videoWidth);
    capture.width = Math.round(video.videoWidth * ratio);
    capture.height = Math.round(video.videoHeight * ratio);
    const ctx = capture.getContext("2d", { alpha: false });
    ctx.drawImage(video, 0, 0, capture.width, capture.height);
    const data = capture.toDataURL("image/jpeg", 0.55);
    socket.send(JSON.stringify({ type: "frame", data }));
  }, []);

  const startWorkout = async () => {
    setError("");
    setSummary(null);
    setAnalysis({ reps: 0, score: 0, average_score: 0, feedback: "Starting camera...", state: "up", angles: {} });
    setConnecting(true);

    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: "user", width: { ideal: 1280 }, height: { ideal: 720 } },
        audio: false,
      });
      streamRef.current = stream;
      videoRef.current.srcObject = stream;
      await videoRef.current.play();

      const socket = new WebSocket(wsUrl);
      socketRef.current = socket;

      socket.onopen = () => {
        socket.send(JSON.stringify({ type: "start", exercise, user_id: USER_ID }));
        setConnecting(false);
        setRunning(true);
        frameTimerRef.current = setInterval(sendFrame, 200);
      };

      socket.onmessage = (event) => {
        const data = JSON.parse(event.data);
        if (data.type === "analysis") {
          setAnalysis(data);
          drawPose(data.landmarks);
        } else if (data.type === "summary") {
          setSummary(data.summary);
          if (socketRef.current) {
            socketRef.current.close();
            socketRef.current = null;
          }
        } else if (data.type === "error") {
          setError(data.message || "Live analysis error");
        }
      };

      socket.onerror = () => setError("Could not connect to the SmartFit live-analysis server.");
      socket.onclose = () => {
        if (frameTimerRef.current) clearInterval(frameTimerRef.current);
        frameTimerRef.current = null;
      };
    } catch (err) {
      console.error(err);
      setConnecting(false);
      setError(err.name === "NotAllowedError" ? "Camera permission was denied." : "Could not access your camera.");
      stopCamera();
    }
  };

  useEffect(() => () => stopWorkout(), [stopWorkout]);

  const saveSummary = async () => {
    if (!summary) return;
    try {
      const response = await fetch(`${BASE_URL}/workout/save`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          user_id: USER_ID,
          exercise: summary.exercise,
          score: summary.average_score ?? summary.score ?? 0,
          reps: summary.reps ?? 0,
          feedback: summary.feedback || "Live workout completed",
          duration: 0,
        }),
      });
      if (!response.ok) throw new Error("Could not save workout");
    } catch (err) {
      console.error(err);
      setError("Workout was analyzed, but saving the session failed.");
    }
  };

  return (
    <div className="live-page">
      <div className="live-header">
        <div>
          <p className="eyebrow">SMARTFIT AI</p>
          <h1>Live Workout Coach</h1>
          <p>Real-time pose analysis, rep counting and form feedback.</p>
        </div>
        <a className="dashboard-link" href="/dashboard">Dashboard →</a>
      </div>

      <div className="live-controls">
        <label>
          Exercise
          <select value={exercise} onChange={(e) => setExercise(e.target.value)} disabled={running || connecting}>
            <option value="squat">Squat</option>
            <option value="pushup">Push-up</option>
            <option value="pullup">Pull-up</option>
          </select>
        </label>
        {!running ? (
          <button className="primary-button" onClick={startWorkout} disabled={connecting}>
            {connecting ? "Connecting..." : "Start Live Workout"}
          </button>
        ) : (
          <button className="danger-button" onClick={stopWorkout}>Stop Workout</button>
        )}
      </div>

      {error && <div className="live-error">⚠ {error}</div>}

      <div className="live-grid">
        <section className="camera-card">
          <div className="camera-stage">
            <video ref={videoRef} muted playsInline className="camera-video" />
            <canvas ref={canvasRef} className="pose-overlay" />
            {!running && <div className="camera-placeholder">📷<span>Start the workout to activate your camera</span></div>}
            {running && <div className="live-badge">● LIVE</div>}
          </div>
          <canvas ref={captureRef} className="hidden-canvas" />
        </section>

        <aside className="metrics-card">
          <div className="metric-main">
            <span>REPS</span>
            <strong>{analysis.reps}</strong>
          </div>
          <div className="metric-row">
            <div><span>Current form</span><strong>{analysis.score}%</strong></div>
            <div><span>Session average</span><strong>{analysis.average_score}%</strong></div>
          </div>
          <div className="feedback-box">
            <span>LIVE COACHING</span>
            <p>{analysis.feedback}</p>
          </div>
          {Object.entries(analysis.angles || {}).map(([key, value]) => (
            <div className="angle-row" key={key}>
              <span>{key.replaceAll("_", " ")}</span><strong>{value}°</strong>
            </div>
          ))}
          <div className="state-pill">Position: {analysis.state}</div>
        </aside>
      </div>

      {summary && (
        <section className="summary-card">
          <h2>Workout Complete 🎉</h2>
          <div className="summary-grid">
            <div><span>Exercise</span><strong>{summary.exercise}</strong></div>
            <div><span>Reps</span><strong>{summary.reps}</strong></div>
            <div><span>Form score</span><strong>{summary.average_score}%</strong></div>
            <div><span>Frames analyzed</span><strong>{summary.frames_analyzed}</strong></div>
          </div>
          <p>{summary.feedback}</p>
          <button className="primary-button" onClick={saveSummary}>Save Workout to Dashboard</button>
        </section>
      )}
    </div>
  );
}

export default LiveWorkout;
