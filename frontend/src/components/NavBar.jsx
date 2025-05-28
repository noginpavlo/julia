import React from 'react';

export default function NavBar({ onCloseMenu }) {
  return (
    <nav id="menu">
      <div className="inner">
        <ul className="links">
          <li><a href="/">Home</a></li>
          <li><a href="/create">Create cards</a></li>
          <li><a href="/study/page">Learn my cards</a></li>
          <li><a href="generic.html">My stats</a></li>
          <li><a href="elements.html">About</a></li>
        </ul>
        <ul className="actions stacked">
          <li><a href="#" className="button primary fit">Log In</a></li>
          <li><a href="#" className="button fit">Sign Up</a></li>
        </ul>
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
