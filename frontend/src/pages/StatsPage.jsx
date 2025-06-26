import React, { useState } from "react";
import { useUser } from "../context/UserContext";
import "../assets/css/StatsPage.css";

const months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
const years = [2023, 2024, 2025];

const dummyData = Array(365).fill(0).map((_, i) => {
  // Cycle intensity for demo: 0 to 3
  return i % 4;
});

const getDayColorClass = (count) => {
  switch (count) {
    case 0: return "bg-gray-200";
    case 1: return "bg-green-300";
    case 2: return "bg-green-500";
    case 3: return "bg-green-700";
    default: return "bg-gray-200";
  }
};

const StatsPage = () => {
  const { username } = useUser();
  const [selectedYear, setSelectedYear] = useState(2025);

  return (
    <section id="stats-section">
      <div className="stats-container">

        {/* Profile Section */}
        <div className="profile-container">
          <img
            src="https://via.placeholder.com/80"
            alt="Profile"
            className="profile-picture"
          />
          <div className="profile-username">{username || "User Name"}</div>
        </div>

        {/* Progress Section */}
        <div className="progress-container">
          {/* Month Labels */}
          <div className="month-labels">
            {months.map((m) => (
              <div key={m} className="month-label">
                {m}
              </div>
            ))}
          </div>

          {/* Scrollable Grid */}
          <div className="grid-scroll">
            <div className="grid">
              {dummyData.map((count, idx) => (
                <div
                  key={idx}
                  className={getDayColorClass(count)}
                  title={`Day ${idx + 1}, Intensity: ${count}`}
                />
              ))}
            </div>
          </div>
        </div>

        {/* Years Section */}
        <div className="years-container">
          {years.map((year) => (
            <button
              key={year}
              className={`year-btn ${year === selectedYear ? "active-year" : ""}`}
              onClick={() => setSelectedYear(year)}
            >
              {year}
            </button>
          ))}
        </div>
      </div>
    </section>
  );
};

export default StatsPage;