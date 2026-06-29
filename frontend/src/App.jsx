import axios from 'axios';
import { useState } from 'react';

axios.defaults.withCredentials = true;

function App() {
  const [password, setPassword] = useState("");
  const [username, setUsername] = useState("");

  const handleAuth = async (endpoint) => {
    try {
      const response = await axios.post(`http://localhost:5000/${endpoint}`, {
        username,
        password
      });
      alert(response.data.message);
    } catch (error) {
      const errorMessage = error.response?.data?.error || error.response?.data?.message || "An error occurred";
      alert(errorMessage);
    }
  };

  return (
    <>
      <header>
        <h1>Group Study</h1>
      </header>
      <form className="usernameBox">
        <label>
          Username:
          <input
            type="text"
            value={username}
            onChange={(e) => setUsername(e.target.value)} />
        </label><br />
        <label>
          Password:
          <input
            id="pass"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          /><br />
        </label>
        <button type='button' id='signIn' onClick={() => handleAuth('/login/')}>Sign In</button>
        <button type='button' id='createAcc' onClick={() => handleAuth('/register/')}>Create Account</button>
      </form>
      <p>Needs styling</p>
    </>
  )
}

export default App
