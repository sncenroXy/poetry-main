<template>
  <van-tabbar v-model="active" :safe-area-inset-bottom="true" active-color="#c8851a" inactive-color="#6b6882">
    <van-tabbar-item name="home" icon="home-o" @click="go('/')">
      <span class="font-kai text-xs">鉴赏</span>
    </van-tabbar-item>
    <van-tabbar-item name="challenge" icon="flag-o" @click="go('/challenge')">
      <span class="font-kai text-xs">挑战</span>
    </van-tabbar-item>
    <van-tabbar-item name="create" icon="edit" @click="go('/create')">
      <span class="font-kai text-xs">创作</span>
    </van-tabbar-item>
  </van-tabbar>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()

const active = computed(() => {
  if (route.path.startsWith('/challenge')) return 'challenge'
  if (route.path.startsWith('/create')) return 'create'
  return 'home'
})

function go(path) {
  router.push(path)
}
</script>
