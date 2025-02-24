import { useState, useEffect, useRef, useCallback } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import ParticlesBackground from './ParticlesBackground';

const myId = Math.floor(Math.random() * 100);
const DEFAULT_PANELS = {
  1: { content: '', visible: false },
  2: { content: '', visible: false },
  3: { content: '', visible: false }
};

const HintPanels = ({ panels }) => {
  return (
    <>
      {Object.keys(panels).map((panelKey) => (
        <div key={panelKey} className={`transform transition-all duration-500 ${panels[panelKey].visible? 'translate-x-0 opacity-100' : '-translate-x-full opacity-0' }`}>
          <div className="bg-yellow-300 rounded-lg p-4 w-full h-24 flex items-center justify-center shadow-lg">
            <span className="text-2xl">{panels[panelKey].content}</span>
          </div>
        </div>
      ))}
    </>
  );
};

const Quiz = () => {
  const navigate = useNavigate();
  const location = useLocation();

  const wsRef = useRef(null);

  const [timeLeft, setTimeLeft] = useState(30);
  const [answer, setAnswer] = useState('');
  const [panels, setPanels] = useState(DEFAULT_PANELS);
  const [score, setScore] = useState(0);

  const maxQuestions = location.state?.maxQuestions || 5;
  const [currentQuestion, setCurrentQuestion] = useState({
    question: 'Question 1',
    questionNumber: 1,
  });

  // Send a message over WebSocket
  const sendMessage = useCallback((type, payload) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ type, payload }));
    }
  }, []);

  // Update panels with a new hint
  const handleNewHint = useCallback((hint) => {
    setPanels((prev) => {
      const nextPanelKey =
        Object.entries(prev).find(([_, panel]) => !panel.visible)?.[0] || '1';
      return {
        ...prev,
        [nextPanelKey]: { content: hint, visible: true },
      };
    });
  }, []);

  // Handle answer results from the server
  const handleAnswerResult = useCallback((isCorrect, rawScore) => {
    const newScore = rawScore * 10;
    setScore(newScore);
    localStorage.setItem('score', newScore);
    handleNextQuestion();
  }, []);

  // Dispatch server messages based on type
  const handleServerMessage = useCallback(
    (message) => {
      switch (message.type) {
        case 'hint':
          handleNewHint(message.hint);
          break;
        case 'answer_result':
          handleAnswerResult(message.correct, message.score);
          break;
        case 'game_status':
          console.log('Game status:', message.status);
          break;
        default:
          break;
      }
    },
    [handleNewHint, handleAnswerResult]
  );

  // WebSocket connection management
  useEffect(() => {
    const wsUrl = `ws://localhost/ws/quiz/${myId}?${maxQuestions}`;
    const ws = new WebSocket(wsUrl);
    wsRef.current = ws;

    ws.onopen = () => {
      console.log('WebSocket connected');
      sendMessage('start_question', {});
    };

    ws.onmessage = (event) => {
      try {
        const message = JSON.parse(event.data);
        handleServerMessage(message);
      } catch (error) {
        console.error('Failed to parse message:', error);
      }
    };

    ws.onerror = (error) => console.error('WebSocket error:', error);

    return () => {
      sendMessage('end_game', {});
      ws.close();
    };
  }, [handleServerMessage, sendMessage]);

  // Timer management
  useEffect(() => {
    if (timeLeft <= 0) {
      sendMessage('start_question', {});
      handleNextQuestion();
      return;
    }
    const timerId = setTimeout(() => setTimeLeft((prev) => prev - 1), 1000);
    return () => clearTimeout(timerId);
  }, [timeLeft]);

  // Move to the next question or navigate to results if done
  const handleNextQuestion = useCallback(() => {
    setCurrentQuestion((prev) => {
      const nextNumber = prev.questionNumber + 1;
      if (nextNumber > maxQuestions) {
        navigate('/results');
        return prev; // Returning prev since we don't need to update state further
      }
      return {
        ...prev,
        questionNumber: nextNumber,
        question: `Question ${nextNumber}`,
      };
    });
    setTimeLeft(30);
    setPanels(DEFAULT_PANELS);
  }, [navigate]);
  

  // Handle answer form submission
  const handleSubmit = (e) => {
    e.preventDefault();
    sendMessage('submit_answer', { answer });
    setAnswer('');
  };


  return (
    <div className="relative min-h-screen w-full">
      <ParticlesBackground />
      <div className="relative z-10 flex min-h-screen w-full">
        {/* Left Half: Question and Hints */}
        <div className="w-1/2 p-8 flex flex-col">
          <div className="bg-white rounded-lg p-8 mb-8 shadow-xl">
            <h2 className="text-4xl font-bold text-center">
              {currentQuestion.question}
            </h2>
          </div>
          <div className="flex flex-col space-y-4">
            <HintPanels panels={panels}/>
          </div>
        </div>
        {/* Right Half */}
        <div className="w-1/2 p-8 flex flex-col">
            {/* Timer Section */}
            <div className="bg-white rounded-lg p-8 mb-8 shadow-xl">
                <div className="text-8xl font-bold text-center text-blue-500">{timeLeft}</div>
            </div>

            {/* Answer Section */}
            <div className="bg-white rounded-lg p-8 shadow-xl mb-8">
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

            {/* Score Section */}
            <div className="bg-white rounded-lg p-6 shadow-xl">
                <div className="text-4xl font-bold text-center text-blue-500">Score: {score}</div>
            </div>
        </div>
    </div>
</div>
    );
};

export default Quiz; 