<template>
  <div class="min-h-screen p-6 transition-colors duration-300">
    <!-- 容器 -->
    <div
      ref="container"
      class="max-w-6xl mx-auto transition-all duration-500"
      :style="{ height: isExpanded ? 'auto' : '400px' }"
      v-if="!currentKbId"
    >
      <!-- 标题区域 -->
      <div class="flex justify-between items-center mb-6">
        <h1 class="text-2xl font-bold text-[#6653e8]">知识库管理</h1>
        <button
          @click="create_knowledge_base"
          class="btn btn-sm btn-outline border-[#6653e8] text-[#6653e8] hover:bg-[#6653e8] hover:text-white transition-all duration-300"
        >
          创建知识库
        </button>
      </div>

      <div v-if="knowledges_data.items.length===0">
        <div class="flex justify-center items-center h-full">
          <div class="text-center">
            <div class="text-gray-500">暂无文件</div>
          </div>
        </div>
      </div>
      <div v-else>
        <div
          ref="grid"
          class="grid gap-4"
          :class="{
          'grid-cols-1 sm:grid-cols-2 lg:grid-cols-3': !isExpanded,
          'grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4': isExpanded,
        }"
        >
          <div
            v-for="(kb, index) in knowledges_data.items"
            :key="kb.id"
            ref="cards"
            class="card bg-base-100 shadow-xl border border-[#6653e8]/20 hover:shadow-2xl transition-all duration-300 cursor-pointer"
            @click="getKbFiles(kb.id)"
            :style="{
            animationDelay: `${index * 0.05}s`,
            opacity: isExpanded ? 1 : 0.9,
          }"
          >

            <!-- 操作按钮组 -->
            <div class="absolute top-3 right-3 flex space-x-2">
              <button
                @click.stop="editKnowledge(kb)"
                class="btn btn-circle btn-sm btn-primary btn-outline opacity-70 hover:opacity-100 transition-opacity"
                title="编辑知识库"
              >
                <i class="fa fa-pencil"></i>
              </button>

              <button
                @click.stop="openDeleteKnowledgeDialog(kb.id)"
                class="btn btn-circle btn-sm btn-error btn-outline opacity-70 hover:opacity-100 transition-opacity"
                title="删除知识库"
              >
                <i class="fa fa-trash"></i>
              </button>
            </div>

            <div class="card-body pt-6">
              <div class="badge badge-secondary mb-2">{{ kb.label }}</div>
              <h2 class="card-title text-[#6653e8]">{{ kb.name }}</h2>
              <p class="text-sm text-opacity-70 line-clamp-2">{{ kb.description }}</p>
              <div class="mt-4 flex justify-between items-center">
                <span class="text-xs opacity-70">{{ kb.created }}</span>
                <span class="badge badge-primary badge-outline">{{ kb.document_count }} 文档</span>
              </div>
            </div>
          </div>
        </div>
        <div class="flex w-full justify-center mt-4">
          <div class="join flex">
            <button
              class="join-item btn btn-sm"
              :class="{ 'btn-disabled': page_params.offset === 1 }"
              @click="previous_page('knowledge')"
            >
              «
            </button>
            <button class="join-item btn btn-sm">第{{ page_params.offset }}页</button>
            <button
              class="join-item btn btn-sm"
              :class="{ 'btn-disabled': page_params.offset >= total_page }"
              @click="next_page('knowledge')"
            >
              »
            </button>
          </div>
          <span class="flex justify-center items-center ml-4">共{{ total_page }}页</span>
        </div>
      </div>

    </div>
    <div v-else class="bg-white rounded-xl shadow-sm p-4 mb-6">
      <button class="btn btn-outline btn-primary btn-sm" @click="currentKbId  = null">
        <i class="fa fa-angle-left"></i>回退
      </button>
      <div>
        <div class="mt-4 flex justify-end">
          <!-- 新增的刷新按钮 -->
          <button class="btn btn-outline btn-sm mr-2" @click="refreshKbFiles">
            <i class="fa fa-refresh"></i> 刷新列表
          </button>
          <button class="btn btn-outline btn-info btn-sm" @click="listAllFiles">
            将文件导入知识库
          </button>
        </div>
        <div v-if="kb_files.items.length===0">
          <div class="flex justify-center items-center h-full">
            <div class="text-center">
              <div class="text-gray-500">暂无文件</div>
            </div>
          </div>
        </div>
        <div v-else>
          <div class="overflow-x-auto">
            <table class="table w-full">
              <colgroup>
                <col style="width: 10%">
                <col style="width: 35%">
                <col style="width: 15%">
                <col style="width: 15%">
                <col style="width: 30%">
              </colgroup>
              <thead>
              <tr>
                <th></th>
                <th>文件名</th>
                <th>上传时间</th>
                <th>解析状态</th>
                <th>操作</th>
              </tr>
              </thead>
              <tbody>
              <tr v-for="(item,index) in kb_files.items" :key="item.id"
                  class="hover:bg-gray-50 transition-colors">
                <th>{{ index + 1 }}</th>
                <td>
                  <div
                    class="flex items-center cursor-pointer hover:text-primary transition-colors">
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"
                         stroke-width="1.5" stroke="currentColor" class="w-5 h-5">
                      <path stroke-linecap="round" stroke-linejoin="round"
                            d="M19.5 14.25v-2.625a3.375 3.375 0 0 0-3.375-3.375h-1.5A1.125 1.125 0 0 1 13.5 7.125v-1.5a3.375 3.375 0 0 0-3.375-3.375H8.25m0 12.75h7.5m-7.5 3H12M10.5 2.25H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 0 0-9-9Z"/>
                    </svg>
                    <span class="ml-2 text-ellipsis overflow-hidden">{{ item.name }}</span>
                  </div>
                </td>
                <td>
                  {{ item.created }}
                </td>
                <td>
                  <div class="badge badge-success rounded p-2 text-white"
                       v-if="item.status_code === 3">
                    {{ item.status_text }}
                  </div>
                  <div class="badge badge-error rounded p-2 text-white"
                       v-if="item.status_code === 2">
                    {{ item.status_text }}
                  </div>
                  <div class="badge badge-primary rounded p-2 text-white"
                       v-if="item.status_code === 1">
                    {{ item.status_text }}
                  </div>
                  <div class="badge badge-secondary rounded p-2 text-white"
                       v-if="item.status_code === 4">{{ item.status_text }}
                  </div>
                  <div class="badge badge-secondary rounded p-2 text-white"
                       v-if="item.status_code === 0">{{ item.status_text }}
                  </div>
                </td>
                <td class="space-x-1">
                  <button class="btn btn-sm btn-primary btn-outline" @click="analysis([item.id])"
                          v-if="[2,4].includes(item.status_code)">
                    解析
                  </button>
                  <button class="btn btn-sm btn-info btn-outline"
                          @click="currentSettingFiles.push(item);
                      settingModal.showModal();
                      settingForm.split_length=item.split_length;
                      settingForm.split_overlap=item.split_overlap;
                      " v-if="[2,4].includes(item.status_code)">
                    设置
                  </button>
                  <button class="btn btn-sm btn-error btn-outline"
                          @click="delete_id=item.id;item.status_code===3?deleteFileDialog.showModal():deleteFile()">
                    删除
                  </button>
                </td>
              </tr>
              </tbody>
            </table>
          </div>
          <div class="flex w-full justify-center mt-4">
            <div class="join flex">
              <button class="join-item btn btn-sm"
                      @click="previous_page('files')"
                      :class="{'btn-disabled':  file_page_param.offset === 1}">«
              </button>
              <button class="join-item btn btn-sm">第{{ file_page_param.offset }}页</button>
              <button class="join-item btn btn-sm" @click="next_page('files')"
                      :class="{'btn-disabled':  file_page_param.offset >= files_total_page}">
                »
              </button>
            </div>
            <span class="flex justify-center items-center ml-4">共{{ files_total_page }}页</span>
          </div>
        </div>

      </div>
    </div>

    <!-- 新增知识库模态框 -->
    <dialog ref="addModal" class="modal" :class="{ 'modal-open': showAddModal }">
      <div class="modal-box max-w-lg">
        <h3 class="text-lg font-bold text-[#6653e8] mb-4">新建知识库</h3>
        <form @submit.prevent="submitNewKnowledge">
          <div class="form-control">
            <label class="label">
              <span class="label-text">名称（必填）</span>
            </label>
            <input
              v-model="newKnowledge.name"
              @input="formErrors.name=''"
              type="text"
              placeholder="请输入知识库名称"
              class="input input-bordered w-full"
            />
            <label class="label">
              <span class="label-text-alt text-error">{{ formErrors.name }}</span>
            </label>
          </div>

          <div class="form-control mt-2">
            <label class="label">
              <span class="label-text">标签（必填）</span>
            </label>
            <input
              v-model="newKnowledge.label"
              @input="formErrors.label=''"
              type="text"
              placeholder="请输入知识库标签"
              class="input input-bordered w-full"
            />
            <label class="label">
              <span class="label-text-alt text-error">{{ formErrors.label }}</span>
            </label>
          </div>

          <div class="form-control mt-2">
            <label class="label">
              <span class="label-text">描述</span>
            </label>
            <textarea
              v-model="newKnowledge.description"
              rows="3"
              placeholder="可选描述"
              class="textarea textarea-bordered w-full"
            ></textarea>
          </div>

          <div class="modal-action">
            <button type="submit" class="btn btn-primary btn-sm">提交</button>
            <button @click="showAddModal = false" type="button" class="btn btn-sm">取消</button>
          </div>
        </form>
      </div>
    </dialog>

    <dialog ref="settingModal" class="modal">
      <div class="modal-box">
        <div class="space-y-6">
          <div class="flex space-x-4">
            <span class="label-text flex-1">分割长度(句子)</span>
            <div class="w-full flex-[2]">
              <input type="range" min="5" max="40" v-model="settingForm.split_length"
                     class="range range-xs"
                     step="5"/>
            </div>
            <div class="min-w-6">{{ settingForm.split_length }}</div>
          </div>
          <div class="flex space-x-4">
            <span class="label-text flex-1">分割重叠(句子)</span>
            <div class="w-full flex-[2]">
              <input type="range" min="1" max="8" v-model="settingForm.split_overlap"
                     class="range range-xs"
                     step="1"/>
            </div>
            <div class="min-w-6">{{ settingForm.split_overlap }}</div>
          </div>
        </div>
        <div class="modal-action">
          <form method="dialog" class="space-x-4">
            <!-- if there is a button in form, it will close the modal -->
            <button class="btn btn-primary btn-outline" @click="saveSetting">
              保存
            </button>
            <button class="btn btn-outline"
                    @click="settingModal.close();currentSettingFiles.length=0">取消
            </button>
          </form>
        </div>
      </div>
    </dialog>

    <dialog ref="chooseFileModal" class="h-[80%] w-[40%] rounded p-4">
      <div class="flex w-full h-full flex-col space-y-3">
        <div class="flex flex-[8] space-x-4 min-h-0">  <!-- 添加 min-h-0 防止 flex 项目溢出 -->
          <div class="max-w-xs h-full flex-1 overflow-y-auto rounded bg-base-200">
            <ul class="menu menu-xs font-bold">
              <li v-for="i in folders" :key="i.folder.id">
                <details>
                  <summary>
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"
                         stroke-width="1.5" stroke="currentColor" class="w-4 h-4">
                      <path stroke-linecap="round" stroke-linejoin="round"
                            d="M2.25 12.75V12A2.25 2.25 0 014.5 9.75h15A2.25 2.25 0 0121.75 12v.75m-8.69-6.44l-2.12-2.12a1.5 1.5 0 00-1.061-.44H4.5A2.25 2.25 0 002.25 6v12a2.25 2.25 0 002.25 2.25h15A2.25 2.25 0 0021.75 18V9a2.25 2.25 0 00-2.25-2.25h-5.379a1.5 1.5 0 01-1.06-.44z"/>
                    </svg>
                    <div class="truncate overflow-hidden">{{ i.folder.name }}</div>
                  </summary>
                  <ul>
                    <li v-for="file in i.documents" :key="file.id" @click="chooseFile(file)"><a>
                      <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"
                           stroke-width="1.5" stroke="currentColor" class="w-4 h-4">
                        <path stroke-linecap="round" stroke-linejoin="round"
                              d="M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m2.25 0H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z"/>
                      </svg>
                      <div class="truncate overflow-hidden">{{ file.name }}</div>
                    </a></li>
                  </ul>
                </details>
              </li>
            </ul>
          </div>
          <div class="flex-1 p-4 space-y-3 overflow-y-auto min-h-0">
            <div class="indicator w-full" v-for="f in chosenFiles" :key="f.id"
                 v-if="chosenFiles.length>0">
              <div
                class="indicator-item bg-warning w-5 h-5 rounded-full p-0.5 text-wh cursor-pointer"
                @click="chosenFiles = chosenFiles.filter(file => f.id !== file.id)">
                <svg viewBox="0 0 24 24" fill="none"
                     stroke="currentColor"
                     xmlns="http://www.w3.org/2000/svg">
                  <path d="M18 6L6 18" stroke="black" stroke-width="2" stroke-linecap="round"/>
                  <path d="M6 6L18 18" stroke="black" stroke-width="2" stroke-linecap="round"/>
                </svg>
              </div>
              <div class="flex rounded h-10 bg-base-300 place-items-center w-full px-2 space-x-2">
                <i :class="`fa ${getFileIcon(getFileExtension(f.name))}`"></i>
                <div class="truncate overflow-hidden font-bold text-xs">{{ f.name }}</div>
              </div>
            </div>
            <div v-else class="mt-8 text-center text-gray-400">
              暂未选择任何文件
            </div>
          </div>
        </div>
        <div class="flex flex-1 justify-end space-x-4">
          <button class="btn btn-primary btn-outline" @click="addFilesToKnowledge">保存</button>
          <button class="btn btn-outline" @click="chooseFileModal.close();chosenFiles.length=0">
            取消
          </button>
        </div>
      </div>
    </dialog>
    <dialog ref="deleteFileDialog" class="modal modal-bottom sm:modal-middle">
      <div class="modal-box">
        <h3 class="font-bold text-lg">删除文件</h3>
        <p class="py-4">删除文件后，向量数据库中的数据将一并删除，确认删除？</p>
        <div class="modal-action">
          <form method="dialog">
            <button class="btn btn-outline btn-error"
                    @click="deleteFile">确定
            </button>
            <button class="btn btn-outline ml-2" @click="delete_id=null">取消</button>
          </form>
        </div>
      </div>
    </dialog>
    <!-- 修改知识库模态框 -->
    <dialog ref="editModal" class="modal" :class="{ 'modal-open': showEditModal }">
      <div class="modal-box max-w-lg">
        <h3 class="text-lg font-bold text-[#6653e8] mb-4">修改知识库</h3>
        <form @submit.prevent="submitEditKnowledge">
          <div class="form-control">
            <label class="label">
              <span class="label-text">名称（必填）</span>
            </label>
            <input
              v-model="editKnowledgeData.name"
              @input="editFormErrors.name=''"
              type="text"
              placeholder="请输入知识库名称"
              class="input input-bordered w-full"
            />
            <label class="label">
              <span class="label-text-alt text-error">{{ editFormErrors.name }}</span>
            </label>
          </div>

          <div class="form-control mt-2">
            <label class="label">
              <span class="label-text">标签（必填）</span>
            </label>
            <input
              v-model="editKnowledgeData.label"
              @input="editFormErrors.label=''"
              type="text"
              placeholder="请输入知识库标签"
              class="input input-bordered w-full"
            />
            <label class="label">
              <span class="label-text-alt text-error">{{ editFormErrors.label }}</span>
            </label>
          </div>

          <div class="form-control mt-2">
            <label class="label">
              <span class="label-text">描述</span>
            </label>
            <textarea
              v-model="editKnowledgeData.description"
              rows="3"
              placeholder="可选描述"
              class="textarea textarea-bordered w-full"
            ></textarea>
          </div>

          <div class="modal-action">
            <button type="submit" class="btn btn-primary btn-sm">提交</button>
            <button @click="showEditModal = false" type="button" class="btn btn-sm">取消</button>
          </div>
        </form>
      </div>
    </dialog>
    <!-- 知识库删除确认对话框 -->
    <dialog ref="deleteKnowledgeDialog" class="modal modal-bottom sm:modal-middle">
      <div class="modal-box">
        <h3 class="font-bold text-lg">删除知识库</h3>
        <p class="py-4">确定要删除这个知识库吗？删除后将无法恢复。</p>
        <div class="modal-action">
          <form method="dialog">
            <button class="btn btn-outline btn-error" @click="confirmDeleteKnowledge">
              确定删除
            </button>
            <button class="btn btn-outline ml-2" @click="deleteKnowledgeDialog.close()">
              取消
            </button>
          </form>
        </div>
      </div>
    </dialog>
  </div>
