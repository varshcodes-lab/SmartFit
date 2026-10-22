import { useState } from "react";

const BASE_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

const MUSCLES = [
  "chest", "back", "shoulders", "biceps", "triceps",
  "quadriceps", "glutes", "hamstrings", "calves", "core",
];

const EQUIPMENT = [
  { value: "bodyweight", label: "No equipment" },
  { value: "dumbbell", label: "Dumbbells" },
  { value: "resistance band", label: "Resistance bands" },
  { value: "barbell", label: "Barbell" },
  { value: "gym", label: "Gym equipment" },
];

const styles = {
  page: {
    minHeight: "100vh", background: "#0b1220", color: "#e5e7eb",
    padding: "32px 18px 60px", fontFamily: "system-ui, sans-serif",
  },
  container: { maxWidth: 1000, margin: "0 auto" },
  card: {
    background: "#111c2f", border: "1px solid #26364e",
    borderRadius: 16, padding: 22, marginBottom: 20,
  },
  field: {
    display: "grid", gap: 7, marginBottom: 18,
  },
  input: {
    width: "100%", boxSizing: "border-box", padding: 11,
    borderRadius: 8, border: "1px solid #40516b",
    background: "#0b1220", color: "#e5e7eb",
  },
  button: {
    padding: "12px 18px", borderRadius: 9, border: 0,
    background: "#22c55e", color: "#052e16", fontWeight: 700,
    cursor: "pointer",
  },
  muted: { color: "#a7b4c7", lineHeight: 1.6 },
  tag: {
    display: "inline-block", padding: "4px 9px", margin: "4px 5px 4px 0",
    borderRadius: 20, background: "#1d3048", color: "#cbd5e1",
    fontSize: 13,
  },
};

function pretty(value) {
  if (Array.isArray(value)) return value.map(pretty).join(", ");
  if (typeof value === "string") {
    return value.replaceAll("_", " ");
  }
  return value == null ? "" : String(value);
}

function firstValue(object, keys) {
  for (const key of keys) {
    if (object?.[key] != null && object[key] !== "") return object[key];
  }
  return null;
}

