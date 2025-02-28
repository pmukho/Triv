import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Login from "./components/Login";
import Leaderboard from "./components/Leaderboard";
import Quiz from "./components/Quiz";
import GameHistory from "./components/GameHistory";
import Results from "./components/Results";

import "./index.css";

const root = ReactDOM.createRoot(document.getElementById("root"));

root.render(
    <React.StrictMode>
        <Router>
            <Routes>
                <Route path="/" element={<Login />} />
                <Route path="/quiz" element={<Quiz />} />
                <Route path="/results" element={<Results />} />
                <Route path="/leaderboard" element={<Leaderboard />} />
                <Route path="/gamehistory" element={<GameHistory/>} />
            </Routes>
        </Router>
    </React.StrictMode>
);
