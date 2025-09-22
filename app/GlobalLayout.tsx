'use client';

import { useEffect, useState } from 'react';
import { useTheme } from 'next-themes';

export default function GlobalLayout({ children }: { children: React.ReactNode }) {
  const { resolvedTheme } = useTheme();
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    // Mark component as mounted
    setMounted(true);
  }, []);

  // Determine background style based on theme, but only after mounting
  const backgroundStyle = mounted ? {
    zIndex: -1,
    backgroundImage: resolvedTheme === 'dark'
      ? 'linear-gradient(135deg, #053230 0%, #064641 25%, #085c56 50%, #0A5E5C 75%, #0d7b77 100%)'
      : 'linear-gradient(135deg, #edfaf6 0%, #def7ef 25%, #c7f2e6 50%, #a9ebd9 75%, #7ee0c6 100%)',
    backgroundSize: '400% 400%',
    animation: 'gradient 15s ease infinite',
  } : {
    // Default styles that will match the server render
    zIndex: -1
  };

  return (
    <>
      {/* Background wrapper with conditional styles */}
      <div className="fixed inset-0" style={backgroundStyle}>
        {/* Optional overlay */}
        <div className="absolute inset-0 bg-black opacity-10"></div>
      </div>
      {children}
    </>
  );
}
