<template>
  <div class="flex h-screen bg-gray-50 overflow-hidden">
    <!-- 左侧聊天历史 -->
    <div class="w-64 bg-white border-r border-gray-200 flex flex-col">
      <div class="h-16 flex items-center justify-between px-4 border-b border-gray-200">
        <h2 class="text-lg font-semibold gradient-text">Vanilla RAG</h2>
        <button
          class="btn btn-circle btn-sm btn-ghost text-gray-500 hover:bg-gray-100 cursor-pointer"
          @click="newChat()">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20"
               fill="currentColor">
            <path fill-rule="evenodd"
                  d="M10 3a1 1 0 011 1v5h5a1 1 0 110 2h-5v5a1 1 0 11-2 0v-5H4a1 1 0 110-2h5V4a1 1 0 011-1z"
                  clip-rule="evenodd"/>
          </svg>
        </button>
      </div>
      <InfiniteScroll
        v-model="chatHistory.loading"
        :no-more="chatHistory.noMore"
        :load="chatHistory.loadData"
        :distance="20"
        :disabled="false"
        :immediate="true"
        :delay="300"
        :class="'flex-1 overflow-y-auto'"
        listen-for-event="refresh-data"
      >
        <div class="space-y-1 p-2">
          <div
            class="chat-history-item p-3 rounded-lg cursor-pointer group relative overflow-hidden"
            :class="item.selected?'active':''"
            ref="chatHistoryItem"
            @click="selectChatHistory(item)"
            v-for="(item, index) in chatHistory.list" v-bind:key="index">
            <input type="text" placeholder="Type here"
                   class="input input-bordered input-primary w-full max-w-xs"
                   v-model="item.title"
                   v-if="item.editTitle"
                   @click.stop
                   @change="updateTitle(item)"
            />
            <div v-else class="bg-inherit">
              <p class="text-sm font-medium truncate">{{ item.title }}</p>
              <Dropdown :position="'bottom'">
                <template #trigger="{ toggle, triggerAttrs   }">
                  <div
                    v-bind="triggerAttrs"
                    @click.stop="toggle"
                    class="group-hover:flex absolute right-0 top-0 h-full items-center hidden justify-center bg-inherit pl-2"
                  >
                    <svg width="32" height="8" viewBox="0 0 32 8"
                         xmlns="http://www.w3.org/2000/svg">
                      <circle cx="2" cy="4" r="2" fill="currentColor"/>
                      <circle cx="10" cy="4" r="2" fill="currentColor"/>
                      <circle cx="18" cy="4" r="2" fill="currentColor"/>
                    </svg>
                  </div>
                </template>

                <template #content>
                  <div class="p-2">
                    <div
                      @click="item.editTitle = true"
                      class="p-2 hover:bg-gray-100 cursor-pointer flex items-center rounded">
                      <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"
                           stroke-width="1.5" stroke="currentColor" class="size-4 mr-1.5">
                        <path stroke-linecap="round" stroke-linejoin="round"
                              d="m16.862 4.487 1.687-1.688a1.875 1.875 0 1 1 2.652 2.652L6.832 19.82a4.5 4.5 0 0 1-1.897 1.13l-2.685.8.8-2.685a4.5 4.5 0 0 1 1.13-1.897L16.863 4.487Zm0 0L19.5 7.125"/>
                      </svg>
                      重命名
                    </div>
                    <div
                      onclick="document.getElementById('deleteConfirm').showModal()"
                      class="p-2 hover:bg-gray-100 cursor-pointer flex items-center text-warning rounded">
                      <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"
                           stroke-width="1.5" stroke="currentColor" class="size-4 mr-1.5">
                        <path stroke-linecap="round" stroke-linejoin="round"
                              d="m14.74 9-.346 9m-4.788 0L9.26 9m9.968-3.21c.342.052.682.107 1.022.166m-1.022-.165L18.16 19.673a2.25 2.25 0 0 1-2.244 2.077H8.084a2.25 2.25 0 0 1-2.244-2.077L4.772 5.79m14.456 0a48.108 48.108 0 0 0-3.478-.397m-12 .562c.34-.059.68-.114 1.022-.165m0 0a48.11 48.11 0 0 1 3.478-.397m7.5 0v-.916c0-1.18-.91-2.164-2.09-2.201a51.964 51.964 0 0 0-3.32 0c-1.18.037-2.09 1.022-2.09 2.201v.916m7.5 0a48.667 48.667 0 0 0-7.5 0"/>
                      </svg>
                      删除
                    </div>
                    <dialog id="deleteConfirm" class="modal modal-bottom sm:modal-middle">
                      <div class="modal-box">
                        <h3 class="font-bold text-lg">删除会话</h3>
                        <p class="py-4">删除后将无法恢复，您确定要删除吗？</p>
                        <div class="modal-action">
                          <form method="dialog">
                            <button class="btn btn-outline btn-error"
                                    @click="deleteChatHistory(item.id)">确定
                            </button>
                            <button class="btn btn-outline ml-2">取消</button>
                          </form>
                        </div>
                      </div>
                    </dialog>
                  </div>
                </template>
              </Dropdown>
            </div>
          </div>
        </div>
      </InfiniteScroll>
      <div class="p-4 border-t border-gray-200">
        <div class="flex items-center space-x-3">
          <div
            class="w-8 h-8 rounded-full bg-[#6653e8] flex items-center justify-center text-white">
            <span class="text-xs">{{ currentUser[0].toUpperCase() }}</span>
          </div>
          <div class="font-extrabold">{{ currentUser }}</div>
        </div>
      </div>
    </div>

    <!-- 主聊天区 -->
    <div class="flex-1 flex flex-col overflow-hidden">
      <!-- 顶部栏 -->
      <div class="h-16 flex items-center justify-between px-6 bg-white border-b border-gray-200">
        <div class="flex items-center">
          <h1 class="text-xl font-bold gradient-text">{{ selectedHistory.title }}</h1>
        </div>
        <div class="flex items-center space-x-4">

          <div class="drawer drawer-end">
            <input id="setting-drawer" type="checkbox" class="drawer-toggle"/>
            <div class="drawer-content">
              <label for="setting-drawer" class="drawer-button text-gray-500">
                <div class="rounded-full hover:bg-gray-100 p-2 cursor-pointer">
                  <svg xmlns="http://www.w3.org/2000/svg"
                       class="h-5 w-5 " viewBox="0 0 20 20"
                       fill="currentColor">
                    <path fill-rule="evenodd"
                          d="M11.49 3.17c-.38-1.56-2.6-1.56-2.98 0a1.532 1.532 0 01-2.286.948c-1.372-.836-2.942.734-2.106 2.106.54.886.061 2.042-.947 2.287-1.561.379-1.561 2.6 0 2.978a1.532 1.532 0 01.947 2.287c-.836 1.372.734 2.942 2.106 2.106a1.532 1.532 0 012.287.947c.379 1.561 2.6 1.561 2.978 0a1.533 1.533 0 012.287-.947c1.372.836 2.942-.734 2.106-2.106a1.533 1.533 0 01.947-2.287c1.561-.379 1.561-2.6 0-2.978a1.532 1.532 0 01-.947-2.287c.836-1.372-.734-2.942-2.106-2.106a1.532 1.532 0 01-2.287-.947zM10 13a3 3 0 100-6 3 3 0 000 6z"
                          clip-rule="evenodd"/>
                  </svg>
                </div>

              </label>
            </div>
            <div class="drawer-side z-50">
              <label for="setting-drawer" aria-label="close sidebar" class="drawer-overlay"></label>
              <div id="settings-drawer"
                   class="fixed inset-y-0 right-0 w-80 bg-white shadow-lg border-l border-gray-200">
                <div class="h-full flex flex-col">
                  <!-- 抽屉标题 -->
                  <div class="h-16 flex items-center justify-between px-6 border-b border-gray-200">
                    <h2 class="text-lg font-semibold text-gray-800">设置</h2>
                  </div>
                  <!-- 抽屉内容 -->
                  <div class="flex-1 overflow-y-auto p-6">
                    <div class="space-y-4">
                      <!-- 模型选择 -->
                      <div>
                        <label
                          class="block text-sm font-medium text-gray-700 mb-2">系统提示词</label>
                        <textarea v-model="llm_config.system_prompt"
                                  class="textarea textarea-bordered w-full max-w-xs"
                                  placeholder="请输入系统提示词"></textarea>
                      </div>
                      <div>
                        <label
                          class="block text-sm font-medium text-gray-700 mb-2">模型供应商API地址</label>
                        <input type="text" class="input input-bordered w-full max-w-xs"
                               v-model="llm_config.base_url"/>
                      </div>
                      <div>
                        <label
                          class="block text-sm font-medium text-gray-700 mb-2">API 类型</label>
                        <div class="join">
                          <input class="join-item btn" type="radio" name="options"
                                 checked
                                 v-model="llm_config.api_type"
                                 value="openai"
                                 aria-label="openai"/>
                          <input
                            class="join-item btn"
                            type="radio"
                            name="options"
                            disabled
                            v-model="llm_config.api_type"
                            value="ollama"
                            aria-label="ollama"
                          />
                        </div>
                      </div>
                      <div>
                        <label class="block text-sm font-medium text-gray-700 mb-2">API Key</label>
                        <input type="text" class="input input-bordered w-full max-w-xs"
                               v-model="llm_config.api_key"/>
                      </div>
                      <div>
                        <label class="block text-sm font-medium text-gray-700 mb-2">模型</label>
                        <input type="text" class="input input-bordered w-full max-w-xs"
                               v-model="llm_config.model"/>
                      </div>
                      <div>
                        <label
                          class="block text-sm font-medium text-gray-700 mb-2">知识库选择</label>
                        <v-select multiple :options="knowledgeList"
                                  :reduce="item => item.index_name"
                                  label="name"
                                  v-model="retriever_config.collection_name">
                        </v-select>
                      </div>
                      <div>
                        <label class="label cursor-pointer">
                          <span class="label-text">知识库检索</span>
                          <input type="checkbox" v-model="retriever_config.open_rag"
                                 class="checkbox checkbox-primary"/>
                        </label>
                      </div>

                      <!-- 高级选项 -->
                      <div class="collapse collapse-plus border border-gray-200 rounded-lg">
                        <input type="checkbox"/>
                        <div
                          class="collapse-title text-sm font-medium text-gray-700 flex items-center">
                          高级选项
                        </div>
                        <div class="collapse-content">
                          <div class="space-y-4 pt-2">
                            <!-- 检索设置 -->
                            <div>
                              <label
                                class="block text-sm text-primary font-medium mb-2">采样参数</label>
                              <div class="space-y-2">
                                <label class="flex items-center space-x-0.5 cursor-pointer">
                                  <label
                                    class="block text-xs font-medium text-gray-700 mb-2 flex-[2]">温度</label>
                                  <input type="range" min="0.0" max="2.0" step="0.1"
                                         class="range range-xs flex-[5] range-primary"
                                         v-model="llm_config.options.temperature"/>
                                  <div class="flex-1 text-xs">{{ llm_config.options.temperature }}
                                  </div>
                                </label>
                              </div>
                            </div>
                            <div>
                              <label
                                class="block text-sm text-primary font-medium mb-2">检索设置</label>
                              <div class="space-y-2">
                                <label class="items-center space-x-0.5 cursor-pointer flex">
                                  <label
                                    class="block text-xs font-medium text-gray-700 mb-2 flex-[2]">检索召回数</label>
                                  <input type="range" min="1" max="40"
                                         class="range range-xs flex-[5] range-primary"
                                         v-model="retriever_config.retriever_top_k"/>
                                  <div class="flex-1 text-xs">{{
                                      retriever_config.retriever_top_k
                                    }}
                                  </div>
                                </label>
                                <label class="flex items-center space-x-0.5 cursor-pointer">
                                  <label
                                    class="block text-xs font-medium text-gray-700 mb-2 flex-[2]">重排召回数</label>
                                  <input type="range" min="1" max="40"
                                         class="range range-xs flex-[5] range-primary"
                                         v-model="retriever_config.rerank_top_k"/>
                                  <div class="flex-1 text-xs">{{ retriever_config.rerank_top_k }}
                                  </div>
                                </label>
                                <label class="flex items-center space-x-0.5 cursor-pointer">
                                  <label
                                    class="block text-xs font-medium text-gray-700 mb-2 flex-[2]">相似度阈值</label>
                                  <input type="range" min="0.1" max="0.9" step="0.1"
                                         class="range range-xs flex-[5] range-primary"
                                         v-model="retriever_config.rerank_similarity_threshold"/>
                                  <div class="flex-1 text-xs">
                                    {{
                                      retriever_config.rerank_similarity_threshold
                                    }}
                                  </div>
                                </label>
                                <label class="flex items-center space-x-0.5 cursor-pointer">
                                  <label
                                    class="block text-xs font-medium text-gray-700 mb-2 flex-[2]">关键字权重</label>
                                  <input type="range" min="0.1" max="0.9" step="0.1"
                                         class="range range-xs flex-[5] range-primary"
                                         v-model="retriever_config.keyword_weight"/>
                                  <div class="flex-1 text-xs">
                                    {{
                                      retriever_config.keyword_weight
                                    }}
                                  </div>
                                </label>
                              </div>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                  <!-- 抽屉底部 -->
                  <div class="p-4 border-t border-gray-200">
                    <button
                      class="btn btn-primary btn-block bg-[#6653e8] border-none hover:bg-[#5748c7]"
                      @click="saveSettings">
                      保存设置
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div
            class="avatar placeholder cursor-pointer dropdown dropdown-bottom dropdown-end">
            <div tabindex="0" class="flex items-center space-x-3">
              <div
                class="w-8 h-8 rounded-full bg-[#6653e8] flex items-center justify-center text-white">
                <span class="text-xs">{{ currentUser[0].toUpperCase() }}</span>
              </div>
            </div>
            <ul tabindex="0"
                class="dropdown-content z-[1] menu p-2 shadow bg-base-100 rounded w-40 mt-1">
              <li><i class="fa fa-gears" aria-hidden="true"
                     @click="router.push({ name: 'manager' })">后台</i></li>
              <li><i class="fa fa-sign-out" aria-hidden="true"
                     @click="store.dispatch('auth/logout')">登出</i></li>
            </ul>
          </div>
        </div>
      </div>

      <!-- 消息区 -->
      <div id="chat-messages" class="flex-1 overflow-auto p-6 pl-36 pr-36 space-y-4">
        <div v-if="messages.list.length > 0" v-for="(item, index) in messages.list" :key="index">
          <div class="message-enter flex items-start justify-end" id="user"
               @mouseenter="()=>{
                   if (index === messages.list.length - 1){
                     return
                   }
                   item.showOperation = true
                 }"
               @mouseleave="()=>{
                   if (index === messages.list.length - 1){
                     return
                   }
                   item.showOperation = false
                 }"
               v-if="item.role==='user'">
            <div v-if="index !== editIndex" class="flex">
              <div class="h-[1.25rem] mr-4 mt-[16px]">
                <Transition name="fade">
                  <div class="flex text-gray-500" v-if="item.showOperation">
                    <svg xmlns="http://www.w3.org/2000/svg"
                         fill="none"
                         @click="copyContent(index)"
                         viewBox="0 0 24 24"
                         stroke-width="2" stroke="currentColor"
                         class="w-[1.25rem] cursor-pointer mr-4 hover:text-[#6653e8]">
                      <path stroke-linecap="round" stroke-linejoin="round"
                            d="M15.75 17.25v3.375c0 .621-.504 1.125-1.125 1.125h-9.75a1.125 1.125 0 0 1-1.125-1.125V7.875c0-.621.504-1.125 1.125-1.125H6.75a9.06 9.06 0 0 1 1.5.124m7.5 10.376h3.375c.621 0 1.125-.504 1.125-1.125V11.25c0-4.46-3.243-8.161-7.5-8.876a9.06 9.06 0 0 0-1.5-.124H9.375c-.621 0-1.125.504-1.125 1.125v3.5m7.5 10.375H9.375a1.125 1.125 0 0 1-1.125-1.125v-9.25m12 6.625v-1.875a3.375 3.375 0 0 0-3.375-3.375h-1.5a1.125 1.125 0 0 1-1.125-1.125v-1.5a3.375 3.375 0 0 0-3.375-3.375H9.75"/>
                    </svg>
                    <svg xmlns="http://www.w3.org/2000/svg"
                         fill="none"
                         viewBox="0 0 24 24"
                         @click="editIndex = index;editContent=item.content"
                         stroke-width="2" stroke="currentColor"
                         class="w-[1.25rem] cursor-pointer hover:text-[#6653e8]">
                      <path stroke-linecap="round" stroke-linejoin="round"
                            d="m16.862 4.487 1.687-1.688a1.875 1.875 0 1 1 2.652 2.652L10.582 16.07a4.5 4.5 0 0 1-1.897 1.13L6 18l.8-2.685a4.5 4.5 0 0 1 1.13-1.897l8.932-8.931Zm0 0L19.5 7.125M18 14v4.75A2.25 2.25 0 0 1 15.75 21H5.25A2.25 2.25 0 0 1 3 18.75V8.25A2.25 2.25 0 0 1 5.25 6H10"/>
                    </svg>
                  </div>
                </Transition>
              </div>
              <div class="max-w-[60rem]">
                <div class="bg-[#6653e8] text-white p-4 rounded-lg shadow-sm">
                  <p class="text-sm">{{ item.content }}</p>
                  <div class="mt-3 space-y-2" v-if="item.files && item.files.length>0">
                    <!-- 文件预览 -->
                    <div class="grid grid-rows-[auto_1fr] grid-cols-[1fr_auto] gap-2">
                      <div v-for="(f,i) in item.files" :key="i"
                           class="file-preview bg-white bg-opacity-20 p-3 rounded-lg flex items-center">
                        <div class="mr-3 text-white">
                          <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none"
                               viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                  d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
                          </svg>
                        </div>
                        <div>
                          <p
                            class="text-sm font-medium max-w-36 whitespace-nowrap overflow-hidden text-ellipsis">
                            {{ f.filename }}</p>
                          <p class="text-xs opacity-70">{{ f.mimetype }}</p>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            <div v-else class="flex flex-col">
              <textarea class="textarea textarea-primary min-w-[40rem] resize-none"
                        @input="resize"
                        v-model="editContent"></textarea>
              <div class="mt-4 flex justify-end">
                <button class="btn btn-outline btn-primary mr-4 btn-sm"
                        @click="item.content=editContent;editContent='';reGenerate(index+1);editIndex=-1">
                  发送
                </button>
                <button class="btn btn-outline btn-sm" @click="editIndex = -1;editContent=''">取消
                </button>
              </div>
            </div>
          </div>
          <div class="message-enter flex items-start" id="assistant" v-else>
            <div class="flex-shrink-0 mr-3">
              <div class="w-10 h-10 rounded-full flex items-center justify-center text-[#6653e8]">
                <img src="/src/assets/img/tzzz.png" alt="">
              </div>
            </div>
            <div class="flex-1"
                 @mouseenter="()=>{
                   if (index === messages.list.length - 1){
                     return
                   }
                   item.showOperation = true
                 }"
                 @mouseleave="()=>{
                   if (index === messages.list.length - 1){
                     return
                   }
                   item.showOperation = false
                 }"
            >
              <div class="bg-white p-4 rounded-lg shadow-sm border border-gray-200 max-w-full">
                <div class="w-full" v-if="item.think">
                  <div class="mb-4 bg-gray-400/10 cursor-pointer rounded-lg border border-gray-500">
                    <div class="flex justify-between p-2.5"
                         @click="toggleThinking(item,$event)">
                      <span v-if="item.think_time">深度思考 (时间: {{ item.think_time }}秒)</span>
                      <span v-else>深度思考中...</span>
                      <span class="select-none">{{ item.isOpen ? '▼' : '►' }}</span>
                    </div>
                    <div v-show="item.isOpen" class="pl-2.5 pr-2.5 pb-2.5 overflow-hidden"
                         id="think-content">
                      <div class="border-l-2 border-l-gray-500 pl-5 text-gray-500 text-sm">
                        <MarkdownRenderer
                          :id="item.id + '-think'"
                          :content="item.think"
                        />
                      </div>
                    </div>
                  </div>
                </div>
                <MarkdownRenderer
                  :id="item.id + '-content'"
                  :content="item.content"
                />
                <flowing-text-animation :text="item.stepcontent"
                                        v-if="item.stepcontent && item.stepcontent!==''">

                </flowing-text-animation>
                <div class="grid grid-rows-[auto_1fr] grid-cols-[1fr_auto] gap-2 mt-3"
                     v-if="item.files && item.files.length>0">
                  <div v-for="(f,i) in item.files" :key="i"
                       @click="downloadBase64File(f.base64Data, f.filename, f.mimetype)"
                       class="file-preview bg-gray-300 bg-opacity-20 p-3 rounded-lg flex items-center cursor-pointer">
                    <div class="mr-3">
                      <i
                        :class="`fa ${getFileIcon(getFileExtension(f.filename))} text-primary`"></i>
                    </div>
                    <div>
                      <p
                        class="text-sm font-medium max-w-36 whitespace-nowrap overflow-hidden text-ellipsis">
                        {{ f.filename }}</p>
                      <p class="text-xs opacity-70">{{ f.mimetype }}</p>
                    </div>
                  </div>
                </div>
                <div
                  id="galley"
                  class="grid grid-rows-[auto_1fr] grid-cols-[1fr_auto] gap-2 mt-3"
                  v-if="item.media && item.media.length>0">
                  <ul>
                    <li v-for="(m,i) in item.media" :key="i" class="max-w-[100px]">
                      <img v-if="m.mimetype.startsWith('image')" :src="m.base64Data"
                           :data-original="m.base64Data" alt="">
                    </li>
                  </ul>
                </div>
              </div>
              <div class="h-[1.25rem] mt-4">
                <Transition name="fade">
                  <div class="flex text-gray-500" v-if="item.showOperation">
                    <svg xmlns="http://www.w3.org/2000/svg"
                         fill="none"
                         @click="copyContent(index)"
                         viewBox="0 0 24 24"
                         stroke-width="2" stroke="currentColor"
                         class="w-[1.25rem] cursor-pointer hover:text-[#6653e8]">
                      <path stroke-linecap="round" stroke-linejoin="round"
                            d="M15.75 17.25v3.375c0 .621-.504 1.125-1.125 1.125h-9.75a1.125 1.125 0 0 1-1.125-1.125V7.875c0-.621.504-1.125 1.125-1.125H6.75a9.06 9.06 0 0 1 1.5.124m7.5 10.376h3.375c.621 0 1.125-.504 1.125-1.125V11.25c0-4.46-3.243-8.161-7.5-8.876a9.06 9.06 0 0 0-1.5-.124H9.375c-.621 0-1.125.504-1.125 1.125v3.5m7.5 10.375H9.375a1.125 1.125 0 0 1-1.125-1.125v-9.25m12 6.625v-1.875a3.375 3.375 0 0 0-3.375-3.375h-1.5a1.125 1.125 0 0 1-1.125-1.125v-1.5a3.375 3.375 0 0 0-3.375-3.375H9.75"/>
                    </svg>
                    <svg xmlns="http://www.w3.org/2000/svg"
                         fill="none"
                         viewBox="0 0 24 24"
                         @click="reGenerate(index)"
                         stroke-width="2" stroke="currentColor"
                         class="w-[1.25rem] ml-4 cursor-pointer hover:text-[#6653e8]">
                      <path stroke-linecap="round" stroke-linejoin="round"
                            d="M16.023 9.348h4.992v-.001M2.985 19.644v-4.992m0 0h4.992m-4.993 0 3.181 3.183a8.25 8.25 0 0 0 13.803-3.7M4.031 9.865a8.25 8.25 0 0 1 13.803-3.7l3.181 3.182m0-4.991v4.99"/>
                    </svg>
                    <div class="drawer drawer-end w-6 h-6 ml-4">
                      <input id="references" type="checkbox" class="drawer-toggle"/>
                      <div class="drawer-content">
                        <!-- Page content here -->
                        <label for="references">
                          <svg xmlns="http://www.w3.org/2000/svg"
                               fill="none"
                               viewBox="0 0 24 24"
                               stroke-width="2" stroke="currentColor"
                               class="w-[1.25rem] h-6 cursor-pointer hover:text-[#6653e8]">
                            <path stroke-linecap="round" stroke-linejoin="round"
                                  d="M19.5 14.25v-2.625a3.375 3.375 0 0 0-3.375-3.375h-1.5A1.125 1.125 0 0 1 13.5 7.125v-1.5a3.375 3.375 0 0 0-3.375-3.375H8.25m0 12.75h7.5m-7.5 3H12M10.5 2.25H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 0 0-9-9Z"/>

                          </svg>
                        </label>
                      </div>
                      <div class="drawer-side z-50">
                        <label for="references" aria-label="close sidebar"
                               class="drawer-overlay"></label>
                        <references-viewer class="max-w-[70%] h-full" :documents="item.references">

                        </references-viewer>
                      </div>
                    </div>
                  </div>
                </Transition>
              </div>
            </div>
          </div>
        </div>
        <div v-else class="h-full">
          <!-- 默认介绍页面 -->
          <div id="intro-page" class="h-full flex flex-col items-center justify-center intro-enter">
            <div class="max-w-3xl w-full text-center">
              <div
                class="w-20 h-20 mx-auto mb-6 rounded-full bg-gradient-to-r from-[#6653e8] to-[#8a7aed] flex items-center justify-center">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-10 w-10 text-white"
                     viewBox="0 0 20 20" fill="currentColor">
                  <path
                    d="M2 5a2 2 0 012-2h7a2 2 0 012 2v4a2 2 0 01-2 2H9l-3 3v-3H4a2 2 0 01-2-2V5z"/>
                  <path
                    d="M15 7v2a4 4 0 01-4 4H9.828l-1.766 1.767c.28.149.599.233.938.233h2l3 3v-3h2a2 2 0 002-2V9a2 2 0 00-2-2h-1z"/>
                </svg>
              </div>
              <h2 class="text-2xl font-bold text-gray-800 mb-2">欢迎使用RAG智能助手</h2>
              <p class="text-gray-600 mb-8">
                基于检索增强生成技术，为您提供精准的知识问答和智能分析</p>
            </div>
          </div>
        </div>
      </div>

      <!-- 输入区 -->
      <div class="input-area flex justify-center">
        <div class="max-w-[80%] flex-1 mb-8 pl-4 pr-4 pt-8 pb-4 bg-gray-100 rounded-xl">
          <div class="grid grid-cols-5">
            <div class="indicator mb-4 group cursor-pointer" v-for="(f,i) in uploadedFiles"
                 :key="i">
              <div
                class="indicator-item bg-white w-5 h-5 rounded-full p-0.5 hidden group-hover:block"
                @click="removeFile(i)">
                <svg viewBox="0 0 24 24" fill="none"
                     stroke="currentColor"
                     xmlns="http://www.w3.org/2000/svg">
                  <path d="M18 6L6 18" stroke="black" stroke-width="2" stroke-linecap="round"/>
                  <path d="M6 6L18 18" stroke="black" stroke-width="2" stroke-linecap="round"/>
                </svg>
              </div>
              <div
                class="bg-base-300 place-items-center p-4 rounded-xl flex">
                <label class="swap" :class="{'swap-active':  f.loading}">
                  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"
                       stroke-width="1.5" stroke="currentColor" class="swap-off">
                    <path stroke-linecap="round" stroke-linejoin="round"
                          d="M19.5 14.25v-2.625a3.375 3.375 0 0 0-3.375-3.375h-1.5A1.125 1.125 0 0 1 13.5 7.125v-1.5a3.375 3.375 0 0 0-3.375-3.375H8.25m0 12.75h7.5m-7.5 3H12M10.5 2.25H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 0 0-9-9Z"/>
                  </svg>
                  <span class="loading loading-spinner text-primary swap-on"></span>
                </label>

                <div>
                  <div
                    class="max-w-36 whitespace-nowrap overflow-hidden text-ellipsis text-sm ml-2">
                    {{ f.file.name }}
                  </div>
                  <div class="text-xs text-gray-400 ml-2">
                    {{
                      f.file.size / 1024 >= 1024
                        ? (f.file.size / 1024 / 1024).toFixed(2) + 'MB'
                        : (f.file.size / 1024).toFixed(2) + 'KB'
                    }}
                  </div>
                </div>

              </div>
            </div>
          </div>
          <div class="flex items-center space-x-2">
            <label class="btn btn-circle btn-sm btn-ghost text-gray-500 hover:bg-gray-100">
              <input type="file" class="hidden" @change="handleFileUpload" multiple ref="fileInput">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-7 w-7" fill="none"
                   viewBox="0 0 24 24"
                   stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                      d="M15.172 7l-6.586 6.586a2 2 0 102.828 2.828l6.414-6.586a4 4 0 00-5.656-5.656l-6.415 6.585a6 6 0 108.486 8.486L20.5 13"/>
              </svg>
            </label>
            <div class="flex-1 relative">
            <textarea id="message-input"
                      @input="resize"
                      v-model="userInput.input"
                      class="w-full border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-[#6653e8] focus:border-transparent resize-none"
                      rows="1" placeholder="输入消息..." style="max-height: 150px;"></textarea>
            </div>
            <label class="swap swap-flip" :class="{'swap-active':  generating}">
              <div
                @click.stop="sendMessage(false)"
                :disabled="sendMessageDisabled"
                class="swap-off btn btn-sm btn-primary bg-[#6653e8] border-none hover:bg-[#5748c7] text-white">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20"
                     fill="currentColor">
                  <path fill-rule="evenodd"
                        d="M10.293 3.293a1 1 0 011.414 0l6 6a1 1 0 010 1.414l-6 6a1 1 0 01-1.414-1.414L14.586 11H3a1 1 0 110-2h11.586l-4.293-4.293a1 1 0 010-1.414z"
                        clip-rule="evenodd"/>
                </svg>
              </div>
              <div
                @click.stop="stopGenerate"
                class="swap-on btn btn-sm btn-primary bg-[#6653e8] border-none hover:bg-[#5748c7] text-white">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20"
                     fill="currentColor">
                  <rect x="3" y="3" width="14" height="14"/>
                </svg>
              </div>
            </label>
          </div>
        </div>

      </div>
    </div>
  </div>
