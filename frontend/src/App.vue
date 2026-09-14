<template>
  <div class="app-shell">
    <!-- Desktop Sidebar (lg+) -->
    <SideNav v-if="showNav" class="hidden lg:flex" />

    <!-- Mobile Top Nav (<lg) -->
    <TopNav v-if="showNav" />

    <!-- Main Content Area -->
    <main class="app-main" :class="{ 'has-nav': showNav }">
      <router-view v-slot="{ Component }">
        <transition name="page" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </main>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import TopNav from '@/components/common/TopNav.vue'
import SideNav from '@/components/common/SideNav.vue'

const route = useRoute()

const showNav = computed(() => {
  return !route.path.startsWith('/login')
})
</script>

<style scoped>
.app-shell {
  min-height: 100vh;
}

/* Mobile: top nav padding */
.app-main.has-nav {
  padding-top: 52px;
}

/* Desktop: sidebar offset */
@media (min-width: 1024px) {
  .app-main.has-nav {
    padding-top: 0;
    margin-left: 240px;
  }
}
</style>
