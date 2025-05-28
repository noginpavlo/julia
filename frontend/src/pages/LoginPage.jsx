// src/pages/LoginPage.jsx
import React from 'react';
import { Link } from 'react-router-dom';
import '../assets/css/LoginPage.css';

function LoginPage() {
  return (
    <section id="login-page">
      <div id="login-container">
        <h2 id="login-title">Login to Your Account</h2>

        <form id="login-form">
          <div className="login-field">
            <label htmlFor="email">Email</label>
            <input type="email" id="email" placeholder="Enter your email" required />
          </div>

          <div className="login-field">
            <label htmlFor="password">Password</label>
            <input type="password" id="password" placeholder="Enter your password" required />
          </div>

          <button type="submit" id="login-submit">Login</button>
        </form>

        <div id="social-login">
          <p>Or login with</p>
          <div className="social-buttons">
            <button className="social-btn" id="google-login">
              <i className="fab fa-google"></i> Google
            </button>
            <button className="social-btn" id="github-login">
              <i className="fab fa-github"></i> GitHub
            </button>
          </div>
        </div>

        <div id="register-link">
          <p>Don't have an account? <Link to="/register">Register here</Link></p>
        </div>
      </div>
    </section>
  );
}

export default LoginPage;

