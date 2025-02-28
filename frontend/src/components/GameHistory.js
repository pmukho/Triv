import { useState } from "react";
import { useNavigate } from "react-router-dom";
import ParticlesBackground from './ParticlesBackground';

const GameHistory = () => {
    const [userInput, setUserInput] = useState("");
    const [response, setResponse] = useState("");
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            const res = await fetch('http://localhost:8000/api/user-input', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ userInput }),
            });
            const data = await res.json();
            setResponse(data.message);
        } catch (error) {
            console.error('Error:', error);
            setResponse("An error occurred while processing your request.");
        }
    };

    return (
        <div className="relative min-h-screen">
            <ParticlesBackground />
            <div className="relative z-10 flex justify-center items-center min-h-screen p-8">
                <div className="flex flex-col md:flex-row w-full max-w-7xl bg-white rounded-lg shadow-xl overflow-hidden">
                    <div className="w-full md:w-1/2 bg-blue-500 text-white p-12 flex flex-col justify-center">
                        <h2 className="text-5xl font-bold mb-8">User Input Test</h2>
                        <p className="text-lg leading-relaxed">
                            Enter some text in the input field and submit to see the response from the server.
                        </p>
                    </div>
                    <div className="w-full md:w-1/2 p-12">
                        <h2 className="text-4xl font-bold text-center mb-10">TEST FORM</h2>
                        <form onSubmit={handleSubmit} className="space-y-6">
                            <input 
                                type="text" 
                                placeholder="Enter your text here" 
                                value={userInput} 
                                onChange={(e) => setUserInput(e.target.value)} 
                                className="w-full p-4 text-xl border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                                required
                            />
                            <button 
                                type="submit" 
                                className="w-full bg-blue-500 text-white py-4 text-xl rounded-md font-bold hover:bg-blue-600 transition"
                            >
                                Submit
                            </button>
                        </form>
                        {response && (
                            <div className="mt-6 p-4 bg-gray-100 rounded-md">
                                <h3 className="text-xl font-bold mb-2">Server Response:</h3>
                                <p>{response}</p>
                            </div>
                        )}
                        <button 
                            onClick={() => navigate("/")} 
                            className="w-full mt-6 bg-orange-500 text-white py-4 text-xl rounded-md font-bold hover:bg-orange-600 transition"
                        >
                            Back to Login
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default GameHistory;