</template>
<script setup>
import anime from 'animejs'
import {nextTick, onMounted, reactive, ref, watchEffect} from 'vue'
import {
  chat_stream,
  delete_chat_history_by_id,
  get_all_knowledge,
  get_context_by_id,
  get_context_list,
  save_or_update_context,
  update_context_title,
  upload_file
} from '@/api/chat.js'
import {useStore} from 'vuex'
import {v4 as uuidv4} from 'uuid'
import MarkdownRenderer from '@/components/MarkdownRenderer.vue'
import InfiniteScroll from '@/components/InfiniteScroll.vue'
import notify from '@/components/notify.js'
import Dropdown from '@/components/Dropdown.vue'
import ReferencesViewer from '@/components/ReferencesViewer.vue'
import {downloadBase64File, getFileExtension, getFileIcon} from '@/utils/commonUtil.js'
import FlowingTextAnimation from '@/components/FlowingTextAnimation.vue'
import Viewer from 'viewerjs'
import router from "@/router/index.js";

const llm_config = ref({
  system_prompt: '',
  api_type: 'openai',
  base_url: 'https://api.deepseek.com/v1',
  api_key: '',
  model: 'deepseek-chat',
  options: {
    temperature: 1.0
  }
})


let retriever_config = reactive({
  retriever_top_k: 10,
  rerank_top_k: 10,
  rerank_similarity_threshold: 0.5,
  collection_name: [],
  open_rag: false,
  keyword_weight: 0.5
})

