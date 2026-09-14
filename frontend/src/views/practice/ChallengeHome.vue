<template>
  <div class="min-h-screen bg-sys-bg">
    <!-- 标题 -->
    <div class="content-container pt-6 pb-4">
      <h1 class="text-[28px] lg:text-[36px] font-semibold text-ink tracking-tight">诗词挑战</h1>
      <p class="text-ink-light text-[15px] mt-1">测试你的诗词储备</p>
    </div>

    <!-- 挑战入口 -->
    <div class="content-container">
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <!-- 飞花令 -->
        <div
          class="glass-card-accent glass-card-hover p-5 cursor-pointer active:scale-[0.98] transition-all"
          @click="router.push('/challenge/chain')"
        >
          <div class="flex items-start gap-4">
            <div class="w-12 h-12 rounded-apple-lg bg-accent/8 flex items-center justify-center flex-shrink-0">
              <svg class="w-6 h-6 text-accent" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
                <circle cx="12" cy="12" r="3" />
                <path d="M12 7.5a4.5 4.5 0 1 1 4.5 4.5M12 7.5A4.5 4.5 0 1 0 7.5 12M12 7.5V9m-4.5 3a4.5 4.5 0 1 0 4.5 4.5M7.5 12H9m3 4.5a4.5 4.5 0 1 0 4.5-4.5M12 16.5V15m4.5-3a4.5 4.5 0 1 1-4.5-4.5M16.5 12H15" />
              </svg>
            </div>
            <div class="flex-1">
              <h3 class="text-[18px] font-semibold text-ink mb-1">飞花令</h3>
              <p class="text-ink-light text-[14px] leading-relaxed">
                经典诗词接龙游戏。给出上句，接出下句，考验你的诗词积累！
              </p>
            </div>
          </div>
          <div class="flex justify-between items-center mt-4 pt-3 border-t border-sys-divider">
            <span class="text-[13px] text-ink-light">当前连胜：{{ challengeStore.chainStreak }}</span>
            <span class="text-[13px] text-primary font-medium">开始挑战</span>
          </div>
        </div>

        <!-- 答题闯关 -->
        <div
          class="glass-card-accent glass-card-hover p-5 cursor-pointer active:scale-[0.98] transition-all"
          @click="router.push('/challenge/quiz')"
        >
          <div class="flex items-start gap-4">
            <div class="w-12 h-12 rounded-apple-lg bg-success/8 flex items-center justify-center flex-shrink-0">
              <svg class="w-6 h-6 text-success" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
                <path d="M9 11l3 3L22 4" />
                <path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11" />
              </svg>
            </div>
            <div class="flex-1">
              <h3 class="text-[18px] font-semibold text-ink mb-1">答题闯关</h3>
              <p class="text-ink-light text-[14px] leading-relaxed">
                诗句填空、上下句配对、意境判断…全面考验你的诗词理解力！
              </p>
            </div>
          </div>
          <div class="flex justify-between items-center mt-4 pt-3 border-t border-sys-divider">
            <span class="text-[13px] text-ink-light">答对：{{ challengeStore.quizCorrect }}/{{ challengeStore.quizTotal }}</span>
            <span class="text-[13px] text-primary font-medium">进入答题</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 挑战统计 -->
    <div class="content-container py-5">
      <div class="glass-card p-5 max-w-lg">
        <h4 class="text-[15px] font-semibold text-ink mb-4">挑战统计</h4>
        <div class="grid grid-cols-3 gap-4 text-center">
          <div>
            <p class="text-[24px] font-bold text-primary">{{ challengeStore.chainScore }}</p>
            <p class="text-[12px] text-ink-light mt-1">接龙得分</p>
          </div>
          <div>
            <p class="text-[24px] font-bold text-success">{{ challengeStore.quizScore }}</p>
            <p class="text-[12px] text-ink-light mt-1">答题得分</p>
          </div>
          <div>
            <p class="text-[24px] font-bold text-accent">{{ challengeStore.totalChallenges }}</p>
            <p class="text-[12px] text-ink-light mt-1">总分</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { useChallengeStore } from '@/stores/challenge'

const router = useRouter()
const challengeStore = useChallengeStore()
</script>
