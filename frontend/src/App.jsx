import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { GoogleOAuthProvider } from '@react-oauth/google';
import NavBar from './components/NavBar';
import Header from './components/Header';
import LoginPrompt from './components/LoginPrompt';
import Home from './pages/Home';
import StudyPage from './pages/StudyPage';
import CreatePage from './pages/CreatePage';
import Footer from './components/Footer';
import LoginPage from './pages/LoginPage';
import LogoutPage from './pages/LogoutPage';
import RegisterPage from './pages/RegisterPage';
import { UserProvider } from './context/UserContext';
import OAuthCallbackPage from './pages/OAuthCallbackPage';
import './assets/css/CreatePage.css';
import './assets/css/LoginPrompt.css';
import './assets/css/main.css';

function App() {
  const [menuVisible, setMenuVisible] = useState(false);

  useEffect(() => {
    document.body.classList.toggle('is-menu-visible', menuVisible);
  }, [menuVisible]);

  return (
    <GoogleOAuthProvider clientId="287271048449-11s6kt2edm4q9q2pejh2krjne4vp5tm0.apps.googleusercontent.com">
      <Router>
        <UserProvider>
          <LoginPrompt />
          <Header onToggleMenu={() => setMenuVisible(true)} />
          <NavBar onCloseMenu={() => setMenuVisible(false)} />

          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/study/page" element={<StudyPage />} />
            <Route path="/create" element={<CreatePage />} />
            <Route path="/login" element={<LoginPage />} />
            <Route path="/logout" element={<LogoutPage />} />
            <Route path="/register" element={<RegisterPage />} />
            <Route path="/oauth/callback" element={<OAuthCallbackPage />} />
          </Routes>

          <Footer />
        </UserProvider>
      </Router>
    </GoogleOAuthProvider>
  );
}

export default App;

