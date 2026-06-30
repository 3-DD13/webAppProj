import React, { useState } from 'react';
import axios from 'axios';
import { useNavigate, Link } from 'react-router-dom';

function Login(){
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const navigate = useNavigate();

  const handleLogin = async (e) => {
    e.preventDefault();
    try {
      const response = await axios.post('http://127.0.0.1:5000/login/', {username, password});
      navigate('/dashboard/');
    } catch (error) {
      alert(error.response?.data?.message || "Login failed");
    }
  };


return (
  <>
  <div>
    <h2>Sign In</h2>
    <form onSubmit={handleLogin}>
      <label>Username:
        <input type="text" value={username} onChange={(e) => setUsername(e.target.value)}/>
      </label><br />
      <label>Password:
        <input type='password' value={password} onChange={(e) => setPassword(e.target.value)}/>
      </label><br />
      <button type='submit' id='signIn'>Sign in</button>
    </form>
    <p>Dont have an account? <Link to="/register/">Create Account</Link></p>
  </div>
  </>
);
}

export default Login;