# WeRead Review (微信读书复习系统)

> 让微信读书里的旧句子，重新亮一下。

WeRead Review 是一个基于前后端分离架构开发的微信读书划线复习与数据管理工具。借由微信读书官方 Skill 无感连接，它可以智能同步你的书架信息、划线卡片与想法笔记。通过高效的复习算法和流式语音朗读 (TTS) 技术，重现文字闪光点，帮你将碎片的阅读痕迹转化为个人知识资产。

## ✨ 核心特性

- **📚 微信读书无缝同步**：通过绑定个人专属的微信读书 Skill API Key，安全且实时地拉取书架书籍和划线数据。
- **🧠 划线智能复习**：摒弃焦虑的堆砌，系统每天为你随机抽取数条高价值的划线卡片，进行沉浸式温故。
- **🎧 沉浸式流式朗读 (TTS)**：内置 Edge-TTS，提供毫秒级首字节响应的语音朗读功能，边听边看，释放双眼。
- **🎨 现代级美学设计**：前端采用 Vue3 + Element-Plus，配合高斯模糊玻璃拟物风格、动态微交互，带来极佳的视觉体验。
- **🔒 数据安全隔离**：用户账号隔离体系，配置的 API Key 存于独立存储中，保护你的隐私。

## 🛠️ 技术栈

- **前端 (Front-end)**：
  - 框架：Vue 3 (Composition API) + Vite
  - 路由与状态：Vue Router + Pinia
  - UI 库：Element-Plus
  - 核心逻辑：基于 `fetch` 封装的响应式数据流加载
- **后端 (Back-end)**：
  - 框架：FastAPI (Python)
  - 数据库：MySQL 8.0+ (基于 SQLAlchemy ORM)
  - 语音合成：`edge-tts` 提供流式音频 (StreamingResponse)
  - 用户认证：JWT (JSON Web Tokens)

---

## 🚀 本地部署运行指南

本项目分为前端 (`front`) 和后端 (`back`)，需要分别独立启动。

### 1. 启动后端 (FastAPI)

**环境要求**：Python 3.9+

```bash
# 1. 进入后端目录
cd back

# 2. 创建并激活虚拟环境（可选但强烈建议）
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

# 3. 安装依赖包
pip install -r requirements.txt

# 4. 初始化环境变量
# 将 .env.example 复制一份并重命名为 .env，你可以修改其中的 JWT 密钥等配置
copy .env.example .env  # Windows
# cp .env.example .env  # macOS/Linux

# 5. 启动后端服务 (运行在 http://127.0.0.1:8000)
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

> **注意：** 确保你在本地或服务器上已经启动了 MySQL，并创建了对应的数据库（如 `weread_review`），同时在 `.env` 中正确配置了 `DATABASE_URL`，系统会自动建表并启动服务。

### 2. 启动前端 (Vue3 + Vite)

**环境要求**：Node.js 18+

```bash
# 1. 进入前端目录 (新开一个终端窗口)
cd front

# 2. 安装 Node 依赖
npm install

# 3. 启动本地开发服务器
npm run dev
```

启动成功后，控制台会输出一个类似 `http://localhost:5173/` 的本地访问地址。用浏览器打开该地址即可访问系统界面。

---

## ⚙️ 配置微信读书 Skill (重要)

由于本项目依赖微信读书的数据同步，你需要配置你自己的 API Key 才能拉取数据：

1. 成功运行前后端并在浏览器打开项目后。
2. 注册并登录你的复习书房账号。
3. 登录后系统顶部会提示你 **"未检测到 WeRead API Key"**。
4. 点击提示横幅中的 **“去配置”**，或者点击侧边栏左下角的个人头像进入**个人中心**。
5. 在左侧的配置卡片中，填入你的 **微信读书 Skill API Key** 并保存。
6. 配置成功后，系统会自动开始拉取你的书架与划线数据，回到首页即可开启阅读复习之旅！

## 📄 开源协议

本项目基于 [MIT License](./LICENSE) 开源。允许任何个人或企业免费使用、修改和分发，但请保留原作者版权声明。
