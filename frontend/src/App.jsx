import axios from 'axios';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Login from './Login';
import Register from './Register';
import Dashboard from './Dashboard';
import GameRoom from './GameRoom';


axios.defaults.withCredentials = true;


function App() {
 return (
   <>
     <Router>
       <header>
         <h1>App Name</h1>
       </header>


       <main>
         <Routes>
           <Route path="/" element={<Navigate to="/login/" replace/>} />


           <Route path="/login/" element={<Login />} />
           <Route path="/register/" element={<Register />} />
           <Route path="/dashboard/" element={<Dashboard />} />
           <Route path="/game/" element={<GameRoom />} />
         </Routes>
       </main>


     </Router>
   </>
 );
}


export default App
