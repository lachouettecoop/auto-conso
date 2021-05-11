import axios from 'axios';
import jwt_decode from 'jwt-decode'; // eslint-disable-line camelcase
import serverUrl from '../mixin/url';

const initialState = { status: {}, token: null, user: (process.env.NODE_ENV === 'production') ? null : { role: 'admin' } };

const getters = {
  token: (state) => state.token,
  user: (state) => state.user,
};

const authentication = {
  namespaced: true,
  state: initialState,
  getters,
  actions: {
    login({ commit }, { email, password }) {
      return new Promise((resolve, reject) => {
        axios({
          method: 'post',
          url: `${serverUrl()}/login`,
          data: { email, password },
        }).then(({ data }) => {
          commit('loginSuccess', data);
          resolve(data);
        }).catch((error) => {
          commit('logout');
          reject(error);
        });
      });
    },
    logout({ commit }) {
      commit('logout');
    },
  },
  mutations: {
    loginSuccess(state, data) {
      if (data.token) {
        const user = jwt_decode(data.token);
        state.token = data.token;
        state.user = user;
      }
    },
    logout(state) {
      state.token = null;
      state.user = null;
    },
  },
};

export default authentication;
