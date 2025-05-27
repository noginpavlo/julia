import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import NavBar from './components/NavBar';
import Header from './components/Header';
import Home from './pages/Home';
import StudyPage from './pages/StudyPage';
import './assets/css/main.css';

function App() {
  const [menuVisible, setMenuVisible] = useState(false);

  useEffect(() => {
    document.body.classList.toggle('is-menu-visible', menuVisible);
  }, [menuVisible]);

  return (
    <Router>
      <Header onToggleMenu={() => setMenuVisible(true)} />
      <NavBar onCloseMenu={() => setMenuVisible(false)} />

      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/study/page" element={<StudyPage />} />
      </Routes>
    </Router>
  );
}

export default App;
