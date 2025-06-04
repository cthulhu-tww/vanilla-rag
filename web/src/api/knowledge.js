
import instance from '@/api/request.js'

/**
 * 获取知识库列表
 */
export function getKnowledgeList(params) {
  return instance({
    url: '/knowledge/list',
    method: 'get',
    params
  })
}

/**
 * 添加知识库
 */
export function addKnowledge(data) {
  return instance({
    url: '/knowledge/add',
    method: 'post',
    data
  })
}

/**
 * 更新知识库
 * @param {number} knowledgeId - 知识库ID
 * @param {object} data - 更新的知识库数据
 */
export function updateKnowledge(knowledgeId, data) {
  return instance({
    url: `/knowledge/update_knowledge/${knowledgeId}`,
    method: 'put',
    data
  })
}

/**
 * 删除知识库
 * @param {number} knowledgeId - 知识库ID
 */
export function deleteKnowledge(knowledgeId) {
  return instance({
    url: `/knowledge/delete_knowledge/${knowledgeId}`,
    method: 'delete'
  })
}

/**
 * 查询知识库下的文档列表
 */
export function getDocumentsByKnowledge(params) {
  return instance({
    url: `/knowledge/documents`,
    method: 'get',
    params
  })
}

/**
 * 保存文档到知识库
 */
export function saveDocumentsToKnowledge(knowledgeId, data) {
  return instance({
    url: `/knowledge/documents/${knowledgeId}`,
    method: 'post',
    data
  })
}


/**
 * 删除知识库下的某个或多个文档
 */
export function deleteDocumentsFromKnowledge(knowledgeId, data) {
  return instance({
    url: `/knowledge/documents/${knowledgeId}`,
    method: 'delete',
    data
  })
}

/**
 * 分析文档内容
 */
export function analysisDocument(data) {
  return instance({
    url: `/document/analysis_document`,
    method: 'post',
    data
  })
}

/**
 * 文档切分设置
 */
export function splitSetting(data) {
  return instance({
    url: `/document/split_setting`,
    method: 'post',
    data
  })
}





