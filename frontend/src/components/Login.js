// Updated Login.js with Original Google Auth and Required Username
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import ParticlesBackground from './ParticlesBackground';
import { GoogleLogin } from '@react-oauth/google';
import { jwtDecode } from "jwt-decode";

const sendLogin = async (clientId, userName) => {
    try {
        console.log('Sending login request with username:', userName, 'and client ID:', clientId);
        const res = await fetch(`/ws/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ username: userName, client_id: clientId }),
        });
        const data = await res.json();
        console.log("Data:", data);
        return data;
    } catch (error) {
        console.log('Error:', error);
        return { error: "An error occurred while submitting the answer." };
    }
};

const Login = () => {
    const [name, setName] = useState("");
    const navigate = useNavigate();

    const handleError = () => {
        console.log('Login Failed');
    };

    const handleSuccess = async (credentialResponse) => {
        if (!name.trim()) {
            alert("Username is required to proceed.");
            return;
        }
        const decoded = jwtDecode(credentialResponse.credential);
        const userId = decoded.sub;
        console.log('Login Success:', name, userId);
        localStorage.setItem('userName', name);
        localStorage.setItem('id', userId);
        const response = await sendLogin(userId, name);
        console.log('Response:', response);
        navigate("/category"); // Redirect to Category Page before Quiz
    };

    return (
        <div className="relative min-h-screen">
            <ParticlesBackground />
            <div className="relative z-10 flex justify-center items-center min-h-screen p-8">
                <div className="flex flex-col md:flex-row w-full max-w-7xl bg-white rounded-lg shadow-xl overflow-hidden">
                    <div className="w-full md:w-1/2 bg-blue-500 text-white p-12 flex flex-col justify-center">
                        <h2 className="text-5xl font-bold mb-8">Rules</h2>
                        <p className="text-lg leading-relaxed">
                            Welcome to Triv! Here are some rules: <br></br>
                            1. You will get to pick how many Q's per category up to a total of 10. <br></br>
                            2. You will have a 30 second window to answer each question. <br></br>
                            3. Every 10 seconds, you will see a new hint (up to 3). <br></br>
                            4. You get more points for guessing correctly with less hints. <br></br>
                            5. You can only guess once!
                        </p>
                    </div>
                    <div className="w-full md:w-1/2 p-12 flex flex-col space-y-4">
                        <h2 className="text-4xl font-bold text-center mb-6">TRIVIA GAME</h2>
                        <input 
                            type="text" 
                            placeholder="Name (Required)" 
                            value={name} 
                            onChange={(e) => setName(e.target.value)} 
                            className="w-full p-3 text-lg border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
                            required
                        />
                        <GoogleLogin onSuccess={handleSuccess} onError={handleError} />
                        {/* <button 
                            onClick={() => navigate("/leaderboard")} 
                            className="w-full bg-orange-500 text-white py-3 text-lg rounded-md font-bold hover:bg-orange-600 transition"
                        >
                            Leaderboard
                        </button>
                        <button 
                            onClick={() => navigate("/category")} 
                            className="w-full bg-green-500 text-white py-3 text-lg rounded-md font-bold hover:bg-green-600 transition"
                        >
                            Categories
                        </button> */}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Login;