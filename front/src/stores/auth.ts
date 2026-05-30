import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import { login as loginRequest, register as registerRequest, type AuthUser } from '../api/auth'

const TOKEN_KEY = 'weread_review_token'
const USER_KEY = 'weread_review_user'

export const useAuthStore = defineStore('auth', () => {
  const token = ref<string | null>(localStorage.getItem(TOKEN_KEY))
  const user = ref<AuthUser | null>(readStoredUser())
  const isAuthenticated = computed(() => Boolean(token.value))

  async function login(email: string, password: string) {
    const result = await loginRequest(email, password)
    setSession(result.access_token, result.user)
  }

  async function register(email: string, password: string, nickname: string) {
    const result = await registerRequest(email, password, nickname)
    setSession(result.access_token, result.user)
  }

  function setSession(nextToken: string, nextUser: AuthUser) {
    token.value = nextToken
    user.value = nextUser
    localStorage.setItem(TOKEN_KEY, nextToken)
    localStorage.setItem(USER_KEY, JSON.stringify(nextUser))
  }

  function logout() {
    token.value = null
    user.value = null
    localStorage.removeItem(TOKEN_KEY)
    localStorage.removeItem(USER_KEY)
  }

  return { token, user, isAuthenticated, login, register, logout }
})

function readStoredUser(): AuthUser | null {
  const raw = localStorage.getItem(USER_KEY)
  if (!raw) return null
  try {
    return JSON.parse(raw) as AuthUser
  } catch {
    return null
  }
}

