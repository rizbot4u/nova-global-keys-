"use client";

import React from 'react';
import AnimatedBackground from './AnimatedBackground';
import HeroSection from './HeroSection';
import ContactInfo from './ContactInfo';
import ContactForm from './ContactForm';

const ContactPage = () => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-600/20 to-slate-900 overflow-hidden">
      <AnimatedBackground />
      
      <div className="relative z-10 max-w-7xl mx-auto px-3 sm:px-4 md:px-6 lg:px-8 py-12 sm:py-16 md:py-20">
        <HeroSection />
        
        {/* Main Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 sm:gap-12 md:gap-16 lg:gap-20">
          <ContactInfo />
          <ContactForm />
        </div>
      </div>
    </div>
  );
};

export default ContactPage;