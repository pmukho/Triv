import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import ParticlesBackground from './ParticlesBackground';
import { useCallback } from 'react';

const myId = Math.floor(Math.random() * 100); // Placeholder for the client ID, ideally should be ip address or some unique identifier

const start_game = async () => {
    try {
        const res = await fetch('http://localhost:8001/api/start-game', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ client_id: myId }),// Add client_id to the request body, make actual value dynamic
        });
        const data = await res.json();
        return data; // Return the API response
    } catch (error) {
        console.error('Error:', error);
        return { error: "An error occurred while starting the game." };
    }
};

const request_hints = async (clientId) => {
    try {
        const res = await fetch('http://localhost:8001/api/request-hints', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ client_id: clientId }), // Use the clientId parameter
        });
        const data = await res.json();
        return data; // Return the API response
    } catch (error) {
        console.error('Error:', error);
        return { error: "An error occurred while requesting a hint." };
    }
}

const Quiz = () => {
    const navigate = useNavigate();
    const [timeLeft, setTimeLeft] = useState(30);
    const [answer, setAnswer] = useState('');
    const [showPanel1, setShowPanel1] = useState(false);
    const [Panel1, setPanel1] = useState('Not Loaded Yet');
    const [Panel2, setPanel2] = useState('Not Loaded Yet');
    const [Panel3, setPanel3] = useState('Not Loaded Yet');
    const [showPanel2, setShowPanel2] = useState(false);
    const [showPanel3, setShowPanel3] = useState(false);
    const [score, setScore] = useState(0);
    // Placeholder for question data
    const [currentQuestion, setCurrentQuestion] = useState({
        question: "Question 1",
        questionNumber: 1,  // Add this to track question number
        // Add other question properties as needed
    });
    const initGame = async () => {
        await start_game();
        const hintData = await request_hints(myId);
        console.log("got hint data");
        console.log(hintData);
        if (hintData.hints) {
            console.log("got hints and they are in if statement");
            console.log(hintData.hints);
            setPanel1(hintData.hints[0]);
            setPanel2(hintData.hints[1]);
            setPanel3(hintData.hints[2]);
        }
    };

    useEffect(() => {
        console.log("Init game being called");
        initGame();
    }, [currentQuestion]);

    useEffect(() => {
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

    const handleSubmit = async (e) => {
        console.log("Submit button clicked, sending answer to server:");
        console.log(answer);
        e.preventDefault();
        // Submit answer to the server
        const res = await fetch('http://localhost:8001/api/submit-answer', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ client_id: myId, answer: answer }), // Add client_id and answer to the request body
        });
        const data = await res.json();
        console.log(data);
        // Update score based on the response
        setScore(data.score);
        handleNextQuestion();
    };

    const handleNextQuestion = () => {
        // Reset state for next question
        setTimeLeft(30);
        setAnswer('');
        setShowPanel1(false);
        setShowPanel2(false);
        setShowPanel3(false);
        initGame(); // Fetch new hints for the next question
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
                                <span className="text-4xl">{Panel1}</span>
                            </div>
                        </div>
                        <div className={`transform transition-all duration-500 ${
                            showPanel2 ? 'translate-x-0 opacity-100' : '-translate-x-full opacity-0'
                        }`}>
                            <div className="bg-yellow-300 rounded-lg p-8 w-full h-32 flex items-center justify-center shadow-lg">
                                <span className="text-4xl">{Panel2}</span>
                            </div>
                        </div>
                        <div className={`transform transition-all duration-500 ${
                            showPanel3 ? 'translate-x-0 opacity-100' : '-translate-x-full opacity-0'
                        }`}>
                            <div className="bg-yellow-300 rounded-lg p-8 w-full h-32 flex items-center justify-center shadow-lg">
                                <span className="text-4xl">{Panel3}</span>
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
                            {/* Added to show the score */}
                            <div className="bg-white rounded-lg p-8 w-full h-32 flex items-center justify-center shadow-lg">
                                <span className="text-4xl">Score is: {score}</span>
                            </div>
                        </form>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Quiz; 