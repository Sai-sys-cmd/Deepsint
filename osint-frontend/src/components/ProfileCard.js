import React from "react";

export default function ProfileCard({ profile }) {
  return (
    <div className="profile-card">
      <h3>{profile.name}</h3>
      <h4>SUMMARY</h4>
      <p>{profile.bio}</p>
      <p>{profile.url}</p>
    </div>
  );
}
