// src/components/Login.js
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
        return data; // Return the API response
    } catch (error) {
        console.log('Error:', error);
        return { error: "An error occurred while submitting the answer." };
    }
};

const Login = () => {
    const [name, setName] = useState("");
    const [email, setEmail] = useState("");
    const navigate = useNavigate();

    const handleError = () => {
        console.log('Login Failed');
        // Handle login error
    };

    const handleSuccess = async (credentialResponse) => {
        // Store user info in localStorage or state management
        const decoded = jwtDecode(credentialResponse.credential);
        const email = decoded.email;
        const userId = decoded.sub;
        console.log('Login Success:', name, email, userId);
        localStorage.setItem('userName', name);
        localStorage.setItem('id', userId);
        const response = await sendLogin(userId, name);
        console.log('Response:', response);
        navigate("/quiz", { state: { maxQuestions : 5 }}); 
    };

    const handleSubmit = (e) => {
        // You can add validation here if needed
        // For now, we'll just call handleSuccess with a mock credentialResponse
        //handleSuccess({ clientId: 'mockClientId' });
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
                        <form className="space-y-6" onSubmit={handleSubmit}>
                            <input 
                                type="text" 
                                placeholder="Name" 
                                value={name} 
                                onChange={(e) => setName(e.target.value)} 
                                className="w-full p-4 text-xl border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                                required
                            />
                            {/* <input 
                                type="email" 
                                placeholder="Email" 
                                value={email} 
                                onChange={(e) => setEmail(e.target.value)} 
                                className="w-full p-4 text-xl border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                                required
                            /> */}
                            <GoogleLogin onSuccess={handleSuccess} onError={handleError} />
                            {/* <button 
                                type="submit"
                                className="w-full bg-blue-500 text-white py-4 text-xl rounded-md font-bold hover:bg-blue-600 transition"
                            >
                                Submit
                            </button> */}
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
