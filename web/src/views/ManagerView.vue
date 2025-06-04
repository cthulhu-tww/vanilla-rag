<template>
  <div class="flex flex-col h-screen bg-gray-50 overflow-hidden">
    <div class="navbar bg-base-100 justify-center">
      <ul class="menu menu-md  menu-horizontal bg-base-200 rounded-box">
        <li v-for="(menu,index) in menus" :key="index">
          <a @click="navigateTo(menu)" :class="{'active':menu.active}">
            <div v-html="menu.icon"></div>
            {{ menu.title }}
          </a>
        </li>
      </ul>
      <div
        class="avatar placeholder absolute right-14 cursor-pointer dropdown dropdown-bottom dropdown-end">
        <div tabindex="0" class="flex items-center space-x-3">
          <div
            class="w-8 h-8 rounded-full bg-[#6653e8] flex items-center justify-center text-white">
            <span class="text-xs">{{ currentUser[0].toUpperCase() }}</span>
          </div>
        </div>
        <ul tabindex="0"
            class="dropdown-content z-[1] menu p-2 shadow bg-base-100 rounded w-40 mt-1">
          <li><i class="fa fa-desktop" aria-hidden="true"
                 @click="router.push({ name: 'chat' })">首页</i></li>
          <li><i class="fa fa-sign-out" aria-hidden="true" @click="store.dispatch('auth/logout')">登出</i>
          </li>
        </ul>
      </div>
    </div>
    <div class="flex-1 flex flex-col">
      <component :is="currentComponent"/>
    </div>
  </div>
</template>

<script setup>
import {ref} from 'vue'
import DocumentManagerView from '@/views/DocumentManagerView.vue'
import KnowledgeBaseManager from '@/views/KnowledgeBaseManager.vue'
import router from "@/router/index.js";
import {useStore} from 'vuex'

const store = useStore()

// 获取当前用户信息
const currentUser = store.getters['auth/currentUser']


const menus = [
  {
    title: '文档', component: DocumentManagerView, icon: `<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"
                 stroke-width="1.5" stroke="currentColor" class="h-5 w-5">
              <path stroke-linecap="round" stroke-linejoin="round"
                    d="M19.5 14.25v-2.625a3.375 3.375 0 0 0-3.375-3.375h-1.5A1.125 1.125 0 0 1 13.5 7.125v-1.5a3.375 3.375 0 0 0-3.375-3.375H8.25m2.25 0H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 0 0-9-9Z" />
            </svg>`, active: true
  },
  {
    title: '知识库', component: KnowledgeBaseManager, icon: `<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"
                 stroke-width="1.5" stroke="currentColor" class="h-5 w-5">
              <path stroke-linecap="round" stroke-linejoin="round"
                    d="M12 6.042A8.967 8.967 0 0 0 6 3.75c-1.052 0-2.062.18-3 .512v14.25A8.987 8.987 0 0 1 6 18c2.305 0 4.408.867 6 2.292m0-14.25a8.966 8.966 0 0 1 6-2.292c1.052 0 2.062.18 3 .512v14.25A8.987 8.987 0 0 0 18 18a8.967 8.967 0 0 0-6 2.292m0-14.25v14.25" />
            </svg>`, active: false
  },
]

const currentComponent = ref(DocumentManagerView)
const navigateTo = (menu) => {
  currentComponent.value = menu.component
  menus.forEach(item => {
    item.active = false
  })
  menu.active = true
}
</script>
