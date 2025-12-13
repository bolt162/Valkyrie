import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Shield } from 'lucide-react';
import { Button } from '../components/Button';
import { Input } from '../components/Input';

export const Login: React.FC = () => {
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    navigate('/app/dashboard');
  };

  return (
    <div className="min-h-screen bg-black flex items-center justify-center px-4 scanlines">
      <div className="w-full max-w-md">
        <div className="bg-[#0a0a0a] border border-green-500/30 rounded-lg p-8 glow-green">
          <div className="flex flex-col items-center mb-8">
            <Shield className="h-12 w-12 text-green-500 mb-4" />
            <h1 className="text-xl font-mono font-bold text-white text-center">
              Sign in to
            </h1>
            <p className="text-green-500 font-mono font-bold text-glow">
              LLM Red Team Auditor
            </p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            <Input
              label="Email"
              type="email"
              placeholder="security@company.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />

            <Input
              label="Password"
              type="password"
              placeholder="Enter your password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />

            <Button type="submit" className="w-full mt-6">
              Sign In
            </Button>
          </form>

          <div className="mt-6 text-center">
            <Link
              to="/"
              className="text-green-500 hover:text-green-400 text-sm transition-colors"
            >
              Back to home
            </Link>
          </div>
        </div>

        <p className="text-center text-gray-500 text-xs mt-4">
          Demo mode: Click Sign In to access the dashboard
        </p>
      </div>
    </div>
  );
};
