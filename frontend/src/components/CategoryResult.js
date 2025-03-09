import { useNavigate } from "react-router-dom";
import ParticlesBackground from "./ParticlesBackground";

const categories = [
    "Geography",
    "History",
    "Society/Social Sciences",
    "Mathematics",
    "Philosophy/Religion",
    "Physical Sciences",
    "Technology",
    "Biology/Health Sciences",
    "Arts",
    "People"
];

const ScoreByCategory = () => {
    const navigate = useNavigate();

    // Mock data 
    const categoryStats = categories.map(category => ({
        category,
        avgAccuracy: (Math.random() * 100).toFixed(2),
        avgScore: Math.floor(Math.random() * 10)
    }));

    return (
        <div className="relative min-h-screen flex justify-center items-center">
            <ParticlesBackground />
            <div className="relative z-10 flex flex-col items-center w-full max-w-5xl bg-white p-6 rounded-lg shadow-xl">
                {/* Header */}
                <div className="w-full bg-blue-500 text-white p-4 rounded-lg text-center mb-4">
                    <h2 className="text-3xl font-bold mb-2">Score By Category</h2>
                    <p className="text-md">See your performance across different categories.</p>
                </div>
                {/* Stats Section */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 w-full">
                    {categoryStats.map(({ category, avgAccuracy, avgScore }, index) => (
                        <div key={index} className="mb-2 p-4 border border-gray-300 rounded-lg">
                            <h3 className="text-lg font-semibold">{category}</h3>
                            <p className="text-sm text-gray-600">Avg Accuracy: {avgAccuracy}% | Avg Score: {avgScore}</p>
                        </div>
                    ))}
                </div>
                {/* Try Again Button */}
                <div className="w-full flex justify-center mt-4">
                <button
                onClick={() => navigate("/results")}
                className="w-1/3 bg-blue-500 text-white py-2 rounded-md font-bold hover:bg-blue-600 transition"
                >
                 Continue to Results
                </button>
                </div>
            </div>
        </div>
    );
};

export default ScoreByCategory;
