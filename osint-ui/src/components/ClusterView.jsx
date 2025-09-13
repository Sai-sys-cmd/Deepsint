import React from "react";
import ProfileCard from "./ProfileCard";

export default function ClusterView({ clusters }) {
  return (
    <div className="cluster">
      {clusters.map((cluster, idx) => (
        <div key={idx}>
          {cluster.map(profile => (
            <ProfileCard key={profile.id} profile={profile} />
          ))}
        </div>
      ))}
    </div>
  );
}
