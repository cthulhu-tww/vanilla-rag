import auth from './modules/auth'
import Vuex from 'vuex' // 确认路径正确

export default new Vuex.Store({
  modules: {
    auth // 属性名必须和调用时的模块名一致
  }
})
