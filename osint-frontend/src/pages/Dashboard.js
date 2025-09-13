import React, { useState } from "react";
import Navbar from "../components/Navbar";
import Sidebar from "../components/Sidebar";
import SearchBar from "../components/SearchBar";
import ProfileCard from "../components/ProfileCard";

export default function Dashboard({ darkMode, toggleDarkMode }) {
  const [profiles, setProfiles] = useState([]);
  const [activeTab, setActiveTab] = useState("Profiles");

  const handleSearch = (query) => {
    if (!query) return;
    // placeholder profile
    const newProfile = {
      name: query,
      bio: "This is a placeholder summary for demonstration purposes.",
      url: "https://example.com",
    };
    setProfiles([newProfile, ...profiles]);
  };

  return (
    <>
      <Navbar darkMode={darkMode} toggleDarkMode={toggleDarkMode} />
      <div className="dashboard-container">
        <Sidebar activeTab={activeTab} setActiveTab={setActiveTab} />
        <div style={{ flex: 1 }}>
          <SearchBar onSearch={handleSearch} />
          <div className="profiles-container">
            {profiles.map((p, idx) => (
              <ProfileCard key={idx} profile={p} />
            ))}
          </div>
        </div>
      </div>
    </>
  );
}
