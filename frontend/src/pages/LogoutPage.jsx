import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useUser } from '../context/UserContext';

function LogoutPage() {
  const { logout } = useUser();
  const navigate = useNavigate();

  useEffect(() => {
    logout();
    fetch('http://localhost:8000/api/users/logout/', {
      method: 'POST',
      credentials: 'include',
    });

    navigate('/login');
  }, [logout, navigate]);

  return null; // Or a loading indicator if you want
}

export default LogoutPage;