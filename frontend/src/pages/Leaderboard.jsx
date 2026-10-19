
import { API_BASE_URL } from "../config";
import { useEffect, useState } from "react";

const USER_ID = "demo_user";

export default function Leaderboard() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    let cancelled = false;

    async function loadLeaderboard() {
      try {
        const response = await fetch(
          `${API_BASE_URL}/leaderboard?user_id=${encodeURIComponent(USER_ID)}`
        );

        if (!response.ok) {
          throw new Error("Leaderboard request failed");
        }

        const result = await response.json();
        if (!cancelled) setData(result);
      } catch {
        if (!cancelled) {
          setError("Could not load the leaderboard. Please try again later.");
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    }

    loadLeaderboard();
    return () => {
      cancelled = true;
    };
  }, []);

  const cardStyle = {
    background: "#ffffff",
    border: "1px solid #e5e7eb",
    borderRadius: 14,
    padding: 18,
  };

  return (
    <main
      style={{
        maxWidth: 900,
        margin: "36px auto",
        padding: "0 18px",
        fontFamily: "Arial, sans-serif",
        color: "#172033",
      }}
    >
      <a href="/dashboard">Back to dashboard</a>
      <h1>SmartFit Global Leaderboard</h1>
      <p>Build a consistent workout habit and earn points every day.</p>

      {loading && <p>Loading leaderboard...</p>}
      {error && <p role="alert">{error}</p>}

      {data && (
        <>
          <section
            style={{
              display: "grid",
              gridTemplateColumns: "repeat(auto-fit, minmax(160px, 1fr))",
              gap: 12,
              margin: "24px 0",
            }}
          >
            <div style={cardStyle}>
              <p>Your points</p>
              <h2>{data.current_user?.total_points ?? 0}</h2>
            </div>
            <div style={cardStyle}>
              <p>Current streak</p>
              <h2>{data.current_user?.current_streak ?? 0} days</h2>
            </div>
            <div style={cardStyle}>
              <p>Longest streak</p>
              <h2>{data.current_user?.longest_streak ?? 0} days</h2>
            </div>
          </section>

          <div style={{ overflowX: "auto" }}>
            <table
              style={{
                width: "100%",
                borderCollapse: "collapse",
                textAlign: "left",
              }}
            >
              <thead>
                <tr>
                  {["Rank", "User", "Points", "Current streak"].map((label) => (
                    <th
                      key={label}
                      style={{
                        padding: 12,
                        borderBottom: "2px solid #e5e7eb",
                      }}
                    >
                      {label}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {data.leaderboard.map((entry) => (
                  <tr key={entry.user_id}>
                    <td style={{ padding: 12, borderBottom: "1px solid #eee" }}>
                      {entry.rank <= 3
                        ? ["Gold", "Silver", "Bronze"][entry.rank - 1]
                        : `#${entry.rank}`}
                    </td>
                    <td style={{ padding: 12, borderBottom: "1px solid #eee" }}>
                      {entry.user_id}
                      {entry.user_id === USER_ID ? " (You)" : ""}
                    </td>
                    <td style={{ padding: 12, borderBottom: "1px solid #eee" }}>
                      {entry.total_points}
                    </td>
                    <td style={{ padding: 12, borderBottom: "1px solid #eee" }}>
                      {entry.current_streak} days
                    </td>
                  </tr>
                ))}
                {data.leaderboard.length === 0 && (
                  <tr>
                    <td colSpan={4} style={{ padding: 18 }}>
                      No workout points yet. Save your first workout to join!
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </>
      )}
    </main>
  );
}
