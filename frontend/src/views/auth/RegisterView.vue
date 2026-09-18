<template>
  <div class="min-h-screen bg-sys-bg flex flex-col items-center justify-center px-6">
    <!-- Logo -->
    <div class="text-center mb-12">
      <div class="w-20 h-20 rounded-apple-xl bg-gradient-to-br from-primary to-accent flex items-center justify-center text-white text-[32px] font-kai font-bold mx-auto mb-5 shadow-apple-lg">
        诗
      </div>
      <h1 class="text-[28px] font-semibold text-ink tracking-tight">创建账号</h1>
      <p class="text-ink-light text-[15px] mt-2">注册后即可体验 AI 写诗 · 配图 · 视频</p>
    </div>

    <!-- 注册表单 -->
    <div class="w-full max-w-sm">
      <div class="glass-card p-6">
        <div class="mb-3">
          <input
            v-model="username"
            class="w-full bg-sys-bg-secondary rounded-apple px-4 py-3 text-[15px] text-ink placeholder:text-text-tertiary border-none outline-none"
            placeholder="用户名（3-32 位）"
          />
        </div>
        <div class="mb-3">
          <input
            v-model="password"
            type="password"
            class="w-full bg-sys-bg-secondary rounded-apple px-4 py-3 text-[15px] text-ink placeholder:text-text-tertiary border-none outline-none"
            placeholder="密码（至少 6 位）"
          />
        </div>
        <div class="mb-5">
          <input
            v-model="confirm"
            type="password"
            class="w-full bg-sys-bg-secondary rounded-apple px-4 py-3 text-[15px] text-ink placeholder:text-text-tertiary border-none outline-none"
            placeholder="确认密码"
          />
        </div>
        <van-button
          block
          color="#c8851a"
          size="large"
          style="border-radius: 12px"
          :loading="loading"
          @click="handleRegister"
        >
          注册
        </van-button>
      </div>

      <div class="text-center mt-5">
        <button class="text-[14px] text-text-tertiary font-medium cursor-pointer" @click="goLogin">
          已有账号？去登录
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
import { register as registerApi } from '@/api/auth'

const router = useRouter()
const userStore = useUserStore()

const username = ref('')
const password = ref('')
const confirm = ref('')
const loading = ref(false)

async function handleRegister() {
  if (!username.value.trim() || !password.value) {
    showToast('请填写用户名和密码')
    return
  }
  if (password.value.length < 6) {
    showToast('密码至少 6 位')
    return
  }
  if (password.value !== confirm.value) {
    showToast('两次输入的密码不一致')
    return
  }
  loading.value = true
  try {
    const data = await registerApi({ username: username.value.trim(), password: password.value })
    userStore.login(data.token, data.user)
    showToast('注册成功')
    router.push('/')
  } catch (e) {
    showToast(e.message || '注册失败，请稍后再试')
  } finally {
    loading.value = false
  }
}

function goLogin() {
  router.push('/login')
}
</script>
