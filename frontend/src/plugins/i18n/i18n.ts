import { createI18n } from 'vue-i18n';
import { default as en } from './en.json';
import { default as vi } from './vi.json';

const messages = {
    vi,
    en,
    // ja,
};

// Load default locale from localStorage or fallback to 'en'
const getDefaultLocale = (): string => {
    if (typeof window !== 'undefined') {
        const saved = window.localStorage.getItem('locale');
        if (saved === 'vi' || saved === 'en') return saved;
    }
    return 'en';
};

const i18n = createI18n({
    legacy: false,
    locale: getDefaultLocale(),
    fallbackLocale: 'en',
    messages,
    globalInjection: true,
});

export default i18n;
