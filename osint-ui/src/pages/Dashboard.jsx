import React, { useState } from "react";
import Navbar from "../components/Navbar";
import Sidebar from "../components/Sidebar";
import SearchBar from "../components/SearchBar";
import ClusterView from "../components/ClusterView";

export default function Dashboard({ darkMode, toggleDarkMode }) {
  const [clusters, setClusters] = useState([
    [{ id: 1, name: "Alice", bio: "Bio1", avatar: "", url: "" }, { id: 2, name: "Bob", bio: "Bio2", avatar: "", url: "" }],
    [{ id: 3, name: "Charlie", bio: "Bio3", avatar: "", url: "" }]
  ]);

  const handleSearch = (query) => {
    console.log("Search for:", query);
    // TODO: connect backend
  }

  return (
    <>
      <Navbar darkMode={darkMode} toggleDarkMode={toggleDarkMode} />
      <div className="dashboard-container">
        <Sidebar />
        <div style={{ flex: 1 }}>
          <SearchBar onSearch={handleSearch} />
          <ClusterView clusters={clusters} />
        </div>
      </div>
    </>
  );
}
