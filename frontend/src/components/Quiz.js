import { useState, useEffect, useRef, useCallback } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import ParticlesBackground from './ParticlesBackground';

const DEFAULT_PANELS = {
  1: { content: 'Loading...', visible: true },
  2: { content: 'Loading...', visible: false },
  3: { content: 'Loading...', visible: false }
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
  const [loadingHints, setLoadingHints] = useState(true);
  const [score, setScore] = useState(0);
  const [hintCount, setHintCount] = useState(0);

  const maxQuestions = location.state?.maxQuestions || 10;
  const [currentQuestion, setCurrentQuestion] = useState({
    question: 'Question 1',
    questionNumber: 1,
  });

  // Post Question Logic
  const [answerRevealed, setAnswerRevealed] = useState(false); // toggles once we get the server's result
  const [correctAnswer, setCorrectAnswer] = useState('');       // store the correct answer
  const [postAnswerTimeLeft, setPostAnswerTimeLeft] = useState(0); // 5-second countdown after reveal


  // Send a message over WebSocket
  const sendMessage = useCallback((type, payload) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ type, payload }));
    }
  }, []);

  // Update panels with a new hint
  const handleNewHint = useCallback((hint) => {
    setHintCount((prev) => prev + 1);
    setPanels((prev) => {
      const placeholderEntry = Object.entries(prev).find(
        ([, panel]) => panel.content === 'Loading...'
      );

      if (placeholderEntry) {
        const [placeholderKey] = placeholderEntry;
        return {
          ...prev,
          [placeholderKey]: { content: hint, visible: true },
        };
      } else {
        const nextPanelKey =
          Object.entries(prev).find(([_, panel]) => !panel.visible)?.[0] || '1';
        return {
          ...prev,
          [nextPanelKey]: { content: hint, visible: true },
        };
      }
    });
  }, []);
  

  // Handle answer results from the server
  const handleAnswerResult = useCallback((isCorrect, rawScore, correctAns, questionHints) => {
    const newScore = rawScore;
    setScore(newScore);
    localStorage.setItem('score', newScore);
    // Reveal hints
    setPanels(DEFAULT_PANELS);
    setPanels((prev) => {
      const newPanels = { ...prev };
      questionHints.forEach((hint, idx) => {
        const panelKey = String(idx + 1);
        newPanels[panelKey] = { content: hint, visible: true };
      });
      return newPanels;
    });

    setAnswerRevealed(true);
    setCorrectAnswer(correctAns || 'Unknown');
    setPostAnswerTimeLeft(3);
  }, []);

  // Dispatch server messages based on type
  const handleServerMessage = useCallback(
    (message) => {
      switch (message.type) {
        case 'hint':
          if (loadingHints) setLoadingHints(false);
          handleNewHint(message.hint);
          break;
        case 'answer_result':
          handleAnswerResult(message.correct, message.score, message.answer, message.hints);
          break;
        case 'game_status':
          console.log('Game status:', message.status);
          break;
        default:
          break;
      }
    },
    [handleNewHint, handleAnswerResult, loadingHints]
  );

  // WebSocket connection management
  useEffect(() => {
    const id = localStorage.getItem('id');
    const categoryDist = localStorage.getItem('categorySelection');
    const wsUrl = `/ws/quiz/${id}?maxQuestions=${maxQuestions}`;
    const ws = new WebSocket(wsUrl);
    wsRef.current = ws;

    ws.onopen = () => {
      console.log('WebSocket connected4');
      console.log(categoryDist)
      sendMessage('start_question', JSON.parse(categoryDist));
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
  }, []);

  // Timer management
  useEffect(() => {
    if (loadingHints || postAnswerTimeLeft > 0) return;

    // If user time is up but not revealed, automatically submit blank
    if (timeLeft <= 0 && !answerRevealed) {
      sendMessage('submit_answer', {"answer": answer, "hintCount": hintCount});
      return;
    }

    if (timeLeft > 0 && !answerRevealed) {
      const timerId = setTimeout(() => setTimeLeft((prev) => prev - 1), 1000);
      return () => clearTimeout(timerId);
    }
  }, [timeLeft, answerRevealed, postAnswerTimeLeft, loadingHints, sendMessage]);

  // Post question timer
  useEffect(() => {
    if (!answerRevealed) return; // not in post-answer phase

    if (postAnswerTimeLeft <= 0 && answerRevealed) {
      handleNextQuestion();
      return;
    }
    if (postAnswerTimeLeft > 0) {
      const timerId = setTimeout(
        () => setPostAnswerTimeLeft((prev) => prev - 1),
        1000
      );
      return () => clearTimeout(timerId);
    }
  }, [postAnswerTimeLeft, answerRevealed]);

  // Move to the next question or navigate to results if done
  const handleNextQuestion = useCallback(() => {
    setAnswer('');
    setHintCount(0);

    setAnswerRevealed(false);
    setCorrectAnswer('');
    setPostAnswerTimeLeft(0);
    setLoadingHints(true);

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
    
    // Get category selection from localStorage
    const categoryDist = localStorage.getItem('categorySelection');
    sendMessage('start_question', JSON.parse(categoryDist));
  }, [navigate, sendMessage, setHintCount]);
  

  // Handle answer form submission
  const handleSubmit = (e) => {
    e.preventDefault();
    sendMessage('submit_answer', {"answer": answer, "hintCount": hintCount});
  };

  // Downvote question
  const handleDownvote = () => {
    
    sendMessage('downvote_question', {});
    console.log('Downvoted question');
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
            <HintPanels panels={panels} loading={loadingHints}/>
          </div>
        </div>
        {/* Right Half */}
        <div className="w-1/2 p-8 flex flex-col">
            {/* Timer Section */}
            {!answerRevealed && (
            <div className="bg-white rounded-lg p-8 mb-8 shadow-xl">
              <div className="text-8xl font-bold text-center text-blue-500">
                {timeLeft}
              </div>
            </div>
          )}
          {answerRevealed && (
            <div className="bg-white rounded-lg p-8 mb-8 shadow-xl space-y-4">
              <h3 className="text-2xl font-bold text-center">Your Answer:</h3>
              <div className="text-xl text-center text-black-600">
                {answer || "No answer provided"}
              </div>
              <h3 className="text-2xl font-bold text-center">Correct Answer:</h3>
              <div className="text-xl text-center text-green-600">
                {correctAnswer}
              </div>
              <button
                onClick={handleDownvote}
                className="w-full bg-red-500 text-white py-4 text-xl rounded-md font-bold hover:bg-red-600 transition"
              >
                Downvote
              </button>
              <div className="text-xl text-center text-gray-600">
                Moving to next question in {postAnswerTimeLeft}...
              </div>
            </div>
          )}
            {/* Answer Section */}
            {!answerRevealed && (
              <div className="bg-white rounded-lg p-8 shadow-xl mb-8">
                <form onSubmit={handleSubmit} className="space-y-6">
                  <input
                    type="text"
                    value={answer}
                    onChange={(e) => setAnswer(e.target.value)}
                    placeholder="Type Your Answer here"
                    className="w-full p-4 text-xl border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    disabled={loadingHints}
                  />
                  <button
                    type="submit"
                    className="w-full bg-blue-500 text-white py-4 text-xl rounded-md font-bold hover:bg-blue-600 transition"
                    disabled={loadingHints}
                  >
                    Submit
                  </button>
                </form>
              </div>
            )}
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