const store = useStore()
const currentUser = store.getters['auth/currentUser']
const token = store.state.auth.token
const generating = ref(false)

const chatHistory = reactive({
  list: [],
  loading: false,
  noMore: false,
  error: true,
  pageParam: {
    offset: 1,
    limit: 30
  },
  async loadData() {
    try {
      const res = await get_context_list(chatHistory.pageParam)
      chatHistory.list.push(...res.data.items.map(item => ({...item})))

      // 模拟加载完所有数据后设置 noMore
      if (res.data.items.length < chatHistory.pageParam.limit) {
        chatHistory.noMore = true
      } else {
        chatHistory.pageParam.offset += 1
      }
    } catch (err) {
      chatHistory.error = true
    }
  }
})

//历史列表
let selectedHistory = ref({})

// 历史记录 -> 消息列表
const messages = reactive({
  list: []
})

// 编辑聊天索引
const editIndex = ref(null)
const editContent = ref('')


//知识库列表
const knowledgeList = ref([])

// 新对话
const newChat = () => {
  messages.list = []
  selectedHistory.value = {}
  chatHistory.list.map(i => {
    i.selected = false
  })
}

//输入框相关
const userInput = reactive({
  input: ''
})

//messages 动画
const messageAnime = (last) => {
  nextTick(async () => {
    const mes_dom = document.querySelectorAll('.message-enter')
    if (last) {
      anime({
        targets: mes_dom[mes_dom.length - 1],
        opacity: [0, 1],
        delay: 0,
        duration: 1000,
        easing: 'easeOutExpo'
      })
      return
    }

    mes_dom.forEach((msg, index) => {
      anime({
        targets: msg,
        opacity: [0, 1],
        delay: index * 100,
        duration: 1000,
        easing: 'easeOutExpo'
      })
    })
  })
}

