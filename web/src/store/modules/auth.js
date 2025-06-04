import {login} from '@/api/user.js'
import router from "@/router/index.js";

const state = {
  token: localStorage.getItem('token') || null,
  username: localStorage.getItem('username') || null
}

const mutations = {
  SET_TOKEN(state, token) {
    state.token = token
    localStorage.setItem('token', token)
  },
  CLEAR_TOKEN(state) {
    state.token = null
    localStorage.removeItem('token')
  },
  SET_USER(state, username) {
    state.user = username
    localStorage.setItem('username', username)
  },
  CLEAR_USER(state) {
    state.user = null
    localStorage.removeItem('username')
  }
}

const actions = {
  login({commit}, data) {
    return new Promise((resolve, reject) => {
      login(data)
        .then(response => {
          commit('SET_TOKEN', response.data.token)
          commit('SET_USER', response.data.username)
          resolve(response)
        })
        .catch(error => {
          commit('CLEAR_TOKEN')
          reject(error)
        })
    })
  },

  logout({commit}) {
    return new Promise((resolve) => {
      commit('CLEAR_TOKEN')
      commit('CLEAR_USER')
      resolve()
      router.push({name: 'login'})
    })
  }
}

const getters = {
  isAuthenticated: state => !!state.token,
  currentUser: state => state.username,
  authToken: state => state.token
}

export default {
  namespaced: true,
  state,
  mutations,
  actions,
  getters
}
