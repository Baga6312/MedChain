import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export default function OAuthCallbackPage() {
  const { acceptToken } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    const access = new URLSearchParams(window.location.hash.slice(1)).get('access');
    if (access) {
      acceptToken(access);
      navigate('/dashboard', { replace: true });
    } else navigate('/login', { replace: true });
  }, []); // eslint-disable-line

  return null;
}