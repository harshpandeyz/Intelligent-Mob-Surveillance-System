// src/components/EventCard.jsx
import React from "react";

export default function EventCard({ event }) {
  return (
    <div style={{
      border: "1px solid #e2e8f0",
      borderRadius: 12,
      padding: 14,
      marginBottom: 12,
      background: "#fff",
      boxShadow: "0 1px 3px rgba(0,0,0,0.06)"
    }}>
      <div style={{display:"flex", justifyContent:"space-between", alignItems:"center"}}>
        <h3 style={{margin:0}}>Camera: {event.camera_id}</h3>
        <small>{new Date(event.start_time).toLocaleString()}</small>
      </div>

      <p style={{margin:"8px 0"}}><b>Event:</b> {event.event_type} &nbsp; • &nbsp; <b>Confidence:</b> {Number(event.confidence).toFixed(2)}</p>

      <p style={{margin:"6px 0"}}><b>Clip:</b> {event.clip_path || "—"}</p>

      <p style={{margin:"6px 0", wordBreak:"break-all"}}>
        <b>Blockchain TX:</b>{" "}
        {event.tx_hash
          ? <a href="#" onClick={(e)=>{e.preventDefault(); navigator.clipboard?.writeText(event.tx_hash)}} title="Click to copy">{event.tx_hash}</a>
          : "pending"}
      </p>
    </div>
  );
}
