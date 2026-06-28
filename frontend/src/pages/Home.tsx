import React from 'react';
import { useNavigate } from 'react-router-dom';

export const Home: React.FC = () => {
  const navigate = useNavigate();

  return (
    <div className="w-full max-w-2xl bg-slate-900/60 border border-slate-800/80 rounded-2xl p-8 sm:p-12 shadow-2xl backdrop-blur-md flex flex-col items-center text-center animate-fade-in relative">
      {/* Decorative pulse ring */}
      <div className="absolute -top-12 left-1/2 -translate-x-1/2 w-24 h-24 bg-gradient-to-tr from-cyan-500 to-indigo-500 rounded-2xl flex items-center justify-center shadow-lg shadow-cyan-500/20 rotate-12">
        {/* Simple stethoscope/scribe icon representation */}
        <svg xmlns="http://www.w3.org/2000/svg" className="h-12 w-12 text-slate-950 -rotate-12" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
        </svg>
      </div>

      <div className="mt-10">
        <h1 className="text-3xl sm:text-4xl font-extrabold tracking-tight text-slate-100 sm:leading-none">
          AI Medical Scribe Platform
        </h1>
        <p className="mt-4 text-base text-slate-400 max-w-md mx-auto">
          Automated clinical recording, transcription, and EHR documentation pipeline.
        </p>
      </div>

      {/* Backend Status Section */}
      <div className="mt-8 p-4 bg-slate-950/60 border border-slate-800 rounded-xl w-full max-w-sm flex items-center justify-between">
        <span className="text-sm font-medium text-slate-400">Backend Status</span>
        <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold bg-slate-900 text-slate-400 border border-slate-700/80 space-x-1.5">
          <span className="w-2 h-2 rounded-full bg-slate-500" />
          <span>(Not Connected Yet)</span>
        </span>
      </div>

      {/* Action Button */}
      <div className="mt-10 w-full max-w-sm">
        <button
          onClick={() => navigate('/login')}
          className="w-full py-3.5 px-6 rounded-xl text-slate-900 font-bold bg-gradient-to-r from-cyan-400 via-sky-400 to-indigo-400 hover:from-cyan-300 hover:to-indigo-300 active:scale-[0.98] transition-all shadow-lg shadow-cyan-500/10 hover:shadow-cyan-500/20 text-center"
        >
          Go to Login
        </button>
      </div>
    </div>
  );
};