// 选择历史记录
const selectChatHistory = (item) => {
  if (selectedHistory.value.id === item.id) {
    return
  }
  chatHistory.list.map(i => {
    i.selected = false
    i.editTitle = false
  })
  item.selected = true
  selectedHistory.value = item
  get_context_by_id(item.id).then(async res => {
    messages.list = JSON.parse(res.data.message_content)
    messages.list.map((i, index) => {
      if (index === messages.list.length - 1) {
        i.showOperation = true
        return
      }
      i.showOperation = false
    })
    messageAnime(false)
    await nextTick(() => {
      imagePreview()
    })
  })
}

//保存配置
const saveSettings = (f = true) => {
  let param = {retriever_config: retriever_config, llm_config: llm_config.value}
  localStorage.setItem('params', JSON.stringify(param))
  if (f) {
    notify.success('保存成功')
  }
}

//初始化配置
const initSettings = () => {
  const config = localStorage.getItem('params')
  if (config && config !== '{}') {
    const j = JSON.parse(config)
    if (j.retriever_config) {
      Object.assign(retriever_config, j.retriever_config)
    }
    const _collection_names = knowledgeList.value.map(item => item.index_name)
    if (!_collection_names || _collection_names.length === 0) {
      retriever_config.collection_name = []
    } else {
      retriever_config.collection_name = retriever_config.collection_name.map(item => {
        if (_collection_names.includes(item)) {
          return item
        }
      })
    }

    llm_config.value = j.llm_config
    return
  }

  saveSettings(false)
}

