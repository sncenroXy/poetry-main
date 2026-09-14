<template>
  <div class="min-h-screen bg-sys-bg flex flex-col items-center justify-center px-6">
    <!-- Logo -->
    <div class="text-center mb-12">
      <div class="w-20 h-20 rounded-apple-xl bg-gradient-to-br from-primary to-accent flex items-center justify-center text-white text-[32px] font-kai font-bold mx-auto mb-5 shadow-apple-lg">
        诗
      </div>
      <h1 class="text-[28px] font-semibold text-ink tracking-tight">诗词雅韵</h1>
      <p class="text-ink-light text-[15px] mt-2">学诗 · 练诗 · 创诗</p>
    </div>

    <!-- 登录表单 -->
    <div class="w-full max-w-sm">
      <div class="glass-card p-6">
        <div class="mb-3">
          <input
            v-model="username"
            class="w-full bg-sys-bg-secondary rounded-apple px-4 py-3 text-[15px] text-ink placeholder:text-text-tertiary border-none outline-none"
            placeholder="用户名"
          />
        </div>
        <div class="mb-5">
          <input
            v-model="password"
            type="password"
            class="w-full bg-sys-bg-secondary rounded-apple px-4 py-3 text-[15px] text-ink placeholder:text-text-tertiary border-none outline-none"
            placeholder="密码"
          />
        </div>
        <van-button
          block
          color="#c8851a"
          size="large"
          style="border-radius: 12px"
          :loading="loading"
          @click="handleLogin"
        >
          登录
        </van-button>
      </div>

      <div class="text-center mt-5">
        <button class="text-[14px] text-primary font-medium cursor-pointer" @click="skip">
          暂不登录，直接体验
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { showToast } from 'vant'

const router = useRouter()
const userStore = useUserStore()

const username = ref('')
const password = ref('')
const loading = ref(false)

async function handleLogin() {
  if (!username.value || !password.value) {
    showToast('请填写用户名和密码')
    return
  }
  loading.value = true
  try {
    showToast('功能开发中，请直接体验')
  } finally {
    loading.value = false
  }
}

function skip() {
  router.push('/')
}
</script>
