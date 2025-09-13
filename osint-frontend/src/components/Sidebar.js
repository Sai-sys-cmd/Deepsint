import React from "react";

export default function Sidebar({ activeTab, setActiveTab }) {
  return (
    <div className="sidebar">
      <button
        className={activeTab === "Profiles" ? "active" : ""}
        onClick={() => setActiveTab("Profiles")}
      >
        Profiles
      </button>
    </div>
  );
}
