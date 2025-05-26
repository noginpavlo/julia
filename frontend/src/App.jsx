import React, { useState, useEffect } from 'react';
import NavBar from './components/NavBar';
import Header from './components/Header';
import Homepage from './components/Homepage';
import './assets/css/main.css';

function App() {
  const [menuVisible, setMenuVisible] = useState(false);

  useEffect(() => {
    document.body.classList.toggle('is-menu-visible', menuVisible);
  }, [menuVisible]);

  return (
    <>
      <Header onToggleMenu={() => setMenuVisible(true)} />
      <NavBar onCloseMenu={() => setMenuVisible(false)} />
      <Homepage />
    </>
  );
}

export default App;

