import { useEffect, useState } from "react";
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  PieChart,
  Pie,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  Legend,
  ResponsiveContainer,
} from "recharts";


const BASE_URL = "https://smartfit-70dv.onrender.com";
const USER_ID = "demo_user"; 


function WorkoutDashboard() {
  const [workouts, setWorkouts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const [message, setMessage] = useState("");
  const [coachReply, setCoachReply] = useState("");
  const [coachLoading, setCoachLoading] = useState(false);
  const [coachError, setCoachError] = useState(null);

 
  useEffect(() => {
    async function loadWorkouts() {
      try {
        const res = await fetch(
          `${BASE_URL}/workout/history/${USER_ID}`
        );

        if (!res.ok) {
          throw new Error("Failed to fetch workouts");
        }

        const data = await res.json();
        setWorkouts(data);
      } catch (err) {
        console.error("Workout fetch error:", err);
        setError("Failed to load workouts");
      } finally {
        setLoading(false);
      }
    }

    loadWorkouts();
  }, []);

  
  const sendMessageToCoach = async () => {
    if (!message.trim() || coachLoading) return;

    setCoachLoading(true);
    setCoachError(null);
    setCoachReply("");

    try {
      const res = await fetch(`${BASE_URL}/coach/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          user_id: USER_ID,
          message: message.trim(),
        }),
      });

      if (!res.ok) {
        throw new Error("Coach failed");
      }

      const data = await res.json();
      setCoachReply(data.reply || "🤖 No response from coach.");
    } catch (err) {
      console.error("Coach error:", err);
      setCoachError("⚠️ Coach is unavailable right now.");
    } finally {
      setCoachLoading(false);
      setMessage("");
    }
  };

  
  if (loading) return <p>⏳ Loading dashboard...</p>;
  if (error) return <p style={{ color: "red" }}>❌ {error}</p>;

  
  const chartData = workouts.map((w) => ({
    date: new Date(w.created_at).toLocaleDateString(),
    reps: w.reps,
    duration: w.duration || 0,
    exercise: w.exercise,
  }));

  const exerciseCount = {};
  workouts.forEach((w) => {
    exerciseCount[w.exercise] = (exerciseCount[w.exercise] || 0) + 1;
  });

  const pieData = Object.keys(exerciseCount).map((key) => ({
    name: key,
    value: exerciseCount[key],
  }));

 
  return (
    <div style={{ padding: "20px" }}>
      <h1>📊 SmartFit Workout Dashboard</h1>
      <p>User ID: <b>{USER_ID}</b></p>

      {/* ---------- LINE CHART ---------- */}
      <h2>📈 Progress Over Time</h2>
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="date" />
          <YAxis />
          <Tooltip />
          <Legend />
          <Line dataKey="reps" stroke="#8884d8" />
          <Line dataKey="duration" stroke="#82ca9d" />
        </LineChart>
      </ResponsiveContainer>

      {/* ---------- BAR CHART ---------- */}
      <h2>📊 Reps Per Workout</h2>
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="date" />
          <YAxis />
          <Tooltip />
          <Legend />
          <Bar dataKey="reps" fill="#8884d8" />
        </BarChart>
      </ResponsiveContainer>

      {/* ---------- PIE CHART ---------- */}
      <h2>🥧 Exercise Distribution</h2>
      <ResponsiveContainer width="100%" height={300}>
        <PieChart>
          <Pie
            data={pieData}
            dataKey="value"
            nameKey="name"
            label
            fill="#82ca9d"
          />
          <Tooltip />
        </PieChart>
      </ResponsiveContainer>

      {/* ---------- AI COACH ---------- */}
      <hr style={{ margin: "40px 0" }} />
      <h2>🤖 AI Coach</h2>

      <input
        type="text"
        value={message}
        placeholder="Ask the coach about your workout..."
        onChange={(e) => setMessage(e.target.value)}
        style={{ width: "70%", padding: "8px" }}
      />

      <button
        onClick={sendMessageToCoach}
        disabled={coachLoading}
        style={{ marginLeft: "10px", padding: "8px 16px" }}
      >
        {coachLoading ? "Thinking..." : "Send"}
      </button>

      {coachError && <p style={{ color: "red" }}>{coachError}</p>}

      {coachReply && (
        <div
          style={{
            marginTop: "15px",
            padding: "15px",
            background: "#f4f4f4",
            borderRadius: "6px",
          }}
        >
          <b>Coach:</b>
          <p>{coachReply}</p>
        </div>
      )}
    </div>
  );
}

export default WorkoutDashboard;
