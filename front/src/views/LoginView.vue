<template>
  <main class="login-page">
    <div class="login-card stagger-item stagger-1">
      <section class="reading-cover">
        <div class="brand large stagger-item stagger-2">
          <img src="../images/logo.png" class="brand-logo large" alt="WeRead Review" />
          <div>
            <span>WeRead Review</span>
          </div>
        </div>

        <div class="cover-copy stagger-item stagger-3">
          <p class="section-kicker">微信读书·划线复习</p>
          <h1>让微信读书里的旧句子，重新亮一下。</h1>
          <p>
            借由官方 Skill 无感连接，拾取你曾划下的灵光。智能导入你的书架信息、划线卡片与想法笔记，
            依托高效的复习算法，重现文字闪光点，开启沉浸式的阅读温故之旅。
          </p>
        </div>

        <div class="reading-sample stagger-item stagger-4" aria-hidden="true">
          <div class="page page-main">
            <span>今日复习</span>
            <strong>18 条划线</strong>
            <p>先回忆，再展开原文。</p>
          </div>
          <div class="page page-note">
            <span>来自《置身事内》</span>
            <p>地方政府既是政策执行者，也是地方经济发展的组织者。</p>
          </div>
          <div class="book-spine spine-green" />
          <div class="book-spine spine-paper" />
        </div>
      </section>

      <section class="login-panel">
        <div class="login-heading stagger-item stagger-2">
          <p class="section-kicker">{{ mode === 'login' ? '登录' : '注册' }}</p>
          <h2>WeRead Review</h2>
          <span>{{ mode === 'login' ? '进入后即可同步自己的微信读书数据。' : '每个账号的数据相互独立，适合长期积累。' }}</span>
        </div>

        <div class="login-tabs stagger-item stagger-3">
          <button :class="{ active: mode === 'login' }" @click="mode = 'login'">登录</button>
          <button :class="{ active: mode === 'register' }" @click="mode = 'register'">注册</button>
        </div>

        <div class="stagger-item stagger-4">
          <label class="field-label">邮箱</label>
          <input v-model="email" class="login-input" placeholder="reader@example.com" />
        </div>

        <div v-if="mode === 'register'">
          <label class="field-label">昵称</label>
          <input v-model="nickname" class="login-input" placeholder="你的名字" />
        </div>

        <div class="stagger-item stagger-5">
          <label class="field-label">密码</label>
          <input v-model="password" class="login-input" type="password" placeholder="至少 6 位" />
        </div>

        <button class="primary-action full stagger-item stagger-6" :disabled="submitting" @click="submit">
          {{ submitting ? '处理中...' : mode === 'login' ? '登录' : '注册' }}
        </button>
        <p class="muted stagger-item stagger-7">{{ message }}</p>
      </section>
    </div>
  </main>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const auth = useAuthStore()
const mode = ref<'login' | 'register'>('login')
const email = ref('')
const nickname = ref('')
const password = ref('')
const submitting = ref(false)
const message = ref('系统账号仅用于数据隔离；您的书架与划线数据将通过微信读书 Skill 安全同步与复习。')

async function submit() {
  console.log('Login/Register Submit:', {
    mode: mode.value,
    email: email.value,
    password: password.value,
    nickname: nickname.value
  })
  submitting.value = true
  message.value = ''
  try {
    if (mode.value === 'login') {
      await auth.login(email.value, password.value)
    } else {
      await auth.register(email.value, password.value, nickname.value)
    }
    await router.push('/')
  } catch (err: any) {
    console.error('Submit error:', err)
    const validationDetails = err.response?.data?.detail
    if (validationDetails) {
      console.error('FastAPI Validation details:', validationDetails)
      if (Array.isArray(validationDetails)) {
        const errorText = '格式验证失败: ' + validationDetails.map((d: any) => {
          const field = d.loc[d.loc.length - 1]
          let msg = d.msg
          if (msg === 'value is not a valid email address') msg = '请输入有效的邮箱地址'
          if (msg === 'String should have at least 6 characters') msg = '至少需要 6 个字符'
          return `${field === 'email' ? '邮箱' : field === 'password' ? '密码' : field}: ${msg}`
        }).join('; ')
        ElMessage.error(errorText)
      } else {
        ElMessage.error('验证失败: ' + JSON.stringify(validationDetails))
      }
    } else {
      ElMessage.error(mode.value === 'login' ? '登录失败，请检查邮箱和密码。' : '注册失败，请检查邮箱是否已使用。')
    }
  } finally {
    submitting.value = false
  }
}
</script>
