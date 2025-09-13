import React from "react";

export default function ProfileCard({ profile }) {
  return (
    <div className="profile-card">
      <img src={profile.avatar || "https://via.placeholder.com/60"} alt="avatar"/>
      <div>
        <h3>{profile.name}</h3>
        <p>{profile.bio}</p>
        <p>{profile.url}</p>
      </div>
    </div>
  );
}
