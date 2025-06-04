<template>
  <div class="document-manager min-h-screen bg-gray-50 p-4 md:p-8">
    <!-- 文件列表 -->
    <div class="bg-white rounded-xl shadow-sm p-4 mb-6" v-if="files_data.items.length === 0">
      <button @click="create_folder_dialog.showModal()" class="btn btn-primary btn-outline btn-sm">
        创建文件夹
      </button>
      <div v-if="folders_data.items.length===0">
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
              <col style="width: 5%">
              <col style="width: 40%">
              <col style="width: 30%">
              <col style="width: 25%">
            </colgroup>
            <thead>
            <tr>
              <th></th>
              <th>名称</th>
              <th>创建时间</th>
              <th>操作</th>
            </tr>
            </thead>
            <tbody>
            <tr v-for="(folder,index) in folders_data.items" :key="folder.id"
                class="hover:bg-gray-50 transition-colors">
              <th>{{ index + 1 }}</th>
              <td>
                <div class="flex items-center cursor-pointer hover:text-primary transition-colors"
                     @click="get_files(folder.id)">
                  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"
                       stroke-width="1.5" stroke="currentColor" class="w-5 h-5">
                    <path stroke-linecap="round" stroke-linejoin="round"
                          d="M2.25 12.75V12A2.25 2.25 0 0 1 4.5 9.75h15A2.25 2.25 0 0 1 21.75 12v.75m-8.69-6.44-2.12-2.12a1.5 1.5 0 0 0-1.061-.44H4.5A2.25 2.25 0 0 0 2.25 6v12a2.25 2.25 0 0 0 2.25 2.25h15A2.25 2.25 0 0 0 21.75 18V9a2.25 2.25 0 0 0-2.25-2.25h-5.379a1.5 1.5 0 0 1-1.06-.44Z"/>
                  </svg>
                  <span class="ml-2">{{ folder.name }}</span>
                </div>
              </td>
              <td>
                {{ folder.created }}
              </td>
              <td>
                <button @click="upload_dialog.showModal();upload_folder_id=folder.id"
                        class="btn btn-sm btn-primary btn-outline mr-2">上传
                </button>
                <button @click="delete_folder_dialog.showModal(); delete_id = folder.id"
                        class="btn btn-sm btn-error btn-outline">删除
                </button>
              </td>
            </tr>
            </tbody>
          </table>
        </div>
        <div class="flex w-full justify-center mt-4">
          <div class="join flex">
            <button class="join-item btn btn-sm"
                    @click="previous_page('folders')"
                    :class="{'btn-disabled':  page_params.offset === 1}">
              «
            </button>
            <button class="join-item btn btn-sm">第{{ page_params.offset }}页</button>
            <button class="join-item btn btn-sm"
                    @click="next_page('folders')"
                    :class="{'btn-disabled':  page_params.offset >= total_page}">
              »
            </button>
          </div>
          <span class="flex justify-center items-center ml-4">共{{ total_page }}页</span>
        </div>
      </div>

    </div>
    <div v-else class="bg-white rounded-xl shadow-sm p-4 mb-6">
      <button class="btn btn-outline btn-primary btn-sm" @click="files_data.items = []">
        <i class="fa fa-angle-left"></i>回退
      </button>
      <div class="overflow-x-auto">
        <table class="table w-full">
          <colgroup>
            <col style="width: 5%">
            <col style="width: 40%">
            <col style="width: 30%">
            <col style="width: 25%">
          </colgroup>
          <thead>
          <tr>
            <th></th>
            <th>名称</th>
            <th>创建时间</th>
            <th>操作</th>
          </tr>
          </thead>
          <tbody>
          <tr v-for="(item,index) in files_data.items" :key="item.id"
              class="hover:bg-gray-50 transition-colors">
            <th>{{ index + 1 }}</th>
            <td>
              <div class="flex items-center cursor-pointer hover:text-primary transition-colors">
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"
                     stroke-width="1.5" stroke="currentColor" class="w-5 h-5">
                  <path stroke-linecap="round" stroke-linejoin="round"
                        d="M19.5 14.25v-2.625a3.375 3.375 0 0 0-3.375-3.375h-1.5A1.125 1.125 0 0 1 13.5 7.125v-1.5a3.375 3.375 0 0 0-3.375-3.375H8.25m0 12.75h7.5m-7.5 3H12M10.5 2.25H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 0 0-9-9Z"/>
                </svg>
                <span class="ml-2">{{ item.name }}</span>
              </div>
            </td>
            <td>
              {{ item.created }}
            </td>
            <td>
              <button @click="delete_file_dialog.showModal(); delete_id = item.id"
                      class="btn btn-sm btn-error btn-outline ml-2">删除
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

    <dialog class="modal" ref="create_folder_dialog">
      <div class="modal-box max-w-[36rem]">
        <input type="text" placeholder="输入文件夹名称"
               class="input input-bordered w-full max-w-xs input-primary"
               v-model="create_folder_name"/>
        <button class="btn btn-primary ml-4 btn-outline" @click="create_folder">确认</button>
        <button class="btn btn-secondary ml-4 btn-outline" @click="create_folder_name = ''">清空
        </button>
      </div>
      <form method="dialog" class="modal-backdrop">
        <button>close</button>
      </form>
    </dialog>
    <dialog ref="delete_folder_dialog" class="modal modal-bottom sm:modal-middle">
      <div class="modal-box">
        <h3 class="font-bold text-lg">删除文件夹</h3>
        <p class="py-4">将删除此文件夹以及文件夹下的所有文件，删除后将无法恢复，您确定要删除吗？</p>
        <div class="modal-action">
          <form method="dialog">
            <button class="btn btn-outline btn-error"
                    @click="delete_folder">确定
            </button>
            <button class="btn btn-outline ml-2" @click="delete_id=null">取消</button>
          </form>
        </div>
      </div>
    </dialog>
    <dialog ref="delete_file_dialog" class="modal modal-bottom sm:modal-middle">
      <div class="modal-box">
        <h3 class="font-bold text-lg">删除文件</h3>
        <p class="py-4">确定要删除此文件吗？</p>
        <div class="modal-action">
          <form method="dialog">
            <button class="btn btn-outline btn-error"
                    @click="delete_file">确定
            </button>
            <button class="btn btn-outline ml-2" @click="delete_id=null">取消</button>
          </form>
        </div>
      </div>
    </dialog>
    <dialog ref="upload_dialog" class="modal">
      <div class="modal-box max-w-[40rem]">
        <upload
          :folder_id="upload_folder_id"
          ref="uploadComponent"
        ></upload>
        <div class="modal-action">
          <form method="dialog">
            <button class="btn btn-outline ml-2" @click="uploadComponent.resetUploadState()">关闭
            </button>
          </form>
        </div>
      </div>
    </dialog>
  </div>
