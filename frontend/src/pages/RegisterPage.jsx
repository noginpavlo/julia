import React from 'react';
import { Link } from 'react-router-dom';
import '../assets/css/RegisterPage.css';

const RegisterPage = () => {
  return (
    <div id="register-page">
      <div id="register-container">
        <h2 id="register-title">Create Your Account</h2>

        <form id="register-form">
          <div className="register-field">
            <label htmlFor="username">
              Username <span className="required">*</span>
            </label>
            <input type="text" id="username" name="username" required />
          </div>

          <div className="register-field">
            <label htmlFor="email">
              Email <span className="optional">(optional)</span>
            </label>
            <input type="email" id="email" name="email" />
          </div>

          <div className="register-field">
            <label htmlFor="password">
              Password <span className="required">*</span>
            </label>
            <input type="password" id="password" name="password" required />
          </div>

          <div className="register-field">
            <label htmlFor="confirm-password">
              Confirm Password <span className="required">*</span>
            </label>
            <input
              type="password"
              id="confirm-password"
              name="confirm-password"
              required
            />
          </div>

          <button type="submit" id="register-submit">
            Register
          </button>
        </form>

        <div id="login-link">
          Already have an account? <Link to="/login">Login here</Link>
        </div>
      </div>
    </div>
  );
};

export default RegisterPage;