</template>

<script setup>
import {computed, onMounted, reactive, ref} from 'vue'
import {
  updateKnowledge,
  deleteKnowledge,
  addKnowledge,
  analysisDocument, deleteDocumentsFromKnowledge,
  getDocumentsByKnowledge,
  getKnowledgeList,
  saveDocumentsToKnowledge,
  splitSetting
} from '@/api/knowledge.js'
import notify from "@/components/notify.js";
import {all_folders_info} from "@/api/file-folder.js";
import {getFileExtension, getFileIcon} from "@/utils/commonUtil.js";

const refreshKbFiles = () => {
  if (!currentKbId.value) return;
  file_page_param.value.offset = 1;
  getKbFiles(currentKbId.value);
};
// 新增修改相关状态
const showEditModal = ref(false)
const editKnowledgeData = ref({
  id: null,
  name: '',
  label: '',
  description: ''
})
const editFormErrors = ref({
  name: '',
  label: ''
})

const showAddModal = ref(false)
const newKnowledge = ref({
  name: '',
  label: '',
  description: '',
})
const formErrors = ref({
  name: '',
  label: '',
})

// 编辑知识库
function editKnowledge(knowledge) {
  // 填充表单数据
  editKnowledgeData.value = {
    id: knowledge.id,
    name: knowledge.name,
    label: knowledge.label,
    description: knowledge.description
  }
  editFormErrors.value = {}
  showEditModal.value = true
}

