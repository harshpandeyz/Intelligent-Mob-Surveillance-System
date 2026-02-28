import React from "react";

export default function LiveFeed() {
  return (
    <div style={{ marginTop: "1rem" }}>
      <h2 style={{ marginBottom: "0.5rem", color: "#fff" }}>🔴 Live CCTV Feed</h2>
      <div style={{ border: "2px solid #444", borderRadius: "8px", overflow: "hidden" }}>
        <img
          src="http://127.0.0.1:8000/live_feed"
          alt="Live Camera Feed"
          style={{ width: "100%", maxHeight: "480px", objectFit: "cover" }}
        />
      </div>
    </div>
  );
}