//思考框开启关闭
const toggleThinking = (message, event) => {
  message.isOpen = !message.isOpen
  if (message.isOpen) {
    nextTick(() => {
      const element = event.target.parentElement.querySelector('#think-content')
      const fullHeight = element.scrollHeight
      anime({
        targets: element,
        height: ['0px', `${fullHeight}px`],
        paddingBottom: ['0px', '10px'],
        duration: 300,
        easing: 'easeOutExpo',
        complete: function () {
          element.removeAttribute('style')
        }
      })
    })
  }
}

let sendMessageDisabled = ref(null)
let uploadedFiles = reactive([])
let fileInput = ref(null)
//处理文件上传解析
const handleFileUpload = (event) => {
  const files = Array.from(event.target.files).map(file => ({
    file,          // 原始 File 对象
    loading: true,
    uuid: null
  }))

  uploadedFiles.push(...files)
  sendMessageDisabled.value = 'disabled'

  upload_file(files.map(file => file.file)).then(response => {
    for (let f of response.data) {
      for (let _f of uploadedFiles) {
        if (f.filename === _f.file.name) {
          _f.loading = false
          _f.uuid = f.uuid
        }
      }
    }
    sendMessageDisabled.value = null
  })
}

//删除文件
const removeFile = (index) => {
  uploadedFiles.splice(index, 1)
  if (fileInput.value) {
    fileInput.value.value = null
  }
  if (uploadedFiles.length === 0) {
    sendMessageDisabled.value = null
  }
}