// 提交编辑知识库
async function submitEditKnowledge() {
  // 验证表单
  editFormErrors.value = {
    name: '',
    label: ''
  }

  let hasError = false

  if (!editKnowledgeData.value.name.trim()) {
    editFormErrors.value.name = '名称不能为空'
    hasError = true
  }

  if (!editKnowledgeData.value.label.trim()) {
    editFormErrors.value.label = '标签不能为空'
    hasError = true
  }

  if (hasError) return

  try {
    // 调用API更新知识库
    await updateKnowledge(editKnowledgeData.value.id, {
      name: editKnowledgeData.value.name,
      label: editKnowledgeData.value.label,
      description: editKnowledgeData.value.description
    })

    showEditModal.value = false
    notify.success('知识库更新成功')
    fetchKnowledgeList() // 刷新知识库列表
  } catch (error) {
    notify.error(error.message || '更新失败')
  }
}

const deleteKnowledgeDialog = ref(null)
const knowledgeIdToDelete = ref(null)

// 打开删除确认对话框
function openDeleteKnowledgeDialog(id) {
  knowledgeIdToDelete.value = id
  deleteKnowledgeDialog.value.showModal()
}

// 确认删除知识库
async function confirmDeleteKnowledge() {
  if (!knowledgeIdToDelete.value) return

  try {
    await deleteKnowledge(knowledgeIdToDelete.value)
    notify.success('知识库删除成功')
    fetchKnowledgeList()
  } catch (error) {
    notify.error(error.message || '删除失败')
  } finally {
    deleteKnowledgeDialog.value.close()
    knowledgeIdToDelete.value = null
  }
}

