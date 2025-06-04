import markdownit from 'markdown-it'
import hljs from 'highlight.js'
import { markdownItMermaid } from '@/plug/markdown-it-mermaid.js'
// Actual default values
const md = markdownit({
  highlight: function(str, lang) {
    if (lang && hljs.getLanguage(lang)) {
      try {
        return hljs.highlight(str, { language: lang }).value
      } catch (__) {
      }
    }
    return '' // use external default escaping
  },
  html: true
})
md.use(markdownItMermaid)
md.disable(['escape'])

md.renderer.rules.table_open = function() {
  return '<div style="max-width: 100%; max-height: 700px; overflow: auto; padding: 10px; margin: 10px 0; border: 2px dashed #7b75b0; border-radius: 4px;">' +
    '<table style="width: auto; border-collapse: collapse;">'  // 改为 width: auto 让表格宽度适应内容
}

md.renderer.rules.table_close = function() {
  return '</table></div>'
}

md.renderer.rules.th_open = function() {
  return '<th style="border: 1px solid #ddd; padding: 12px 8px; text-align: left; white-space: nowrap;">'
}

md.renderer.rules.td_open = function() {
  return '<td style="border: 1px solid #ddd; padding: 12px 8px;">'
}

md.renderer.rules.paragraph_open = function(tokens, idx) {
  let line
  if (tokens[idx].lines && tokens[idx].level === 0) {
    line = tokens[idx].lines[0]
    return '<p class="line" data-line="' + line + '" style="overflow-wrap: anywhere">'
  }
  return '<p>'
}

md.renderer.rules.heading_open = function(tokens, idx) {
  let line
  if (tokens[idx].lines && tokens[idx].level === 0) {
    line = tokens[idx].lines[0]
    return '<h' + tokens[idx].hLevel + ' class="line" data-line="' + line + '">'
  }
  return '<h' + tokens[idx].hLevel + '>'
}


export default md
