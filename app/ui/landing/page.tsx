'use client';

import dynamic from 'next/dynamic';

const HeroSection = dynamic(() => import('./HeroSection'), { ssr: false });
const FeaturesSection = dynamic(() => import('./FeaturesSection'), { ssr: false });
const WorkflowSection = dynamic(() => import('./WorkflowSection'), { ssr: false });
const CallToActionSection = dynamic(() => import('./CallToActionSection'), { ssr: false });


export default function Landing() {
    return (
      <div>
        <HeroSection />
        <FeaturesSection />
        <WorkflowSection />
        <CallToActionSection />
      </div>
    );
  }