import mermaid from 'mermaid'
// 初始化 mermaid 配置
mermaid.initialize({
  startOnLoad: false, // 禁用自动渲染
  theme: 'default',
  suppressErrorRendering: true
})

//切换代码/图表展示
window.toggleCode = function toggleCode(element, value, idx) {
  const p = element.closest('.codeHome')
  const menu = p.querySelectorAll('#togglebtn')
  for (const item of menu) {
    item.classList.remove('bg-gray-100')
  }
  element.classList.add('bg-gray-100')
  element.classList.add('bg-gray-100')


  if (value === 0) {
    p.querySelector('#mermaid-box-' + idx).style.display = 'flex'
    p.querySelector('#code').style.display = 'none'
    p.querySelector('#svgOper').classList.remove('hidden')
    p.querySelector('#codeOper').classList.add('hidden')
  } else if (value === 1) {
    p.querySelector('#mermaid-box-' + idx).style.display = 'none'
    p.querySelector('#code').style.display = 'flex'
    p.querySelector('#svgOper').classList.add('hidden')
    p.querySelector('#codeOper').classList.remove('hidden')
  }
}


//复制代码
window.copyCode = function copyCode(element) {
  let code = element.closest('.codeTitle').nextElementSibling.querySelector('code').cloneNode(true)
  navigator.clipboard.writeText(code.textContent)
  element.textContent = 'Copied!'
  setTimeout(() => {
    element.textContent = 'Copy code'
  }, 2000)
}

//复制mermaid
window.copyMermaid = function copyMermaid(element) {
  const code = element.closest('#codeHome').querySelector('#code').innerHTML
  navigator.clipboard.writeText(code)
  const originhtml = element.innerHTML
  element.textContent = 'Copied!'
  setTimeout(() => {
    element.innerHTML = originhtml
  }, 2000)
}


const svgToPng = (svgElement, callback, width, height) => {
  // 创建 canvas 元素
  const canvas = document.createElement('canvas')
  const ctx = canvas.getContext('2d')

  // 设置 canvas 尺寸
  canvas.width = width || svgElement.width.baseVal.value
  canvas.height = height || svgElement.height.baseVal.value

  // 将 SVG 数据转换为 data URL
  const svgData = new XMLSerializer().serializeToString(svgElement)
  const img = new Image()

  // 设置 SVG 为图像的源
  img.onload = function () {
    // 在 canvas 上绘制图像
    ctx.drawImage(img, 0, 0)

    // 将 canvas 转换为 PNG data URL
    const pngData = canvas.toDataURL('image/png')
    callback(pngData)
  }

  // 设置 SVG 数据为 base64
  img.src = 'data:image/svg+xml;base64,' + btoa(unescape(encodeURIComponent(svgData)))
}

const addBackgroundToSvg = (svgElement, backgroundColor = 'white') => {
  const copyed = svgElement.cloneNode(true)
  copyed.style.transform = ''
  document.body.appendChild(copyed)
  const width = copyed.width.baseVal.value
  const height = copyed.height.baseVal.value
  // 创建背景矩形
  const rect = document.createElementNS('http://www.w3.org/2000/svg', 'rect')
  rect.setAttribute('x', -20)
  rect.setAttribute('y', -20)
  rect.setAttribute('width', width + 40)
  rect.setAttribute('height', height + 40)
  rect.setAttribute('fill', backgroundColor)

  // 将背景矩形插入为第一个元素
  copyed.insertBefore(rect, copyed.firstChild)
  return copyed
}

window.saveToPng = (dom) => {
  const svgDom = dom.closest('#codeHome').querySelector('svg')
  const svgDomWithBackground = addBackgroundToSvg(svgDom)
  svgToPng(svgDomWithBackground, (pngData) => {
    // 创建一个新的图像元素显示 PNG
    const img = new Image()
    img.src = pngData
    document.body.appendChild(img)

    // 或者下载 PNG
    const link = document.createElement('a')
    link.download = 'image.png'
    link.href = pngData
    link.click()
    document.body.removeChild(img)
    document.body.removeChild(svgDomWithBackground)
    setTimeout(() => {
      document.body.removeChild(img)
      document.body.removeChild(svgDomWithBackground)
    }, 100)
  })
}

window.saveToSVG = (dom) => {
  const svgDom = dom.closest('#codeHome').querySelector('svg')

  // Clone the SVG to avoid modifying the original
  const svgClone = svgDom.cloneNode(true)

  // Set necessary attributes if they don't exist
  if (!svgClone.hasAttribute('xmlns')) {
    svgClone.setAttribute('xmlns', 'http://www.w3.org/2000/svg')
  }

  // Serialize the SVG to a string
  const serializer = new XMLSerializer()
  let svgString = serializer.serializeToString(svgClone)

  // Add XML declaration
  svgString = '<?xml version="1.0" standalone="no"?>\n' + svgString

  // Create a Blob with the SVG data
  const blob = new Blob([svgString], {type: 'image/svg+xml;charset=utf-8'})

  // Create a download link and trigger the download
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url

  // Use the SVG's title or id as filename, or default to 'image'
  const filename = svgDom.id || svgDom.getAttribute('title') || 'image'
  link.download = `${filename}.svg`

  document.body.appendChild(link)
  link.click()

  // Clean up
  setTimeout(() => {
    document.body.removeChild(link)
    URL.revokeObjectURL(url)
  }, 100)
}

