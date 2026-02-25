// src/components/EventList.jsx
import React, { useEffect, useState } from "react";
import axios from "axios";
import EventCard from "./EventCard";

const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

export default function EventList() {
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [err, setErr] = useState(null);

  const fetchEvents = async () => {
    try {
      setLoading(true);
      setErr(null);
      
      const token = localStorage.getItem("token");
      const res = await axios.get(`${API_URL}/events`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      const list = res.data?.events ?? res.data ?? [];
      setEvents(list);
    } catch (e) {
      setErr(e.response?.data?.detail || e.message || "Failed to fetch");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchEvents();
    const timer = setInterval(fetchEvents, 10000); // refresh every 10s
    return () => clearInterval(timer);
  }, []);

  return (
    <div style={{ maxWidth: 900, margin: "18px auto", padding: "0 12px" }}>
      <h2>Event Log</h2>
      {loading && <p>Loading...</p>}
      {err && <p style={{ color: "red" }}>Error: {err}</p>}
      {!loading && events.length === 0 && <p>No events yet.</p>}
      {events.map((ev, i) => (
        <EventCard key={i} event={ev} />
      ))}
    </div>
  );
}
