<template>
  <div class="bg-white flex flex-col h-screen">
    <div v-if="!showDetail" class="flex flex-col flex-[20] overflow-hidden">
      <!-- Document Grid -->
      <div
        class="grid grid-cols-1 lg:grid-cols-3 gap-6 mt-8 px-4 flex-[10] overflow-auto max-h-full grid-auto-rows-auto">
        <div
          v-for="doc in filteredDocuments"
          :key="doc.id"
          class="max-h-60 bg-white rounded-lg overflow-hidden border border-[#e5e7eb] hover:border-[#6653e8] transition-all cursor-pointer min-h-60"
        >
          <div class="p-6">
            <div class="flex justify-between items-start mb-2">
              <h3 class="text-lg font-semibold text-gray-900 line-clamp-1">{{ doc.meta.file_name
                }}</h3>
              <span
                class="badge badge-primary bg-[#6653e8] text-white border-none">{{ Math.round(doc.score * 100)
                }}%</span>
            </div>
            <p class="text-gray-600 text-sm mb-4 line-clamp-3" v-html="doc.content"></p>
            <div class="flex justify-between items-center text-sm text-gray-500">
              <span>{{ doc.meta.create_time }}</span>
              <span>{{ doc.meta.source_name }}</span>
            </div>
          </div>
          <div class="bg-[#f8f7ff] px-6 py-3 border-t border-[#e5e7eb]">
            <button
              @click="showDocumentDetail(doc)"
              class="btn btn-sm bg-[#6653e8] text-white border-none hover:bg-[#5a48d1] w-full">
              View Document
            </button>
          </div>
        </div>
      </div>
      <!-- Stats -->
      <div class="mt-8 bg-[#f8f7ff] rounded-lg p-6 mx-4 flex-1">
        <div class="stats shadow">
          <div class="stat">
            <div class="stat-figure text-[#6653e8]">
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"
                   class="inline-block w-8 h-8 stroke-current">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                      d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
              </svg>
            </div>
            <div class="stat-title">总文档数</div>
            <div class="stat-value text-[#6653e8]">{{ filteredDocuments.length }}</div>
          </div>
          <div class="stat">
            <div class="stat-figure text-[#6653e8]">
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"
                   class="inline-block w-8 h-8 stroke-current">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                      d="M13 10V3L4 14h7v7l9-11h-7z"></path>
              </svg>
            </div>
            <div class="stat-title">平均可信度</div>
            <div class="stat-value text-[#6653e8]">{{ avgRelevance }}%</div>
          </div>
        </div>
      </div>
    </div>

    <!-- Document Detail View -->
    <div v-else id="document-detail" class="container mx-auto px-4 py-8 max-h-full flex flex-col">
      <div>
        <button
          class="btn btn-ghost text-[#6653e8] mb-6 flex items-center"
          @click="backToDocumentList"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2" fill="none"
               viewBox="0 0 24 24"
               stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                  d="M10 19l-7-7m0 0l7-7m-7 7h18" />
          </svg>
          Back to Documents
        </button>
      </div>
      <div class="bg-white rounded-lg shadow-lg overflow-hidden flex flex-col">
        <div class="p-8 flex-[10] max-h-full overflow-hidden flex flex-col">
          <div class="flex mb-6 flex-1">
            <h2 class="text-2xl font-bold text-[#6653e8] line-clamp-1 flex-[3]">
              {{ selectedDoc.meta.file_name }}</h2>
            <div class="flex items-center justify-end space-x-4 flex-[2]">
              <span
                class="badge badge-primary bg-[#6653e8] text-white border-none line-clamp-1">Relevance: {{ Math.round(selectedDoc.score * 100)
                }}%</span>
              <span class="text-gray-500 text-sm line-clamp-1">{{ selectedDoc.meta.create_time
                }}</span>
              <span
                class="text-gray-500 text-sm line-clamp-1 max-w-32">{{ selectedDoc.meta.source_name
                }}</span>
            </div>
          </div>
          <div class="prose max-w-none flex-10 overflow-auto max-h-full"
               v-html="selectedDoc.content"></div>
        </div>
        <div class="bg-[#f8f7ff] px-8 py-6 border-t border-[#e5e7eb] flex-1">
          <div class="flex justify-end space-x-4">
            <button class="btn bg-[#6653e8] text-white border-none hover:bg-[#5a48d1]"
                    disabled>
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2" fill="none"
                   viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                      d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
              </svg>
              Download
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import md from '../../markdownit.config.js'
import notify from '@/components/notify.js'

const props = defineProps({
  documents: {
    type: Array,
    required: true
  }
})


const documents = props.documents


// 响应式状态
const showDetail = ref(false)
const selectedDoc = ref(null)
const searchQuery = ref('')

// 过滤后的文档
const filteredDocuments = computed(() => {
  if (!searchQuery.value) return documents
  const query = searchQuery.value.toLowerCase()
  return documents.filter(doc =>
    doc.title.toLowerCase().includes(query) ||
    doc.excerpt.toLowerCase().includes(query)
  )
})

// 平均相关性
const avgRelevance = computed(() => {
  const total = filteredDocuments.value.reduce((sum, d) => sum + d.score, 0) * 100
  return Math.round(total / (filteredDocuments.value.length || 1))
})

// 显示文档详情
function showDocumentDetail(doc) {

  selectedDoc.value = { ...doc }
  selectedDoc.value.content = md.render(doc.content)
  showDetail.value = true
}

// 返回文档列表
function backToDocumentList() {
  showDetail.value = false
}

</script>