//滚动到最底部
const scrollTop = () => {
  const chatMessages = document.getElementById('chat-messages')
  chatMessages.scrollTop = chatMessages.scrollHeight
}

// 用户是否手动控制窗口
let userControl = false

// 处理流式返回
const processStream = async (response) => {
  const readWithTimeout = (reader, timeoutMs) => {
    return Promise.race([
      reader.read(),
      new Promise((_, reject) =>
        setTimeout(() => reject(new Error('读取超时')), timeoutMs)
      )
    ])
  }

  const reader = response.body.getReader()
  const decoder = new TextDecoder('utf-8')
  let newChat = false
  if (Object.keys(selectedHistory.value).length === 0) {
    const uuid = uuidv4()
    selectedHistory.value = {
      title: '新对话',
      id: null,
      uuid: uuid
    }
    chatHistory.list.unshift({
      title: '新对话',
      id: null,
      selected: true,
      uuid: uuid
    })
    newChat = true
  }
  let partialData = ''
  let allText = ''
  let allThink = ''
  let timeout = false
  let think_time_start = null
  messages.list.push({
    role: 'assistant',
    think: '',
    content: '',
    flag: false,
    references: [],
    files: [],
    media: [],
    id: 'id-' + uuidv4().split('-')[0]
  })

  const handleWheel = (event) => {
    //监听用户滚动是否向上，则不再强制scroll top
    if (event.deltaY < 0) {
      userControl = true
    }
  }

  window.addEventListener('wheel', handleWheel)

  messageAnime(true)
  const assistant = messages.list[messages.list.length - 1]
  while (true) {
    let readResult
    try {
      readResult = await readWithTimeout(reader, 150000)
    } catch (error) {
      if (error.name === 'AbortError') {
        return
      }
      timeout = true
      break
    }

    const {done, value} = readResult
    if (done) {
      break
    }

    partialData += decoder.decode(value, {stream: true})
    let lines = partialData.split('\n')
    partialData = lines.pop()
    for (let line of lines) {
      if (line.trim()) {
        const res = JSON.parse(line)
        if (res.heartbeat) {
          continue
        }
        if (res.reference) {
          messages.list[messages.list.length - 1].references = res.reference
        }

        if (res.files && res.files.length > 0) {
          for (let f of res.files) {
            if (f.mimetype.startsWith('image') || f.mimetype.startsWith('video') || f.mimetype.startsWith('audio')) {
              assistant.media.push({
                filename: f.filename,
                mimetype: f.mimetype,
                base64Data: f.filedata
              })
            } else {
              assistant.files.push({
                filename: f.filename,
                mimetype: f.mimetype,
                base64Data: f.filedata
              })
            }
          }
        }

        const message = res.message

        if (!userControl) {
          scrollTop()
        }


        let content = message.content
        let think = message.think

        if (content === null && think !== null) {
          if (think_time_start === null) {
            think_time_start = Date.now()
            assistant.isOpen = true
          }
          allThink += think
          assistant.think = allThink
        } else {
          if (think_time_start !== null) {
            const think_time = ((Date.now() - think_time_start) / 1000).toFixed(1)
            think_time_start = null
            assistant.think_time = think_time
          }
          if (res.step_content) {
            assistant.stepcontent = content
          } else {
            allText += content
            assistant.content = allText
            assistant.stepcontent = null
          }
        }
      }
    }
  }
  assistant.stepcontent = null

  // 清除wheel
  window.removeEventListener('wheel', handleWheel)
  userControl = false

  if (timeout) {
    messages.list.pop()
    messages.list.push({
      role: 'assistant',
      content: '回答超时，请重试。',
      flag: false
    })
    return
  }

  if (!allText || allText === '') return

  await nextTick(() => {
    imagePreview()
  })

  //如果message长度为2 就强制生成标题
  save_or_update_context({
    id: selectedHistory.value.id ? selectedHistory.value.id : -1,
    message_content: JSON.stringify(messages.list),
    title: (selectedHistory.value.title === '新对话' ||
      selectedHistory.value.title === '' ||
      selectedHistory.value.title === null ||
      messages.list.length === 2) ? '' : selectedHistory.value.title,
    llm_config: llm_config.value
  }).then(e => {
    if (newChat) {
      // 顺序不能颠倒
      chatHistory.list.forEach(item => {
        if (item.uuid === selectedHistory.value.uuid) {
          item.title = e.data.title
          item.selected = true
          item.id = e.data.id
        }
      })
      selectedHistory.value.id = e.data.id
      selectedHistory.value.title = e.data.title
    }
  })

  messages.list[messages.list.length - 1].showOperation = true
  generating.value = false
}

