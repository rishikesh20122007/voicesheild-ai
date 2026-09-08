import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { loginUser } from '../services/api';

function Login() {
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const response = await loginUser({ email, password });
      localStorage.setItem('vs_token', response.data.access_token);
      navigate('/dashboard');
    } catch (err) {
      const detail = err.response?.data?.detail || 'Login failed. Please try again.';
      setError(detail);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-vs-dark flex items-center justify-center px-4">
      <div className="bg-vs-panel p-8 rounded-lg shadow-xl border border-slate-700 w-full max-w-md">
        <h1 className="text-2xl font-bold text-vs-accent mb-1">VoiceShield AI</h1>
        <p className="text-slate-400 text-sm mb-6">Sign in to your account</p>

        {error && (
          <div className="bg-red-900/30 border border-vs-danger text-red-300 text-sm rounded p-3 mb-4">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm text-slate-300 mb-1">Email</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              className="w-full bg-slate-800 border border-slate-600 rounded px-3 py-2 text-slate-100 focus:outline-none focus:border-vs-accent"
              placeholder="you@example.com"
            />
          </div>

          <div>
            <label className="block text-sm text-slate-300 mb-1">Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              className="w-full bg-slate-800 border border-slate-600 rounded px-3 py-2 text-slate-100 focus:outline-none focus:border-vs-accent"
              placeholder="••••••••"
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-vs-accent text-vs-dark font-semibold py-2 rounded hover:bg-cyan-300 transition disabled:opacity-50"
          >
            {loading ? 'Signing in...' : 'Sign In'}
          </button>
        </form>

        <p className="text-slate-400 text-sm mt-4 text-center">
          Don't have an account?{' '}
          <Link to="/register" className="text-vs-accent hover:underline">
            Register
          </Link>
        </p>
      </div>
    </div>
  );
}

export default Login;