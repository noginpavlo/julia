import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useUser } from '../context/UserContext';

export default function OAuthCallbackPage() {
  const { setAccessToken } = useUser();
  const navigate = useNavigate();

  useEffect(() => {
    async function fetchToken() {
      try {
        const response = await fetch('http://localhost:8000/api/users/social/token/', { // requests access token
          method: 'GET',
          credentials: 'include',
        });

        if (!response.ok) throw new Error('Token fetch failed');

        const data = await response.json();
        if (data.access) {
          setAccessToken(data.access);
          setContextUsername(data.username);
          navigate('/'); // Redirect to homepage
        } else {
          throw new Error('No access token in response');
        }
      } catch (err) {
        console.error('OAuth login failed:', err);
        navigate('/login'); // Redirect to login on failure
      }
    }

    fetchToken();
  }, [setAccessToken, navigate]);

  return <p>Logging you in via Google...</p>;
}