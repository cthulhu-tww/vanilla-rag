<template>
  <div class="w-full max-w-2xl">
    <div class="bg-white rounded-xl p-6 shadow-lg upload-shadow space-y-3">
      <!-- 拖放区域 -->
      <div
        id="drop-area"
        class="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center upload-hover cursor-pointer"
        @dragenter.prevent="highlightDropArea"
        @dragover.prevent="highlightDropArea"
        @dragleave.prevent="unhighlightDropArea"
        @drop.prevent="handleDrop"
      >
        <div class="flex flex-col items-center">
          <i class="fa fa-cloud-upload text-primary text-4xl mb-3"></i>
          <p class="text-gray-600 mb-2">拖放文件至此处</p>
          <p class="text-sm text-gray-500">或</p>
          <label class="mt-3">
              <span
                class="bg-primary hover:bg-primary/90 text-white font-medium py-2 px-4 rounded-md cursor-pointer transition-all duration-300 inline-flex items-center">
                <i class="fa fa-plus mr-2"></i> 选择文件
                <input
                  type="file"
                  id="file-input"
                  class="hidden"
                  multiple
                  @change="handleFileSelect"
                >
              </span>
          </label>
          <p class="text-xs text-gray-500 mt-3">支持的格式: PDF, TXT, MD, DOCX, PPT, PPTX, XLS, XLSX, CSV, JPG, JPEG, PNG (最大 20MB)</p>
        </div>
      </div>
      <!-- 文件列表 -->
      <div class="space-y-3 mb-4 overflow-auto max-h-[200px]" v-if="selectedFiles.length>0">
        <div
          v-for="(item, index) in selectedFiles"
          :key="index"
          class="bg-gray-50 rounded-lg p-3 upload-shadow upload-hover"
          :data-filename="item.file.name"
        >
          <div class="flex items-center max-w-full justify-between">
            <div class="w-10 h-10 rounded bg-primary/10 flex items-center justify-center mr-3">
              <i :class="`fa ${getFileIcon(getFileExtension(item.file.name))} text-primary`"></i>
            </div>
            <div class="flex-1 min-w-0  overflow-hidden">
              <p class="text-sm font-medium text-gray-900 truncate">{{ item.file.name }}</p>
              <p class="text-xs text-gray-500">{{ formatFileSize(item.file.size) }}</p>
            </div>
            <div>
              <button
                class="remove-file text-gray-400 hover:text-error transition-colors duration-300 ml-4"
                @click="removeFile(index)"
                v-if="!item.uploaded"
              >
                <i class="fa fa-times-circle"></i>
              </button>
              <div v-else
                   class="w-10 h-10 rounded bg-success/10 flex items-center justify-center">
                <i class="fa fa-check text-success"></i>
              </div>
            </div>
          </div>
        </div>
      </div>
      <!-- 进度条-->
      <div class="flex items-center justify-center max-w-full" v-if="progressValue>0">
        <progress class="progress progress-primary w-56" :value="progressValue"
                  max="100"></progress>
      </div>
      <!-- 上传按钮 -->
      <div class="flex justify-end">
        <button
          class="bg-primary hover:bg-primary/90 text-white font-medium py-2 px-6 rounded-md shadow-md transition-all duration-300 flex items-center disabled:opacity-50 disabled:cursor-not-allowed"
          @click="uploadFiles"
          :disabled="selectedFiles.length === 0"
        >
          <i class="fa fa-upload mr-2"></i>
          <span>上传文件</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import {ref} from 'vue'
import notify from '@/components/notify.js'
import {upload_docs} from '@/api/file-folder.js'
import {getFileExtension, getFileIcon} from '@/utils/commonUtil.js'

const ALLOWED_EXTENSIONS = ['pdf', 'txt', 'md', 'docx', 'ppt', 'pptx', 'xls', 'xlsx', 'csv', 'jpg', 'jpeg', 'png']

const isValidFileType = (filename) => {
  const ext = filename.split('.').pop().toLowerCase()
  return ALLOWED_EXTENSIONS.includes(ext)
}

const resetUploadState = () => {
  selectedFiles.value = []
  progressValue.value = 0
  unhighlightDropArea() // 清除可能残留的高亮样式
}

defineExpose({resetUploadState})

const props = defineProps({
  folder_id: {
    type: String,
    default: ''
  }
})


const selectedFiles = ref([])


const highlightDropArea = () => {
  const dropArea = document.getElementById('drop-area')
  dropArea.classList.add('border-primary', 'bg-primary/5')
}

const unhighlightDropArea = () => {
  const dropArea = document.getElementById('drop-area')
  dropArea.classList.remove('border-primary', 'bg-primary/5')
}

const handleDrop = (e) => {
  unhighlightDropArea()
  const files = e.dataTransfer.files
  handleFiles(files)
}

const handleFileSelect = (e) => {
  const files = e.target.files
  handleFiles(files)
  e.target.value = '' // Reset input to allow selecting same file again
}

const handleFiles = (files) => {
  for (let i = 0; i < files.length; i++) {
    const file = files[i]

    // Check if file already exists
    if (selectedFiles.value.some(f => f.name === file.name)) {
      notify.warning('文件 "' + file.name + '" 已在列表中')
      continue
    }

    // Check file size
    if (file.size > 20 * 1024 * 1024) {
      notify.error('文件 "' + file.name + '" 超过 20MB 限制')
      continue
    }

    // Check file type
    if (!isValidFileType(file.name)) {
      notify.error('文件 "' + file.name + '" 类型不支持')
      continue
    }

    // Add file to list with additional properties
    selectedFiles.value.push({
      file: file,
      progress: 0,
      uploading: false,
      uploaded: false,
      error: false
    })
  }
}

const removeFile = (index) => {
  selectedFiles.value.splice(index, 1)
}

const progressValue = ref(0)

const uploadFiles = async () => {
  if (selectedFiles.value.length === 0) return
  const formData = new FormData()
  for (let i of selectedFiles.value) {
    formData.append('files', i.file)
  }
  formData.append('folder_id', props.folder_id)
  upload_docs(formData, (progressEvent) => {  // 使用箭头函数保持 this 上下文
    if (progressEvent.event.lengthComputable) {
      progressValue.value = Math.round((progressEvent.event.loaded / progressEvent.event.total) * 100)
    }
  }).then((r) => {
    if (r.code === 200) {
      notify.success('上传成功')
    } else {
      notify.error('上传失败')
    }
  }).catch((error) => {
    notify.error('上传失败' + error)
  }).finally(() => {
    resetUploadState()
  })
}

const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}


</script>

<style>
@tailwind base;
@tailwind components;
@tailwind utilities;

@layer utilities {
  .content-auto {
    content-visibility: auto;
  }

  .upload-shadow {
    box-shadow: 0 4px 20px rgba(59, 130, 246, 0.1);
  }

  .upload-hover {
    transition: all 0.3s ease;
  }

  .upload-hover:hover {
    transform: translateY(-5px);
    box-shadow: 0 8px 30px rgba(59, 130, 246, 0.15);
  }
}

@layer base {
  :root {
    --color-primary: 59, 130, 246;
    --color-secondary: 100, 116, 139;
    --color-accent: 6, 182, 212;
    --color-neutral: 30, 41, 59;
    --color-base-100: 255, 255, 255;
    --color-success: 16, 185, 129;
    --color-warning: 245, 158, 11;
    --color-error: 239, 68, 68;
    --color-info: 59, 130, 246;
  }
}
</style>
