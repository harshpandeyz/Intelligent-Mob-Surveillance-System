import React, { useState, useEffect } from "react";
import Login from "./pages/login";
import EventList from "./components/EventList";

export default function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);

  useEffect(() => {
    const token = localStorage.getItem("token");
    setIsLoggedIn(!!token);
  }, []);

  const handleLogin = () => {
    setIsLoggedIn(true);
  };

  return (
    <div>
      <header style={{
        background: "#0f172a",
        color: "white",
        padding: "16px 12px",
        textAlign: "center"
      }}>
        <h1 style={{ margin: 0 }}>CCTV Events Dashboard</h1>
      </header>

      <main>
        {isLoggedIn ? <EventList /> : <Login onLoginSuccess={handleLogin} />}
      </main>
    </div>
  );
}