// 取消HTTP请求控制器
let controller

//发送消息
const sendMessage = async (re = false) => {
  if (!re && userInput.input.trim() === '') {
    generating.value = false
    return
  }

  if (!re) {
    generating.value = true
    let message = {
      role: 'user',
      content: userInput.input,
      files: uploadedFiles.map(f => {
        return {
          filename: f.file.name,
          uuid: f.uuid,
          mimetype: f.file.type
        }
      })
    }
    messages.list.push(message)
    uploadedFiles.splice(0)
    messageAnime(true)
    userInput.input = ''
  }

  controller = new AbortController()
  const response = await chat_stream(JSON.stringify({
    context: messages.list,
    params: {
      retriever_config: retriever_config,
      llm_config: llm_config.value
    }
  }), controller.signal, token)
  await processStream(response)
}

//停止生成
const stopGenerate = () => {
  generating.value = false
  controller.abort()
}

//重新生成
const reGenerate = (index) => {
  generating.value = true
  messages.list.splice(index)
  sendMessage(true)
}

// 复制生成内容
const copyContent = (index) => {
  if (!navigator.clipboard) {
    // 降级方案：使用旧版 execCommand
    const textarea = document.createElement('textarea')
    textarea.value = messages.list[index].content
    document.body.appendChild(textarea)
    textarea.select()
    document.execCommand('copy')
    document.body.removeChild(textarea)
    notify.success('成功复制到粘贴板')
    return
  }

  navigator.clipboard.writeText(messages.list[index].content)
    .then(() => {
      notify.success('成功复制到粘贴板')
    })
    .catch(err => {
      notify.error('复制失败，请手动复制。')
    })
}

