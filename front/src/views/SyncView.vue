<template>
  <section class="settings-grid">
    <article class="panel">
      <p class="section-kicker">微信读书</p>
      <h3>同步数据</h3>
      <p class="muted">快速同步只处理新增或变更的书；完整同步会重新扫描所有有笔记的书。</p>
      <div class="sync-actions">
        <button class="primary-action full" :disabled="syncing" @click="syncNow('quick')">
          {{ syncing ? '同步中...' : '快速同步' }}
        </button>
        <button class="secondary-action full" :disabled="syncing" @click="syncNow('full')">
          完整同步
        </button>
      </div>
      <p class="muted">{{ syncMessage }}</p>
      <div class="sync-progress">
        <div>
          <span>{{ activeJob ? `${activeJob.progress ?? 0}%` : '0%' }}</span>
          <em>{{ activeJob?.total_books ? `${activeJob.books_synced} / ${activeJob.total_books} 本` : '等待任务' }}</em>
        </div>
        <i :style="{ width: `${activeJob?.progress ?? 0}%` }" />
      </div>
      <button v-if="canCancel" class="danger-action full" @click="cancelActiveJob">
        中止同步
      </button>
      <div class="sync-log">
        <div v-for="(line, index) in activeLogs" :key="`${index}-${line}`">{{ line }}</div>
        <span v-if="!activeLogs.length">等待同步开始。</span>
      </div>
    </article>

    <article class="panel">
      <p class="section-kicker">最近记录</p>
      <div class="quiet-list">
        <div v-for="job in jobs" :key="job.id" class="quiet-row">
          <div>
            <strong>{{ job.status === 'success' ? '同步完成' : job.status === 'failed' ? '同步失败' : '同步中' }}</strong>
            <span>{{ job.books_synced }} 本书，{{ job.highlights_synced }} 条划线</span>
          </div>
          <em>{{ job.finished_at ?? job.started_at }}</em>
        </div>
      </div>
    </article>
  </section>
</template>

<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { cancelSyncJob, fetchSyncJob, fetchSyncJobs, runFullSync, runQuickSync, type SyncJob } from '../api/sync'

const syncing = ref(false)
const syncMessage = ref('')
const jobs = ref<SyncJob[]>([])
const activeJob = ref<SyncJob | null>(null)
const activeLogs = ref<string[]>([])
let pollTimer: number | undefined
const canCancel = computed(() => activeJob.value?.status === 'running')

async function loadJobs() {
  jobs.value = await fetchSyncJobs()
  const running = jobs.value.find((job) => job.status === 'running')
  if (running && pollTimer === undefined) {
    applyJob(running)
    startPolling(running.id)
  }
}

async function syncNow(mode: 'quick' | 'full') {
  syncing.value = true
  activeLogs.value = []
  syncMessage.value = mode === 'quick' ? '快速同步任务已提交。' : '完整同步任务已提交。'
  try {
    const result = mode === 'quick' ? await runQuickSync() : await runFullSync()
    if (result.job_id === null) {
      syncMessage.value = '同步任务创建失败。'
      syncing.value = false
      return
    }
    activeLogs.value = result.logs ?? result.message.split('\n').filter(Boolean)
    activeJob.value = {
      id: result.job_id,
      job_type: mode,
      status: result.status,
      books_synced: result.books_synced,
      highlights_synced: result.highlights_synced,
      total_books: null,
      progress: 0,
      message: result.message,
      logs: activeLogs.value,
      started_at: null,
      finished_at: null
    }
    startPolling(result.job_id)
  } catch (error: any) {
    await loadJobs().catch(() => undefined)
    if (error?.response?.data?.detail) {
      syncMessage.value = `同步请求失败：${error.response.data.detail}`
    } else {
      syncMessage.value = '同步任务没有正常创建，请检查登录状态、后端服务和网络。'
    }
    syncing.value = false
  }
}

function startPolling(jobId: number) {
  stopPolling()
  pollTimer = window.setInterval(async () => {
    const job = await fetchSyncJob(jobId)
    applyJob(job)
    if (!['running', 'cancel_requested'].includes(job.status)) {
      stopPolling()
      syncing.value = false
      await loadJobs()
    }
  }, 1000)
}

function applyJob(job: SyncJob) {
  activeJob.value = job
  activeLogs.value = job.logs ?? []
  syncing.value = ['running', 'cancel_requested'].includes(job.status)
  syncMessage.value =
    job.status === 'running'
      ? `正在同步：${job.books_synced}${job.total_books ? ` / ${job.total_books}` : ''} 本书，${job.highlights_synced} 条划线已入库。`
      : job.status === 'cancel_requested'
        ? '正在中止同步，当前网络请求返回后会停止。'
        : job.status === 'cancelled'
          ? `同步已中止：已处理 ${job.books_synced}${job.total_books ? ` / ${job.total_books}` : ''} 本书。`
          : job.status === 'success'
            ? `同步完成：${job.books_synced} 本书，${job.highlights_synced} 条划线。`
            : `同步失败：${job.message ?? '请查看日志。'}`
}

async function cancelActiveJob() {
  if (!activeJob.value) return
  const job = await cancelSyncJob(activeJob.value.id)
  applyJob(job)
}

function stopPolling() {
  if (pollTimer !== undefined) {
    window.clearInterval(pollTimer)
    pollTimer = undefined
  }
}

onMounted(async () => {
  await loadJobs()
})
onBeforeUnmount(stopPolling)
</script>
