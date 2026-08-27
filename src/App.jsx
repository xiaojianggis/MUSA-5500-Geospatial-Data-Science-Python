import React from "react";
import { HashRouter as Router, Route, Routes, Link } from "react-router-dom";
// import { HashRouter as Router } from 'react-router-dom';

import Syllabus from "./pages/Syllabus";
import Home from "./pages/Home";
// import LecturePage from "./pages/LecturePage";
import Assignments from "./pages/Assignments";
import FinalProject from "./pages/FinalProjects";
import Schedule from "./pages/Schedule";


function Layout({ children }) {
  return (
    <div className="page">
      <header className="header">
        <div className="container header-inner">
          <h1 className="site-title">MUSA 5500: Python for Spatial Data Science</h1>
          <nav className="nav">
            <Link to="/">Home</Link>
            <Link to="/syllabus">Syllabus</Link>
            <Link to="/schedule">Schedule</Link>
            <Link to="/assignments">Assignments</Link>
            <Link to="/project">Final Project</Link>
            {/* <Link to="/Github">Github</Link> */}
            <a href="https://github.com/xiaojianggis/MUSA-5500-Geospatial-Data-Science-Python" target="_blank" rel="noopener noreferrer">GitHub</a>
          </nav>
        </div>
      </header>
      
      <main className="main">
        {children}
      </main>

      <footer className="footer">
        &copy; {new Date().getFullYear()} MUSA 550: Python for Spatial Data Science - University of Pennsylvania by Xiaojiang Li
      </footer>
    </div>
  );
}

function Lectures() {
  return <div className="container"><h2>Lectures</h2><p>[Add lecture materials or links]</p></div>;
}
function Project() {
  return <div className="container"><h2>Final Project</h2><p>[Add final project info]</p></div>;
}
// function Syllabus() {
//   return <div className="container"><h2>Syllabus</h2><p>[Add syllabus content or embed PDF]</p></div>;
// }

export default function App() {
  return (
    <Router>
      <Layout>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/schedule" element={<Schedule />} />
          <Route path="/syllabus" element={<Syllabus />} />
          <Route path="/assignments" element={<Assignments />}   />
          <Route path="/project" element={<FinalProject />} />

          {/* <Route path="/lecture/:lectureId" element={<LecturePage />} /> */}
        </Routes>
      </Layout>
    </Router>
  );
}
