# GenePlayBook_Preview

## GenePlayBook_Server

### 🧩 项目简介

GenePlayBook Server 是 GenePlayBook 系统的后端模块，负责处理以下核心任务：

- 对话文本分析与游戏内容生成请求
- 将生成结果上传至阿里云 OSS

---

### 📦 环境依赖安装


```bash
pip install -r requirements.txt
```

---

### ⚙️ 配置说明

在启动服务之前，请根据以下参考文档，修改 `config.py` 文件中的相关变量。

#### ✅ 阿里云 OSS 配置

请参考阿里云 OSS 开发者文档，配置以下变量：

- `OSS_ACCESS_KEY_ID`
- `OSS_ACCESS_KEY_SECRET`
- `OSS_ENDPOINT`
- `OSS_BUCKET_NAME`

📘 文档地址：  
[https://help.aliyun.com/zh/oss/developer-reference/description](https://help.aliyun.com/zh/oss/developer-reference/description)

---

#### ✅ 通义千问（Qwen）与 DeepSeek 配置

如果与源代码保持一致，可以参考 SiliconFlow 平台的官方文档，配置以下变量：

- `QWEN_API_KEY`
- `QWEN_BASE_URL`
- `DEEPSEEK_API_KEY`
- `DEEPSEEK_API_URL`

📘 文档地址：  
[https://docs.siliconflow.cn/cn/userguide/introduction](https://docs.siliconflow.cn/cn/userguide/introduction)

---

#### ✅ 图像生成 API 配置（通义万相）

请参考图像生成 API 使用指南，配置以下变量：

- `IMAGE_API_KEY`
- `IMAGE_MODEL`（推荐值：`wanx2.1-t2i-turbo`）
- `DEFAULT_IMAGE_SIZE`（推荐值：`1440*768`）

📘 文档地址：  
[https://help.aliyun.com/zh/model-studio/user-guide/text-to-image](https://help.aliyun.com/zh/model-studio/user-guide/text-to-image)

---

#### ✅ 应用配置

根据实际项目设置以下变量：

- `secret_key`：用于标识 OSS 存储路径的唯一标识（如用户名）
- `speaker_identifier`：用于标记对话文本中主角说话的标识词（如 `"Speaker 2"`）

---

### 🚀 启动服务

配置完成后，使用以下命令启动服务：

```bash
python app.py \
  --game_path "<path_to_your_GameData_folder>" \
  --dialogue_path "<path_to_your_dialogue_text_file>" \
  --init_message_path "<path_to_your_init_message_file>"
```


#### 参数说明：

- `--game_path`：临时 `GameData` 文件夹路径（用于存储 Unity 游戏所需数据）
- `--dialogue_path`：输入的对话文本文件路径（如 `mygrand.txt`）
- `--init_message_path`：角色背景信息初始化文件路径（如 `init_message.txt`）

##### 📄 对话文本格式示例（dialogue_path）

对话文件需明确标注说话人，每轮对话由说话人标识和对应发言组成。格式如下：

```
Speaker1
Speaker1 的讲话内容

Speaker2
Speaker2 的回答

Speaker1
Speaker1 的回答
```


---

### 🔗 参考文档索引

| 配置项 | 文档链接 |
|--------|----------|
| 阿里云 OSS | [https://help.aliyun.com/zh/oss/developer-reference/description](https://help.aliyun.com/zh/oss/developer-reference/description) |
| DeepSeek | [https://docs.siliconflow.cn/cn/userguide/introduction](https://docs.siliconflow.cn/cn/userguide/introduction) |
| 通义万相 图像生成 | [https://help.aliyun.com/zh/model-studio/user-guide/text-to-image](https://help.aliyun.com/zh/model-studio/user-guide/text-to-image) |

## GenePlayBook_Client

### 🧩 项目简介

**GenePlayBook Client** 是基于 Unity 开发的跨平台前端客户端，负责与用户交互，并渲染由后端生成的图像、语音和剧情内容。支持多平台部署（Windows/macOS/iOS/Android）。

---

### 📦 下载方式

您可以通过以下链接获取完整的 Unity 工程源码：

👉 [📁 点击下载客户端（Google Drive）](https://drive.google.com/drive/folders/186EsRTCjFjtLUHTylLJqFOf33CLES-Qk?usp=drive_link)

---

### ⚙️ 配置说明

在启动 Unity 工程之前，请先完成以下配置步骤。

#### ✅ Unity 插件依赖

请从 Unity Asset Store 安装并导入以下插件：

- 📖 **Book - Page Curl Pro**  
  用于实现电子书翻页动画效果  
  ➡️ [插件链接](https://assetstore.unity.com/packages/tools/gui/book-page-curl-pro-77222)

---

#### ✅ 配置 `Config.cs` 文件

项目中的 `Config.cs` 文件用于配置前端所需的外部服务 API 接口信息。请根据以下技术文档，填写缺失的字段。

---

##### 🎙️ 文本转语音（TTS）配置

用于将文本内容转为语音播放，基于 SiliconFlow 平台的语音合成服务。

**参考文档：**  
[https://docs.siliconflow.cn/cn/api-reference/audio/create-speech](https://docs.siliconflow.cn/cn/api-reference/audio/create-speech)

---

##### 🧱 Tripo3D 图像生成配置（3D 模型）

用于通过文字描述生成 3D 场景图像，基于 Tripo AI 提供的服务。

**参考文档：**  
[https://platform.tripo3d.ai/docs/introduction](https://platform.tripo3d.ai/docs/introduction)

---

##### 🎮 腾讯 GME 实时语音服务配置

用于语音通话、语音识别或语音消息的实时交互，需配置腾讯云的 GME 服务。

**参考文档：**  
[https://cloud.tencent.com/document/product/607/18248](https://cloud.tencent.com/document/product/607/18248)

---

### 🛠 Unity 环境要求

- Unity 版本建议：**2021.3 LTS 或更高**
- 支持平台：**Windows / macOS / iOS / Android**

---