// 打开新增模态框
function create_knowledge_base() {
  // 重置表单
  newKnowledge.value = {
    name: '',
    label: '',
    description: '',
  }
  formErrors.value = {}
  showAddModal.value = true
}

// 提交新增知识库
async function submitNewKnowledge() {
  // 清空旧错误
  formErrors.value = {
    name: '',
    label: ''
  }

  let hasError = false

  if (!newKnowledge.value.name.trim()) {
    formErrors.value.name = '名称不能为空'
    hasError = true
  }

  if (!newKnowledge.value.label.trim()) {
    formErrors.value.label = '标签不能为空'
    hasError = true
  }

  if (hasError) return
  await addKnowledge(newKnowledge.value)
  showAddModal.value = false
  fetchKnowledgeList()
}

// 封装获取知识库列表的方法以便复用
async function fetchKnowledgeList() {
  const res = await getKnowledgeList(page_params.value)
  knowledges_data.value.items = res.items
  knowledges_data.value.total = res.total
}

const page_params = ref({
  offset: 1,
  limit: 6,
})

const knowledges_data = ref({
  total: 0,
  items: [],
})

const total_page = computed(() => {
  return Math.ceil(knowledges_data.value.total / page_params.value.limit)
})

const isExpanded = ref(false)
const container = ref(null)
const grid = ref(null)
const cards = ref([])

