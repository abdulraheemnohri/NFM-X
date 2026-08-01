import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';

const resources = {
  en: {
    translation: {
      app_name: 'NFM-X',
      app_full_name: 'Non-Forgettable Evolutionary AI Memory',
      welcome: 'Welcome to NFM-X',
      loading: 'Loading...',
      error: 'Error',
      success: 'Success',
      cancel: 'Cancel',
      save: 'Save',
      delete: 'Delete',
      edit: 'Edit',
      create: 'Create',
      search: 'Search',
      clear: 'Clear',
      back: 'Back',
      next: 'Next',
      previous: 'Previous',
      nav_dashboard: 'Dashboard',
      nav_memories: 'Memories',
      nav_search: 'Search',
      nav_graph: 'Knowledge Graph',
      nav_analytics: 'Analytics',
      nav_settings: 'Settings'
    }
  },
  ur: {
    translation: {
      app_name: 'NFM-X',
      app_full_name: 'نا بھولنے والی ایولوشنری AI میموری',
      welcome: 'NFM-X میں خوش آمدید',
      loading: 'لوڈ ہو رہا ہے...',
      error: 'خطا',
      success: 'کامیابی',
      cancel: 'منسوخ کریں',
      save: 'محفوظ کریں',
      delete: 'حذف کریں',
      edit: 'ترمیم کریں',
      create: 'بنائیں',
      search: 'تلاش کریں',
      clear: 'صاف کریں',
      back: 'واپس',
      next: 'اگلا',
      previous: 'پچھلا',
      nav_dashboard: 'ڈیش بورڈ',
      nav_memories: 'یاداشتیں',
      nav_search: 'تلاش',
      nav_graph: 'گراف',
      nav_analytics: 'تحلیل',
      nav_settings: 'ترتیبات'
    }
  }
};

i18n
  .use(initReactI18next)
  .init({
    resources,
    lng: 'en',
    fallbackLng: 'en',
    interpolation: {
      escapeValue: false
    }
  });

export default i18n;