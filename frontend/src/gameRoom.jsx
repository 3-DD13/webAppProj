import React, { useEffect, useState } from "react";
import axios from "axios";

function GameRoom(){
  const [gameState, setGameState] = useState(null);
  const [guessText, setGuessText] = useState("");

  const API_BASE_URL = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1' ? 
  'http://127.0.0.1:5000' : 'https://hjuarez.pythonanywhere.com'

  useEffect(() => {
    const joinGame = async () => {
      try {
        const res = await axios.post(`${API_BASE_URL}/api/game/join`, {}, { withCredentials:true});
        setGameState(res.data);
      } catch (err) {
        console.error("Could not join game room:", err);
      }
    };
    joinGame();
    const interval = setInterval(async () => {
      try {
        const res = await axios.get(`${API_BASE_URL}/api/game/state`, {withCredentials:true});
        setGameState(res.data);
      } catch (err) {
        console.error("Error pulling game:", err);
      }
    }, 1000);
    return () => clearInterval(interval);
  }, [API_BASE_URL]); 

  const handleSendGuess = async (e) => {
    e.preventDefault();
    if(!guessText.trim()){
      return;
    }
    try {
      const res = await axios.post(`${API_BASE_URL}/api/game/guess`, {text: guessText}, { withCredentials:true});
      setGuessText("");
    } catch (err) {
      alert(err.response?.data?.error || "Guess submission failed");
    }
  };

  if(!gameState){
    return <p>Connecting to game engine...</p>
  }

  return (
    <>
    <div>
      <h1>Game Phase: {gameState.phase}</h1>
      <h3>Hint: {gameState.word_hint}</h3>
      {gameState.my_word && <h2>Your word to draw: {gameState.my_word}</h2>}

      <div>
        <h4>Active Players</h4>
        <ul>
          {gameState.players?.map((p, idx) =>(
            <li key={idx}>{p.username} - {p.score} pts {gameState.drawer === p.username && " (Drawing)"} </li>
          ))}
        </ul>
      </div>

          <form onSubmit={handleSendGuess}>
            <input
            type="text" 
            placeholder="Enter a guess here..."
            value={guessText}
            onChange={(e) => setGuessText(e.target.value)}
            disabled={gameState.drawer === current_user}
            />
            <button type="submit">Submit Guess</button>
          </form>
    </div>
    </>
  );
}

export default GameRoom;