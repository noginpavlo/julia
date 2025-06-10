import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useUser } from '../context/UserContext';

export default function OAuthCallbackPage() {
  const { setAccessToken, setContextUsername } = useUser();
  const navigate = useNavigate();

  useEffect(() => {
    async function fetchOAuthTokens() {
      try {
        // Hit the OAuth callback endpoint to finalize login
        const response = await fetch('http://localhost:8000/api/users/oauth/callback/', {
          method: 'GET',
          credentials: 'include', // Required to include refresh_token cookie
        });

        if (!response.ok) {
          throw new Error(`OAuth callback failed: ${response.status}`);
        }

        const data = await response.json();

        if (data.access && data.username) {
          setAccessToken(data.access);          // Set access token in context and localStorage
          setContextUsername(data.username);    // Set username in context and localStorage
          navigate('/');                        // Redirect to homepage
        } else {
          throw new Error('Access token or username missing in response');
        }
      } catch (err) {
        console.error('OAuth login failed:', err);
        navigate('/login'); // Redirect to login page if something goes wrong
      }
    }

    fetchOAuthTokens();
  }, [setAccessToken, setContextUsername, navigate]);

  return <p>Logging you in via Google...</p>;
}
