import React, { useState } from "react";
import axios from "axios";

const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

export default function SimulateEventForm() {
  const [cameraId, setCameraId] = useState("cam1");
  const [file, setFile] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file) return;

    setLoading(true);
    setResult(null);

    const formData = new FormData();
    formData.append("camera_id", cameraId);
    formData.append("file", file);

    try {
      const token = localStorage.getItem("token");
      const res = await axios.post(`${API_URL}/classify_upload`, formData, {
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "multipart/form-data"
        }
      });

      const { event_type, tx_hash } = res.data;
      setResult({ event_type, tx_hash });
    } catch (err) {
      console.error("Upload failed", err?.response?.data || err.message);
      setResult({ error: "Upload failed." });
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} style={{
      padding: 20,
      border: "1px solid gray",
      borderRadius: 8,
      marginBottom: 20
    }}>
      <h2>Simulate Event Upload (AI Detection)</h2>

      <div style={{ marginBottom: 10 }}>
        <label>Camera ID: </label>
        <input value={cameraId} onChange={(e) => setCameraId(e.target.value)} />
      </div>

      <div style={{ marginBottom: 10 }}>
        <label>CCTV Clip (MP4): </label>
        <input type="file" accept=".mp4" onChange={(e) => setFile(e.target.files[0])} />
      </div>

      <button type="submit" disabled={loading}>
        {loading ? "Analyzing..." : "Upload & Analyze"}
      </button>

      {result && (
        <div style={{ marginTop: 10, color: result.error ? "red" : "green" }}>
          {result.error
            ? `❌ ${result.error}`
            : `✅ Detected event: ${result.event_type || "unknown"} (tx: ${result.tx_hash || "N/A"})`}
        </div>
      )}
    </form>
  );
}
