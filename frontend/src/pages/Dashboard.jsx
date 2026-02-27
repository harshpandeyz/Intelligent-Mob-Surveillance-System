// frontend/src/pages/Dashboard.jsx
import React, { useEffect, useState } from "react";
import axios from "axios";

export default function Dashboard() {
  const [events, setEvents] = useState([]);
  const token = localStorage.getItem("token");

  useEffect(() => {
    if (!token) {
      window.location.href = "/";
      return;
    }
    const fetchEvents = async () => {
      try {
        const res = await axios.get("http://127.0.0.1:8000/events", {
          headers: { Authorization: `Bearer ${token}` }
        });
        setEvents(res.data.events || []);
      } catch (err) {
        console.error("Fetch events error", err?.response?.data || err.message);
        // token invalid -> force re-login
        localStorage.removeItem("token");
        window.location.href = "/";
      }
    };
    fetchEvents();
  }, [token]);

  const handleLogout = () => {
    localStorage.removeItem("token");
    window.location.href = "/";
  };

  return (
    <div style={{padding:20}}>
      <header style={{display:"flex",justifyContent:"space-between",alignItems:"center",marginBottom:20}}>
        <h1>CCTV Events Dashboard</h1>
        <div>
          <button onClick={handleLogout} style={{padding:"8px 12px",borderRadius:6}}>Logout</button>
        </div>
      </header>

      {events.length === 0 ? (
        <p>No events yet.</p>
      ) : (
        <table style={{width:"100%",borderCollapse:"collapse"}}>
          <thead>
            <tr>
              <th style={{border:"1px solid #ddd",padding:8}}>Camera</th>
              <th style={{border:"1px solid #ddd",padding:8}}>Type</th>
              <th style={{border:"1px solid #ddd",padding:8}}>Confidence</th>
              <th style={{border:"1px solid #ddd",padding:8}}>Start</th>
              <th style={{border:"1px solid #ddd",padding:8}}>TX</th>
            </tr>
          </thead>
          <tbody>
            {events.map((e, i) => (
              <tr key={i}>
                <td style={{border:"1px solid #eee",padding:8}}>{e.camera_id}</td>
                <td style={{border:"1px solid #eee",padding:8}}>{e.event_type}</td>
                <td style={{border:"1px solid #eee",padding:8}}>{e.confidence}</td>
                <td style={{border:"1px solid #eee",padding:8}}>{e.start_time}</td>
                <td style={{border:"1px solid #eee",padding:8,wordBreak:"break-all"}}>{e.tx_hash}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
