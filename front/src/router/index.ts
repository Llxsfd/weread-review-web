import { createRouter, createWebHistory } from 'vue-router'
import AppLayout from '../layouts/AppLayout.vue'
import DashboardView from '../views/DashboardView.vue'
import TodayReviewView from '../views/TodayReviewView.vue'
import HighlightsView from '../views/HighlightsView.vue'
import BooksView from '../views/BooksView.vue'
import SyncView from '../views/SyncView.vue'
import LoginView from '../views/LoginView.vue'
import ProfileView from '../views/ProfileView.vue'
import DataCenterView from '../views/DataCenterView.vue'
import { useAuthStore } from '../stores/auth'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/login', name: 'login', component: LoginView },
    {
      path: '/',
      component: AppLayout,
      children: [
        { path: '', name: 'dashboard', component: DashboardView },
        { path: 'review', name: 'review', component: TodayReviewView },
        { path: 'data-center', name: 'data-center', component: DataCenterView },
        { path: 'highlights', name: 'highlights', component: HighlightsView },
        { path: 'books', name: 'books', component: BooksView },
        { path: 'sync', name: 'sync', component: SyncView },
        { path: 'settings', redirect: '/profile' },
        { path: 'profile', name: 'profile', component: ProfileView }
      ]
    }
  ]
})

router.beforeEach((to) => {
  const auth = useAuthStore()
  if (to.name !== 'login' && !auth.isAuthenticated) {
    return { name: 'login' }
  }
  if (to.name === 'login' && auth.isAuthenticated) {
    return { name: 'dashboard' }
  }
  return true
})

export default router
