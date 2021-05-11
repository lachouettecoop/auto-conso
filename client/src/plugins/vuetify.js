import Vue from 'vue';
import Vuetify from 'vuetify/lib/framework';
import fr from 'vuetify/es5/locale/fr';
import '@mdi/font/css/materialdesignicons.css';

Vue.use(Vuetify);

export default new Vuetify({
  lang: {
    locales: { fr },
    current: 'fr',
  },
  theme: {
    themes: {
      light: {
        primary: '#445448',
      },
    },
  },
});
