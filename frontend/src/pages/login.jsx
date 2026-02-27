// frontend/src/pages/Login.jsx
import React, { useState } from "react";
import axios from "axios";

export default function Login() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  const handleLogin = async (e) => {
    e.preventDefault();
    setError("");
    try {
      // OAuth2-compatible form data (backend expects form)
      const params = new URLSearchParams();
      params.append("username", username);
      params.append("password", password);

      const res = await axios.post("http://127.0.0.1:8000/login", params, {
        headers: { "Content-Type": "application/x-www-form-urlencoded" }
      });

      // Save token
      localStorage.setItem("token", res.data.access_token);
      // Navigate to dashboard
      window.location.href = "/dashboard";
    } catch (err) {
      console.error("Login error:", err?.response?.data || err.message);
      setError("Invalid credentials or server error");
    }
  };

  return (
    <div style={{display:"flex",height:"100vh",alignItems:"center",justifyContent:"center",background:"#f3f4f6"}}>
      <form onSubmit={handleLogin} style={{width:320,background:"#fff",padding:20,borderRadius:8,boxShadow:"0 4px 14px rgba(0,0,0,0.06)"}}>
        <h2 style={{marginBottom:10,textAlign:"center"}}>Login</h2>
        <input value={username} onChange={e=>setUsername(e.target.value)} placeholder="Username" style={{width:"100%",padding:8,marginBottom:8}} />
        <input value={password} onChange={e=>setPassword(e.target.value)} placeholder="Password" type="password" style={{width:"100%",padding:8,marginBottom:8}} />
        {error && <div style={{color:"red",marginBottom:8}}>{error}</div>}
        <button type="submit" style={{width:"100%",padding:10,background:"#1d4ed8",color:"#fff",border:0,borderRadius:6}}>Login</button>
        <p style={{marginTop:12,fontSize:13,color:"#555"}}>Default admin: <b>admin / admin123</b></p>
      </form>
    </div>
  );
}
