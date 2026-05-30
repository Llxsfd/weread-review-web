<template>
  <section class="highlights-shell">
    <el-card shadow="never" class="highlights-card">
      <template #header>
        <div class="highlights-header">
          <div>
            <p class="section-kicker">划线库</p>
            <h3>搜索与整理</h3>
          </div>
          <div class="highlights-header-actions">
            <el-button type="primary" @click="openCreateModal">创建专题</el-button>
          </div>
        </div>
      </template>

      <el-form :inline="false" class="highlights-form">
        <div class="highlights-query-grid">
          <el-input v-model="filters.q" placeholder="搜索划线内容" clearable @keyup.enter="runSearch" />
          <el-input v-model="filters.book" placeholder="书名" clearable @keyup.enter="runSearch" />
          <el-input v-model="filters.author" placeholder="作者" clearable @keyup.enter="runSearch" />
          <el-input v-model="filters.category" placeholder="分类" clearable @keyup.enter="runSearch" />
          <el-input v-model="filters.chapter" placeholder="章节" clearable @keyup.enter="runSearch" />
          <div class="highlights-query-actions">
            <el-button type="primary" @click="runSearch">查询</el-button>
            <el-button @click="resetFilters">清空</el-button>
          </div>
        </div>
      </el-form>

      <div class="collection-strip" v-if="collections.length">
        <div class="collection-strip-head">
          <span>专题收藏夹</span>
        </div>
        <div class="collection-strip-list">
          <button
            v-for="collection in collections"
            :key="collection.id"
            class="collection-pill"
            :class="{ active: activeCollection?.id === collection.id }"
            @click="openCollection(collection.id)"
          >
            {{ collection.name }}
            <small>{{ collection.highlight_count }}</small>
          </button>
        </div>
      </div>

      <el-card v-if="activeCollection" shadow="never" class="collection-focus-card">
        <template #header>
          <div class="collection-focus-head">
            <div>
              <p class="section-kicker">当前专题</p>
              <h3>{{ activeCollection.name }}</h3>
            </div>
            <div class="collection-focus-actions">
              <el-button @click="openEditModal">编辑</el-button>
              <el-button type="danger" plain @click="removeActiveCollection">删除</el-button>
              <el-button @click="activeCollection = null">收起</el-button>
              <el-button type="primary" plain @click="downloadMarkdown">导出 Markdown</el-button>
            </div>
          </div>
        </template>
        <p class="muted">{{ activeCollection.description || '还没有写专题描述。' }}</p>
        <div class="collection-inline-list">
          <article
            v-for="item in activeCollection.highlights"
            :key="`${activeCollection.id}-${item.id}`"
            class="collection-inline-row"
          >
            <span>{{ item.book }} · {{ item.chapter || '未识别章节' }}</span>
            <p>{{ item.text }}</p>
          </article>
        </div>
      </el-card>

      <div class="highlights-results">
        <article v-for="item in highlights" :key="item.id" class="highlight-library-row">
          <div class="highlight-library-main">
            <div class="highlight-library-meta">
              <span>{{ item.book }}</span>
              <span>{{ item.author || '未知作者' }}</span>
              <span>{{ item.chapter || '未识别章节' }}</span>
              <el-tag v-if="item.category" size="small" effect="plain" type="success">{{ item.category }}</el-tag>
            </div>
            <p>{{ item.text }}</p>
            <div class="highlight-library-actions">
              <el-button link type="primary" @click="openCollectDialog(item.id)">加入专题</el-button>
            </div>
          </div>
          <el-tag size="small" effect="plain">{{ item.status }}</el-tag>
        </article>

        <el-empty v-if="!highlights.length" description="没有找到匹配的划线" />
      </div>

      <div class="highlights-pagination">
        <span>共 {{ total }} 条划线</span>
        <el-pagination
          v-model:current-page="page"
          :page-size="pageSize"
          background
          layout="total, prev, pager, next, jumper"
          :total="total"
          @current-change="loadHighlights"
        />
      </div>
    </el-card>

    <el-dialog v-model="showCreateModal" :title="editingCollectionId === null ? '创建专题' : '编辑专题'" width="520px">
      <div class="collection-dialog-body">
        <p class="collection-dialog-note">专题用于把不同书里的相关划线收在一起，方便跨书整理、复习和导出。</p>
        <el-input v-model="collectionName" placeholder="专题名称" />
        <el-input
          v-model="collectionDescription"
          type="textarea"
          :rows="3"
          placeholder="一句描述，可选"
        />
      </div>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="showCreateModal = false">取消</el-button>
          <el-button type="primary" @click="saveCollection">
            {{ editingCollectionId === null ? '创建专题' : '保存修改' }}
          </el-button>
        </div>
      </template>
    </el-dialog>

    <el-dialog v-model="showCollectModal" title="加入专题" width="460px">
      <div class="collection-dialog-body">
        <el-select v-model="selectedCollectionId" placeholder="选择一个专题" style="width: 100%">
          <el-option
            v-for="collection in collections"
            :key="collection.id"
            :label="`${collection.name} · ${collection.highlight_count} 条`"
            :value="collection.id"
          />
        </el-select>
      </div>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="showCollectModal = false">取消</el-button>
          <el-button type="primary" @click="confirmCollect">加入</el-button>
        </div>
      </template>
    </el-dialog>
  </section>
