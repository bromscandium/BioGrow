import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Home from './pages/Home';
import Login from './pages/Login';
import AI from './pages/AI';
import AllProjects from './pages/AllProjects';
import Project from './pages/Project';
import Community from './pages/Community';
import Profile from './pages/Profile';

function App() {
    return (
        <Router>
            <Routes>
                <Route path="/home" element={<Home />} />
                <Route path="/ai" element={<AI />} />
                <Route path="/" element={<Login />} />
                <Route path="/projects" element={<AllProjects />} />
                <Route path="/projects/:id" element={<Project />} />
                <Route path="/community" element={<Community />} />
                <Route path="/profile" element={<Profile />} />
            </Routes>
        </Router>
    );
}

export default App;
