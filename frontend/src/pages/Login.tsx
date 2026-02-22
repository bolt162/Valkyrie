import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Shield } from 'lucide-react';
import { Button } from '../components/Button';
import { Input } from '../components/Input';
import { useTheme } from '../contexts/ThemeContext';

export const Login: React.FC = () => {
  const navigate = useNavigate();
  const { theme } = useTheme();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (email === 'ksap@valkyrie.ai' && password === 'eq2(C3G;QE62') {
      localStorage.setItem('valkyrie_authenticated', 'true');
      navigate('/app/dashboard');
    } else {
      setError('Invalid email or password');
    }
  };

  return (
    <div className="min-h-screen bg-light-bg dark:bg-black flex items-center justify-center px-4 dark:scanlines transition-colors duration-300">
      <div className="w-full max-w-md">
        <div className="bg-white dark:bg-[#0a0a0a] border border-green-500/30 rounded-lg p-8 dark:glow-green shadow-lg">
          <div className="flex flex-col items-center mb-8">
            <img
              src={theme === 'dark' ? '/white_logo.png' : '/black_logo.png'}
              alt="Valkyrie Logo"
              className="h-16 w-16 object-contain mb-4"
              onError={(e) => {
                e.currentTarget.style.display = 'none';
                e.currentTarget.nextElementSibling?.classList.remove('hidden');
              }}
            />
            <Shield className="h-12 w-12 text-green-500 mb-4 hidden" />
            <h1 className="text-2xl font-mono font-bold text-green-600 dark:text-green-500 text-center dark:text-glow">
              Sign in to Valkyrie
            </h1>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            {error && (
              <div className="p-3 rounded-lg bg-red-500/10 border border-red-500/30 text-red-500 text-sm text-center">
                {error}
              </div>
            )}

            <Input
              label="Email"
              type="email"
              placeholder="security@company.com"
              value={email}
              onChange={(e) => { setEmail(e.target.value); setError(''); }}
              required
            />

            <Input
              label="Password"
              type="password"
              placeholder="Enter your password"
              value={password}
              onChange={(e) => { setPassword(e.target.value); setError(''); }}
              required
            />

            <Button type="submit" className="w-full mt-6">
              Sign In
            </Button>
          </form>

          <div className="mt-6 text-center">
            <Link
              to="/"
              className="text-green-600 dark:text-green-500 hover:text-green-500 dark:hover:text-green-400 text-sm transition-colors"
            >
              Back to home
            </Link>
          </div>
        </div>

        <p className="text-center text-gray-500 dark:text-gray-500 text-xs mt-4">
          Authorized personnel only
        </p>
      </div>
    </div>
  );
};
