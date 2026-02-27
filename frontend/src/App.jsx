// src/App.jsx
import React from "react";
import EventList from "./components/EventList";

export default function App() {
  return (
    <div>
      <header style={{
        background: "#0f172a",
        color: "white",
        padding: "16px 12px",
        textAlign: "center"
      }}>
        <h1 style={{margin:0}}>CCTV Events Dashboard</h1>
      </header>

      <main>
        <EventList />
      </main>
    </div>
  );
}
