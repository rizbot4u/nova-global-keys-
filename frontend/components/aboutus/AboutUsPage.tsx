"use client";

import React from 'react';
import HeroSection from '../../components/aboutus/HeroSection';
import StatsSection from '../../components/aboutus/StatsSection';
import OurStorySection from '../../components/aboutus/OurStorySection';
import TeamSection from '../../components/aboutus/TeamSection';
import CTASection from '../../components/aboutus/CTASection';

const AboutUsPage = () => {
  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-900 via-slate-800 to-slate-900">
      <HeroSection />
      <StatsSection />
      <OurStorySection />
      <TeamSection />
      <CTASection />
    </div>
  );
};

export default AboutUsPage;