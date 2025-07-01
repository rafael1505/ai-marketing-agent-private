import { createTranslator } from 'next-intl';
import { createLocalizedPathnamesNavigation } from 'next-intl/navigation';

export const locales = ['en', 'pt'] as const;
export const defaultLocale = 'en' as const;

export type Locale = (typeof locales)[number];

export const { Link, redirect, usePathname, useRouter } = createLocalizedPathnamesNavigation({ 
  locales,
  pathnames: () => ({
    '/': '/',
    '/dashboard': '/dashboard',
    '/login': '/login',
  }),
  defaultLocale 
});

export function getTranslations(locale: Locale = defaultLocale) {
  try {
    // Use dynamic import to load the translations
    const translations = locale === 'pt' 
      ? require('./locales/pt.json') 
      : require('./locales/en.json');
    return translations;
  } catch (error) {
    console.error(`Failed to load translations for ${locale}:`, error);
    // Fallback to English
    return require('./locales/en.json');
  }
}
