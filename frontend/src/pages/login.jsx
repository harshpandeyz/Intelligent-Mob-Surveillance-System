// src/pages/Login.jsx
import React, { useState } from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom";

const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

export default function Login() {
  const navigate = useNavigate();
  const [username, setUsername] = useState("admin");
  const [password, setPassword] = useState("admin123");
  const [error, setError] = useState("");

  const handleLogin = async (e) => {
    e.preventDefault();
    setError("");

    try {
      const form = new URLSearchParams();
      form.append("username", username);
      form.append("password", password);   
      form.append("grant_type", "password");

      const res = await axios.post(`${API_URL}/login`, form);
      const token = res.data.access_token;
      localStorage.setItem("token", token);

      navigate("/dashboard"); // redirect to home or dashboard
    } catch (err) {
      console.error("Login failed:", err);
      setError(err.response?.data?.detail || "Login error");
    }
  };

  return (
    <div style={{ padding: 20, maxWidth: 300, margin: "50px auto" }}>
      <h2>Login</h2>
      <form onSubmit={handleLogin}>
        <div>
          <label>Username</label>
          <input
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            style={{ width: "100%", marginBottom: 10 }}
          />
        </div>
        <div>
          <label>Password</label>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            style={{ width: "100%", marginBottom: 10 }}
          />
        </div>
        <button type="submit" style={{ width: "100%" }}>
          Log In
        </button>
        {error && <p style={{ color: "red" }}>{error}</p>}
      </form>
    </div>
  );
}
  