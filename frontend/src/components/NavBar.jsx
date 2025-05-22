import React from 'react';

export default function NavBar() {
  return (
    <nav id="menu">
      <ul className="links">
        <li><a href="index.html">Home</a></li>
        <li><a href="landing.html">Create cards</a></li>
        <li><a href="landing.html">Learn my cards</a></li>
        <li><a href="generic.html">My stats</a></li>
        <li><a href="elements.html">About</a></li>
      </ul>
      <ul className="actions stacked">
        <li><a href="#" className="button primary fit">Log In</a></li>
        <li><a href="#" className="button fit">Sign Up</a></li>
      </ul>
    </nav>
  );
}