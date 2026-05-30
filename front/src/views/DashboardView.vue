<template>
  <section class="dashboard-hero-grid">
    <article class="hero-panel dashboard-hero">
      <div>
        <p class="section-kicker">今日翻阅 · WeReview</p>
        <h2>连接微信读书，让划线再次闪烁。</h2>
        <p class="hero-copy">
          基于 Skill 接口实时同步你的阅读轨迹。<br/>
          知识无需急于吞咽，每天只翻开一张卡片，让旧时光里的好句子，慢慢沉淀。
        </p>
      </div>
      <RouterLink to="/review" class="primary-action">抽一张卡片</RouterLink>
    </article>

    <article v-for="metric in metrics" :key="metric.label" :class="['metric-tile', 'compact', `metric-${metric.key}`]">
      <span>{{ metric.label }}</span>
      <strong>{{ metric.value }}</strong>
      <small>{{ metric.hint }}</small>
    </article>
  </section>

  <section class="analytics-grid">

    <article class="panel">
      <div class="panel-head">
        <div>
          <p class="section-kicker">笔记</p>
          <h3>留下了什么</h3>
        </div>
      </div>
      <div class="bar-list">
        <div v-for="item in dashboard?.note_composition ?? []" :key="item.label" class="bar-item">
          <div>
            <span>{{ item.label }}</span>
            <strong>{{ item.value }}</strong>
          </div>
          <div class="bar-track"><i :style="{ width: `${ratio(item.value, noteMax)}%` }" /></div>
        </div>
      </div>
    </article>

    <article class="panel">
      <div class="panel-head">
        <div>
          <p class="section-kicker">复习</p>
          <h3>等待重逢的句子</h3>
        </div>
      </div>
      <div class="bar-list">
        <div v-for="item in dashboard?.review_status ?? []" :key="item.label" class="bar-item">
          <div>
            <span>{{ item.label }}</span>
            <strong>{{ item.value }}</strong>
          </div>
          <div class="bar-track"><i :style="{ width: `${ratio(item.value, reviewMax)}%` }" /></div>
        </div>
      </div>
    </article>

    <article class="panel">
      <div class="panel-head">
        <div>
          <p class="section-kicker">分类</p>
          <h3>书架里的主题</h3>
        </div>
      </div>
      <div class="bar-list">
        <div v-for="item in dashboard?.category_distribution ?? []" :key="item.label" class="bar-item">
          <div>
            <span>{{ item.label }}</span>
            <strong>{{ item.value }}</strong>
          </div>
          <div class="bar-track"><i :style="{ width: `${ratio(item.value, categoryMax)}%` }" /></div>
        </div>
      </div>
    </article>
  </section>

  <section class="content-row dashboard-lower">
    <article class="panel wide">
      <div class="panel-head">
        <div>
          <p class="section-kicker">常回头看的书</p>
          <h3>划线最多的几本</h3>
        </div>
      </div>
      <div class="book-rank-list">
        <div v-for="(book, index) in dashboard?.top_highlight_books ?? []" :key="book.title" class="book-rank-row">
          <span class="rank-index">{{ index + 1 }}</span>
          <img v-if="book.cover" :src="book.cover" :alt="book.title" />
          <div v-else class="rank-cover-fallback">{{ book.title.slice(0, 1) }}</div>
          <div class="rank-main">
            <strong>{{ book.title }}</strong>
            <span>{{ book.author || '未知作者' }}</span>
            <small v-if="book.category" class="category-chip">{{ book.category }}</small>
          </div>
          <em>{{ book.highlight_count }} 条划线</em>
        </div>
      </div>
    </article>

    <article class="panel">
      <p class="section-kicker">书架同步</p>
      <h3>{{ dashboard?.latest_sync_at ?? '尚未同步' }}</h3>
      <p class="muted">把微信读书里的新划线带回来，安静地放进这里。</p>
      <RouterLink to="/sync" class="secondary-action">管理同步</RouterLink>
    </article>
  </section>

  <section class="panel review-preview-panel">
    <div class="panel-head">
      <div>
        <p class="section-kicker">待翻阅</p>
        <h3>可以从这些句子开始</h3>
      </div>
      <RouterLink to="/review" class="text-link">去抽卡</RouterLink>
    </div>
    <div class="quiet-list">
      <div v-for="card in reviewCards.slice(0, 5)" :key="card.id" class="quiet-row">
        <div>
          <strong>{{ card.book }}</strong>
          <span>{{ card.question }}</span>
        </div>
        <em>{{ card.due }}</em>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { RouterLink } from 'vue-router'
import { fetchDashboard, type DashboardStats } from '../api/dashboard'
import { fetchTodayReview, type ReviewCard } from '../api/review'

const dashboard = ref<DashboardStats | null>(null)
const reviewCards = ref<ReviewCard[]>([])

const metrics = computed(() => [
  { key: 'books', label: '书籍', value: dashboard.value?.book_count ?? 0, hint: '在你的书架里' },
  { key: 'highlights', label: '划线', value: dashboard.value?.highlight_count ?? 0, hint: '曾经停下的地方' },
  { key: 'thoughts', label: '想法', value: dashboard.value?.user_note_count ?? 0, hint: '写给自己的旁注' },
  { key: 'cards', label: '卡片', value: dashboard.value?.review_card_count ?? 0, hint: '等待再次遇见' }
])

const noteMax = computed(() => Math.max(...(dashboard.value?.note_composition ?? []).map((item) => item.value), 1))
const reviewMax = computed(() => Math.max(...(dashboard.value?.review_status ?? []).map((item) => item.value), 1))
const categoryMax = computed(() => Math.max(...(dashboard.value?.category_distribution ?? []).map((item) => item.value), 1))

function ratio(value: number, max: number) {
  if (!max) return 0
  return Math.max(4, Math.round((value / max) * 100))
}

onMounted(async () => {
  dashboard.value = await fetchDashboard()
  reviewCards.value = await fetchTodayReview()
})
</script>
