import { useNavigate } from "react-router-dom";
import ParticlesBackground from './ParticlesBackground';
import Confetti from 'react-confetti';
import { useEffect, useState } from 'react';

const Results = () => {
    const navigate = useNavigate();
    const [windowDimension, setWindowDimension] = useState({
        width: window.innerWidth,
        height: window.innerHeight
    });
    const score = localStorage.getItem('score') || 0;

    const detectSize = () => {
        setWindowDimension({
            width: window.innerWidth,
            height: window.innerHeight
        });
    };

    useEffect(() => {
        window.addEventListener('resize', detectSize);
        return () => {
            window.removeEventListener('resize', detectSize);
        };
    }, []);

    return (
        <div className="relative min-h-screen">
            <ParticlesBackground />
            <Confetti
                width={windowDimension.width}
                height={windowDimension.height}
                numberOfPieces={1000}
                gravity={0.3}
                colors={['#FFD700', '#FFA500', '#FF6347', '#4169E1', '#32CD32']}
            />
            <div className="relative z-10 flex justify-center items-center min-h-screen p-4">
                <div className="bg-white rounded-xl shadow-2xl p-8 max-w-md w-full mx-4">
                    <div className="text-center">
                        <h1 className="text-4xl font-bold text-blue-600 mb-4">Quiz Complete!</h1>
                        <div className="text-7xl font-bold text-blue-500 mb-8 animate-bounce">
                            {score}
                        </div>
                        <p className="text-xl text-gray-600 mb-8">Congratulations on completing the quiz!</p>
                        <div className="space-y-4">
                            <button 
                                onClick={() => navigate("/quiz")}
                                className="w-full bg-blue-500 text-white py-4 text-xl rounded-lg font-bold hover:bg-blue-600 transition-colors duration-300"
                            >
                                Try Again
                            </button>
                            <button 
                            onClick={() => navigate("/category-results")}
                            className="w-full bg-green-500 text-white py-4 text-xl rounded-lg font-bold hover:bg-green-600 transition-colors duration-300"
                            >
                            View Category Results
                            </button>
                            {/* <button 
                                onClick={() => navigate("/gamehistory")}
                                className="w-full bg-orange-500 text-white py-4 text-xl rounded-lg font-bold hover:bg-orange-600 transition-colors duration-300"
                            >
                                Check Your Game History
                            </button> */}
                            <button 
                            onClick={() => navigate("/leaderboard")}
                            className="w-full bg-purple-500 text-white py-4 text-xl rounded-lg font-bold hover:bg-purple-600 transition-colors duration-300"
                            >
                            View Leaderboard
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Results; 