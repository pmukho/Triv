import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Login from "./components/Login";
import Leaderboard from "./components/Leaderboard";
import Quiz from "./components/Quiz";
import UserInputTest from "./components/UserInputTest";

import "./index.css";

const root = ReactDOM.createRoot(document.getElementById("root"));

root.render(
    <React.StrictMode>
        <Router>
            <Routes>
                <Route path="/" element={<Login />} />
                <Route path="/quiz" element={<Quiz />} />
                <Route path="/leaderboard" element={<Leaderboard />} />
                <Route path="/userinputtest" element={<UserInputTest/>} />
            </Routes>
        </Router>
    </React.StrictMode>
);
