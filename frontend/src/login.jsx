import React, { useState } from 'react';
import axios from 'axios';
import { useNavigate, Link } from 'react-router-dom';

function Login(){
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const navigate = useNavigate();

  const API_BASE_URL = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1' ? 
  'http://127.0.0.1:5000' : 'https://hjuarez.pythonanywhere.com'

  const handleLogin = async (e) => {
    e.preventDefault();
    try {
      const response = await axios.post(`${API_BASE_URL}/login/`,
        {username, password},
        { withCredentials: true}
      );
      navigate('/dashboard/');
    } catch (error) {
      alert(error.response?.data?.message || "Login failed");
    }
  };


return (
  <>
  <div className='loginBox'>
    <h2>Sign In</h2>
    <form onSubmit={handleLogin} className='login-form'>
      <label><b id='input'>Username:</b>
        <input type="text" value={username} onChange={(e) => setUsername(e.target.value)}/>
      </label>

      <label><b id='input'>Password:</b>
        <input type='password' value={password} onChange={(e) => setPassword(e.target.value)}/>
      </label>
      
      <button type='submit' id='signIn'>Sign in</button>
    </form>
    <p>Don't have an account? <Link to="/register/">Create Account</Link></p>
  </div>
  </>
);
}

export default Login;