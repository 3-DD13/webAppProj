import React, { useEffect , useState} from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';

function Dashboard(){
  const [message, setMessage] = useState("Loading your dashboard...");
  const navigate = useNavigate();
  
  const API_BASE_URL = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1' ? 
  'http://127.0.0.1:5000' : 'https://hjuarez.pythonanywhere.com'

  useEffect(() => {
    axios.get(`${API_BASE_URL}/dashboard/`, { withCredentials: true})
  .then(response => {
    setMessage(response.data.message);
  })
  .catch(error => {
    alert("Unauthorized session. Please sign in again.");
    navigate('/login');
  });
}, [navigate, API_BASE_URL]);

  return (
    <>
    <div>
      <h2>User Dashboard</h2>
      <p>{message}</p>
      <button onClick={() => navigate('/game/')}>Enter Game Lobby</button>
      <button onClick={() => navigate('/login/')}>Sign Out</button>
    </div>
    </>
  )
}

export default Dashboard;