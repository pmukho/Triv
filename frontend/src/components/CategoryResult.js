import { useNavigate } from "react-router-dom";
import ParticlesBackground from "./ParticlesBackground";
import { useState, useEffect } from "react";
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
const DEFAULT_ACCURACY = 0.0;
const DEFAULT_AVG_HINTS = 0.0;

const getCategoryStats = async () => {
    try {
        const res = await fetch(`/ws/category-stats/${localStorage.getItem("id")}`, {
            method: 'GET',
        });
        const data = await res.json();
        return data;
    } catch (error) {
        console.log('Error:', error);
        return { error: "An error occurred while fetching" };
    }
};

const ScoreByCategory = () => {
    const navigate = useNavigate();
    const [stats, setStats] = useState([]);

    useEffect(() => {
        const fetchCategoryStats = async () => {
            const data = await getCategoryStats();
            
            if (!data.error) {
                console.log(data);
                const proc_data = categories.map((category) => {
                    if (!data[category]) {
                        return {
                            category,
                            accuracy: DEFAULT_ACCURACY,
                            avgHints: DEFAULT_AVG_HINTS
                        };
                    }
                    
                    const { accuracy, avg_hints_used } = data[category];
                    
                    return {
                        category,
                        accuracy: accuracy !== undefined ? accuracy : DEFAULT_ACCURACY,
                        avgHints: avg_hints_used !== undefined ? avg_hints_used : DEFAULT_AVG_HINTS
                    };
                });

                console.log(proc_data);
                setStats(proc_data);
            }
        }
        fetchCategoryStats();
        console.log(stats);
    }, []);

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
                    {stats.map(({ category, accuracy, avgHints }, index) => (
                        <div key={index} className="mb-2 p-4 border border-gray-300 rounded-lg">
                            <h3 className="text-lg font-semibold">{category}</h3>
                            <p className="text-sm text-gray-600">Accuracy: {(accuracy*100).toFixed(2)}% | Avg. Hints Used: {avgHints !== undefined ? avgHints.toFixed(2) : "N/A"}</p>
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
