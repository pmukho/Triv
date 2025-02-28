// src/components/Login.js
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import ParticlesBackground from './ParticlesBackground';

const Login = () => {
    const [name, setName] = useState("");
    const [email, setEmail] = useState("");
    const navigate = useNavigate();

    const handleSubmit = (e) => {
        e.preventDefault();
        // You can add validation here if needed
        // Store user info in localStorage or state management
        localStorage.setItem('userName', name);
        localStorage.setItem('userEmail', email);
        navigate("/quiz", { state: { maxQuestions : 5 }}); // Navigate to quiz instead of leaderboard
    };

    return (
        <div className="relative min-h-screen">
            <ParticlesBackground />
            <div className="relative z-10 flex justify-center items-center min-h-screen p-8">
                <div className="flex flex-col md:flex-row w-full max-w-7xl bg-white rounded-lg shadow-xl overflow-hidden">
                    <div className="w-full md:w-1/2 bg-blue-500 text-white p-12 flex flex-col justify-center">
                        <h2 className="text-5xl font-bold mb-8">Rules</h2>
                        <p className="text-lg leading-relaxed">
                            Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec sit amet lacus viverra.
                        </p>
                    </div>
                    <div className="w-full md:w-1/2 p-12">
                        <h2 className="text-4xl font-bold text-center mb-10">TRIVIA GAME</h2>
                        <form onSubmit={handleSubmit} className="space-y-6">
                            <input 
                                type="text" 
                                placeholder="Name" 
                                value={name} 
                                onChange={(e) => setName(e.target.value)} 
                                className="w-full p-4 text-xl border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                                required
                            />
                            <input 
                                type="email" 
                                placeholder="Email" 
                                value={email} 
                                onChange={(e) => setEmail(e.target.value)} 
                                className="w-full p-4 text-xl border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                                required
                            />
                            <button 
                                type="submit" 
                                className="w-full bg-blue-500 text-white py-4 text-xl rounded-md font-bold hover:bg-blue-600 transition"
                            >
                                Start Quiz
                            </button>
                        </form>
                        <button 
                            onClick={() => navigate("/leaderboard")} 
                            className="w-full mt-6 bg-orange-500 text-white py-4 text-xl rounded-md font-bold hover:bg-orange-600 transition"
                        >
                            Leaderboard
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Login;


