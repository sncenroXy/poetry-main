<template>
  <div class="min-h-screen bg-sys-bg">
    <div class="content-container pt-6 pb-20">
      <div class="flex items-start justify-between gap-4 mb-6">
        <div>
          <h1 class="text-[28px] lg:text-[36px] font-semibold text-ink tracking-tight">我的学习</h1>
          <p class="text-ink-light text-[14px] mt-1">学习记录、收藏与个性化推荐</p>
        </div>
        <van-button plain size="small" style="border-radius: 10px" @click="logout">退出登录</van-button>
      </div>

      <Loading v-if="loading" text="正在整理学习记录…" />

      <template v-else>
        <div class="grid grid-cols-2 lg:grid-cols-4 gap-3 mb-6">
          <div v-for="item in statCards" :key="item.label" class="glass-card p-4">
            <p class="text-[12px] text-ink-light">{{ item.label }}</p>
            <p class="text-[24px] font-semibold text-primary mt-1">{{ item.value }}</p>
          </div>
        </div>

        <div class="grid grid-cols-1 lg:grid-cols-[340px_1fr] gap-5">
          <section class="glass-card p-5 h-fit">
            <h2 class="text-[18px] font-semibold text-ink mb-4">个人资料</h2>
            <label class="form-label">显示名称</label>
            <input v-model="profile.display_name" class="profile-input" maxlength="32" />
            <label class="form-label mt-4">个人简介</label>
            <textarea v-model="profile.bio" class="profile-input resize-none" rows="3" maxlength="200" />
            <label class="form-label mt-4">偏好朝代</label>
            <input v-model="preferenceText.dynasties" class="profile-input" placeholder="例如：唐、宋" />
            <label class="form-label mt-4">偏好体裁</label>
            <input v-model="preferenceText.genres" class="profile-input" placeholder="例如：七言绝句、宋词" />
            <label class="form-label mt-4">偏好意象</label>
            <input v-model="preferenceText.tags" class="profile-input" placeholder="例如：明月、山水、思乡" />
            <van-button block color="#c8851a" class="mt-5" style="border-radius: 10px" :loading="saving" @click="saveProfile">
              保存资料
            </van-button>

            <div class="divider-brush my-6" />
            <h2 class="text-[18px] font-semibold text-ink mb-4">账号安全</h2>
            <label class="form-label">当前密码</label>
            <input v-model="passwordForm.current" class="profile-input" type="password" autocomplete="current-password" />
            <label class="form-label mt-4">新密码</label>
            <input v-model="passwordForm.next" class="profile-input" type="password" autocomplete="new-password" placeholder="至少 8 位" />
            <label class="form-label mt-4">确认新密码</label>
            <input v-model="passwordForm.confirm" class="profile-input" type="password" autocomplete="new-password" />
            <van-button block plain color="#c8851a" class="mt-5" style="border-radius: 10px" :loading="passwordSaving" @click="savePassword">
              修改密码
            </van-button>
          </section>

          <div class="space-y-6 min-w-0">
            <section>
              <div class="flex items-center justify-between mb-3">
                <h2 class="text-[19px] font-semibold text-ink">学习画像</h2>
                <button class="text-[12px] text-primary" @click="router.push('/profile/wrong-answers')">
                  错题本{{ wrongCount ? ` (${wrongCount})` : '' }} →
                </button>
              </div>
              <div v-if="hasPortraitData" class="glass-card p-4 space-y-3">
                <div v-if="portrait.interests?.authors?.length">
                  <p class="text-[12px] text-ink-light mb-1.5">偏爱诗人</p>
                  <div class="flex flex-wrap gap-2">
                    <span v-for="[name] in portrait.interests.authors" :key="name" class="portrait-chip">{{ name }}</span>
                  </div>
                </div>
                <div v-if="portrait.interests?.tags?.length">
                  <p class="text-[12px] text-ink-light mb-1.5">偏爱意象</p>
                  <div class="flex flex-wrap gap-2">
                    <span v-for="[tag] in portrait.interests.tags.slice(0, 8)" :key="tag" class="portrait-chip portrait-chip-tag">{{ tag }}</span>
                  </div>
                </div>
                <div v-if="portrait.weak_points?.length">
                  <p class="text-[12px] text-ink-light mb-1.5">薄弱题型</p>
                  <div class="flex flex-wrap gap-2">
                    <span v-for="wp in portrait.weak_points" :key="wp.type" class="portrait-chip portrait-chip-weak">{{ typeLabels[wp.type] || wp.type }} ×{{ wp.count }}</span>
                  </div>
                </div>
                <p v-if="recentTotal" class="text-[12px] text-ink-light">近 7 日练习 {{ recentTotal }} 次</p>
              </div>
              <div v-else class="glass-card p-5 text-center">
                <p class="text-[13px] text-ink-light">收藏、答题后，这里会生成你的学习画像</p>
              </div>
            </section>

            <section>
              <div class="flex items-center justify-between mb-3">
                <h2 class="text-[19px] font-semibold text-ink">为你推荐</h2>
                <span v-if="recommendations.basis?.tags?.length" class="text-[12px] text-ink-light">
                  根据 {{ recommendations.basis.tags.slice(0, 3).join('、') }}
                </span>
              </div>
              <div v-if="recommendations.items?.length" class="grid grid-cols-1 md:grid-cols-2 gap-3">
                <PoemCard v-for="poem in recommendations.items" :key="poem.id" :poem="poem" @click="openPoem" />
              </div>
              <EmptyState v-else message="多读几首诗，推荐会更懂你" />
            </section>

            <section>
              <h2 class="text-[19px] font-semibold text-ink mb-3">我的收藏</h2>
              <div v-if="favorites.length" class="grid grid-cols-1 md:grid-cols-2 gap-3">
                <PoemCard v-for="poem in favorites" :key="poem.id" :poem="poem" @click="openPoem" />
              </div>
              <EmptyState v-else message="还没有收藏诗词" />
            </section>

            <section>
              <h2 class="text-[19px] font-semibold text-ink mb-3">最近阅读</h2>
              <div v-if="history.length" class="grid grid-cols-1 md:grid-cols-2 gap-3">
                <PoemCard v-for="poem in history" :key="poem.id" :poem="poem" @click="openPoem" />
              </div>
              <EmptyState v-else message="暂无阅读记录" />
            </section>

            <section>
              <h2 class="text-[19px] font-semibold text-ink mb-3">创作记录</h2>
              <div v-if="creations.length" class="space-y-2">
                <div v-for="item in creations" :key="item.id" class="glass-card p-4">
                  <div class="flex items-center justify-between gap-3">
                    <h3 class="font-medium text-ink">{{ item.title || '无题' }}</h3>
                    <span class="text-[11px] text-primary">{{ creationLabels[item.creation_type] || item.creation_type }}</span>
                  </div>
                  <p v-if="item.content?.length" class="text-[13px] text-ink-light mt-2 line-clamp-2">{{ item.content.join('，') }}</p>
                </div>
              </div>
              <EmptyState v-else message="暂无创作记录" />
            </section>
          </div>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { showToast } from 'vant'