// 知识库文件部分

const file_page_param = ref({
  limit: 8,
  offset: 1,
  folder_id: null
})

const currentKbId = ref(null)
const kb_files = ref({
  items: [],
  total: 0
})
const files_total_page = computed(() => {
  return Math.ceil(kb_files.value.total / file_page_param.value.limit)
})
const getKbFiles = (id) => {
  currentKbId.value = id
  getDocumentsByKnowledge({
    knowledge_id: id,
    offset: file_page_param.value.offset,
    limit: file_page_param.value.limit
  }).then((res) => {
    kb_files.value.items = res.items
    kb_files.value.total = res.total
  })
}

const settingModal = ref()

const settingForm = reactive({
  split_length: 20,
  split_overlap: 4
})
const currentSettingFiles = ref([])

const saveSetting = () => {
  if (currentSettingFiles.value.length === 0) {
    return
  }
  currentSettingFiles.value.forEach(file => {
    file.split_length = settingForm.split_length
    file.split_overlap = settingForm.split_overlap
  })

  splitSetting({
    knowledgeId: currentKbId.value,
    documentIds: currentSettingFiles.value.map(file => file.id),
    split_length: settingForm.split_length,
    split_overlap: settingForm.split_overlap
  }).then(() => {
    notify.success('保存成功')
  }).catch(e => {
    notify.error(e)
  }).finally(() => {
    settingModal.value.close()
    currentSettingFiles.value = []
  })
}