function markdownItMermaid(md) {

  md.renderer.rules.fence = function (tokens, idx, options, env, self) {
    const token = tokens[idx]
    const code = token.content.trim()
    const info = token.info ? token.info.trim() : ''
    // 检查是否是 mermaid 代码块
    if (info === 'mermaid' || info.startsWith('mermaid')) {
      const contentDom = document.querySelector(`#${env.id}`)
      let renderDone = false
      if (tokens.length > idx + 1) {
        renderDone = true
      }
      if (renderDone) {
        if (contentDom) {
          let lastMermaid = contentDom.querySelector(`#mermaid-box-${idx}`)
          if (lastMermaid) {
            const svg = lastMermaid.innerHTML
            if (!svg) {
              renderDone = false
            }
            return `
            <pre>
              <div class="codeHome" id="codeHome">
                  <div class="flex h-[50px] items-center bg-gray-200 justify-between">
                      <div class="join h-[40px] bg-gray-300 flex items-center ml-2 p-1 font-bold">
                        <button class="btn-sm join-item bg-gray-100 select-none" id="togglebtn" onclick="toggleCode(event.target,0,${idx})">图表</button>
                        <button class="btn-sm join-item select-none" id="togglebtn" onclick="toggleCode(event.target,1,${idx})">代码</button>
                      </div>
                      <div class="flex flex-none justify-between items-center mr-2" id="svgOper">
                        <img src="/src/assets/icon/zoomin.svg" id="zoomin" alt="" class="select-none hover:bg-gray-300 mr-2 rounded h-[20px] cursor-pointer"/>
                        <img src="/src/assets/icon/zoomout.svg" id="zoomout" alt="" class="select-none hover:bg-gray-300 mr-2 rounded h-[20px] cursor-pointer"/>
                        <div class="select-none mr-2">|</div>
                        <button class="btn-sm hover:bg-gray-300 rounded select-none" onclick="saveToPng(event.target)">下载图片</button>
                        <button class="btn-sm hover:bg-gray-300 rounded select-none" onclick="saveToSVG(event.target)">下载SVG</button>
                      </div>
                      <div class="flex flex-none justify-between items-center mr-2 hidden" id="codeOper">
                        <button class="copyCode" onclick="copyMermaid(event.target)">
                        <img src="/src/assets/icon/copy.svg" alt="" class="select-none h-[20px]">复制</button>
                      </div>
                  </div>

                  <div class="codeBody bg-base-100">
                      <code class="language-${info}" hidden="hidden" id="code">${code}</code>
                      <div id="mermaid-box-${idx}" class="flex h-[400px] justify-center" data-code="${encodeURIComponent(code)}" data-renderDone="${renderDone}">${svg}</div>
                  </div>
              </div>
         </pre>`
          }
        }
      }
      return `
         <pre>
              <div class="codeHome" id="codeHome">
                  <div class="flex h-[50px] items-center bg-gray-200 justify-between">
                      <div class="join h-[40px] bg-gray-300 flex items-center ml-2 p-1 font-bold">
                        <button class="btn-sm join-item bg-gray-100 select-none" id="togglebtn" onclick="toggleCode(event.target,0,${idx})">图表</button>
                        <button class="btn-sm join-item select-none" id="togglebtn" onclick="toggleCode(event.target,1,${idx})">代码</button>
                      </div>
                      <div class="flex flex-none justify-between items-center mr-2" id="svgOper">
                        <img src="/src/assets/icon/zoomin.svg" id="zoomin" alt="" class="select-none hover:bg-gray-300 mr-2 rounded h-[20px] cursor-pointer"/>
                        <img src="/src/assets/icon/zoomout.svg" id="zoomout" alt="" class="select-none hover:bg-gray-300 mr-2 rounded h-[20px] cursor-pointer"/>
                        <div class="select-none mr-2">|</div>
                        <button class="btn-sm hover:bg-gray-300 rounded select-none" onclick="saveToPng(event.target)">下载图片</button>
                        <button class="btn-sm hover:bg-gray-300 rounded select-none" onclick="saveToSVG(event.target)">下载SVG</button>
                      </div>
                      <div class="flex flex-none justify-between items-center mr-2 hidden" id="codeOper">
                        <button class="copyCode" onclick="copyMermaid(event.target)">
                        <img src="/src/assets/icon/copy.svg" alt="" class="select-none h-[20px]">复制</button>
                      </div>
                  </div>

                  <div class="codeBody bg-base-100">
                      <code class="language-${info}" hidden="hidden" id="code">${code}</code>
                      <div id="mermaid-box-${idx}" class="flex h-[400px] justify-center" data-code="${encodeURIComponent(code)}"></div>
                  </div>
              </div>
         </pre>`
    }

    return `
    <pre>
        <div class="codeHome">
            <div class="codeTitle flex items-center">
                <div>${info}</div>
                <button class="copyCode" onclick="copyCode(event.target)">Copy code</button>
            </div>
            <div class="codeBody">
                <code class="language-${info}">${options.highlight(code, info)}</code>
            </div>
        </div>
    </pre>
    `
  }
}


export {markdownItMermaid}
