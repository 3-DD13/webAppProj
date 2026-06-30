import axios from 'axios';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Login from './login';
import Register from './register';
import Dashboard from './dashboard';


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
         </Routes>
       </main>


     </Router>
   </>
 );
}


export default App
