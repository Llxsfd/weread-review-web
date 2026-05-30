<template>
  <div class="app-shell">
    <aside class="sidebar">
      <div class="brand">
        <img src="../images/logo.png" class="brand-logo" alt="WeRead Review" />
        <div>
          <span>WeRead Review</span>
        </div>
      </div>

      <nav class="nav-list">
        <RouterLink v-for="item in navItems" :key="item.to" :to="item.to" class="nav-item">
          <component :is="item.icon" :size="18" />
          <span>{{ item.label }}</span>
        </RouterLink>
      </nav>

      <RouterLink to="/profile" class="profile-entry">
        <div class="profile-entry-avatar">{{ profileInitial }}</div>
        <div>
          <span>个人中心</span>
          <strong>{{ auth.user?.nickname || auth.user?.email || '读者' }}</strong>
        </div>
      </RouterLink>
    </aside>

    <main class="main-panel">
      <div v-if="settingsStore.initialized && !settingsStore.status?.weread_key_configured" class="global-alert-banner">
        <div>
          <strong>未配置微信读书 API Key</strong>
          <span>请前往个人中心完成配置，否则无法同步您的阅读数据。</span>
        </div>
        <RouterLink to="/profile" class="alert-action">去配置</RouterLink>
      </div>

      <header class="topbar">
        <div>
          <p class="eyebrow">个人阅读记忆系统</p>
          <h1>{{ currentTitle }}</h1>
        </div>
        <button class="sync-button" @click="logout">
          退出
        </button>
      </header>
      <RouterView />
    </main>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { RouterLink, RouterView, useRoute, useRouter } from 'vue-router'
import { BarChart3, BookOpen, CalendarCheck, Highlighter, Library, Waves } from 'lucide-vue-next'
import { useAuthStore } from '../stores/auth'
import { useSettingsStore } from '../stores/settings'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()
const settingsStore = useSettingsStore()
const navItems = [
  { to: '/', label: '总览', icon: Waves, title: '今天从哪条划线开始？' },
  { to: '/review', label: '今日复习', icon: CalendarCheck, title: '今日复习' },
  { to: '/data-center', label: '数据中心', icon: BarChart3, title: '数据中心' },
  { to: '/highlights', label: '划线库', icon: Highlighter, title: '划线卡片库' },
  { to: '/books', label: '书籍', icon: Library, title: '书籍知识页' },
  { to: '/sync', label: '同步', icon: BookOpen, title: '同步管理' }
]

const currentTitle = computed(() => {
  return navItems.find((item) => item.to === route.path)?.title ?? '今天从哪条划线开始？'
})
const profileInitial = computed(() => (auth.user?.nickname || auth.user?.email || '读').slice(0, 1))

function logout() {
  auth.logout()
  router.push('/login')
}

onMounted(() => {
  settingsStore.fetchStatus()
})
</script>
