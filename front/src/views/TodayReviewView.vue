<template>
  <section class="review-layout">
    <article class="review-card">
      <div class="review-scope-bar">
        <div>
          <p class="section-kicker">复习范围</p>
          <strong>{{ scopeLabel }}</strong>
        </div>
        <div class="review-filter-bar">
          <button
            v-for="item in modes"
            :key="item.value"
            class="review-mode-button"
            :class="{ active: mode === item.value }"
            @click="switchMode(item.value)"
          >
            {{ item.label }}
          </button>
        </div>
      </div>

      <div class="review-filter-row">
        <select v-if="mode === 'book'" v-model="selectedBookId" class="search-input" @change="drawCard()">
          <option value="">选择一本书</option>
          <option v-for="book in books" :key="book.id" :value="book.id">{{ book.title }}</option>
        </select>
        <select v-if="mode === 'category'" v-model="selectedCategory" class="search-input" @change="drawCard()">
          <option value="">选择一个分类</option>
          <option v-for="category in categories" :key="category" :value="category">{{ category }}</option>
        </select>
      </div>

      <div v-if="!current" class="empty-state">
        <p class="section-kicker">今日复习</p>
        <h2>{{ loading ? '正在抽取卡片...' : '暂时没有可复习卡片。' }}</h2>
        <span>{{ loading ? loadingCopy : '同步微信读书数据后，新的划线会进入复习队列。' }}</span>
      </div>
      <template v-else-if="!loading">
        <div :key="current.id" class="review-card-shell">
          <div class="card-stack" aria-hidden="true"></div>
          <div class="card-face">
            <div class="review-topline">
              <div class="review-meta">
                <span class="review-book">{{ current.book }}</span>
                <span class="review-chapter" v-if="current.chapter">{{ current.chapter }}</span>
              </div>
            </div>

            <div class="review-bookmark">Review Card</div>
            <h2>{{ current.question }}</h2>

            <button class="reveal-button" @click="revealed = !revealed">
              {{ revealed ? '收起原文' : '展开划线原文' }}
            </button>

            <div v-if="revealed" class="highlight-paper">
              <blockquote>{{ current.text }}</blockquote>
              <div class="tts-container">
                <button class="tts-button" :class="{ 'is-playing': isPlaying }" @click="playAudio(current.text)">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M11 5L6 9H2v6h4l5 4V5z"></path>
                    <path d="M15.54 8.46a5 5 0 0 1 0 7.07"></path>
                    <path d="M19.07 4.93a10 10 0 0 1 0 14.14"></path>
                  </svg>
                  <span>{{ isPlaying ? '停止朗读' : '朗读划线' }}</span>
                </button>
              </div>
              <p v-if="current.note" class="note-line">我的想法：{{ current.note }}</p>
            </div>
          </div>
        </div>

        <div class="feedback-panel">
          <span>这张卡片现在的熟悉程度</span>
          <div class="feedback-bar">
            <button class="rating-forgot" @click="answer('forgot')">
              <strong>忘了</strong>
              <span>重新排入近期</span>
            </button>
            <button class="rating-hard" @click="answer('hard')">
              <strong>模糊</strong>
              <span>需要再遇见</span>
            </button>
            <button class="rating-remembered" @click="answer('remembered')">
              <strong>记得</strong>
              <span>正常间隔</span>
            </button>
            <button class="rating-mastered" @click="answer('mastered')">
              <strong>很熟</strong>
              <span>延后复习</span>
            </button>
          </div>
        </div>
      </template>
      <div v-else class="review-loading-shell">
        <div class="review-loading-stack" aria-hidden="true">
          <i />
          <i />
          <i />
        </div>
        <div class="review-loading-card">
          <div class="review-loading-mark">
            <span />
            正在翻找
          </div>
          <h2>{{ loadingLines[loadingLineIndex] }}</h2>
          <p>{{ loadingCopy }}</p>
        </div>
      </div>
    </article>

    <aside class="review-side">
      <p class="section-kicker">进度</p>
      <strong>今日已复习 {{ stats.reviewed_count }} 个划线</strong>
      <div class="progress-track">
        <i :style="{ width: progressWidth }" />
      </div>
      <div class="today-reviewed-list">
        <div v-if="stats.reviewed_items.length" class="today-reviewed-head">
          <span>最近复习</span>
          <small>最近 5 条</small>
        </div>
        <span v-if="!stats.reviewed_items.length">完成第一张后，这里会留下今天复习过的划线。</span>
        <div v-for="item in stats.reviewed_items" :key="item.id" class="today-reviewed-item">
          <div>
            <strong>{{ item.book }}</strong>
            <em :class="`rating-pill rating-${item.rating}`">{{ ratingText(item.rating) }}</em>
          </div>
          <p>{{ item.text }}</p>
        </div>
      </div>
    </aside>
  </section>
