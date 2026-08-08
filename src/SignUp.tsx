import React, { useState } from 'react';
import { supabase } from './supabaseClient';

interface SignUpProps {
  onSignUpSuccess?: (email: string) => void;
  navigateToSignIn?: (email: string) => void;
}

export default function SignUp({ onSignUpSuccess, navigateToSignIn }: SignUpProps = {}) {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    const fullName = name.trim() || email.split('@')[0];

    const { data, error: supabaseError } = await supabase.auth.signUp({
      email,
      password,
      options: {
        data: {
          full_name: fullName,
          username: fullName,
          name: fullName
        }
      }
    });

    // Sync to local database
    try {
      await fetch('/api/auth/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password, name: fullName })
      });
    } catch (e) {}

    setLoading(false);

    if (supabaseError && !supabaseError.message.includes('FetchError')) {
      setError(supabaseError.message);
    } else {
      // Do NOT auto-login. Redirect/pass email to Sign In page.
      if (onSignUpSuccess) {
        onSignUpSuccess(email);
      } else if (navigateToSignIn) {
        navigateToSignIn(email);
      } else {
        const searchParams = new URLSearchParams();
        searchParams.set('email', email);
        searchParams.set('signedUp', 'true');
        window.location.href = `/signin?${searchParams.toString()}`;
      }
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-900 text-slate-100 p-4">
      <div className="w-full max-w-md glass-panel p-8 rounded-2xl border border-slate-700 bg-slate-800/80 shadow-2xl space-y-6">
        <h2 className="text-2xl font-bold text-center text-white">Sign Up</h2>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-xs font-semibold uppercase text-slate-400 mb-1">Full Name / Username</label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              required
              className="w-full px-4 py-2.5 bg-slate-900/80 border border-slate-700 rounded-lg text-slate-100 focus:outline-none focus:border-indigo-500"
              placeholder="John Doe"
            />
          </div>
          <div>
            <label className="block text-xs font-semibold uppercase text-slate-400 mb-1">Email</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              className="w-full px-4 py-2.5 bg-slate-900/80 border border-slate-700 rounded-lg text-slate-100 focus:outline-none focus:border-indigo-500"
              placeholder="you@example.com"
            />
          </div>
          <div>
            <label className="block text-xs font-semibold uppercase text-slate-400 mb-1">Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              className="w-full px-4 py-2.5 bg-slate-900/80 border border-slate-700 rounded-lg text-slate-100 focus:outline-none focus:border-indigo-500"
              placeholder="••••••••"
            />
          </div>
          
          <button
            type="submit"
            disabled={loading}
            className="w-full py-3 bg-gradient-to-r from-indigo-600 to-violet-600 text-white font-semibold rounded-lg shadow-lg hover:from-indigo-500 hover:to-violet-500 transition-all disabled:opacity-50"
          >
            {loading ? 'Signing Up...' : 'Sign Up'}
          </button>

          {error && (
            <p className="text-sm text-red-400 mt-2 text-center bg-red-950/40 border border-red-800/50 p-2 rounded-lg">
              {error}
            </p>
          )}
        </form>
      </div>
    </div>
  );
}
