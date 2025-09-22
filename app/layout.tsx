'use client';

import "./globals.css";
import "./theme-config.css";
import "@radix-ui/themes/styles.css";
import "./radix-overrides.css";
import { lusitana } from '@/app/ui/fonts';
import { Theme } from "@radix-ui/themes";
import { ThemeProvider } from "@/app/ui/theme-provider";
import Footer from "./ui/footer";
import { Analytics } from "@vercel/analytics/react";
import I18nProviderClientWrapper from "./providers/i18n-client-wrapper";
import "@aws-amplify/ui-react/styles.css";
import dynamic from 'next/dynamic';
import GlobalLayout from "./GlobalLayout";

const Navbar = dynamic(() => import('@/app/ui/navbar/navbar'), { ssr: false });

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body
        className={`${lusitana.className} antialiased bg-background text-foreground`}
      >
        <ThemeProvider
          attribute="class"
          defaultTheme="system"
          enableSystem
        >
          <Theme accentColor="mint" grayColor="slate" scaling="100%" radius="medium">
            <I18nProviderClientWrapper>
              {/* <Auth> */}
                <Navbar />
                <GlobalLayout>
                <main className="min-h-screen">
                  {children}
                </main>
                </GlobalLayout>
                <Analytics />
                <Footer />
              {/* </Auth> */}
            </I18nProviderClientWrapper>
            {/* Uncomment for development to adjust theme visually */}
            {/* <ThemePanel /> */}
          </Theme>
        </ThemeProvider>
      </body>
    </html>
  );
}