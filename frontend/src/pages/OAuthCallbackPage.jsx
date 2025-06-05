import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useUser } from '../context/UserContext';

function OAuthCallbackPage() {
  const { setAccessToken, setUsername } = useUser();
  const navigate = useNavigate();

  useEffect(() => {
    async function finishLogin() {
      try {
        const response = await fetch('http://localhost:8000/api/users/social-login/', {
          method: 'GET',
          credentials: 'include', // Include refresh token cookie
        });

        if (response.ok) {
          const data = await response.json();
          setAccessToken(data.access);
          // Optional: fetch user info if needed
          setUsername("OAuthUser");
          navigate('/');
        } else {
          navigate('/login');
        }
      } catch (err) {
        navigate('/login');
      }
    }

    finishLogin();
  }, [setAccessToken, setUsername, navigate]);

  return <p>Logging in...</p>;
}

export default OAuthCallbackPage;
