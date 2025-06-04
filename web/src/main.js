import './assets/main.css'

import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import store from '@/store/index.js'
import VueSelect from 'vue-select'

const app = createApp(App)
app.component('v-select', VueSelect)
app.use(router)
app.use(store)
app.mount('#app')
