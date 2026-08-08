import React, { useState, useEffect } from 'react';
import { supabase } from '../supabaseClient';

export default function SignIn({ initialEmail, showSuccessMessage, successMessage } = {}) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const queryParams = new URLSearchParams(window.location.search);
    const paramEmail = queryParams.get('email');
    const isSignedUp = queryParams.get('signedUp') === 'true' || queryParams.get('registered') === 'true';

    const prefilledEmail = initialEmail || paramEmail || '';
    if (prefilledEmail) {
      setEmail(prefilledEmail);
    }

    if (successMessage) {
      setSuccess(successMessage);
    } else if (showSuccessMessage || isSignedUp) {
      setSuccess('Your account has been created. Please check your email and verify your address before logging in.');
    }
  }, [initialEmail, showSuccessMessage, successMessage]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    const { data, error: supabaseError } = await supabase.auth.signInWithPassword({
      email,
      password,
    });

    setLoading(false);

    if (supabaseError) {
      setError(supabaseError.message);
    } else if (data?.user || data?.session) {
      try {
        await fetch('/api/auth/supabase-sync', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            email: data.user.email,
            name: data.user.user_metadata?.full_name || data.user.email.split('@')[0],
            supabase_id: data.user.id
          })
        });
      } catch (e) {}
      window.location.href = '/';
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-900 text-slate-100 p-4">
      <div className="w-full max-w-md glass-panel p-8 rounded-2xl border border-slate-700 bg-slate-800/80 shadow-2xl space-y-6">
        <h2 className="text-2xl font-bold text-center text-white">Sign In</h2>

        {success && (
          <div className="p-3.5 rounded-lg text-sm bg-emerald-950/50 border border-emerald-800/60 text-emerald-300 text-center font-medium leading-relaxed shadow-sm">
            {success}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
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
            {loading ? 'Signing In...' : 'Sign In'}
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
