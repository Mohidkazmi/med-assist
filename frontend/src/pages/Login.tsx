import React from 'react';
import { useNavigate } from 'react-router-dom';

export const Login: React.FC = () => {
  const navigate = useNavigate();

  return (
    <div className="w-full max-w-md bg-slate-900/60 border border-slate-800/80 rounded-2xl p-8 sm:p-10 shadow-2xl backdrop-blur-md flex flex-col items-center text-center animate-fade-in">
      {/* Decorative Locked Padlock icon */}
      <div className="w-16 h-16 bg-slate-950/80 border border-slate-800 rounded-xl flex items-center justify-center text-cyan-400 mb-6">
        <svg xmlns="http://www.w3.org/2000/svg" className="h-8 w-8" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
        </svg>
      </div>

      <h1 className="text-2xl font-bold tracking-tight text-slate-100">
        Login Screen
      </h1>
      
      <p className="mt-3 text-sm text-slate-400">
        This screen will be implemented later.
      </p>

      {/* Action Button */}
      <div className="mt-8 w-full">
        <button
          onClick={() => navigate('/')}
          className="w-full py-3 px-4 rounded-xl text-slate-300 font-semibold bg-slate-800 hover:bg-slate-750 active:scale-[0.98] border border-slate-700/60 hover:border-slate-600 transition-all text-center"
        >
          Back to Home
        </button>
      </div>
    </div>
  );
};
