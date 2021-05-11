import Vue from 'vue';
import Vuex from 'vuex';
import authentication from './authentication';
import odoo from './odoo';

Vue.use(Vuex);

export default new Vuex.Store({
  modules: {
    authentication,
    odoo,
  },
  strict: process.env.NODE_ENV !== 'production',
});