export default function Recommendations() {
  const [goal, setGoal] = useState("muscle_gain");
  const [experience, setExperience] = useState("intermediate");
  const [equipment, setEquipment] = useState(["dumbbell"]);
  const [muscles, setMuscles] = useState(["chest"]);
  const [preferences, setPreferences] = useState("");
  const [performance, setPerformance] = useState("75");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const toggle = (value, current, setter) => {
    setter(
      current.includes(value)
        ? current.filter((item) => item !== value)
        : [...current, value]
    );
  };

  async function submit(event) {
    event.preventDefault();
    setLoading(true);
    setError("");
    setResult(null);

    const payload = {
      goal,
      experience,
      equipment,
      target_muscles: muscles,
      preferences: preferences
        .split(",")
        .map((item) => item.trim())
        .filter(Boolean),
      workout_history: [],
    };

    if (performance.trim() !== "") {
      const number = Number(performance);
      if (!Number.isFinite(number) || number < 0 || number > 100) {
        setLoading(false);
        setError("Performance score must be between 0 and 100.");
        return;
      }
      payload.performance_score = number;
    }

    try {
      const response = await fetch(`${BASE_URL}/recommendations/generate`, {
        method: "POST",
        headers: { "Content-Type": "application/json", Accept: "application/json" },
        body: JSON.stringify(payload),
      });

      const data = await response.json().catch(() => ({}));
      if (!response.ok) {
        const detail = Array.isArray(data.detail)
          ? data.detail.map((item) => item.msg).join("; ")
          : data.detail;
        throw new Error(detail || `Request failed (HTTP ${response.status}).`);
      }
      setResult(data);
    } catch (err) {
      setError(
        `${err.message || "Could not reach the recommendation API."} ` +
        "Check that the backend is running and VITE_API_URL points to it."
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <main style={styles.page}>
<p style={{textAlign:"center",margin:"10px"}}><a href="/diet-plan">ðŸ½ï¸ Create a personalized diet plan</a></p>

      <div style={styles.container}>
        <header style={{ marginBottom: 24 }}>
          <a href="/" style={{ color: "#86efac", textDecoration: "none" }}>
            ← Live Workout
          </a>
          <p style={{ color: "#86efac", letterSpacing: 2, fontWeight: 700 }}>
            SMARTFIT AI
          </p>
          <h1 style={{ fontSize: "clamp(30px, 5vw, 44px)", margin: "8px 0" }}>
            Personalized Exercise Recommendations
          </h1>
          <p style={styles.muted}>
            Choose your goal, experience, available equipment, and target muscles.
            SmartFit will retrieve relevant guidance and rank exercises for your profile.
          </p>
        </header>

        <form style={styles.card} onSubmit={submit}>
          <h2 style={{ marginTop: 0 }}>Your training profile</h2>

          <div style={styles.field}>
            <label htmlFor="goal">Fitness goal</label>
            <select id="goal" style={styles.input} value={goal}
              onChange={(event) => setGoal(event.target.value)}>
              <option value="muscle_gain">Muscle gain</option>
              <option value="strength">Strength</option>
              <option value="general_fitness">General fitness</option>
              <option value="weight_loss">Weight loss</option>
            </select>
          </div>

          <div style={styles.field}>
            <label htmlFor="experience">Experience level</label>
            <select id="experience" style={styles.input} value={experience}
              onChange={(event) => setExperience(event.target.value)}>
              <option value="beginner">Beginner</option>
              <option value="intermediate">Intermediate</option>
              <option value="advanced">Advanced</option>
            </select>
          </div>

          <fieldset style={{ border: 0, padding: 0, margin: "0 0 20px" }}>
            <legend style={{ marginBottom: 10, fontWeight: 600 }}>
              Available equipment
            </legend>
            <div style={{ display: "flex", flexWrap: "wrap", gap: 12 }}>
              {EQUIPMENT.map((item) => (
                <label key={item.value} style={{ display: "flex", gap: 7, alignItems: "center" }}>
                  <input type="checkbox"
                    checked={equipment.includes(item.value)}
                    onChange={() => toggle(item.value, equipment, setEquipment)} />
                  {item.label}
                </label>
              ))}
            </div>
          </fieldset>

          <fieldset style={{ border: 0, padding: 0, margin: "0 0 20px" }}>
            <legend style={{ marginBottom: 10, fontWeight: 600 }}>
              Target muscles
            </legend>
            <div style={{ display: "flex", flexWrap: "wrap", gap: 12 }}>
              {MUSCLES.map((muscle) => (
                <label key={muscle} style={{ display: "flex", gap: 7, alignItems: "center" }}>
                  <input type="checkbox"
                    checked={muscles.includes(muscle)}
                    onChange={() => toggle(muscle, muscles, setMuscles)} />
                  {pretty(muscle)}
                </label>
              ))}
            </div>
          </fieldset>

          <div style={styles.field}>
            <label htmlFor="preferences">Preferences (comma-separated, optional)</label>
            <input id="preferences" style={styles.input}
              placeholder="e.g. low impact, compound exercises"
              value={preferences} onChange={(event) => setPreferences(event.target.value)} />
          </div>

          <div style={styles.field}>
            <label htmlFor="performance">Performance score (0–100, optional)</label>
            <input id="performance" type="number" min="0" max="100"
              style={styles.input} value={performance}
              onChange={(event) => setPerformance(event.target.value)} />
          </div>

          <button type="submit" disabled={loading} style={{
            ...styles.button, opacity: loading ? 0.65 : 1,
          }}>
            {loading ? "Generating recommendations..." : "Get recommendations"}
          </button>
        </form>

        {error && (
          <div role="alert" style={{
            ...styles.card, borderColor: "#ef4444", color: "#fecaca",
          }}>
            <strong>Request failed</strong>
            <p>{error}</p>
          </div>
        )}

        {result && (
          <section aria-live="polite">
            <div style={styles.card}>
              <h2 style={{ marginTop: 0 }}>Your recommendations</h2>
              <p style={styles.muted}>
                Goal: {pretty(result.goal)} · Experience: {pretty(result.experience)}
              </p>
              {result.model && (
                <p style={styles.muted}>Explanation model: {result.model}</p>
              )}
              {result.llm_error_type && (
                <p style={{ color: "#fde68a" }}>
                  Model unavailable ({result.llm_error_type}); showing available
                  recommendation results.
                </p>
              )}
              {Array.isArray(result.recommendations) &&
                result.recommendations.map((exercise, index) => {
                  const name = firstValue(exercise, ["name", "exercise_name", "exercise"]);
                  const description = firstValue(exercise, ["description", "instructions", "how_to"]);
                  const reason = firstValue(exercise, ["reason", "explanation", "recommendation_reason"]);
                  const targets = firstValue(exercise, ["target_muscles", "muscles", "muscle_groups"]);
                  const gear = firstValue(exercise, ["equipment", "required_equipment"]);
                  const score = firstValue(exercise, ["score", "selection_score"]);
                  return (
                    <article key={`${name || "exercise"}-${index}`} style={{
                      padding: "16px 0", borderTop: "1px solid #26364e",
                    }}>
                      <h3>{index + 1}. {name || `Exercise ${index + 1}`}</h3>
                      {score != null && (
                        <span style={styles.tag}>Score: {pretty(score)}</span>
                      )}
                      {targets != null && (
                        <span style={styles.tag}>Targets: {pretty(targets)}</span>
                      )}
                      {gear != null && (
                        <span style={styles.tag}>Equipment: {pretty(gear)}</span>
                      )}
                      {description && <p style={styles.muted}>{pretty(description)}</p>}
                      {reason && <p>{pretty(reason)}</p>}
                    </article>
                  );
                })}
              {result.explanation && (
                <>
                  <h3>Why these exercises?</h3>
                  <p style={{ ...styles.muted, whiteSpace: "pre-line" }}>
                    {result.explanation}
                  </p>
                </>
              )}
              {result.warning && (
                <p style={{ ...styles.muted, fontSize: 13 }}>{result.warning}</p>
              )}
            </div>

            <div style={styles.card}>
              <h2 style={{ marginTop: 0 }}>Retrieved evidence and guidance</h2>
              <p style={styles.muted}>
                External references provide general fitness guidance; internal
                guidance is project material, not independent validation.
              </p>
              {Array.isArray(result.sources) && result.sources.length > 0 ? (
                result.sources.map((source, index) => (
                  <div key={`${source.url || source.title}-${index}`} style={{
                    padding: "12px 0", borderTop: "1px solid #26364e",
                  }}>
                    <strong>{source.title || "Fitness source"}</strong>
                    <p style={styles.muted}>
                      {source.publisher || source.source || "Source not specified"}
                      {" · "}{pretty(source.source_type)}
                    </p>
                    {source.evidence_scope && (
                      <p style={styles.muted}>{source.evidence_scope}</p>
                    )}
                    {Array.isArray(source.evidence_claims) &&
                      source.evidence_claims.length > 0 && (
                        <ul>
                          {source.evidence_claims.map((claim, claimIndex) => (
                            <li key={claimIndex}>{claim}</li>
                          ))}
                        </ul>
                      )}
                    {typeof source.url === "string" &&
                      source.url.startsWith("https://") && (
                        <a href={source.url} target="_blank" rel="noopener noreferrer"
                          style={{ color: "#86efac" }}>
                          Read source ↗
                        </a>
                      )}
                  </div>
                ))
              ) : (
                <p style={styles.muted}>No source metadata was returned.</p>
              )}
            </div>
          </section>
        )}
      </div>
    </main>
  );
}
