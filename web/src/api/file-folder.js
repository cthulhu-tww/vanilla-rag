import instance from '@/api/request.js'

export function get_folders_list(params) {
  return instance({
    url: '/document/folders',
    method: 'get',
    params
  })
}

export function add_folder(data) {
  return instance({
    url: '/document/folder/add',
    method: 'post',
    data
  })
}

export function get_file_list(params) {
  return instance({
    url: '/document/list',
    method: 'get',
    params
  })
}

export function delete_file_by_id(document_id) {
  return instance({
    url: `/document/${document_id}`,
    method: 'delete'
  })
}


export function delete_folder_by_id(folder_id) {
  return instance({
    url: `/document/folder/${folder_id}`,
    method: 'delete'
  })
}

export function all_folders_info() {
  return instance({
    url: `/document/all_folders_info`,
    method: 'get'
  })
}


export function upload_docs(data, fun) {
  return instance({
    url: '/document/uploads',
    method: 'post',
    headers: {
      'Content-Type': 'multipart/form-data'
    },
    timeout: 3000 * 1000,
    data,
    onUploadProgress: fun
  })
}

