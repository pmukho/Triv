import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import ParticlesBackground from './ParticlesBackground';

const Quiz = () => {
    const navigate = useNavigate();
    const [timeLeft, setTimeLeft] = useState(30);
    const [answer, setAnswer] = useState('');
    const [showPanel1, setShowPanel1] = useState(false);
    const [showPanel2, setShowPanel2] = useState(false);
    const [showPanel3, setShowPanel3] = useState(false);
    
    // Placeholder for question data
    const [currentQuestion, setCurrentQuestion] = useState({
        question: "Question 1",
        questionNumber: 1,  // Add this to track question number
        // Add other question properties as needed
    });

    useEffect(() => {
        // Show first panel immediately
        setShowPanel1(true);

        // Show second panel after 10 seconds
        const timer2 = setTimeout(() => {
            setShowPanel2(true);
        }, 10000);

        // Show third panel after 20 seconds
        const timer3 = setTimeout(() => {
            setShowPanel3(true);
        }, 20000);

        return () => {
            clearTimeout(timer2);
            clearTimeout(timer3);
        };
    }, [currentQuestion]); // Reset panels when question changes

    // Timer countdown effect
    useEffect(() => {
        if (timeLeft > 0) {
            const timer = setTimeout(() => {
                setTimeLeft(timeLeft - 1);
            }, 1000);

            return () => clearTimeout(timer);
        } else {
            // Move to next question when timer reaches 0
            handleNextQuestion();
        }
    }, [timeLeft]);

    const handleSubmit = (e) => {
        e.preventDefault();
        handleNextQuestion();
    };

    const handleNextQuestion = () => {
        // Reset state for next question
        setTimeLeft(30);
        setAnswer('');
        setShowPanel1(false);
        setShowPanel2(false);
        setShowPanel3(false);
        // Update to next sequential question
        setCurrentQuestion(prev => ({
            ...prev,
            questionNumber: prev.questionNumber + 1,
            question: `Question ${prev.questionNumber + 1}`
        }));
    };

    return (
        <div className="relative min-h-screen w-full">
            <ParticlesBackground />
            <div className="relative z-10 flex min-h-screen w-full">
                {/* Left Half */}
                <div className="w-1/2 p-8 flex flex-col">
                    {/* Question Section */}
                    <div className="bg-white rounded-lg p-8 mb-8 shadow-xl">
                        <h2 className="text-4xl font-bold text-center">{currentQuestion.question}</h2>
                    </div>

                    {/* Panels Section */}
                    <div className="flex flex-col space-y-6">
                        <div className={`transform transition-all duration-500 ${
                            showPanel1 ? 'translate-x-0 opacity-100' : '-translate-x-full opacity-0'
                        }`}>
                            <div className="bg-yellow-300 rounded-lg p-8 w-full h-32 flex items-center justify-center shadow-lg">
                                <span className="text-4xl">Panel 1</span>
                            </div>
                        </div>
                        <div className={`transform transition-all duration-500 ${
                            showPanel2 ? 'translate-x-0 opacity-100' : '-translate-x-full opacity-0'
                        }`}>
                            <div className="bg-yellow-300 rounded-lg p-8 w-full h-32 flex items-center justify-center shadow-lg">
                                <span className="text-4xl">Panel 2</span>
                            </div>
                        </div>
                        <div className={`transform transition-all duration-500 ${
                            showPanel3 ? 'translate-x-0 opacity-100' : '-translate-x-full opacity-0'
                        }`}>
                            <div className="bg-yellow-300 rounded-lg p-8 w-full h-32 flex items-center justify-center shadow-lg">
                                <span className="text-4xl">Panel 3</span>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Right Half */}
                <div className="w-1/2 p-8 flex flex-col">
                    {/* Timer Section */}
                    <div className="bg-white rounded-lg p-8 mb-8 shadow-xl">
                        <div className="text-8xl font-bold text-center text-blue-500">{timeLeft}</div>
                    </div>

                    {/* Answer Section */}
                    <div className="bg-white rounded-lg p-8 shadow-xl">
                        <form onSubmit={handleSubmit} className="space-y-6">
                            <input
                                type="text"
                                value={answer}
                                onChange={(e) => setAnswer(e.target.value)}
                                placeholder="Type Your Answer here"
                                className="w-full p-4 text-xl border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                            />
                            <button
                                type="submit"
                                className="w-full bg-blue-500 text-white py-4 text-xl rounded-md font-bold hover:bg-blue-600 transition"
                            >
                                Submit
                            </button>
                        </form>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Quiz; 