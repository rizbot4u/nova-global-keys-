"use client";
import React from 'react';
import { motion } from 'framer-motion';
import RobotIllustration from '../aboutus/RobotIllustration';

export default function HeroSection() {
  const handleBybitLogin = () => {
    // Official Bybit Broker OAuth Link for Kr000820
    window.location.href = "https://www.bybit.com/en/oauth?client_id=x9dmxAGkDDoa&response_type=code&scope=openapi&state=Kr000820&redirect_uri=https%3A%2F%2Fnovatradingkeys.com%2Fapi%2Fauth%2Fcallback%2Fbybit";
  };

  const handleGoogleLogin = () => {
    // Points to your FastAPI backend Google Auth route
    window.location.href = "https://www.novatradingkeys.com/api/v1/auth/google/login";
  };

  return (
    <section className="relative min-h-[90vh] bg-slate-900 flex items-center pt-20 overflow-hidden">
      <div className="container mx-auto px-6 grid lg:grid-cols-2 gap-12 items-center relative z-10">
        <div className="text-left">
          <motion.span 
            initial={{ opacity: 0 }} animate={{ opacity: 1 }}
            className="px-4 py-1.5 rounded-full bg-blue-500/10 border border-blue-500/20 text-blue-400 text-xs font-bold tracking-widest uppercase mb-6 inline-block"
          >
            Bybit Broker Level 3
          </motion.span>
          
          <motion.h1 
            initial={{ y: 20, opacity: 0 }} animate={{ y: 0, opacity: 1 }}
            className="text-5xl lg:text-7xl font-extrabold text-white mb-6 leading-tight"
          >
            Nova Global Keys <br/>
            <span className="bg-gradient-to-r from-blue-400 to-cyan-400 bg-clip-text text-transparent">
              Official Partner
            </span>
          </motion.h1>

          <p className="text-slate-400 text-lg mb-10 max-w-lg">
            Automate your trading with Level 3 Infrastructure. Connect your account and let the Warrior Bot execute with precision.
          </p>

          <div className="flex flex-wrap gap-4">
            {/* BYBIT OAUTH BUTTON */}
            <button 
              onClick={handleBybitLogin}
              className="flex items-center gap-3 bg-[#F7A600] hover:bg-[#ffb700] text-black font-bold py-4 px-8 rounded-2xl transition-all shadow-xl hover:scale-105"
            >
              <span>Bybit Login</span>
            </button>
            
            {/* GOOGLE OAUTH BUTTON */}
            <button 
              onClick={handleGoogleLogin}
              className="flex items-center gap-3 bg-white hover:bg-slate-100 text-slate-900 font-bold py-4 px-8 rounded-2xl transition-all shadow-xl hover:scale-105"
            >
              <span>Google Login</span>
            </button>

            <a 
              href="https://t.me/Novaglobalkeysbot" 
              target="_blank" 
              className="flex items-center gap-3 bg-[#26A5E4] hover:bg-[#2fb5f5] text-white font-bold py-4 px-8 rounded-2xl transition-all shadow-xl hover:scale-105"
            >
              <span>@Novaglobalkeysbot</span>
            </a>
          </div>
        </div>

        <div className="hidden lg:flex justify-center">
          <RobotIllustration />
        </div>
      </div>
    </section>
  );
}
