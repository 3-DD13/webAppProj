import React, { useEffect , useState} from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';

function Dashboard(){
  const [message, setMessage] = useState("Loading your dashboard...");
  const navigate = useNavigate();

  useEffect(() => {
    axios.get('http://127.0.0.1:5000/dashboard/')
  .then(response => {
    setMessage(response.data.message);
  })
  .catch(error => {
    alert("Unauthorized session. Please sign in again.");
    navigate('/login');
  });
}, [navigate]);

  return (
    <>
    <div>
      <h2>User Dashboard</h2>
      <p>{message}</p>
      <button onClick={() => navigate('/login/')}>Sign Out</button>
    </div>
    </>
  )
}

export default Dashboard;