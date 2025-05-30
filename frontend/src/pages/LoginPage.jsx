import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import '../assets/css/LoginPage.css';

function LoginPage() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    // Basic validation: username should not contain '@'
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
        body: JSON.stringify({ username, password }),
      });

      if (!response.ok) {
        if (response.status === 401) {
          setError('Invalid username or password.');
        } else {
          setError('Server error. Please try again later.');
        }
        return;
      }

      const data = await response.json();
      // Save tokens (e.g., in localStorage)
      localStorage.setItem('accessToken', data.access);
      localStorage.setItem('refreshToken', data.refresh);

      // Redirect user after successful login (for example, to dashboard)
      navigate('/dashboard');
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
