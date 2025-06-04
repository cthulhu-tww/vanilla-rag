<template>
  <slot name="trigger" :toggle="toggleDropdown" :isOpen="isOpen"
        :triggerAttrs="{ ref: setTriggerRef }"></slot>

  <!-- 只有在 isOpen 为 true 时才渲染 Teleport 内容 -->
  <Teleport to="body" v-if="isOpen">
    <div
      class="fixed z-[9999]"
      :style="dropdownPosition"
    >
      <div
        tabindex="0"
        class="dropdown-content"
        :class="menuClasses"
        @click.stop
        ref="menuRef"
      >
        <slot name="content"></slot>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount, nextTick, watch } from 'vue'

const props = defineProps({
  position: {
    type: String,
    default: 'bottom',
    validator: (value) => ['bottom', 'top', 'left', 'right'].includes(value)
  },
  align: {
    type: String,
    default: 'start',
    validator: (value) => ['start', 'center', 'end'].includes(value)
  },
  closeOnClickOutside: {
    type: Boolean,
    default: true
  },
  closeOnScroll: {
    type: Boolean,
    default: true
  }
})

const emit = defineEmits(['open', 'close', 'toggle'])

const isOpen = ref(false)
const triggerRef = ref(null)
const menuRef = ref(null)
const dropdownPosition = ref({ top: '0px', left: '0px' })

const setTriggerRef = (el) => {
  triggerRef.value = el
}


const toggleDropdown = async () => {
  isOpen.value = !isOpen.value

  if (isOpen.value) {
    await nextTick()
    updatePosition()
    emit('open')
  } else {
    emit('close')
  }

  emit('toggle', isOpen.value)
}

const open = async () => {
  if (isOpen.value) return
  isOpen.value = true
  await nextTick()
  updatePosition()
  emit('open')
  emit('toggle', true)
}

const close = () => {
  if (!isOpen.value) return
  isOpen.value = false
  emit('close')
  emit('toggle', false)
}

defineExpose({
  open,
  close,
  toggle: toggleDropdown
})

const updatePosition = () => {
  if (!triggerRef.value?.$el && !triggerRef.value) return
  const triggerEl = triggerRef.value?.$el || triggerRef.value
  if (!triggerEl || !menuRef.value) return

  const triggerRect = triggerEl.getBoundingClientRect()
  const menuRect = menuRef.value.getBoundingClientRect()
  const scrollY = window.scrollY || window.pageYOffset
  const scrollX = window.scrollX || window.pageXOffset

  let top = 0
  let left = 0

  switch (props.position) {
    case 'bottom':
      top = triggerRect.bottom + scrollY
      left = triggerRect.left + scrollX
      break
    case 'top':
      top = triggerRect.top + scrollY - menuRect.height
      left = triggerRect.left + scrollX
      break
    case 'left':
      top = triggerRect.top + scrollY
      left = triggerRect.left + scrollX - menuRect.width
      break
    case 'right':
      top = triggerRect.top + scrollY
      left = triggerRect.right + scrollX
      break
  }

  if (props.align === 'center') {
    left = triggerRect.left + scrollX + (triggerRect.width / 2) - (menuRect.width / 2)
  } else if (props.align === 'end') {
    if (props.position === 'bottom' || props.position === 'top') {
      left = triggerRect.right + scrollX - menuRect.width
    }
  }

  const viewportWidth = window.innerWidth
  const viewportHeight = window.innerHeight

  if (left + menuRect.width > viewportWidth + scrollX) {
    left = viewportWidth + scrollX - menuRect.width - 5
  } else if (left < scrollX) {
    left = scrollX + 5
  }

  if (top + menuRect.height > viewportHeight + scrollY) {
    top = viewportHeight + scrollY - menuRect.height - 5
  } else if (top < scrollY) {
    top = scrollY + 5
  }

  dropdownPosition.value = {
    top: `${top}px`,
    left: `${left}px`
  }
}

const menuClasses = computed(() => {
  const positionClasses = {
    bottom: 'origin-top',
    top: 'origin-bottom',
    left: 'origin-right',
    right: 'origin-left'
  }

  return [
    positionClasses[props.position],
    'animate-[fadeIn_0.2s_ease-out]'
  ]
})

const handleClickOutside = (event) => {
  if (!props.closeOnClickOutside || !isOpen.value) return

  const triggerEl = triggerRef.value?.$el || triggerRef.value
  const clickedInsideMenu = menuRef.value?.contains(event.target)
  const clickedInsideTrigger = triggerEl?.contains(event.target)

  if (!clickedInsideMenu && !clickedInsideTrigger) {
    close()
  }
}

const handleScroll = () => {
  if (!isOpen.value) return

  if (props.closeOnScroll) {
    close()
  } else {
    updatePosition()
  }
}

const handleKeydown = (event) => {
  if (!isOpen.value) return

  if (event.key === 'Escape') {
    close()
    const triggerEl = triggerRef.value?.$el || triggerRef.value
    triggerEl?.focus()
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
  window.addEventListener('scroll', handleScroll, { passive: true })
  document.addEventListener('keydown', handleKeydown)
})

onBeforeUnmount(() => {
  document.removeEventListener('click', handleClickOutside)
  window.removeEventListener('scroll', handleScroll)
  document.removeEventListener('keydown', handleKeydown)
  const dropdowns = document.querySelectorAll('.dropdown-content')
  dropdowns.forEach(el => {
    if (el.closest('body')) {
      el.parentNode.removeChild(el)
    }
  })
})
</script>

<style scoped>
.dropdown-content {
  @apply shadow-lg bg-base-100 rounded-box min-w-[120px] overflow-hidden;
  transform-origin: var(--dropdown-transform-origin);
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: scale(0.95);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}
</style>
