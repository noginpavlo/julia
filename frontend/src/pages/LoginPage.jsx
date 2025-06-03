import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import '../assets/css/LoginPage.css';
import { useUser } from '../context/UserContext';

function LoginPage() {
  const [username, setUsername] = useState(''); // local input
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate();

  // Get context functions with aliasing
  const { setAccessToken, setUsername: setContextUsername } = useUser();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    if (username.includes('@')) {
      setError("Username should not contain '@'");
      return;
    }

    try {
      const response = await fetch('http://localhost:8000/api/users/token/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({ username, password }),
      });

      if (!response.ok) {
        setError(response.status === 401
          ? 'Invalid username or password.'
          : 'Server error. Please try again later.');
        return;
      }

      const data = await response.json();

      setAccessToken(data.access);        // update token in context
      setContextUsername(username);       // update username in context

      navigate('/');
    } catch (err) {
      setError('Network error. Please check your connection.');
    }
  };

  return (
    <section id="login-page">
      <div id="login-container">
        <h2 id="login-title">Login to Your Account</h2>

        <form id="login-form" onSubmit={handleSubmit}>
          <div className="login-field">
            <label htmlFor="username">Username</label>
            <input
              type="text"
              id="username"
              placeholder="Enter your username"
              required
              value={username}
              onChange={(e) => setUsername(e.target.value)}
            />
          </div>

          <div className="login-field">
            <label htmlFor="password">Password</label>
            <input
              type="password"
              id="password"
              placeholder="Enter your password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
          </div>

          {error && <p style={{ color: 'red' }}>{error}</p>}

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
