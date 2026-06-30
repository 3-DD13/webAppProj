import React, { useState } from "react";
import axios from 'axios';
import { useNavigate, Link } from 'react-router-dom';

function Register(){
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const navigate = useNavigate();

  const handleRegister = async (e) => {
    e.preventDefault();
    try {
      const response = await axios.post('http://127.0.0.1:5000/register/', {username, password});
      navigate('/login/');
    } catch (error) {
      alert(error.response?.data?.error || error.response?.data?.message || "Registration Failed");
    }
  }

  return (
  <>
  <div>
    <h2>Create Account</h2>
    <form onSubmit={handleRegister}>
      <label>Username:
        <input type="text" value={username} onChange={(e) => setUsername(e.target.value)}/>
      </label><br />
      <label>Password:
        <input type='password' value={password} onChange={(e) => setPassword(e.target.value)}/>
      </label><br />
      <button type='submit' id='signIn'>Create Account</button>
    </form>
    <p>Already have an account? <Link to="/login/">Sign In here</Link></p>
  </div>
  </>
  );
}

export default Register;