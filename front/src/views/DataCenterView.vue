<template>
  <section class="analytics-shell">
    <el-card shadow="never" class="analytics-hero" v-loading="loading.summary">
      <div class="analytics-hero-copy">
        <p class="section-kicker">数据中心</p>
        <h2>看见阅读留下的结构。</h2>
        <p>从书架、划线到复习状态，把零散阅读变成一张有脉络的长期地图。</p>
      </div>
      <div class="analytics-metrics">
        <div v-for="metric in metrics" :key="metric.label" class="analytics-metric-tile">
          <span>{{ metric.label }}</span>
          <strong>{{ metric.value }}</strong>
          <small>{{ metric.hint }}</small>
        </div>
      </div>
    </el-card>

    <div class="analytics-panels">
      <el-card shadow="never" class="analytics-panel" v-loading="loading.distributions">
        <template #header>
          <div class="analytics-panel-head">
            <div>
              <p class="section-kicker">作者</p>
              <h3>常读作者</h3>
            </div>
          </div>
        </template>
        <VChart class="chart-surface tall" :option="authorOption" autoresize />
      </el-card>

      <el-card shadow="never" class="analytics-panel" v-loading="loading.distributions">
        <template #header>
          <div class="analytics-panel-head">
            <div>
              <p class="section-kicker">阅读</p>
              <h3>进度分布</h3>
            </div>
          </div>
        </template>
        <VChart class="chart-surface" :option="progressOption" autoresize />
      </el-card>

      <el-card shadow="never" class="analytics-panel" v-loading="loading.review">
        <template #header>
          <div class="analytics-panel-head">
            <div>
              <p class="section-kicker">流向</p>
              <h3>阅读与复习漏斗</h3>
            </div>
          </div>
        </template>
        <div class="funnel-steps">
          <div v-for="item in funnelRows" :key="item.label" class="funnel-step">
            <div class="funnel-step-main">
              <span>{{ item.label }}</span>
              <strong>{{ item.value }}{{ item.unit }}</strong>
            </div>
            <el-progress
              :percentage="item.percent"
              :show-text="false"
              :stroke-width="8"
              :color="item.color"
            />
            <small>{{ item.note }}</small>
          </div>
        </div>
      </el-card>

      <el-card shadow="never" class="analytics-panel" v-loading="loading.review">
        <template #header>
          <div class="analytics-panel-head">
            <div>
              <p class="section-kicker">分类</p>
              <h3>分类复习效果</h3>
            </div>
          </div>
        </template>
        <VChart class="chart-surface tall" :option="categoryEffectOption" autoresize />
      </el-card>

      <el-card shadow="never" class="analytics-panel wide" v-loading="loading.review">
        <template #header>
          <div class="analytics-panel-head">
            <div>
              <p class="section-kicker">趋势</p>
              <h3>近 14 天复习曲线</h3>
            </div>
          </div>
        </template>
        <VChart class="chart-surface wide-chart" :option="trendOption" autoresize />
      </el-card>
    </div>

    <el-card shadow="never" class="analytics-table-panel" v-loading="loading.books">
      <template #header>
        <div class="analytics-panel-head">
          <div>
            <p class="section-kicker">排行</p>
            <h3>划线最密集的书</h3>
          </div>
        </div>
      </template>
      <el-table :data="topHighlightBooks" stripe>
        <el-table-column label="#" width="60">
          <template #default="scope">
            {{ scope.$index + 1 }}
          </template>
        </el-table-column>
        <el-table-column label="书名" min-width="220">
          <template #default="scope">
            <div class="table-book-cell">
              <img v-if="scope.row.cover" :src="scope.row.cover" :alt="scope.row.title" />
              <div v-else class="table-cover-fallback">{{ scope.row.title.slice(0, 1) }}</div>
              <div>
                <strong>{{ scope.row.title }}</strong>
                <span>{{ scope.row.author || '未知作者' }}</span>
              </div>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="分类" width="160">
          <template #default="scope">
            <el-tag v-if="scope.row.category" effect="plain" type="success">{{ scope.row.category }}</el-tag>
            <span v-else class="muted">未分类</span>
          </template>
        </el-table-column>
        <el-table-column prop="highlight_count" label="划线数" width="120" />
      </el-table>
    </el-card>
  </section>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import VChart from 'vue-echarts'
