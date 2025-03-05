import { useNavigate } from "react-router-dom";
import { useState, useEffect } from "react";
import ParticlesBackground from './ParticlesBackground';
const getLeaderboard = async () => {
    try {
        const res = await fetch(`/ws/leaderboard/get_leaderboard`, {
            method: 'GET',
        });
        const data = await res.json();
        return data; // Return the API response
    } catch (error) {
        console.log('Error:', error);
        return { error: "An error occurred while submitting the answer." };
    }   
};
const Leaderboard = () => {
    const navigate = useNavigate();
    const [animatedPlayers, setAnimatedPlayers] = useState([])
    const [players, setPlayers] = useState([
        { name: "Player 1", score: 1500, email: "player1@example.com" },
        { name: "Player 2", score: 1200, email: "player2@example.com" },
        { name: "Player 3", score: 1000, email: "player3@example.com" },
        { name: "Player 4", score: 800, email: "player4@example.com" },
        { name: "Player 5", score: 600, email: "player5@example.com" },
    ]);
    const [loaded, setLoaded] = useState(false);
    // Actual data fetching from the API
    useEffect(() => {
        const fetchLeaderboard = async () => {
            const data = await getLeaderboard();
            if (!data.error) {
                console.log(data);
                setPlayers(
                    data.map((player, index) => ({
                        name: player.username,
                        score: player.score,
                        email: "user" + index + "@example.com"
                    }))
                );
                setLoaded(true);
            }
        };
        fetchLeaderboard();
        console.log(players);
    }, []);
    useEffect(() => {
        // Animate players one by one
        if (loaded) {
        const timer = setInterval(() => {
            if (animatedPlayers.length < players.length) {
                setAnimatedPlayers(prev => [...prev, players[prev.length]]);
            }
        }, 200); // Adjust timing as needed

        return () => clearInterval(timer);
    }
    }, [animatedPlayers.length,loaded]);
    return (
        <div className="relative min-h-screen">
            <ParticlesBackground />
            <div className="relative z-10 flex justify-center items-center min-h-screen p-4">
                <div className="w-full max-w-4xl bg-white rounded-lg shadow-xl overflow-hidden">
                    <div className="bg-blue-500 text-white p-6">
                        <h2 className="text-3xl font-bold text-center">Leaderboard</h2>
                    </div>
                    <div className="p-6">
                        <div className="space-y-4">
                            {animatedPlayers.map((player, index) => (
                                <div
                                    key={index}
                                    className="transform transition-all duration-500 translate-y-0 opacity-100"
                                    style={{
                                        animation: `slideIn 0.5s ease-out ${index * 0.2}s both`
                                    }}
                                >
                                    <div className="bg-gray-50 p-4 rounded-lg flex justify-between items-center">
                                        <div className="flex items-center space-x-4">
                                            <span className="text-2xl font-bold text-blue-500">#{index + 1}</span>
                                            <div>
                                                <p className="font-semibold">{player.name}</p>
                                                <p className="text-sm text-gray-500">{player.email}</p>
                                            </div>
                                        </div>
                                        <span className="text-xl font-bold text-blue-500">{player.score}</span>
                                    </div>
                                </div>
                            ))}
                        </div>
                        <button 
                            onClick={() => navigate("/")} 
                            className="w-full mt-6 bg-orange-500 text-white py-4 text-xl rounded-md font-bold hover:bg-orange-600 transition"
                        >
                            Back to Login
                        </button>
                    </div>
                </div>
            </div>
            <style jsx>{`
                @keyframes slideIn {
                    from {
                        opacity: 0;
                        transform: translateY(20px);
                    }
                    to {
                        opacity: 1;
                        transform: translateY(0);
                    }
                }
            `}</style>
        </div>
    );
};

export default Leaderboard; 