import React from 'react';

export default function Header({ onToggleMenu }) {
  return (
    <header id="header" className="alt">
      <a href="/" className="logo">
        <strong>Julia</strong> <span>by highlander-95</span>
      </a>
      <nav>
        <a
          href="#menu"
          onClick={(e) => {
            e.preventDefault();
            onToggleMenu(); // Call parent to toggle
          }}
        >
          Menu
        </a>
      </nav>
    </header>
  );
}