import { useNavigate } from 'react-router-dom';

function Navbar() {
  const navigate = useNavigate();

  const handleLogout = () => {
    localStorage.removeItem('vs_token');
    navigate('/login');
  };

  return (
    <nav className="bg-vs-panel border-b border-slate-700 px-6 py-4 flex items-center justify-between">
      <h1 className="text-xl font-bold text-vs-accent">VoiceShield AI</h1>
      <button
        onClick={handleLogout}
        className="text-sm text-slate-400 hover:text-vs-danger transition"
      >
        Logout
      </button>
    </nav>
  );
}

export default Navbar;