</template>

<script setup>
import {
  add_folder,
  delete_file_by_id,
  delete_folder_by_id,
  get_file_list,
  get_folders_list
} from '@/api/file-folder'
import {computed, onMounted, ref} from 'vue'
import notify from '@/components/notify.js'
import Upload from '@/components/Upload.vue'

let page_params = ref({
  limit: 8,
  offset: 1
})

let folders_data = ref({
  items: [],
  total: 0
})

const total_page = computed(() => {
  return Math.ceil(folders_data.value.total / page_params.value.limit)
})

const files_total_page = computed(() => {
  return Math.ceil(files_data.value.total / file_page_param.value.limit)
})

const getFolderList = async () => {
  try {
    const res = await get_folders_list({
      limit: page_params.value.limit,
      offset: page_params.value.offset
    })
    folders_data.value.items = res.data.items
    folders_data.value.total = res.data.total
  } catch (error) {
    notify.error(error)
  }
}

// dialogs start
const create_folder_dialog = ref()
const delete_folder_dialog = ref()
const upload_dialog = ref()
const delete_file_dialog = ref()
// dialogs end

const uploadComponent = ref()

const create_folder_name = ref('')
const create_folder = () => {
  if (!create_folder_name.value) {
    notify.warning('请输入文件夹名称')
    return
  }
  add_folder({name: create_folder_name.value}).then(() => {
    notify.success('创建成功')
    getFolderList()
    create_folder_dialog.value.close()
    create_folder_name.value = ''
  })
}

const delete_id = ref()
const delete_folder = () => {
  if (!delete_id.value) {
    return
  }
  delete_folder_by_id(delete_id.value).then(() => {
    notify.success('删除成功')
    delete_folder_dialog.value.close()
    getFolderList()
    delete_id.value = null
  })
}

const delete_file = () => {
  delete_file_by_id(delete_id.value).then(() => {
    notify.success('删除成功')
    delete_file_dialog.value.close()
    get_files(file_page_param.value.folder_id)
    delete_id.value = null
  })
}

const upload_folder_id = ref()

//文件部分
let file_page_param = ref({
  limit: 8,
  offset: 1,
  folder_id: null
})
let files_data = ref({
  items: [],
  total: 0
})

const get_files = (folder_id) => {
  file_page_param.value.folder_id = folder_id
  get_file_list(file_page_param.value)
    .then(response => {
      if (!response.data.items || response.data.items.length === 0) {
        notify.warning('该文件夹下没有文件')
      }
      files_data.value.items = response.data.items
      files_data.value.total = response.data.total
    })
    .catch(error => {
      notify.error(error)
    })
}

//翻页
const next_page = (type) => {
  if (type === 'folders') {
    if (page_params.value.offset < total_page.value) {
      page_params.value.offset++
      getFolderList()
    }
  } else {
    if (file_page_param.value.offset < files_total_page.value) {
      file_page_param.value.offset++
      get_files(file_page_param.value.folder_id)
    }
  }
}

const previous_page = (type) => {
  if (type === 'folders') {
    if (page_params.value.offset > 1) {
      page_params.value.offset--
      getFolderList()
    }
  } else {
    if (file_page_param.value.offset > 1) {
      file_page_param.value.offset--
      get_files(file_page_param.value.folder_id)
    }
  }
}


onMounted(() => {
  getFolderList()
})
</script>

<style scoped>
.notification {
  position: fixed;
  top: 20px;
  right: 20px;
  z-index: 100;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }

  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.animate-fade-in {
  animation: fadeIn 0.3s ease-out forwards;
}
</style>
