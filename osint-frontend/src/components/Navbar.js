import React from "react";

export default function Navbar({ toggleDarkMode, darkMode }) {
  return (
    <div className="navbar">
      <h1>DEEPSINT</h1>
      <button className="toggle-btn" onClick={toggleDarkMode}>
        {darkMode ? "Light Mode" : "Dark Mode"}
      </button>
    </div>
  );
}
