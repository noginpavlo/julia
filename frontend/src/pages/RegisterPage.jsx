import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import '../assets/css/RegisterPage.css';

const RegisterPage = () => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    confirmPassword: '',
  });
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const handleChange = (e) => {
    setFormData((prev) => ({
      ...prev,
      [e.target.name]: e.target.value,
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    const { username, password, confirmPassword } = formData;

    if (password !== confirmPassword) {
      setError("Passwords don't match.");
      return;
    }

    try {
      const res = await fetch('http://localhost:8000/api/users/register/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ username, password }),
      });

      if (res.ok) {
        setSuccess('Registration successful! Redirecting to login...');
        setTimeout(() => navigate('/login'), 2000);
      } else {
        const data = await res.json();
        setError(data.detail || 'Registration failed.');
      }
    } catch (err) {
      setError('Server error. Please try again later.');
    }
  };

  return (
    <div id="register-page">
      <div id="register-container">
        <h2 id="register-title">Create Your Account</h2>

        <form id="register-form" onSubmit={handleSubmit}>
          <div className="register-field">
            <label htmlFor="username">Username *</label>
            <input type="text" id="username" name="username" required value={formData.username} onChange={handleChange} />
          </div>

          <div className="register-field">
            <label htmlFor="email">Email (optional)</label>
            <input type="email" id="email" name="email" value={formData.email} onChange={handleChange} />
          </div>

          <div className="register-field">
            <label htmlFor="password">Password *</label>
            <input type="password" id="password" name="password" required value={formData.password} onChange={handleChange} />
          </div>

          <div className="register-field">
            <label htmlFor="confirm-password">Confirm Password *</label>
            <input type="password" id="confirm-password" name="confirmPassword" required value={formData.confirmPassword} onChange={handleChange} />
          </div>

          <button type="submit" id="register-submit">Register</button>

          {error && <p style={{ color: 'red' }}>{error}</p>}
          {success && <p style={{ color: 'green' }}>{success}</p>}
        </form>

        <div id="login-link">
          Already have an account? <Link to="/login">Login here</Link>
        </div>
      </div>
    </div>
  );
};

export default RegisterPage;
