import axios from 'axios';
import serverUrl from '../mixin/url';
import authHeader from '../mixin/authHeader';

const initialState = {
  products: [],
  error: null,
  loading: false,
};

const getters = {
  products: (state) => state.products,
  error: (state) => state.error,
  loading: (state) => state.loading,
};

const authentication = {
  namespaced: true,
  state: initialState,
  getters,
  actions: {
    getProducts({ commit }, { token }) {
      commit('inProgress', true);
      return new Promise((resolve, reject) => {
        axios({
          method: 'get',
          url: `${serverUrl()}/products`,
          headers: authHeader(token),
        }).then(({ data }) => {
          commit('addProducts', data);
          resolve(data);
        }).catch((error) => {
          commit('setDataError', error);
          reject(error);
        }).finally(() => {
          commit('inProgress', false);
        });
      });
    },
  },
  mutations: {
    addProducts(state, products) {
      state.products = products;
    },
    inProgress(state, status) {
      state.loading = status;
    },
    setDataError(state, error) {
      state.error = error;
    },
  },
};

export default authentication;