// 调整textarea 高度
const resize = (event) => {
  const dom = event.target
  dom.style.height = 'auto'
  const newHeight = Math.min(dom.scrollHeight, 150)
  dom.style.height = newHeight + 1 + 'px'
}


//侧边栏事件
//删除聊天记录
const deleteChatHistory = (id) => {
  delete_chat_history_by_id(id).then(res => {
    if (res.code === 200) {
      chatHistory.list = chatHistory.list.filter(item => item.id !== id)
      if (selectedHistory.value.id === id) {
        newChat()
      }
    }
  })
}

const updateTitle = (item) => {
  update_context_title({
    id: item.id,
    title: item.title
  }).then(() => {
    item.editTitle = false
  })
}

//图片预览
const imagePreview = () => {
  const gs = document.querySelectorAll('#galley')
  if (gs && gs.length > 0) {
    for (let g of gs) {
      new Viewer(g, {
        url: 'data-original'
      })
    }
  }
}


onMounted(() => {

  //获取知识库列表
  get_all_knowledge({
    offset: 1,
    limit: 99999
  }).then(res => {
    knowledgeList.value = res.items.map(item => ({...item}))
    initSettings()
  })


  const messageInput = document.getElementById('message-input')
  messageInput.addEventListener('keypress', function (e) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage(false)
    }
  })
  imagePreview()
})
</script>
<style>
@import "vue-select/dist/vue-select.css";

.v-select > .vs__dropdown-toggle {
  min-height: 3rem;
  border-radius: 8px;
}

.v-select > .vs__dropdown-toggle > .vs__actions {
  width: 40px;
  justify-content: center;
}

.v-select .vs__dropdown-option--highlight {
  background-color: #0078d7;
}

</style>
<style scoped>


.message-enter {
  opacity: 1;
}

.file-preview {
  transition: all 0.2s ease;
}

.file-preview:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 6px -1px rgba(102, 83, 232, 0.1), 0 2px 4px -1px rgba(102, 83, 232, 0.06);
}

.drawer-slide {
  transform: translateX(100%);
}

.gradient-text {
  background: linear-gradient(90deg, #6653e8, #8a7aed);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
}

.chat-history-item {
  transition: all 0.2s ease;
}

.chat-history-item:hover {
  background-color: #f8f7ff;
}

.chat-history-item.active {
  background-color: #f0edff;
  border-left: 3px solid #6653e8;
}

#message-input {
  max-height: 150px;
  overflow-y: auto;
  padding: 12px 16px;
}

.input-area {
  background-color: transparent;
}

.intro-enter {
  animation: fadeIn 0.5s ease-out forwards;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.feature-card {
  transition: all 0.3s ease;
}

.feature-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 15px -3px rgba(102, 83, 232, 0.1), 0 4px 6px -2px rgba(102, 83, 232, 0.05);
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.5s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

</style>