</template>

<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import {
  answerReviewCard,
  fetchRandomReview,
  fetchTodayReviewStats,
  type ReviewCard,
  type ReviewDrawParams,
  type TodayReviewStats
} from '../api/review'
import { fetchBooks, type BookItem } from '../api/books'

const current = ref<ReviewCard | null>(null)
const revealed = ref(true)
const stats = ref<TodayReviewStats>({ reviewed_count: 0, reviewed_items: [] })
const loading = ref(false)
const books = ref<BookItem[]>([])
const mode = ref<'random' | 'book' | 'category'>('random')
const selectedBookId = ref('')
const selectedCategory = ref('')
const lastBookId = ref('')
const isPlaying = ref(false)
let currentAudio: HTMLAudioElement | null = null
const loadingLineIndex = ref(0)
let loadingTextTimer: number | undefined
const progressWidth = computed(() => `${Math.min(100, stats.value.reviewed_count * 12)}%`)
const scopeLabel = computed(() => {
  if (mode.value === 'book') {
    return books.value.find((book) => book.id === selectedBookId.value)?.title || '按书复习'
  }
  if (mode.value === 'category') {
    return selectedCategory.value || '按分类复习'
  }
  return '随机抽取'
})
const loadingCopy = computed(() => {
  if (mode.value === 'book') return '正在从这本书里翻出一句旧标记。'
  if (mode.value === 'category') return '正在从这个分类里挑出一句值得回看的话。'
  return '正在从你的划线里拣出一句该重逢的话。'
})
const loadingLines = [
  '翻开旧页，寻找刚好该重逢的那一句。',
  '让划线在纸堆里亮一下，再落回眼前。',
  '正在替你翻找，那句还值得再读一遍的话。'
]
const categories = computed(() =>
  Array.from(new Set(books.value.map((book) => book.category).filter((value): value is string => Boolean(value)))).sort()
)
const modes = [
  { value: 'random', label: '随机复习' },
  { value: 'book', label: '按书复习' },
  { value: 'category', label: '按分类复习' }
] as const

const ratingLabels: Record<string, string> = {
  forgot: '忘了',
  hard: '模糊',
  remembered: '记得',
  mastered: '很熟'
}

async function drawCard() {
  stopAudio()
  loading.value = true
  startLoadingAnimation()
  try {
    const params: ReviewDrawParams = { mode: mode.value, exclude_book_id: mode.value === 'random' ? lastBookId.value : undefined }
    if (mode.value === 'book' && selectedBookId.value) params.book_id = selectedBookId.value
    if (mode.value === 'category' && selectedCategory.value) params.category = selectedCategory.value
    current.value = await fetchRandomReview(params)
    revealed.value = true
  } finally {
    loading.value = false
    stopLoadingAnimation()
  }
}

async function loadStats() {
  stats.value = await fetchTodayReviewStats()
}

function ratingText(rating: string) {
  return ratingLabels[rating] ?? rating
}

async function answer(rating: string) {
  if (!current.value) return
  lastBookId.value = current.value.book_id
  await answerReviewCard(current.value.id, rating)
  await loadStats()
  revealed.value = true
  await drawCard()
}

async function switchMode(nextMode: 'random' | 'book' | 'category') {
  mode.value = nextMode
  await drawCard()
}

function startLoadingAnimation() {
  window.clearInterval(loadingTextTimer)
  loadingLineIndex.value = 0
  loadingTextTimer = window.setInterval(() => {
    loadingLineIndex.value = (loadingLineIndex.value + 1) % loadingLines.length
  }, 520)
}

function stopLoadingAnimation() {
  if (loadingTextTimer !== undefined) {
    window.clearInterval(loadingTextTimer)
    loadingTextTimer = undefined
  }
}

function playAudio(text: string) {
  if (isPlaying.value && currentAudio) {
    currentAudio.pause()
    isPlaying.value = false
    return
  }

  if (currentAudio) {
    currentAudio.pause()
  }

  const baseUrl = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000'
  const url = `${baseUrl}/api/tts/stream?text=${encodeURIComponent(text)}`
  currentAudio = new Audio(url)
  isPlaying.value = true

  currentAudio.onended = () => {
    isPlaying.value = false
  }
  currentAudio.onerror = () => {
    isPlaying.value = false
    console.error('Audio playback failed')
  }
  currentAudio.play().catch(e => {
    console.error('Playback error:', e)
    isPlaying.value = false
  })
}

function stopAudio() {
  if (currentAudio) {
    currentAudio.pause()
    currentAudio = null
    isPlaying.value = false
  }
}

onMounted(async () => {
  books.value = await fetchBooks()
  await Promise.all([drawCard(), loadStats()])
})

onBeforeUnmount(() => {
  stopLoadingAnimation()
  stopAudio()
})
</script>
