import React from "react";

export default function SearchBar({ onSearch }) {
  const [query, setQuery] = React.useState("");

  return (
    <div className="search-bar">
      <input
        type="text"
        placeholder="Search profiles..."
        value={query}
        onChange={(e) => setQuery(e.target.value)}
      />
      <button onClick={() => onSearch(query)}>Search</button>
    </div>
  );
}
