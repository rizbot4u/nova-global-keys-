"use client";

import React, { useState } from 'react';
import { motion } from 'framer-motion';
import HeroSection from './HeroSection';
import PricingPlans from './PricingPlans';
import FAQSection from './FAQSection';
import CTASection from './CTASection';

const PlansPage = () => {
  const [billingCycle, setBillingCycle] = useState<'monthly' | 'yearly'>('monthly');

  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-900 via-slate-800 to-slate-900">
      <HeroSection 
        billingCycle={billingCycle} 
        setBillingCycle={setBillingCycle} 
      />
      <PricingPlans billingCycle={billingCycle} />
      <FAQSection />
      <CTASection />
    </div>
  );
};

export default PlansPage;