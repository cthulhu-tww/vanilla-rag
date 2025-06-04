export function downloadBase64File(base64Data, filename, mimeType = 'application/json') {
  // 1. 去掉 data URL 前缀（如果有）
  const base64String = base64Data.replace(/^data:.+;base64,/, '')

  // 2. 将 Base64 转换为 byte 字符串
  let byteString
  try {
    byteString = atob(base64String)
  } catch (e) {
    console.error('Invalid base64 string')
    return
  }

  // 3. 创建 Uint8Array 并填充二进制数据
  const arrayBuffer = new ArrayBuffer(byteString.length)
  const intArray = new Uint8Array(arrayBuffer)
  for (let i = 0; i < byteString.length; i++) {
    intArray[i] = byteString.charCodeAt(i)
  }

  // 4. 创建 Blob 对象
  const blob = new Blob([intArray], { type: mimeType })

  // 5. 创建下载链接并触发下载
  const downloadLink = document.createElement('a')
  downloadLink.href = window.URL.createObjectURL(blob)
  downloadLink.download = filename
  document.body.appendChild(downloadLink)
  downloadLink.click()

  // 6. 清理
  document.body.removeChild(downloadLink)
  window.URL.revokeObjectURL(downloadLink.href)
}

export function getMimeType(filename) {
  const extToMime = {
    '.txt': 'text/plain',
    '.html': 'text/html',
    '.css': 'text/css',
    '.js': 'application/javascript',
    '.json': 'application/json',
    '.xml': 'application/xml',
    '.pdf': 'application/pdf',
    '.zip': 'application/zip',
    '.rar': 'application/x-rar-compressed',
    '.tar': 'application/x-tar',
    '.gz': 'application/gzip',
    '.7z': 'application/x-7z-compressed',
    '.jpg': 'image/jpeg',
    '.jpeg': 'image/jpeg',
    '.png': 'image/png',
    '.gif': 'image/gif',
    '.svg': 'image/svg+xml',
    '.bmp': 'image/bmp',
    '.webp': 'image/webp',
    '.mp3': 'audio/mpeg',
    '.wav': 'audio/wav',
    '.mp4': 'video/mp4',
    '.webm': 'video/webm',
    '.ogg': 'video/ogg',
    '.avi': 'video/x-msvideo',
    '.doc': 'application/msword',
    '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    '.xls': 'application/vnd.ms-excel',
    '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    '.ppt': 'application/vnd.ms-powerpoint',
    '.pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation'
    // 你可以继续添加你需要的类型
  }

  const ext = filename.slice(filename.lastIndexOf('.')).toLowerCase()
  return extToMime[ext] || 'application/octet-stream'
}


export const getFileIcon = (extension) => {
  const fileIcons = {
    'jpg': 'fa-file-image-o',
    'jpeg': 'fa-file-image-o',
    'png': 'fa-file-image-o',
    'gif': 'fa-file-image-o',
    'pdf': 'fa-file-pdf-o',
    'doc': 'fa-file-word-o',
    'docx': 'fa-file-word-o',
    'xls': 'fa-file-excel-o',
    'xlsx': 'fa-file-excel-o',
    'ppt': 'fa-file-powerpoint-o',
    'pptx': 'fa-file-powerpoint-o',
    'txt': 'fa-file-text-o',
    'zip': 'fa-file-archive-o',
    'rar': 'fa-file-archive-o',
    'mp3': 'fa-file-audio-o',
    'mp4': 'fa-file-video-o',
    'html': 'fa-file-code-o',
    'css': 'fa-file-code-o',
    'js': 'fa-file-code-o',
    'json': 'fa-file-code-o',
    'xml': 'fa-file-code-o',
    'svg': 'fa-file-code-o',
    'default': 'fa-file-o'
  }

  return fileIcons[extension] || fileIcons['default']
}

export const getFileExtension = (filename) => {
  return filename.slice((filename.lastIndexOf('.') - 1 >>> 0) + 2).toLowerCase()
}
