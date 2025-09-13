import React from "react";

export default function ClusterView({ clusters, onProfileClick }) {
  return (
    <div className="cluster">
      {clusters.map((cluster, idx) => (
        <div key={idx} style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill,minmax(200px,1fr))", gap: "1rem", marginBottom: "1rem" }}>
          {cluster.map(profile => (
            <div 
              key={profile.id} 
              className="profile-card" 
              onClick={() => onProfileClick(profile)}
              style={{ padding: "1rem", borderRadius: "12px", backgroundColor: "var(--card-light)", cursor: "pointer", boxShadow: "0 4px 12px rgba(0,0,0,0.05)" }}
            >
              <h3>{profile.name}</h3>
              <p>{profile.bio}</p>
            </div>
          ))}
        </div>
      ))}
    </div>
  );
}
