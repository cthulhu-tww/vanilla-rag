<template>
  <div ref="textContainer"
       class="font-medium my-1 text-[#6653e8]">
    <span v-for="(char, index) in props.text" :key="index">{{ char }}</span>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import anime from 'animejs'

const props = defineProps({
  text: {
    type: String,
    default: ''
  }
})

const textContainer = ref(null)
let animationInstance = null

onMounted(() => {
  if (!textContainer.value) return

  const characters = textContainer.value.querySelectorAll('span')

  animationInstance = anime.timeline({
    loop: true,
    easing: 'easeInOutSine'
  })

  characters.forEach((char, index) => {
    animationInstance.add({
      targets: char,
      color: ['#3B82F6'],
      duration: 1500,
      delay: index * 150,
      direction: 'normal'
    }, 0)
  })
})

onUnmounted(() => {
  if (animationInstance) {
    animationInstance.pause()
    animationInstance = null
  }
})
</script>

<style scoped>
/* 这里可以添加额外的自定义样式，如果需要的话 */
</style>
