import React, { useState } from 'react';
import SignIn from './SignIn';
import SignUp from './SignUp';

export default function App() {
  const [isSignUp, setIsSignUp] = useState(false);
  const [prefilledEmail, setPrefilledEmail] = useState('');
  const [signupSuccess, setSignupSuccess] = useState(false);

  const handleSignUpSuccess = (email: string) => {
    setPrefilledEmail(email);
    setSignupSuccess(true);
    setIsSignUp(false);
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100">
      <div className="max-w-md mx-auto pt-6 px-4">
        <div className="flex bg-slate-900 p-1 rounded-xl border border-slate-800 mb-4">
          <button
            onClick={() => {
              setIsSignUp(false);
              setSignupSuccess(false);
            }}
            className={`flex-1 py-2 text-sm font-semibold rounded-lg transition-all ${
              !isSignUp ? 'bg-indigo-600 text-white shadow' : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            Sign In
          </button>
          <button
            onClick={() => setIsSignUp(true)}
            className={`flex-1 py-2 text-sm font-semibold rounded-lg transition-all ${
              isSignUp ? 'bg-indigo-600 text-white shadow' : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            Sign Up
          </button>
        </div>
      </div>

      {isSignUp ? (
        <SignUp onSignUpSuccess={handleSignUpSuccess} />
      ) : (
        <SignIn initialEmail={prefilledEmail} showSuccessMessage={signupSuccess} />
      )}
    </div>
  );
}
