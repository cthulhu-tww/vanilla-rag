<template>
  <div class="infinite-scroll-container" ref="scrollContainer">
    <!-- 使用插槽渲染内容 -->
    <slot></slot>

    <!-- 加载中状态 -->
    <div v-if="loading" class="flex justify-center items-center py-4">
      <span class="loading loading-spinner loading-md"></span>
      <span class="ml-2">加载中...</span>
    </div>

    <!-- 加载失败提示 -->
    <div v-if="error && !loading" class="text-center py-4 text-error cursor-pointer"
         @click="handleRetry">
      加载失败，请点击重试
    </div>

    <!-- 没有更多数据提示 -->
    <div v-if="noMore && !loading && !error" class="text-center py-2 text-gray-300 text-sm">
      没有更多内容了
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { debounce } from 'lodash-es'

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  },
  noMore: {
    type: Boolean,
    default: false
  },
  load: {
    type: Function,
    required: true
  },
  distance: {
    type: Number,
    default: 0
  },
  disabled: {
    type: Boolean,
    default: false
  },
  immediate: {
    type: Boolean,
    default: true
  },
  delay: {
    type: Number,
    default: 250
  },
  target: {
    type: [String, Object],
    default: null // 可传 window / body / '.custom-selector'
  },
  listenForEvent: {
    type: String,
    default: null // 可监听自定义事件名，比如 "refresh"
  },
  containerClass: {
    type: String,
    default: 'infinite-scroll-container'
  }
})

const emit = defineEmits(['update:modelValue', 'retry'])

// 状态
const loading = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val)
})
const error = ref(false)

// 容器引用
const scrollContainer = ref(null)

let currentTarget = null

// 处理滚动逻辑
const checkInfiniteScroll = () => {
  if (props.disabled || props.noMore || loading.value) return

  const el = currentTarget === window ? document.documentElement : scrollContainer.value

  const isAtBottom = (() => {
    if (currentTarget === window) {
      return (
        window.innerHeight + window.scrollY >= document.body.offsetHeight - props.distance
      )
    } else {
      return (
        el.scrollHeight - el.scrollTop - el.clientHeight <= props.distance
      )
    }
  })()

  if (isAtBottom) {
    loading.value = true
    error.value = false
    props.load().catch(() => {
      error.value = true
    }).finally(() => {
      loading.value = false
    })
  }
}

// 防抖处理
const debouncedCheck = debounce(checkInfiniteScroll, props.delay)

// 滚动事件监听
const handleScroll = () => {
  debouncedCheck()
}

// 监听自定义事件（比如：刷新）
const handleCustomEvent = () => {
  if (props.noMore) {
    error.value = false
  }
}

// 重试方法
const handleRetry = () => {
  if (!loading.value && error.value) {
    emit('retry')
    checkInfiniteScroll()
  }
}

onMounted(() => {
  // 如果指定了 global，则监听 window 滚动
  if (props.target === 'window' || props.target === window) {
    currentTarget = window
    window.addEventListener('scroll', handleScroll)
  } else if (props.target === 'body') {
    currentTarget = document.body
    document.body.addEventListener('scroll', handleScroll)
  } else if (typeof props.target === 'string') {
    currentTarget = document.querySelector(props.target)
    if (currentTarget) {
      currentTarget.addEventListener('scroll', handleScroll)
    }
  } else {
    currentTarget = scrollContainer.value
    scrollContainer.value.addEventListener('scroll', handleScroll)
  }

  // 初始化检查
  if (props.immediate) {
    debouncedCheck()
  }

  // 监听自定义刷新事件
  if (props.listenForEvent) {
    window.addEventListener(props.listenForEvent, handleCustomEvent)
  }
})

onBeforeUnmount(() => {
  // 移除滚动监听
  if (currentTarget && currentTarget.removeEventListener) {
    currentTarget.removeEventListener('scroll', handleScroll)
  }

  // 移除自定义事件监听
  if (props.listenForEvent) {
    window.removeEventListener(props.listenForEvent, handleCustomEvent)
  }
})
</script>
