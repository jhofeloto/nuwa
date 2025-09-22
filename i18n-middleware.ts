// i18n-middleware.ts
import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

// Supported languages
const supportedLocales = ['en', 'es'];
const defaultLocale = 'en';

// Cookie name for storing language preference
export const COOKIE_NAME = 'i18next';

// Simple language detector function (replaces accept-language dependency)
function detectLanguage(acceptLanguageHeader: string | null): string {
  if (!acceptLanguageHeader) return defaultLocale;
  
  // Parse Accept-Language header
  const languages = acceptLanguageHeader.split(',')
    .map(lang => {
      const [value, quality = 'q=1.0'] = lang.trim().split(';');
      const q = parseFloat(quality.replace('q=', ''));
      return { value: value.split('-')[0].toLowerCase(), q };
    })
    .sort((a, b) => b.q - a.q);
  
  // Find first supported language
  const matchedLanguage = languages.find(lang => 
    supportedLocales.includes(lang.value)
  );
  
  return matchedLanguage ? matchedLanguage.value : defaultLocale;
}

// This middleware handles language detection and routing
export function middleware(request: NextRequest) {
  // Get the pathname
  const pathname = request.nextUrl.pathname;
  
  // Skip for specific paths
  if (
    pathname.startsWith('/_next') ||
    pathname.startsWith('/api') ||
    pathname.includes('.') || // Skip files
    pathname === '/favicon.ico'
  ) {
    return NextResponse.next();
  }
  
  // Check if the pathname already has a locale prefix
  const pathnameHasLocale = supportedLocales.some(locale => 
    pathname === `/${locale}` || pathname.startsWith(`/${locale}/`)
  );
  
  if (pathnameHasLocale) return NextResponse.next();
  
  // Determine locale
  let locale;
  
  // Try getting locale from cookie
  const cookieLocale = request.cookies.get(COOKIE_NAME);
  if (cookieLocale && supportedLocales.includes(cookieLocale.value)) {
    locale = cookieLocale.value;
  } else {
    // Use Accept-Language header as fallback
    locale = detectLanguage(request.headers.get('Accept-Language'));
  }
  
  // Redirect to the localized path
  return NextResponse.redirect(
    new URL(`/${locale}${pathname.startsWith('/') ? pathname : `/${pathname}`}`, request.url)
  );
}

// Configure which paths this middleware applies to
export const config = {
  // Skip static files, API routes, and internal Next.js routes
  matcher: ['/((?!api|_next/static|_next/image|favicon.ico|sitemap.xml|locales).*)'],
};