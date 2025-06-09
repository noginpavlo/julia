import React from 'react';
import { useUser } from '../context/UserContext';

export default function NavBar({ onCloseMenu }) {
  const { isLoggedIn, username } = useUser();
  console.log('NavBar:', { isLoggedIn, username });

  return (
    <nav id="menu">
      <div className="inner">
        <ul className="links">
          <li><a href="/">Home</a></li>
          <li><a href="/create">Create cards</a></li>
          <li><a href="/study/page">Learn my cards</a></li>
          <li><a href="/">My stats</a></li>
          <li><a href="/">About</a></li>
        </ul>

        {isLoggedIn ? (
          <div style={{ padding: '1rem', color: '#ccc', textAlign: 'center', fontWeight: 'bold' }}>
            Hey, {username || 'USER'}!
          </div>
        ) : (
          <ul className="actions stacked">
            <li><a href="/login" className="button primary fit">Log In</a></li>
            <li><a href="/register" className="button fit">Sign Up</a></li>
          </ul>
        )}

        <a
          href="#menu"
          className="close"
          onClick={(e) => {
            e.preventDefault();
            onCloseMenu();
          }}
        ></a>
      </div>
    </nav>
  );
}