import { use } from 'echarts/core'
import { BarChart, LineChart } from 'echarts/charts'
import {
  DatasetComponent,
  GridComponent,
  LegendComponent,
  TitleComponent,
  TooltipComponent
} from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'
import {
  fetchDataCenterBooks,
  fetchDataCenterDistributions,
  fetchDataCenterReview,
  fetchDataCenterSummary,
  type DataCenterBookStats,
  type DataCenterDistributions,
  type DataCenterReviewStats,
  type DataCenterStats,
  type DataCenterSummary
} from '../api/dataCenter'

use([BarChart, LineChart, DatasetComponent, GridComponent, LegendComponent, TitleComponent, TooltipComponent, CanvasRenderer])

const summary = ref<DataCenterSummary | null>(null)
const distributions = ref<DataCenterDistributions | null>(null)
const reviewStats = ref<DataCenterReviewStats | null>(null)
const bookStats = ref<DataCenterBookStats | null>(null)
const loading = ref({
  summary: true,
  distributions: true,
  review: true,
  books: true
})

const emptyStats: DataCenterStats = {
  summary: {
    book_count: 0,
    highlight_count: 0,
    reviewed_highlight_count: 0,
    avg_highlights_per_book: 0
  },
  review_funnel: [],
  category_distribution: [],
  category_review_effect: [],
  author_distribution: [],
  top_highlight_books: [],
  reading_progress: [],
  memory_distribution: [],
  review_trend: [],
  stale_highlights: []
}

const stats = computed<DataCenterStats>(() => ({
  ...emptyStats,
  summary: summary.value ?? emptyStats.summary,
  ...(distributions.value ?? {}),
  ...(reviewStats.value ?? {}),
  ...(bookStats.value ?? {})
}))

const topHighlightBooks = computed(() => stats.value.top_highlight_books)

const metrics = computed(() => [
  { label: '书籍', value: stats.value.summary.book_count, hint: '同步到书架' },
  { label: '划线', value: stats.value.summary.highlight_count, hint: '沉淀下来的句子' },
  { label: '已复习', value: stats.value.summary.reviewed_highlight_count, hint: '重新回看过' },
  { label: '书均划线', value: stats.value.summary.avg_highlights_per_book, hint: '每本书平均' }
])

function percentOf(value: number, total: number) {
  if (!total) {
    return '0%'
  }
  return `${Math.round((value / total) * 100)}%`
}

const funnelRows = computed(() => {
  const values = Object.fromEntries(stats.value.review_funnel.map((item) => [item.label, item.value]))
  const books = Number(values['书籍'] ?? 0)
  const highlights = Number(values['划线'] ?? 0)
  const reviewed = Number(values['已复习划线'] ?? 0)
  const familiar = Number(values['熟悉划线'] ?? 0)
  return [
    {
      label: '书架里的书',
      value: books,
      unit: ' 本',
      percent: books ? 100 : 0,
      note: '已经同步进来的书',
      color: '#7aa8ba'
    },
    {
      label: '留下的划线',
      value: highlights,
      unit: ' 条',
      percent: Math.min(100, Math.round((highlights / Math.max(highlights, reviewed, familiar, 1)) * 100)),
      note: `平均每本 ${stats.value.summary.avg_highlights_per_book} 条`,
      color: '#9f9bc8'
    },
    {
      label: '已经复习过',
      value: reviewed,
      unit: ' 条',
      percent: Number.parseInt(percentOf(reviewed, highlights), 10),
      note: `占全部划线 ${percentOf(reviewed, highlights)}`,
      color: '#c79e97'
    },
    {
      label: '比较熟悉',
      value: familiar,
      unit: ' 条',
      percent: Number.parseInt(percentOf(familiar, reviewed), 10),
      note: `占已复习 ${percentOf(familiar, reviewed)}`,
      color: '#89b2a6'
    }
  ]
})

