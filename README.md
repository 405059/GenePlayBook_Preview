# GenePlayBook_Preview

## GenePlayBook_Server

### 🧩 Project Introduction

GenePlayBook Server is the backend module of the GenePlayBook system, responsible for handling the following core tasks:

- Dialogue text analysis and game content generation requests
- Uploading generated results to Alibaba Cloud OSS

---

### 📦 Environment Dependencies Installation

```bash
pip install -r requirements.txt
```

---

### ⚙️ Configuration Guide

Before starting the service, please modify the relevant variables in the `config.py` file according to the following reference documentation.

#### ✅ Alibaba Cloud OSS Configuration

Please refer to the Alibaba Cloud OSS developer documentation to configure the following variables:

- `OSS_ACCESS_KEY_ID`
- `OSS_ACCESS_KEY_SECRET`
- `OSS_ENDPOINT`
- `OSS_BUCKET_NAME`

📘 Documentation:  
[https://help.aliyun.com/zh/oss/developer-reference/description](https://help.aliyun.com/zh/oss/developer-reference/description)

---

#### ✅ Qwen and DeepSeek Configuration

If following the source code, refer to the SiliconFlow platform's official documentation to configure:

- `QWEN_API_KEY`
- `QWEN_BASE_URL`
- `DEEPSEEK_API_KEY`
- `DEEPSEEK_API_URL`

📘 Documentation:  
[https://docs.siliconflow.cn/cn/userguide/introduction](https://docs.siliconflow.cn/cn/userguide/introduction)

---

#### ✅ Image Generation API Configuration (Tongyi Wanxiang)

Please refer to the image generation API usage guide to configure:

- `IMAGE_API_KEY`
- `IMAGE_MODEL` (Recommended value: `wanx2.1-t2i-turbo`)
- `DEFAULT_IMAGE_SIZE` (Recommended value: `1440*768`)

📘 Documentation:  
[https://help.aliyun.com/zh/model-studio/user-guide/text-to-image](https://help.aliyun.com/zh/model-studio/user-guide/text-to-image)

---

#### ✅ Application Configuration

Set the following variables according to your project requirements:

- `secret_key`: A unique identifier for OSS storage path (e.g., username)
- `speaker_identifier`: The identifier used to mark the protagonist's speech in dialogue text (e.g., `"Speaker 2"`)

---

### 🚀 Starting the Service

After configuration, use the following command to start the service:

```bash
python app.py \
  --game_path "<path_to_your_GameData_folder>" \
  --dialogue_path "<path_to_your_dialogue_text_file>" \
  --init_message_path "<path_to_your_init_message_file>"
```

#### Parameter Description:

- `--game_path`: Temporary `GameData` folder path (for storing Unity game data)
- `--dialogue_path`: Input dialogue text file path (e.g., `mygrand.txt`)
- `--init_message_path`: Character background initialization file path (e.g., `init_message.txt`)

##### 📄 Dialogue Text Format Example (dialogue_path)

The dialogue file must clearly label speakers, with each round of dialogue consisting of a speaker identifier and corresponding speech. Format as follows:

```
Speaker1
Speaker1's dialogue content

Speaker2
Speaker2's response

Speaker1
Speaker1's response
```

---

### 🔗 Reference Documentation Index

| Configuration Item | Documentation Link |
|--------|----------|
| Alibaba Cloud OSS | [https://help.aliyun.com/zh/oss/developer-reference/description](https://help.aliyun.com/zh/oss/developer-reference/description) |
| DeepSeek | [https://docs.siliconflow.cn/cn/userguide/introduction](https://docs.siliconflow.cn/cn/userguide/introduction) |
| Tongyi Wanxiang Image Generation | [https://help.aliyun.com/zh/model-studio/user-guide/text-to-image](https://help.aliyun.com/zh/model-studio/user-guide/text-to-image) |

## GenePlayBook_Client

### 🧩 Project Introduction

**GenePlayBook Client** is a cross-platform frontend client developed with Unity, responsible for user interaction and rendering images, audio, and storyline content generated by the backend. It supports multi-platform deployment (Windows/macOS/iOS/Android).

---

### 📦 Download Method

You can obtain the complete Unity project source code through the following link:

👉 [📁 Click to download client (Google Drive)](https://drive.google.com/drive/folders/186EsRTCjFjtLUHTylLJqFOf33CLES-Qk?usp=drive_link)

---

### ⚙️ Configuration Guide

Before launching the Unity project, please complete the following configuration steps.

#### ✅ Unity Plugin Dependencies

Please install and import the following plugins from the Unity Asset Store:

- 📖 **Book - Page Curl Pro**  
  Used to implement e-book page turning animation effects  
  ➡️ [Plugin Link](https://assetstore.unity.com/packages/tools/gui/book-page-curl-pro-77222)

---

#### ✅ Configure the `Config.cs` file

The `Config.cs` file in the project is used to configure external service API information needed by the frontend. Please fill in the missing fields according to the following technical documentation.

---

##### 🎙️ Text-to-Speech (TTS) Configuration

Used to convert text content to speech playback, based on SiliconFlow platform's speech synthesis service.

**Reference Documentation:**  
[https://docs.siliconflow.cn/cn/api-reference/audio/create-speech](https://docs.siliconflow.cn/cn/api-reference/audio/create-speech)

---

##### 🧱 Tripo3D Image Generation Configuration (3D Models)

Used to generate 3D scene images through text descriptions, based on the service provided by Tripo AI.

**Reference Documentation:**  
[https://platform.tripo3d.ai/docs/introduction](https://platform.tripo3d.ai/docs/introduction)

---

##### 🎮 Tencent GME Real-time Voice Service Configuration

Used for voice calls, speech recognition, or real-time interaction with voice messages, requiring configuration of Tencent Cloud's GME service.

**Reference Documentation:**  
[https://cloud.tencent.com/document/product/607/18248](https://cloud.tencent.com/document/product/607/18248)

---

### 🛠 Unity Environment Requirements

- Recommended Unity version: **2021.3 LTS or higher**
- Supported platforms: **Windows / macOS / iOS / Android**
