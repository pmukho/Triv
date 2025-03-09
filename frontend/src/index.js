import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Login from "./components/Login";
import Leaderboard from "./components/Leaderboard";
import Quiz from "./components/Quiz";
import GameHistory from "./components/GameHistory";
import Results from "./components/Results";
import CategoryPage from "./components/Category";
import ScoreByCategory from "./components/CategoryResult";
import { GoogleOAuthProvider } from '@react-oauth/google';

import "./index.css";

const root = ReactDOM.createRoot(document.getElementById("root"));
const myID = Math.floor(Math.random() * 1000000);

root.render(
    <GoogleOAuthProvider clientId="545499290736-a0ejf7ipir9dctrp7i03a946vdgflsg3.apps.googleusercontent.com">
    <React.StrictMode>
        <Router>
            <Routes>
                <Route path="/" element={<Login />} />
                <Route path="/category" element={<CategoryPage />} />
                <Route path="/quiz" element={<Quiz />} />
                <Route path="/category-results" element={<ScoreByCategory />} />
                <Route path="/results" element={<Results />} />
                <Route path="/leaderboard" element={<Leaderboard />} />
                <Route path="/gamehistory" element={<GameHistory />} />
            </Routes>
        </Router>
    </React.StrictMode>
    </GoogleOAuthProvider>
);
