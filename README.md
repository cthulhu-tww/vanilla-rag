# Vanilla RAG

## 🌟 项目背景

随着大语言模型在上下文理解能力和基础性能上的持续提升，各种高级 **RAG（Retrieval-Augmented Generation）** 技术的最佳实践也在不断演进。然而，
**Native-RAG 的核心机制在较长一段时间内仍将保持稳定**。

本项目的目标是提供一个尽可能“原生”、轻量且易于理解的 RAG 实现，帮助开发者快速入门并掌握 RAG 的基本原理。

---

## 💡 开发初衷

市场上已有许多优秀的开源 RAG 实现，但它们往往伴随着较高的学习门槛或复杂的项目结构，这对于 AI 应用爱好者或中小型团队来说并不友好。

因此，我们创建了 **Vanilla RAG**：一个**极简、透明、无框架依赖**的 RAG 系统实现，让开发者能够轻松上手并深入理解 RAG 的底层逻辑。

---

## 📦 项目概述

本项目为 **南京清湛人工智能研究院** 内部 RAG 平台简化后的开源版本，是一个拥抱 **MCP（Model Context Protocol）** 的 RAG 系统。

与项目名称一致，我们力求使用最“原生”的方式实现 RAG
功能，仅少量依赖如 [Haystack-ai](https://github.com/deepset-ai/haystack) 的工具类函数，**不依赖任何复杂 AI 框架
**，便于理解与二次开发。

---

## 🧱 项目结构说明

### `rag/` —— RAG 核心服务端代码

- 包含两个子模块：
    - `server`：知识库管理服务端代码。
    - `core`：Native-RAG 的核心实现逻辑。

### `inference/` —— 模型推理模块

- 使用以下模型进行关键功能支持：
    - **[Surya-OCR](https://github.com/VikParuchuri/surya)**：用于文档识别。
    - **[BAAI/bge-m3](https://huggingface.co/BAAI/bge-m3)**：用于文本嵌入。
    - **[BAAI/bge-reranker-v2-m3](https://huggingface.co/BAAI/bge-reranker-v2-m3)**：用于重排序检索结果。

### `mcpserver/` —— MCP 协议服务器Demo

- 提供以下辅助功能：
    - PDF 渲染。
    - 基于 Pollinations-AI 的文本生成图像（text2image）能力。

### `web/` —— 轻量级前端界面

- 支持以下功能：
    - 知识库管理 UI。
    - 聊天交互界面。
    - Markdown 增量渲染 + Mermaid 图表 + LaTex公式支持。
    - 文件上传解析 + MCP 功能集成。

---

## ⚙️ 快速启动指南

### 环境准备

- Python 3.11+
- `uv`（Python 包管理器）
- Node.js（用于前端）
- milvus 2.5.x

### 启动步骤

#### 前端项目（web）

```bash
cd web
npm install
npm run dev
```

#### 后端项目（rag / inference / mcpserver）

```bash
cd rag
uv sync
uv run python main.py
```

### 配置相关

rag/config.yaml 可以配置Milvus服务器地址以及MCP和模型服务地址
inference/config.yaml 可以配置OCR并发数，详情可见[surya-ocr](https://github.com/VikParuchuri/surya)


> 其他模块同理，切换目录后执行相同命令即可。

---

## ⚠️ 商标与免责声明

> 本项目中所使用的 **南京清湛人工智能研究院 Logo** 及相关品牌标识均为其合法持有者的商标资产。  
> 未经书面授权，禁止将上述标识用于衍生项目的宣传、包装或品牌标识中。  
> 本项目采用 GPLv3.0 开源协议，该协议不授予任何商标使用权。

> 本项目中的内容和技术实现仅供学习交流使用，不代表官方立场或背书。
> 若你对本项目有任何疑问或合作意向，请通过以下联系方式与我们沟通。
> [南京清湛人工智能研究院](https://tsingzhan.com/)

## 演示

![RAG](./assets/RAG.png)
![mermaid 图表](./assets/mermaid.png)
![数学公式](./assets/laTex.png)
![文件聊天](./assets/file-chat.png)
![MCP文生图](./assets/MCP-text2image.png)
![MCP pdf渲染](./assets/MCP-pdf.png)

## 路线图

- [ ] 更底层的Native-RAG实现
- [ ] Ollama支持
- [ ] 多MCP服务支持
- [ ] RAG-MCP实现


