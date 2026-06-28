import { useState } from 'react'

function App() {
  const [password, setPassword] = useState("");
  const [username, setUsername] = useState("");

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
        <button type='button' id='signIn'>Sign In</button>
        <button type='button' id='createAcc'>Create Account</button>
      </form>
      <p>Needs styling</p>
    </>
  )
}

export default App
