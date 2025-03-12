import { useState } from "react";
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

const CategoryPage = () => {
    const navigate = useNavigate();
    const [values, setValues] = useState(Array(10).fill(1));
    const maxTotal = 10;

    const handleSliderChange = (index, newValue) => {
        let total = values.reduce((sum, val) => sum + val, 0);
        let diff = newValue - values[index];
        
        if (total + diff > maxTotal) return; // Prevent exceeding maxTotal

        let newValues = [...values];
        newValues[index] = newValue;
        setValues(newValues);
    };

    const handleSubmit = () => {
        const categorySelection = categories.reduce((acc, category, index) => {
            acc[category] = values[index];
            return acc;
        }, {});
    
        localStorage.setItem("categorySelection", JSON.stringify(categorySelection)); // Store values in localStorage
        navigate("/quiz"); // Redirect to Quiz Page instead of Login
    };

    const handleReset = () => {
        setValues(Array(10).fill(0)); // Reset all sliders to 0
    };

    return (
        <div className="relative min-h-screen flex justify-center items-center">
            <ParticlesBackground />
            <div className="relative z-10 flex flex-col items-center w-full max-w-5xl bg-white p-6 rounded-lg shadow-xl">
                {/* Combined Header and Sliders Container */}
                <div className="w-full bg-blue-500 text-white p-4 rounded-lg text-center mb-4">
                    <h2 className="text-3xl font-bold mb-2">Select Categories</h2>
                    <p className="text-md">Adjust the sliders to choose how many questions per category. (Total: {values.reduce((a, b) => a + b, 0)}/{maxTotal})</p>
                </div>
                {/* Sliders Section - Split into Two Columns */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 w-full">
                    {categories.map((category, index) => (
                        <div key={index} className="mb-2">
                            <label className="block font-semibold text-md mb-1">{category}</label>
                            <input
                                type="range"
                                min="0"
                                max={maxTotal}
                                value={values[index]}
                                onChange={(e) => handleSliderChange(index, Number(e.target.value))}
                                className="w-full cursor-pointer"
                            />
                            <p className="text-xs text-gray-600">Selected: {values[index]}</p>
                        </div>
                    ))}
                </div>
                
                {/* Buttons Centered at the Bottom */}
                <div className="w-full flex justify-center mt-4 gap-4">
                    <button
                        onClick={handleReset}
                        className="w-1/3 bg-gray-500 text-white py-2 rounded-md font-bold hover:bg-gray-600 transition"
                    >
                        Reset All
                    </button>
                    <button
                        onClick={handleSubmit}
                        className="w-1/3 bg-blue-500 text-white py-2 rounded-md font-bold hover:bg-blue-600 transition"
                    >
                        Submit
                    </button>
                </div>
            </div>
        </div>
    );
};

export default CategoryPage;