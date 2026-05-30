<template>
  <section class="book-toolbar panel">
    <input v-model="keyword" class="search-input" placeholder="输入书名或作者" />
  </section>

  <el-drawer
    v-model="drawerVisible"
    size="50%"
    :with-header="false"
  >
    <div v-if="selectedBook" class="book-drawer-content">
      <div class="panel-head">
        <div>
          <p class="section-kicker">{{ selectedBook.author || '未知作者' }}</p>
          <h3>{{ selectedBook.title }}</h3>
          <span v-if="selectedBook.category" class="category-chip">{{ selectedBook.category }}</span>
        </div>
        <button class="secondary-action" @click="drawerVisible = false">关闭</button>
      </div>

      <div class="book-highlight-summary">
        <span>{{ selectedHighlights.length }} 条划线</span>
        <span>{{ selectedBook.progress }}% 已读</span>
        <span>{{ selectedBook.due }} 条待复习</span>
      </div>

      <div class="book-highlight-list">
        <article v-for="item in selectedHighlights" :key="item.id" class="book-highlight-row">
          <div>
            <span>{{ item.chapter || '未识别章节' }}</span>
            <em>{{ item.created_at || '未知时间' }}</em>
          </div>
          <p>{{ item.text }}</p>
        </article>
        <div v-if="detailLoading" class="empty-state">
          <p class="section-kicker">读取中</p>
          <h2>正在打开这本书的划线。</h2>
        </div>
        <div v-if="!selectedHighlights.length && !detailLoading" class="empty-state">
          <p class="section-kicker">暂无划线</p>
          <h2>这本书还没有同步到划线。</h2>
        </div>
      </div>
    </div>
  </el-drawer>

  <section class="book-grid">
    <article
      v-for="book in books"
      :key="book.id"
      class="book-card clickable"
      :class="{ selected: selectedBook?.id === book.id }"
      @click="selectBook(book)"
    >
      <div class="book-cover-wrap">
        <img v-if="book.cover" class="book-cover" :src="book.cover" :alt="book.title" loading="lazy" />
        <div v-else class="book-cover fallback-cover">
          <span>{{ book.title.slice(0, 2) }}</span>
        </div>
      </div>
      <div class="book-info">
        <p>{{ book.author || '未知作者' }}</p>
        <h3>{{ book.title }}</h3>
        <span v-if="book.category" class="category-chip">{{ book.category }}</span>
      </div>
      <div class="book-stats">
        <span>{{ book.progress }}% 已读</span>
        <span>{{ book.highlights }} 条划线</span>
        <span>{{ book.due }} 条待复习</span>
      </div>
      <button class="book-open-button" @click.stop="selectBook(book)">查看划线</button>
      <div class="book-progress"><i :style="{ width: `${book.progress}%` }" /></div>
    </article>
    <div v-if="!books.length && !loading" class="empty-state panel">
      <p class="section-kicker">没有找到</p>
      <h2>换个关键词试试。</h2>
      <span>可以输入书名的一部分，或者作者名字。</span>
    </div>
  </section>
</template>

<script setup lang="ts">
import { nextTick, onMounted, ref, watch } from 'vue'
import { fetchBookHighlights, fetchBooks, type BookHighlightItem, type BookItem } from '../api/books'

const books = ref<BookItem[]>([])
const selectedBook = ref<BookItem | null>(null)
const selectedHighlights = ref<BookHighlightItem[]>([])
const drawerVisible = ref(false)
const keyword = ref('')
const loading = ref(false)
const detailLoading = ref(false)
let timer: number | undefined

async function loadBooks() {
  loading.value = true
  try {
    books.value = await fetchBooks(keyword.value)
  } finally {
    loading.value = false
  }
}

async function selectBook(book: BookItem) {
  selectedBook.value = book
  detailLoading.value = true
  selectedHighlights.value = []
  drawerVisible.value = true
  try {
    selectedHighlights.value = await fetchBookHighlights(book.id)
  } finally {
    detailLoading.value = false
  }
}

onMounted(async () => {
  await loadBooks()
})

watch(keyword, () => {
  window.clearTimeout(timer)
  timer = window.setTimeout(loadBooks, 280)
})
</script>
