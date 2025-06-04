<template>
  <div class="min-h-screen flex flex-col items-center justify-center bg-white px-4">
    <!-- 404动画 -->
    <div class="text-center mb-8">
      <div class="error-404 text-9xl font-bold mb-4 gradient-text">
        <span class="digit" id="digit4">4</span>
        <span class="digit" id="digit0">0</span>
        <span class="digit" id="digit4-2">4</span>
      </div>
      <div id="error-text">
        <h1 class="text-3xl font-semibold mb-2 text-gray-800">页面未找到</h1>
        <p class="text-gray-500 max-w-md mx-auto">
          您访问的页面不存在或已被移动，请检查URL或返回首页</p>
      </div>
    </div>

    <!-- 操作按钮 -->
    <div class="flex flex-col sm:flex-row gap-4 mt-8">
      <a href="/" id="home-btn"
         class="btn btn-primary bg-[#6653e8] border-[#6653e8] hover:bg-[#5748c7] hover:border-[#5748c7] text-white">
        返回首页
      </a>
    </div>

    <!-- 装饰元素 -->
    <div class="absolute bottom-10 left-10 w-16 h-16 rounded-full bg-[#6653e8] opacity-10 bounce"
         style="animation-delay: 0.2s;"></div>
    <div class="absolute top-20 right-20 w-24 h-24 rounded-full bg-[#6653e8] opacity-10 bounce"
         style="animation-delay: 0.4s;"></div>
  </div>
</template>
<script setup>
import anime from 'animejs'
import { onMounted } from 'vue'

onMounted(() => {
  // 快速404数字动画
  anime.timeline({
    duration: 800,
    easing: 'easeOutExpo'
  })
    .add({
      targets: '#digit4',
      translateY: [-50, 0],
      opacity: [0, 1],
      duration: 200
    })
    .add({
      targets: '#digit0',
      translateY: [-50, 0],
      opacity: [0, 1],
      duration: 200
    }, '-=100')
    .add({
      targets: '#digit4-2',
      translateY: [-50, 0],
      opacity: [0, 1],
      duration: 200
    }, '-=100')
    .add({
      targets: '.error-404',
      scale: [1, 1.05, 1],
      duration: 300,
      easing: 'easeInOutSine'
    })

  // 错误文本快速显示
  anime({
    targets: '#error-text',
    opacity: [0, 1],
    translateY: [10, 0],
    delay: 300,
    duration: 300,
    easing: 'easeOutExpo'
  })

  // 按钮快速显示
  anime({
    targets: '#home-btn',
    opacity: [0, 1],
    translateY: [10, 0],
    delay: 400,
    duration: 300,
    easing: 'easeOutExpo'
  })

  anime({
    targets: '#contact-btn',
    opacity: [0, 1],
    translateY: [10, 0],
    delay: 500,
    duration: 300,
    easing: 'easeOutExpo'
  })

  // 按钮悬停效果
  const buttons = document.querySelectorAll('#home-btn, #contact-btn')
  buttons.forEach(btn => {
    btn.addEventListener('mouseenter', function() {
      anime({
        targets: this,
        scale: 1.05,
        duration: 150
      })
    })
    btn.addEventListener('mouseleave', function() {
      anime({
        targets: this,
        scale: 1,
        duration: 150
      })
    })
  })

  // 404数字持续微动效果
  setInterval(() => {
    anime({
      targets: '.digit',
      translateY: [0, -3],
      duration: 500,
      direction: 'alternate',
      easing: 'easeInOutSine'
    })
  }, 2000)
})

</script>
<style scoped>
.gradient-text {
  background: linear-gradient(90deg, #6653e8, #8a7aed);
  -webkit-background-clip: text;
  background-clip: text;
  color: #6653e8;
}

.error-404 {
  position: relative;
}

.error-404 .digit {
  display: inline-block;
  position: relative;
}

.bounce {
  animation: bounce 0.8s ease infinite alternate;
}

@keyframes bounce {
  to {
    transform: translateY(-5px);
  }
}
</style>
