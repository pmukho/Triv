// Updated Login.js
import { useGoogleLogin } from '@react-oauth/google';
import { useNavigate } from 'react-router-dom';
import ParticlesBackground from './ParticlesBackground';
import { useState } from 'react';

const Login = () => {
    const navigate = useNavigate();
    const [name, setName] = useState("");

    const handleSuccess = async (tokenResponse) => {
        console.log("Google Login Success:", tokenResponse);
        navigate('/quiz', { state: { maxQuestions: 5 } });
    };

    const login = useGoogleLogin({
        onSuccess: handleSuccess,
        onError: () => console.log('Login Failed'),
    });

    return (
        <div className="relative min-h-screen">
            <ParticlesBackground />
            <div className="relative z-10 flex justify-center items-center min-h-screen p-8">
                <div className="flex flex-col md:flex-row w-full max-w-7xl bg-white rounded-lg shadow-xl overflow-hidden">
                    <div className="w-full md:w-1/2 bg-blue-500 text-white p-12 flex flex-col justify-center">
                        <h2 className="text-5xl font-bold mb-8">Rules</h2>
                        <p className="text-lg leading-relaxed">
                            Lorem ipsum dolor sit amet, consectetur adipiscing elit.
                        </p>
                    </div>
                    <div className="w-full md:w-1/2 p-12 flex flex-col space-y-4">
                        <h2 className="text-4xl font-bold text-center mb-6">TRIVIA GAME</h2>
                        <input 
                            type="text" 
                            placeholder="Name" 
                            value={name} 
                            onChange={(e) => setName(e.target.value)} 
                            className="w-full p-3 text-lg border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
                            required
                        />
                        <button 
                            onClick={() => login()} 
                            className="w-full bg-[#4285F4] text-white py-3 text-lg rounded-md font-bold hover:bg-blue-700 transition flex justify-center items-center"
                        >
                            <img
                                src="https://upload.wikimedia.org/wikipedia/commons/thumb/5/53/Google_%22G%22_Logo.svg/512px-Google_%22G%22_Logo.svg.png"
                                alt="Google Logo"
                                className="w-6 h-6 mr-2"
                            />
                            Sign in with Google
                        </button>
                        <button 
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
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Login;