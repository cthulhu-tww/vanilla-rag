<template>
  <div
    class="min-h-screen flex flex-col items-center justify-center bg-white px-4 relative overflow-hidden">
    <div class="w-full max-w-sm z-10">
      <div class="text-center mb-8 floating">
        <h1 id="logo-text" class="text-5xl font-bold mb-2 opacity-0 gradient-text">Vanilla RAG</h1>
        <p id="tagline" class="text-gray-500 opacity-0">智能检索增强平台</p>
      </div>
      <div id="login-card" class="card bg-base-100 shadow-sm border border-gray-100 opacity-0">
        <div class="card-body p-8">
          <label class="swap swap-flip" :class="{'swap-active':  loginForm}">
            <input type="checkbox"/>
            <h2 id="login-title" class="swap-on text-2xl font-semibold mb-6 gradient-text">
              登录您的账户</h2>
            <h2 id="login-title" class="swap-off text-2xl font-semibold mb-6 gradient-text">
              注册账号</h2>
          </label>


          <form class="space-y-5" @submit.prevent="submit">
            <div>
              <div class="form-control">
                <label class="label">
                  <span class="label-text text-gray-600">账号</span>
                </label>
                <input
                  placeholder="请输入账号"
                  class="input input-bordered w-full input-focus opacity-0"
                  v-model="form.username"
                  required
                />
              </div>
            </div>

            <div>
              <div class="form-control">
                <label class="label">
                  <span class="label-text text-gray-600">密码</span>
                </label>
                <input
                  type="password"
                  placeholder="输入您的密码"
                  v-model="form.password"
                  class="input input-bordered w-full input-focus opacity-0"
                  required
                />
              </div>
            </div>

            <div class="flex items-center justify-between mt-2">
              <label class="cursor-pointer label p-0">
                <input type="checkbox" class="checkbox checkbox-primary checkbox-sm"
                       :checked="remember"
                       v-model="remember"/>
                <span class="label-text ml-2 text-gray-600">记住账号</span>
              </label>
              <a href="#" class="text-sm text-[#6653e8] hover:underline"
                 @click="loginForm=false;form.password='';form.username=''"
                 v-if="loginForm">注册</a>
              <a href="#" class="text-sm text-[#6653e8] hover:underline" @click="loginForm=true"
                 v-else>登录</a>
            </div>

            <button
              id="login-btn"
              type="submit"
              class="btn w-full mt-6 bg-[#6653e8] border-[#6653e8] hover:bg-[#5748c7] hover:border-[#5748c7] text-white opacity-0"
            >
              <label class="swap swap-flip" :class="{'swap-active':  loginForm}">
                <input type="checkbox"/>
                <div class="swap-on">
                  登录
                </div>
                <div class="swap-off">
                  注册
                </div>
              </label>
            </button>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import {onMounted, reactive, ref} from 'vue'
import anime from 'animejs'
import {useStore} from 'vuex'
import {register} from "@/api/user.js";

const store = useStore()
const loginState = localStorage.getItem('loginState')
const loginForm = ref(true)
const form = reactive({
  username: '',
  password: ''
})

const remember = ref(false)

if (loginState) {
  const loginStateObj = JSON.parse(loginState)
  form.username = loginStateObj.username
  remember.value = loginStateObj.remember
}

const submit = async () => {
  if (loginForm.value) {
    await store.dispatch('auth/login', form).then(() => {
      if (remember.value) {
        localStorage.setItem('loginState', JSON.stringify({
          username: form.username,
          remember: true
        }))
      } else {
        localStorage.removeItem('loginState')
      }
      window.location.href = '/'
    })
  } else {
    register(form).then(() => {
      loginForm.value = true
      form.password = ''
    })
  }
}

const createAnimation = () => {

  // Logo动画
  anime.timeline()
    .add({
      targets: '#logo-text',
      opacity: [0, 1],
      translateY: [-30, 0],
      duration: 800,
      easing: 'easeOutExpo'
    })
    .add({
      targets: '#logo-text',
      scale: [1, 1.05, 1],
      duration: 1000,
      easing: 'easeInOutSine'
    }, '-=600')

  // 标语动画
  anime({
    targets: '#tagline',
    opacity: [0, 1],
    delay: 500,
    duration: 600,
    easing: 'easeOutExpo'
  })

  // 登录卡片动画
  anime({
    targets: '#login-card',
    opacity: [0, 1],
    translateY: [30, 0],
    delay: 700,
    duration: 600,
    easing: 'easeOutExpo'
  })

  // 输入框动画
  anime({
    targets: '.input',
    opacity: [0, 1],
    translateY: [10, 0],
    delay: anime.stagger(100, {start: 900}),
    duration: 500,
    easing: 'easeOutExpo'
  })

  // 登录按钮动画
  anime({
    targets: '#login-btn',
    opacity: [0, 1],
    scale: [0.9, 1],
    delay: 1200,
    duration: 600,
    easing: 'easeOutElastic'
  })

  // 按钮悬停效果
  const loginBtn = document.getElementById('login-btn')
  loginBtn.addEventListener('mouseenter', function () {
    anime({
      targets: this,
      scale: 1.02,
      duration: 200
    })
  })
  loginBtn.addEventListener('mouseleave', function () {
    anime({
      targets: this,
      scale: 1,
      duration: 200
    })
  })
}

onMounted(() => {
  createAnimation()
})
</script>
<style scoped>
.gradient-text {
  background: linear-gradient(90deg, #6653e8, #8a7aed);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
}

.input-focus:focus {
  border-color: #6653e8 !important;
  box-shadow: 0 0 0 2px rgba(102, 83, 232, 0.2) !important;
}

/* 射线背景动画 */
body {
  overflow: hidden;
}

.ray {
  position: absolute;
  background: linear-gradient(90deg, rgba(102, 83, 232, 0.1), transparent);
  transform-origin: left center;
  height: 1px;
  z-index: 0;
}

/* 浮动动画 */
@keyframes float {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-10px);
  }
}

.floating {
  animation: float 6s ease-in-out infinite;
}
</style>
