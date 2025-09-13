import React, { useState, useEffect } from "react";
import Dashboard from "./pages/Dashboard";

function App() {
  const [darkMode, setDarkMode] = useState(true);

  useEffect(() => {
    document.body.className = darkMode ? "dark" : "light";
  }, [darkMode]);

  const toggleDarkMode = () => setDarkMode(prev => !prev);

  return (
    <div className="app">
      <Dashboard darkMode={darkMode} toggleDarkMode={toggleDarkMode} />
    </div>
  );
}

export default App;