</template>

<script setup lang="ts">
import { ElMessage } from 'element-plus'
import { computed, onMounted, reactive, ref } from 'vue'
import {
  addHighlightToCollection,
  createCollection,
  deleteCollection,
  exportCollectionMarkdown,
  fetchCollectionDetail,
  fetchCollections,
  updateCollection,
  type CollectionDetail,
  type CollectionItem
} from '../api/collections'
import { fetchHighlights, type HighlightItem } from '../api/highlights'

const filters = reactive({
  q: '',
  book: '',
  author: '',
  category: '',
  chapter: ''
})
const highlights = ref<HighlightItem[]>([])
const total = ref(0)
const page = ref(1)
const pageSize = 20
const collections = ref<CollectionItem[]>([])
const activeCollection = ref<CollectionDetail | null>(null)
const collectionName = ref('')
const collectionDescription = ref('')
const showCreateModal = ref(false)
const editingCollectionId = ref<number | null>(null)
const showCollectModal = ref(false)
const pendingHighlightId = ref<number | null>(null)
const selectedCollectionId = ref<number | null>(null)

const totalPages = computed(() => Math.max(1, Math.ceil(total.value / pageSize)))

async function loadHighlights() {
  const result = await fetchHighlights({
    ...filters,
    page: page.value,
    page_size: pageSize
  })
  highlights.value = result.items
  total.value = result.total
  if (page.value > totalPages.value) {
    page.value = totalPages.value
  }
}

async function loadCollections() {
  collections.value = await fetchCollections()
}

async function openCollection(id: number) {
  activeCollection.value = await fetchCollectionDetail(id)
}

async function saveCollection() {
  if (!collectionName.value.trim()) {
    ElMessage.warning('请输入专题名称')
    return
  }
  const isEditing = editingCollectionId.value !== null
  let collection
  if (!isEditing) {
    collection = await createCollection(collectionName.value, collectionDescription.value)
  } else {
    collection = await updateCollection(editingCollectionId.value as number, collectionName.value, collectionDescription.value)
  }
  collectionName.value = ''
  collectionDescription.value = ''
  editingCollectionId.value = null
  showCreateModal.value = false
  await loadCollections()
  await openCollection(collection.id)
  ElMessage.success(isEditing ? '专题已更新' : '专题已创建')
}

async function addToActiveCollection(highlightId: number) {
  if (selectedCollectionId.value === null) {
    ElMessage.info('请先选择一个专题')
    return
  }
  await addHighlightToCollection(selectedCollectionId.value, highlightId)
  await loadCollections()
  await openCollection(selectedCollectionId.value)
  ElMessage.success('已收藏到专题')
}

async function downloadMarkdown() {
  if (!activeCollection.value) return
  const markdown = await exportCollectionMarkdown(activeCollection.value.id)
  const blob = new Blob([markdown], { type: 'text/markdown;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = `${activeCollection.value.name}.md`
  link.click()
  URL.revokeObjectURL(url)
}

function openEditModal() {
  if (!activeCollection.value) return
  editingCollectionId.value = activeCollection.value.id
  collectionName.value = activeCollection.value.name
  collectionDescription.value = activeCollection.value.description || ''
  showCreateModal.value = true
}

function openCreateModal() {
  editingCollectionId.value = null
  collectionName.value = ''
  collectionDescription.value = ''
  showCreateModal.value = true
}

async function removeActiveCollection() {
  if (!activeCollection.value) return
  await deleteCollection(activeCollection.value.id)
  activeCollection.value = null
  await loadCollections()
  ElMessage.success('专题已删除')
}

function resetFilters() {
  filters.q = ''
  filters.book = ''
  filters.author = ''
  filters.category = ''
  filters.chapter = ''
  page.value = 1
  void loadHighlights()
}

function runSearch() {
  page.value = 1
  void loadHighlights()
}

function openCollectDialog(highlightId: number) {
  pendingHighlightId.value = highlightId
  selectedCollectionId.value = activeCollection.value?.id ?? collections.value[0]?.id ?? null
  showCollectModal.value = true
}

async function confirmCollect() {
  if (pendingHighlightId.value === null) return
  await addToActiveCollection(pendingHighlightId.value)
  showCollectModal.value = false
  pendingHighlightId.value = null
}

onMounted(async () => {
  await Promise.all([loadHighlights(), loadCollections()])
})
</script>
