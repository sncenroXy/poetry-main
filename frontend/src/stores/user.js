import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { getToken, setToken, removeToken, getUser, setUser, clearAll } from '@/utils/storage'

export const useUserStore = defineStore('user', () => {
  const token = ref(getToken())
  const userInfo = ref(getUser())

  const isLoggedIn = computed(() => !!token.value)

  function login(tokenVal, user) {
    token.value = tokenVal
    userInfo.value = user
    setToken(tokenVal)
    setUser(user)
  }

  function logout() {
    token.value = null
    userInfo.value = null
    clearAll()
  }

  return {
    token,
    userInfo,
    isLoggedIn,
    login,
    logout
  }
})
