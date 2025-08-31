import { createI18n } from 'vue-i18n';
import { default as en } from './en.json';
import { default as vi } from './vi.json';

const messages = {
    vi,
    en,
    // ja,
};

// Always default to Vietnamese
const getDefaultLocale = (): string => {
    return 'vi';
};

export default createI18n({
    legacy: false,
    locale: getDefaultLocale(), // always "vi"
    fallbackLocale: 'vi',
    messages,
    globalInjection: true,
});
