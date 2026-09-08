import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { registerUser, loginUser } from '../services/api';

function Register() {
  const navigate = useNavigate();
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      await registerUser({ name, email, password });
      // Automatically log in right after registering, for a smoother UX
      const loginResponse = await loginUser({ email, password });
      localStorage.setItem('vs_token', loginResponse.data.access_token);
      navigate('/dashboard');
    } catch (err) {
      const detail = err.response?.data?.detail || 'Registration failed. Please try again.';
      setError(detail);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-vs-dark flex items-center justify-center px-4">
      <div className="bg-vs-panel p-8 rounded-lg shadow-xl border border-slate-700 w-full max-w-md">
        <h1 className="text-2xl font-bold text-vs-accent mb-1">VoiceShield AI</h1>
        <p className="text-slate-400 text-sm mb-6">Create your account</p>

        {error && (
          <div className="bg-red-900/30 border border-vs-danger text-red-300 text-sm rounded p-3 mb-4">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm text-slate-300 mb-1">Full Name</label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              required
              className="w-full bg-slate-800 border border-slate-600 rounded px-3 py-2 text-slate-100 focus:outline-none focus:border-vs-accent"
              placeholder="Your Name"
            />
          </div>

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
              minLength={8}
              className="w-full bg-slate-800 border border-slate-600 rounded px-3 py-2 text-slate-100 focus:outline-none focus:border-vs-accent"
              placeholder="At least 8 characters"
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-vs-accent text-vs-dark font-semibold py-2 rounded hover:bg-cyan-300 transition disabled:opacity-50"
          >
            {loading ? 'Creating account...' : 'Create Account'}
          </button>
        </form>

        <p className="text-slate-400 text-sm mt-4 text-center">
          Already have an account?{' '}
          <Link to="/login" className="text-vs-accent hover:underline">
            Sign In
          </Link>
        </p>
      </div>
    </div>
  );
}

export default Register;