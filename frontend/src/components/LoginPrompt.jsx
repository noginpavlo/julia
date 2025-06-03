import React from 'react';
import { useUser } from '../context/UserContext';
import { useNavigate } from 'react-router-dom';

export default function LoginPrompt() {
  const { username } = useUser();
  const navigate = useNavigate();

  // Hide prompt if user is logged in
  if (username) return null;

  return (
    <div id="login-prompt" role="alert" aria-live="polite">
      <span>Hey, you are not logged in.</span>
      <button
        id="login-prompt-button"
        type="button"
        onClick={() => navigate('/login')}
      >
        Login
      </button>
    </div>
  );
}
