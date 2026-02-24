import React, { useEffect, useState } from "react";
import axios from "axios";
import SimulateEventForm from "../components/SimulateEventForm";
import LiveFeed from "../components/LiveFeed";
import { FaCamera, FaClock, FaLock, FaDownload, FaSignOutAlt, FaFilter } from "react-icons/fa";

const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

export default function Dashboard() {
  const [events, setEvents] = useState([]);
  const [filters, setFilters] = useState({ camera: "", type: "", date: "" });
  const [loading, setLoading] = useState(true);
  const token = localStorage.getItem("token");

  useEffect(() => {
    if (!token) {
      window.location.href = "/";
      return;
    }

    const fetchEvents = async () => {
      try {
        setLoading(true);
        const res = await axios.get(`${API_URL}/events`, {
          headers: { Authorization: `Bearer ${token}` }
        });
        setEvents(res.data.events || []);
      } catch (err) {
        console.error("Fetch error", err?.response?.data || err.message);
        localStorage.removeItem("token");
        window.location.href = "/";
      } finally {
        setLoading(false);
      }
    };

    fetchEvents();
    const interval = setInterval(fetchEvents, 10000);
    return () => clearInterval(interval);
  }, [token]);

  const handleLogout = () => {
    localStorage.removeItem("token");
    window.location.href = "/";
  };

  const filtered = events.filter(e =>
    (!filters.camera || e.camera_id.toLowerCase().includes(filters.camera.toLowerCase())) &&
    (!filters.type || e.event_type.toLowerCase().includes(filters.type.toLowerCase())) &&
    (!filters.date || e.start_time.startsWith(filters.date))
  );

  return (
    <div className="dashboard">
      <header className="dashboard-header">
        <div className="header-content">
          <div className="header-title">
            <div className="camera-icon">📹</div>
            <h1>CCTV Crime Dashboard</h1>
          </div>
          <button onClick={handleLogout} className="logout-btn">
            <FaSignOutAlt className="btn-icon" />
            Logout
          </button>
        </div>
      </header>

      <main className="dashboard-main">
        <LiveFeed /> {/* ⬅️ Inserted Live Preview Above SimulateEventForm */}
        <SimulateEventForm />

        <section className="filters-section">
          <div className="section-header">
            <FaFilter className="section-icon" />
            <h2>Filter Events</h2>
          </div>
          <div className="filters-grid">
            <div className="filter-group">
              <label>Camera ID</label>
              <input
                type="text"
                placeholder="Enter camera ID..."
                className="filter-input"
                onChange={(e) => setFilters({ ...filters, camera: e.target.value })}
              />
            </div>
            <div className="filter-group">
              <label>Event Type</label>
              <input
                type="text"
                placeholder="Enter event type..."
                className="filter-input"
                onChange={(e) => setFilters({ ...filters, type: e.target.value })}
              />
            </div>
            <div className="filter-group">
              <label>Date</label>
              <input
                type="date"
                className="filter-input"
                onChange={(e) => setFilters({ ...filters, date: e.target.value })}
              />
            </div>
          </div>
        </section>

        <section className="events-section">
          <div className="section-header">
            <h2>Event Log</h2>
            <span className="events-count">{filtered.length} events</span>
          </div>

          {loading ? (
            <div className="loading-state">
              <div className="loading-spinner"></div>
              <p>Loading events...</p>
            </div>
          ) : filtered.length === 0 ? (
            <div className="empty-state">
              <div className="empty-icon">📄</div>
              <p>No events found matching your filters.</p>
              <small>Try adjusting your search criteria</small>
            </div>
          ) : (
            <div className="events-grid">
              {filtered.map((e, i) => (
                <div key={i} className="event-card">
                  <div className="event-header">
                    <div className="camera-info">
                      <FaCamera className="info-icon" />
                      <span>{e.camera_id}</span>
                    </div>
                    <div className={`confidence-badge ${e.confidence > 0.8 ? 'high' : e.confidence > 0.5 ? 'medium' : 'low'}`}>
                      {(e.confidence * 100).toFixed(0)}%
                    </div>
                  </div>
                  <div className="event-type">{e.event_type.replace(/_/g, " ")}</div>
                  <div className="event-time">
                    <FaClock className="info-icon" />
                    {new Date(e.start_time).toLocaleString()}
                  </div>
                  <div className="transaction-info">
                    <FaLock className="info-icon" />
                    <span className="tx-hash">TX: {e.tx_hash}</span>
                  </div>
                  <a href={e.enc_path} download className="download-btn">
                    <FaDownload className="btn-icon" />
                    Download Encrypted Clip
                  </a>
                </div>
              ))}
            </div>
          )}
        </section>
      </main>
    </div>
  );
}
