// NotifyPlugin.js

const addDom = function (content, type, duration) {
  const container = document.querySelector('.notify-container') || createContainer()
  let alertHtml = `
  <div class="notify-item overflow-hidden transition-all duration-300 ease-in-out">
    <div class="alert alert-${type} shadow-lg max-w-[30vw] mb-2 opacity-0 translate-y-4 transition-all duration-300 ease-in-out">
      <svg xmlns="http://www.w3.org/2000/svg" class="stroke-current shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24">
        ${getAlertIcon(type)}
      </svg>
      <span>${content}</span>
    </div>
  </div>
  `

  // 插入到通知容器顶部（新通知在最上方）
  container.insertAdjacentHTML('afterbegin', alertHtml)

  const newItem = container.firstElementChild

  // 触发入场动画
  requestAnimationFrame(() => {
    newItem.querySelector('.alert').classList.remove('opacity-0', 'translate-y-4')
  })

  // 定时移除
  setTimeout(() => {
    const alertEl = newItem.querySelector('.alert')

    // 应用离场动画
    alertEl.classList.add('opacity-0', '-translate-y-4')

    // 收缩高度动画
    newItem.style.height = `${newItem.offsetHeight}px`
    requestAnimationFrame(() => {
      newItem.style.height = '0'
      newItem.style.margin = '0'
      newItem.style.padding = '0'
    })

    // 动画完成后移除元素
    setTimeout(() => {
      newItem.remove()

      // 移除空容器
      if (container.children.length === 0) {
        container.remove()
      }
    }, 300)
  }, duration || 2000)
}


function getAlertIcon(type) {
  switch (type) {
    case 'success':
      return '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />'
    case 'error':
      return '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />'
    case 'warning':
      return '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />'
    case 'info':
      return '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />'
    default:
      return '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />'
  }
}

function createContainer() {
  const container = document.createElement('div')
  // 使用daisyUI的toast容器，添加自定义z-index
  container.className = 'notify-container toast toast-top toast-end z-50'
  document.body.appendChild(container)
  return container
}

const notify = {
  success: (content, duration) => addDom(content, 'success', duration),
  error: (content, duration) => addDom(content, 'error', duration),
  warning: (content, duration) => addDom(content, 'warning', duration),
  info: (content, duration) => addDom(content, 'info', duration),
  default: (content, duration) => addDom(content, 'default', duration)
}

export default notify
