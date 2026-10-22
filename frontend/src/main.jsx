import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter, Routes, Route } from "react-router-dom";

import App from "./App";
import WorkoutDashboard from "./pages/WorkoutDashboard";
import Recommendations from "./pages/Recommendations";

import DietPlan from "./pages/DietPlan";
import Leaderboard from "./pages/Leaderboard";
ReactDOM.createRoot(document.getElementById("root")).render(
  <BrowserRouter>
    <Routes>
      <Route path="/" element={<App />} />
      <Route path="/dashboard" element={<WorkoutDashboard />} />
      <Route path="/recommendations" element={<Recommendations />} />
      <Route path="/diet-plan" element={<DietPlan />} />
      <Route path="/leaderboard" element={<Leaderboard />} />
    </Routes>
  </BrowserRouter>
);
