// src/components/Login.js
import { useState } from "react";
import { useNavigate } from "react-router-dom";

const Login = () => {
    const [name, setName] = useState("");
    const [email, setEmail] = useState("");
    const navigate = useNavigate();

    const handleSubmit = (e) => {
        e.preventDefault();
        navigate("/leaderboard");
    };

    return (
        <div className="flex justify-center items-center min-h-screen bg-gray-200 p-4">
            <div className="flex flex-col md:flex-row w-full max-w-4xl bg-white rounded-lg shadow-lg overflow-hidden">
                <div className="w-full md:w-1/2 bg-blue-500 text-white p-8 flex flex-col justify-center">
                    <h2 className="text-3xl font-bold mb-4">Rules</h2>
                    <p className="text-sm">
                        Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec sit amet lacus viverra.
                    </p>
                </div>
                <div className="w-full md:w-1/2 p-8">
                    <h2 className="text-2xl font-bold text-center mb-6">TRIVIA GAME</h2>
                    <form onSubmit={handleSubmit} className="space-y-4">
                        <input 
                            type="text" 
                            placeholder="Name" 
                            value={name} 
                            onChange={(e) => setName(e.target.value)} 
                            className="w-full p-3 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500" 
                            required
                        />
                        <input 
                            type="email" 
                            placeholder="Email" 
                            value={email} 
                            onChange={(e) => setEmail(e.target.value)} 
                            className="w-full p-3 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500" 
                            required
                        />
                        <button 
                            type="submit" 
                            className="w-full bg-blue-500 text-white py-3 rounded-md font-bold hover:bg-blue-600 transition"
                        >
                            Login
                        </button>
                    </form>
                    <button 
                        onClick={() => navigate("/leaderboard")} 
                        className="w-full mt-4 bg-orange-500 text-white py-3 rounded-md font-bold hover:bg-orange-600 transition"
                    >
                        Leaderboard
                    </button>
                </div>
            </div>
        </div>
    );
};

export default Login;
