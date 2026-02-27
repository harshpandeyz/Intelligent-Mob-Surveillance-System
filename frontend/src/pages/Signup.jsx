import React, {useState} from "react";
import axios from "axios";

export default function Signup() {
  const [u,setU]=useState(""); const [p,setP]=useState(""); const [msg,setMsg]=useState("");

  const handle = async (e) => {
    e.preventDefault();
    try {
      const res = await axios.post("http://127.0.0.1:8000/signup", {username:u,password:p});
      setMsg("Created. Please login.");
      setU(""); setP("");
    } catch (err) {
      setMsg("Error: " + (err?.response?.data?.detail || err.message));
    }
  };
  return (
    <form onSubmit={handle}>
      <input value={u} onChange={e=>setU(e.target.value)} placeholder="username"/>
      <input value={p} onChange={e=>setP(e.target.value)} placeholder="password" type="password"/>
      <button>Create</button>
      <div>{msg}</div>
    </form>
  );
}
