import React, { useState } from "react";
import axios from 'axios';
import { useNavigate, Link } from 'react-router-dom';

function Register(){
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const navigate = useNavigate();
  // for local changes put http://127.0.0.1:5000 before /register/
  const handleRegister = async (e) => {
    e.preventDefault();
    try {
      const response = await axios.post('/register/', {username, password});
      navigate('/login/');
    } catch (error) {
      alert(error.response?.data?.error || error.response?.data?.message || "Registration Failed");
    }
  }

  return (
  <>
  <div className="loginBox">
    <h2>Create Account</h2>
    <form onSubmit={handleRegister} className="login-form">
      <label><b id='input'>Username:</b>
        <input type="text" value={username} onChange={(e) => setUsername(e.target.value)}/>
      </label>

      <label><b id='input'>Password:</b>
        <input type='password' value={password} onChange={(e) => setPassword(e.target.value)}/>
      </label>

      <button type='submit' id='signIn'>Create Account</button>
    </form>
    <p>Already have an account? <Link to="/login/">Sign In here</Link></p>
  </div>
  </>
  );
}

export default Register;