const categoryEffectOption = computed(() => ({
  color: ['#7aa8ba', '#c79e97', '#9f9bc8'],
  tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
  legend: { bottom: 0 },
  grid: { left: 40, right: 20, top: 10, bottom: 40, containLabel: true },
  xAxis: { type: 'value' },
  yAxis: {
    type: 'category',
    data: stats.value.category_review_effect.map((item) => item.label)
  },
  series: [
    { name: '划线', type: 'bar', stack: 'total', data: stats.value.category_review_effect.map((item) => item.highlights) },
    { name: '已复习', type: 'bar', stack: 'review', data: stats.value.category_review_effect.map((item) => item.reviewed) },
    { name: '熟悉', type: 'bar', stack: 'review', data: stats.value.category_review_effect.map((item) => item.mastered) }
  ]
}))

const trendOption = computed(() => ({
  color: ['#7aa8ba'],
  tooltip: { trigger: 'axis' },
  grid: { left: 24, right: 16, top: 20, bottom: 28, containLabel: true },
  xAxis: { type: 'category', data: stats.value.review_trend.map((item) => item.label) },
  yAxis: { type: 'value' },
  series: [
    {
      type: 'line',
      smooth: true,
      areaStyle: { color: 'rgba(122, 168, 186, 0.16)' },
      lineStyle: { width: 3 },
      symbolSize: 7,
      data: stats.value.review_trend.map((item) => item.value)
    }
  ]
}))

const authorOption = computed(() => ({
  color: ['#7aa8ba'],
  tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
  grid: { left: 24, right: 16, top: 10, bottom: 20, containLabel: true },
  xAxis: { type: 'value' },
  yAxis: {
    type: 'category',
    inverse: true,
    data: stats.value.author_distribution.map((item) => item.label)
  },
  series: [
    {
      type: 'bar',
      barWidth: 14,
      data: stats.value.author_distribution.map((item) => item.value)
    }
  ]
}))

const progressOption = computed(() => ({
  color: ['#89b2a6'],
  tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
  grid: { left: 24, right: 16, top: 16, bottom: 26, containLabel: true },
  xAxis: {
    type: 'category',
    data: stats.value.reading_progress.map((item) => item.label)
  },
  yAxis: { type: 'value' },
  series: [
    {
      type: 'bar',
      barMaxWidth: 28,
      data: stats.value.reading_progress.map((item) => item.value)
    }
  ]
}))

async function loadDataCenter() {
  const tasks = [
    fetchDataCenterSummary()
      .then((data) => {
        summary.value = data
      })
      .catch((error) => {
        console.error('数据中心摘要加载失败', error)
      })
      .finally(() => {
        loading.value.summary = false
      }),
    fetchDataCenterDistributions()
      .then((data) => {
        distributions.value = data
      })
      .catch((error) => {
        console.error('数据中心分布加载失败', error)
      })
      .finally(() => {
        loading.value.distributions = false
      }),
    fetchDataCenterReview()
      .then((data) => {
        reviewStats.value = data
      })
      .catch((error) => {
        console.error('数据中心复习统计加载失败', error)
      })
      .finally(() => {
        loading.value.review = false
      }),
    fetchDataCenterBooks()
      .then((data) => {
        bookStats.value = data
      })
      .catch((error) => {
        console.error('数据中心书籍排行加载失败', error)
      })
      .finally(() => {
        loading.value.books = false
      })
  ]
  await Promise.allSettled(tasks)
}

onMounted(() => {
  void loadDataCenter()
})
</script>
