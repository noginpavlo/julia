import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useUser } from '../context/UserContext';

function LogoutPage() {
  const { logout } = useUser();
  const navigate = useNavigate();

  useEffect(() => {
    async function handleLogout() {
      try {
        await fetch('http://localhost:8000/api/users/logout/', {
          method: 'POST',
          credentials: 'include',
        });

        localStorage.removeItem('accessToken');
      } catch (err) {
        console.warn('Logout API call failed:', err);
      }

      logout();
      navigate('/login');
    }

    handleLogout();
  }, [logout, navigate]);

  return null;
}

export default LogoutPage;