import { useUserStore } from '@/stores/user'
import {
  changePassword,
  getCreations,
  getFavorites,
  getHistory,
  getLearningSummary,
  getPortrait,
  getProfile,
  getRecommendations,
  getWrongAnswers,
  updateProfile,
} from '@/api/user'
import PoemCard from '@/components/poetry/PoemCard.vue'
import Loading from '@/components/common/Loading.vue'
import EmptyState from '@/components/common/EmptyState.vue'

const router = useRouter()
const userStore = useUserStore()
const loading = ref(true)
const saving = ref(false)
const passwordSaving = ref(false)
const favorites = ref([])
const history = ref([])
const creations = ref([])
const summary = ref({})
const recommendations = ref({ items: [], basis: {} })
const portrait = ref({ interests: {}, weak_points: [], recent_activity: [] })
const wrongCount = ref(0)
const profile = reactive({ display_name: '', bio: '' })
const passwordForm = reactive({ current: '', next: '', confirm: '' })
const preferenceText = reactive({ dynasties: '', genres: '', tags: '' })
const creationLabels = { poem: '诗词创作', mimic: '仿写', image: '诗画', video: '动画' }
const typeLabels = { fill_blank: '填空', next_line: '上下句', author: '作者识别', sentiment: '意境判断', classic_chain: '经典接龙', ai_chain: 'AI 对战' }

