<template>
  <div :id="id" ref="container"></div>
</template>

<script setup>
import {DiffDOM} from 'diff-dom'
import Panzoom from '@panzoom/panzoom'
import {onMounted, ref, watch} from 'vue'
import mermaid from 'mermaid'
import {v4 as uuidv4} from 'uuid'
import md from "../../markdownit.config.js";

mermaid.initialize({
  startOnLoad: false
})
const safeRender = async (code, renderError, id) => {
  try {
    mermaid.detectType(code)
  } catch (error) {
    if (renderError) {
      return `<div class="mermaid-error">Mermaid diagram render failed: \n${error.message}</div>`
    }
    return
  }

  try {
    await mermaid.parse(code)
  } catch (error) {
    if (renderError) {
      return `<div class="mermaid-error">Mermaid diagram render failed: \n${error.message}</div>`
    }
    return
  }

  try {
    const {svg} = await mermaid.render(id, code)
    return svg
  } catch (error) {
    if (renderError) {
      return `<div class="mermaid-error">Mermaid diagram render failed: \n${error.message}</div>`
    }
  }
}

const renderMarkdown = async (dom, markdown, id) => {
  dom.innerHTML = md.render(markdown, {id})
  const mermaidBoxes = dom.querySelectorAll('[id^="mermaid-box"]')
  if (mermaidBoxes.length === 0) return

  for (const box of mermaidBoxes) {
    if (box.dataset.renderdone !== 'true') {
      const svg = await safeRender(decodeURIComponent(box.dataset.code), false, `mermaid-svg${uuidv4().split('-')[0]}`)
      if (!svg) continue
      box.innerHTML = svg
    }
  }
}


const dd = new DiffDOM({})
const props = defineProps({
  id: String,
  content: String
})

const container = ref(null)

// 渲染函数（带缓存检查）
const render = async () => {
  if (!container.value || container.value.__lastContent === props.content) return

  const targetDom = document.createElement('div')
  targetDom.id = props.id
  await renderMarkdown(targetDom, props.content, props.id)

  window.MathJax.typesetPromise([targetDom]).then(() => {
    let diff = dd.diff(container.value.outerHTML, targetDom.outerHTML)
    dd.apply(container.value, diff)

    const svgContainers = container.value.querySelectorAll('[id^="mermaid-box"]')
    if (svgContainers.length === 0) return
    for (const box of svgContainers) {
      const svg = box.querySelector('svg')
      const p = box.closest('#codeHome')
      const zoomin = p.querySelector('#zoomin')
      const zoomout = p.querySelector('#zoomout')
      if (!svg) continue
      const panzoom = Panzoom(svg, {
        maxScale: 5,
        minScale: 0.1,
        startScale: 1,
        contain: 'none'
      })

      zoomin.addEventListener('click', panzoom.zoomIn)
      zoomout.addEventListener('click', panzoom.zoomOut)

      svg.addEventListener('wheel', function (event) {
        if (!event.shiftKey) return
        panzoom.zoomWithWheel(event)
      },{ passive: true })
    }

  })

}

// 初始渲染和内容变化时更新
onMounted(render)
watch(() => props.content, render, {immediate: true})
</script>