const analysis = (ids) => {
  kb_files.value.items.forEach(file => {
    if (ids.includes(file.id)) {
      file.status_code = 0
      file.status_text = '排队中'
    }
  })
  analysisDocument({
    knowledge_id: currentKbId.value,
    documentIds: ids
  }).then(() => {
    notify.success('开始分析')
    getKbFiles(currentKbId.value)
  })
}


//文件选择
const chooseFileModal = ref()
const folders = ref([])
const chosenFiles = ref([])
const deleteFileDialog = ref()
const listAllFiles = () => {
  chooseFileModal.value.showModal();
  all_folders_info().then(res => {
    folders.value = res.data
  })
}

const chooseFile = (file) => {
  if (chosenFiles.value.find(f => f.id === file.id)) {
    chosenFiles.value = chosenFiles.value.filter(f => f.id !== file.id)
  } else {
    chosenFiles.value.push(file)
  }
}

const addFilesToKnowledge = () => {
  saveDocumentsToKnowledge(currentKbId.value, chosenFiles.value.map(file => file.id)).then(() => {
    getKbFiles(currentKbId.value)
    notify.success('添加成功')
  })
}

const delete_id = ref("")

const deleteFile = () => {
  deleteDocumentsFromKnowledge(currentKbId.value, [delete_id.value]).then(() => {
    getKbFiles(currentKbId.value)
    notify.success('删除成功')
  })
}


const next_page = (type) => {
  if (type === 'knowledge') {
    if (page_params.value.offset < total_page.value) {
      page_params.value.offset++
      fetchKnowledgeList()
    }
  } else if (type === 'files') {
    if (file_page_param.value.offset < files_total_page.value) {
      file_page_param.value.offset++
      getKbFiles(currentKbId.value)
    }
  }
}

const previous_page = (type) => {
  if (type === 'knowledge') {
    if (page_params.value.offset > 1) {
      page_params.value.offset--
      fetchKnowledgeList()
    }
  } else if (type === 'files') {
    if (file_page_param.value.offset > 1) {
      file_page_param.value.offset--
      getKbFiles(currentKbId.value)
    }
  }
}


onMounted(() => {
  fetchKnowledgeList()
})
</script>

<style scoped>
/* 自定义主题色 */
:root {
  --p: #6653e8;
  --pf: #ffffff;
}

.card:hover {
  transform: translateY(-5px);
  transition: all 0.3s ease;
}

.modal {
  background: rgba(0, 0, 0, 0.3);
}
</style>