const statCards = computed(() => [
  { label: '学习等级', value: summary.value.level || '初识诗意' },
  { label: '练习次数', value: summary.value.total || 0 },
  { label: '正确率', value: `${summary.value.accuracy || 0}%` },
  { label: '累计积分', value: summary.value.score || 0 },
])

const hasPortraitData = computed(() => {
  const i = portrait.value.interests || {}
  return Boolean(i.authors?.length || i.tags?.length || portrait.value.weak_points?.length)
})

const recentTotal = computed(() => (portrait.value.recent_activity || []).reduce((s, d) => s + d.count, 0))

function splitValues(value) {
  return value.split(/[，,、\s]+/).map(item => item.trim()).filter(Boolean)
}

function openPoem(poem) {
  router.push(`/poem/${poem.id}`)
}

async function loadData() {
  loading.value = true
  try {
    const [profileData, summaryData, favoriteData, historyData, creationData, recommendationData, portraitData, wrongData] = await Promise.all([
      getProfile(), getLearningSummary(), getFavorites(), getHistory(), getCreations(), getRecommendations(), getPortrait(), getWrongAnswers(),
    ])
    Object.assign(profile, profileData)
    preferenceText.dynasties = (profileData.preferred_dynasties || []).join('、')
    preferenceText.genres = (profileData.preferred_genres || []).join('、')
    preferenceText.tags = (profileData.preferred_tags || []).join('、')
    summary.value = summaryData
    favorites.value = favoriteData
    history.value = historyData
    creations.value = creationData
    recommendations.value = recommendationData
    portrait.value = portraitData
    wrongCount.value = wrongData.length
  } catch {
    showToast('学习数据加载失败')
  } finally {
    loading.value = false
  }
}

async function saveProfile() {
  saving.value = true
  try {
    await updateProfile({
      display_name: profile.display_name,
      bio: profile.bio,
      preferred_dynasties: splitValues(preferenceText.dynasties),
      preferred_genres: splitValues(preferenceText.genres),
      preferred_tags: splitValues(preferenceText.tags),
    })
    recommendations.value = await getRecommendations()
    showToast('资料已保存')
  } catch {
    showToast('保存失败')
  } finally {
    saving.value = false
  }
}

async function savePassword() {
  if (!passwordForm.current || !passwordForm.next) {
    showToast('请填写当前密码和新密码')
    return
  }
  if (passwordForm.next.length < 8) {
    showToast('新密码至少需要 8 位')
    return
  }
  if (passwordForm.next !== passwordForm.confirm) {
    showToast('两次输入的新密码不一致')
    return
  }
  passwordSaving.value = true
  try {
    await changePassword({ current_password: passwordForm.current, new_password: passwordForm.next })
    Object.assign(passwordForm, { current: '', next: '', confirm: '' })
    showToast('密码修改成功')
  } catch (error) {
    showToast(error?.message || '密码修改失败')
  } finally {
    passwordSaving.value = false
  }
}

function logout() {
  userStore.logout()
  router.push('/login')
}

onMounted(loadData)
</script>

<style scoped>
.form-label {
  display: block;
  margin-bottom: 6px;
  color: #6e6e73;
  font-size: 12px;
  font-weight: 500;
}

.profile-input {
  width: 100%;
  border: 1px solid rgba(200, 133, 26, 0.12);
  border-radius: 10px;
  background: rgba(255, 255, 255, 0.65);
  padding: 10px 12px;
  color: #1d1d1f;
  font-size: 14px;
  outline: none;
}

.profile-input:focus {
  border-color: rgba(200, 133, 26, 0.45);
}

.portrait-chip {
  display: inline-flex;
  align-items: center;
  padding: 3px 12px;
  border-radius: 12px;
  font-size: 13px;
  color: #1d1d1f;
  background: rgba(200, 133, 26, 0.08);
  border: 1px solid rgba(200, 133, 26, 0.12);
}

.portrait-chip-tag {
  background: rgba(18, 170, 156, 0.08);
  border-color: rgba(18, 170, 156, 0.12);
  color: #12aa9c;
}

.portrait-chip-weak {
  background: rgba(229, 77, 66, 0.08);
  border-color: rgba(229, 77, 66, 0.14);
  color: #e54d42;
}
</style>
