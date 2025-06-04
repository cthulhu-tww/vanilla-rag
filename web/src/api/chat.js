import instance from '@/api/request.js'


export async function chat_stream(data, signal, token) {
  return await fetch(import.meta.env.VITE_APP_BASE_URL + import.meta.env.VITE_APP_BASE_API + '/rag_base/rag_chat_stream', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': 'Bearer ' + token
    },
    body: data,
    signal: signal
  })
}


export function get_all_knowledge(params) {
  return instance({
    url: '/knowledge/list',
    method: 'get',
    params
  })
}

export function get_context_list(param = {
  offset: 1,
  limit: 6
}) {
  return instance({
    url: '/chat/title_list',
    method: 'get',
    params: param
  })
}

export function save_or_update_context(data) {
  return instance({
    url: '/chat/',
    method: 'post',
    data
  })
}


export function get_context_by_id(id) {
  return instance({
    url: '/chat/content/' + id,
    method: 'get'
  })
}

export function delete_chat_history_by_id(id) {
  return instance({
    url: `/chat/${id}`,
    method: 'delete'
  })
}

export function update_context_title(data) {
  return instance({
    url: `/chat/update_title`,
    method: 'post',
    data
  })
}


export function upload_file(files, updateProgressBar) {

  const formData = new FormData()

  // 将每个文件添加到FormData中
  for (let i = 0; i < files.length; i++) {
    formData.append('files', files[i])
  }

  return instance({
    url: '/rag_base/upload_file',
    method: 'post',
    data: formData,
    headers: {
      'Content-Type': 'multipart/form-data'
    },
    timeout: 60000,
    onUploadProgress: (progressEvent) => {
      if (!updateProgressBar) {
        return
      }
      const percentCompleted = Math.round(
        (progressEvent.loaded * 100) / progressEvent.total
      )
      // 更新进度条显示
      updateProgressBar(percentCompleted)
    }
  })
}
