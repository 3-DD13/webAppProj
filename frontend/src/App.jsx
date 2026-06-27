import { useState } from 'react'

function App() {
  const [count, setCount] = useState(0)

  return (
    <>
      <h1>Final Project: Live App</h1>
      <button onClick={() => setCount((count) => count + 1)}>Count: {count}</button>
      <p>For testing, remove later</p>
    </>
  )
}

export default App
