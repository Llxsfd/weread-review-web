<template>
  <section class="profile-hero">
    <div class="profile-avatar large">{{ displayName.slice(0, 1) }}</div>
    <div class="profile-hero-info">
      <h2>{{ displayName }}</h2>
      <span>{{ profile?.email }}</span>
    </div>
  </section>

  <section class="profile-main-grid">
    <article class="panel profile-panel primary-card">
      <div class="panel-head">
        <div>
          <p class="section-kicker">数据来源</p>
          <h3>微信读书 API Key</h3>
        </div>
      </div>
      <div class="key-setup-block">
        <p class="muted">
          绑定微信读书以同步您的阅读记录与划线笔记。请在
          <a class="text-link" href="https://weread.qq.com/r/weread-skills" target="_blank" rel="noreferrer">
            微信读书 Skill 配置页
          </a>
          获取 Key 并填入下方。
        </p>
        <label class="field-label">API Key</label>
        <div class="secret-field">
          <input
            v-model="wereadKey"
            class="search-input full"
            :type="showWeReadKey ? 'text' : 'password'"
            :placeholder="keyPlaceholder"
          />
          <button
            class="secret-toggle"
            :aria-label="showWeReadKey ? '隐藏 API Key' : '查看 API Key'"
            @click="toggleWeReadKey"
          >
            <EyeOff v-if="showWeReadKey" :size="18" />
            <Eye v-else :size="18" />
          </button>
        </div>
        <button class="primary-action full" :disabled="savingKey" @click="saveKey">
          {{ savingKey ? '保存中...' : '保存配置' }}
        </button>
        <p v-if="keyStatusText" class="status-msg" :class="{ success: settingsStore.status?.weread_key_configured }">
          {{ keyStatusText }}
        </p>
      </div>
    </article>

    <div class="profile-secondary-col">
      <article class="panel profile-panel">
        <p class="section-kicker">个人设置</p>
        <h3>基本信息</h3>
        <label class="field-label">昵称</label>
        <input v-model="nickname" class="search-input full" placeholder="你的昵称" />
        <button class="secondary-action full" :disabled="savingProfile" @click="saveProfile">
          {{ savingProfile ? '保存中...' : '保存' }}
        </button>
        <p class="muted">{{ profileMessage }}</p>
      </article>

      <article class="panel profile-panel">
        <p class="section-kicker">安全设置</p>
        <h3>修改密码</h3>
        <label class="field-label">当前密码</label>
        <input v-model="oldPassword" class="search-input full" type="password" placeholder="当前密码" />
        <label class="field-label">新密码</label>
        <input v-model="newPassword" class="search-input full" type="password" placeholder="至少 6 位" />
        <button class="secondary-action full" :disabled="savingPassword" @click="changePassword">
          {{ savingPassword ? '修改中...' : '修改' }}
        </button>
        <p class="muted">{{ passwordMessage }}</p>
      </article>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { Eye, EyeOff } from 'lucide-vue-next'
import { fetchProfile, updatePassword, updateProfile, type UserProfile } from '../api/profile'
import { fetchWeReadKey, saveWeReadKey } from '../api/settings'
import { useAuthStore } from '../stores/auth'
import { useSettingsStore } from '../stores/settings'

const router = useRouter()
const auth = useAuthStore()
const settingsStore = useSettingsStore()
const profile = ref<UserProfile | null>(null)
const nickname = ref('')
const oldPassword = ref('')
const newPassword = ref('')
const wereadKey = ref('')
const showWeReadKey = ref(false)
const savingProfile = ref(false)
const savingPassword = ref(false)
const savingKey = ref(false)
const profileMessage = ref('')
const passwordMessage = ref('修改密码后需要重新登录。')
const keyMessage = ref('')

const displayName = computed(() => profile.value?.nickname || profile.value?.email || '读者')
const keyPlaceholder = computed(() => {
  if (showWeReadKey.value) return 'wrk-xxxxxxxx'
  return settingsStore.status?.weread_key_configured ? '已保存，点击右侧图标查看' : 'wrk-xxxxxxxx'
})
const keyStatusText = computed(() => {
  if (keyMessage.value) return keyMessage.value
  return settingsStore.status?.weread_key_configured ? 'WeRead API Key 已配置。' : '尚未配置 WeRead API Key。'
})

async function loadProfile() {
  profile.value = await fetchProfile()
  nickname.value = profile.value.nickname ?? ''
}

async function saveProfile() {
  savingProfile.value = true
  try {
    profile.value = await updateProfile(nickname.value)
    profileMessage.value = '基本信息已保存。'
  } catch {
    profileMessage.value = '保存失败，请稍后重试。'
  } finally {
    savingProfile.value = false
  }
}

async function changePassword() {
  savingPassword.value = true
  try {
    await updatePassword(oldPassword.value, newPassword.value)
    auth.logout()
    await router.push('/login')
  } catch {
    passwordMessage.value = '修改失败，请检查当前密码和新密码长度。'
  } finally {
    savingPassword.value = false
  }
}

async function saveKey() {
  savingKey.value = true
  try {
    const result = await saveWeReadKey(wereadKey.value)
    settingsStore.updateStatus({
      ...(settingsStore.status ?? { ai_key_configured: false, weread_key_configured: false }),
      weread_key_configured: result.configured
    })
    wereadKey.value = ''
    showWeReadKey.value = false
    keyMessage.value = result.configured ? '保存成功，可以去同步页面拉取真实数据。' : 'API Key 为空，未完成配置。'
  } catch {
    keyMessage.value = '保存失败，请检查后端服务是否启动。'
  } finally {
    savingKey.value = false
  }
}

async function toggleWeReadKey() {
  if (showWeReadKey.value) {
    showWeReadKey.value = false
    wereadKey.value = ''
    return
  }
  const result = await fetchWeReadKey()
  wereadKey.value = result.api_key
  showWeReadKey.value = true
  settingsStore.updateStatus({
    ...(settingsStore.status ?? { ai_key_configured: false, weread_key_configured: false }),
    weread_key_configured: result.configured
  })
}

onMounted(async () => {
  await Promise.all([loadProfile(), settingsStore.fetchStatus()])
})
</script>
