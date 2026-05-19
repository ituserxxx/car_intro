<script setup>
import { ref, reactive } from 'vue'

const keyword = ref('')
const brands = ref([])
const loading = ref(false)
const hasSearched = ref(false)

const expanded = reactive(new Set())
const brandFiles = reactive({})
const brandLoading = reactive({})

const showPdfModal = ref(false)
const currentPdfUrl = ref('')

function openPdf(brand, path) {
  currentPdfUrl.value = `http://localhost:3000/api/files/view?brand=${encodeURIComponent(brand)}&path=${encodeURIComponent(path)}`
  showPdfModal.value = true
}

async function onSearch() {
  if (!keyword.value.trim()) {
    brands.value = []
    hasSearched.value = false
    return
  }
  loading.value = true
  hasSearched.value = true
  try {
    const res = await fetch(
      `http://localhost:3000/api/files/search?keyword=${encodeURIComponent(keyword.value)}`
    )
    brands.value = await res.json()
  } catch (e) {
    console.error(e)
    brands.value = []
  } finally {
    loading.value = false
  }
}

function onInput(e) {
  if (e.key === 'Enter') {
    onSearch()
  }
}

async function toggleBrand(brand) {
  if (expanded.has(brand)) {
    expanded.delete(brand)
    return
  }
  expanded.add(brand)
  if (brandFiles[brand]) return

  brandLoading[brand] = true
  try {
    const res = await fetch(
      `http://localhost:3000/api/files/list?brand=${encodeURIComponent(brand)}`
    )
    brandFiles[brand] = await res.json()
  } catch (e) {
    console.error(e)
    brandFiles[brand] = []
  } finally {
    brandLoading[brand] = false
  }
}
</script>

<template>
  <div class="relative min-h-screen overflow-hidden bg-background">
    <div class="pointer-events-none absolute inset-0 overflow-hidden">
      <div class="absolute -left-[10%] -top-[10%] h-[300px] w-[300px] rounded-full bg-primary/5 blur-[80px] sm:h-[500px] sm:w-[500px] sm:blur-[100px]" />
      <div class="absolute -bottom-[10%] -right-[10%] h-[350px] w-[350px] rounded-full bg-primary/5 blur-[100px] sm:h-[600px] sm:w-[600px] sm:blur-[120px]" />
    </div>

    <div class="relative z-10 mx-auto flex min-h-screen max-w-5xl flex-col px-4 py-8 sm:px-6 sm:py-16">
      <header class="mb-8 text-center sm:mb-16">
        <div class="mb-4 inline-flex h-14 w-14 items-center justify-center rounded-2xl bg-primary text-primary-foreground shadow-lg sm:mb-6 sm:h-16 sm:w-16">
          <svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="sm:hidden">
            <path d="M19 17h2c.6 0 1-.4 1-1v-3c0-.9-.7-1.7-1.5-1.9C18.7 10.6 16 10 16 10s-1.3-1.4-2.2-2.3c-.5-.4-1.1-.7-1.8-.7H5c-.6 0-1.1.4-1.4.9l-1.4 2.9A3.7 3.7 0 0 0 2 12v4c0 .6.4 1 1 1h2" />
            <circle cx="7" cy="17" r="2" />
            <path d="M9 17h6" />
            <circle cx="17" cy="17" r="2" />
          </svg>
          <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="hidden sm:block">
            <path d="M19 17h2c.6 0 1-.4 1-1v-3c0-.9-.7-1.7-1.5-1.9C18.7 10.6 16 10 16 10s-1.3-1.4-2.2-2.3c-.5-.4-1.1-.7-1.8-.7H5c-.6 0-1.1.4-1.4.9l-1.4 2.9A3.7 3.7 0 0 0 2 12v4c0 .6.4 1 1 1h2" />
            <circle cx="7" cy="17" r="2" />
            <path d="M9 17h6" />
            <circle cx="17" cy="17" r="2" />
          </svg>
        </div>
        <h1 class="mb-2 text-3xl font-bold tracking-tight text-foreground sm:mb-3 sm:text-4xl lg:text-5xl">汽车说明书检索</h1>
        <p class="mx-auto max-w-lg text-base text-muted-foreground sm:text-lg">输入品牌关键词，快速定位用户手册与使用说明书</p>
      </header>

      <div class="mx-auto mb-8 w-full max-w-2xl space-y-4 sm:mb-12">
        <div class="flex flex-col gap-3 sm:flex-row sm:items-center">
          <div class="group relative flex flex-1 items-center rounded-2xl border border-input bg-card shadow-xl shadow-black/5 transition-all duration-300 hover:shadow-2xl hover:shadow-black/10 focus-within:ring-2 focus-within:ring-ring">
            <div class="pl-4 text-muted-foreground sm:pl-5">
              <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="sm:hidden">
                <circle cx="11" cy="11" r="8" />
                <path d="m21 21-4.3-4.3" />
              </svg>
              <svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="hidden sm:block">
                <circle cx="11" cy="11" r="8" />
                <path d="m21 21-4.3-4.3" />
              </svg>
            </div>
            <input v-model="keyword" type="text" placeholder="例如：比亚迪、丰田、大众..." class="h-12 w-full bg-transparent px-3 text-base text-foreground placeholder:text-muted-foreground/70 outline-none sm:h-14 sm:px-4" @keydown="onInput" />
          </div>

          <button @click="onSearch" :disabled="loading" class="inline-flex h-12 shrink-0 items-center justify-center rounded-2xl bg-primary px-6 text-base font-semibold text-primary-foreground shadow-lg shadow-primary/25 transition-all hover:bg-primary/90 hover:shadow-xl hover:shadow-primary/30 hover:-translate-y-0.5 active:translate-y-0 disabled:opacity-50 disabled:cursor-not-allowed sm:h-14 sm:px-8">
            <span v-if="loading" class="mr-2">
              <svg class="h-5 w-5 animate-spin" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
              </svg>
            </span>
            {{ loading ? '搜索中' : '搜索' }}
          </button>
        </div>

        <div class="flex flex-wrap justify-center gap-2">
          <button v-for="tag in ['比亚迪', '丰田', '大众', '北京越野', '传祺', '长城']" :key="tag" @click="keyword = tag; onSearch()" class="rounded-full border border-border bg-secondary px-3 py-1 text-sm text-secondary-foreground transition-colors hover:bg-secondary/80 sm:px-4 sm:py-1.5">
            {{ tag }}
          </button>
        </div>
      </div>

      <div v-if="hasSearched" class="w-full">
        <div class="mb-6 flex items-center justify-between">
          <h2 class="text-lg font-semibold text-foreground">
            搜索结果
            <span v-if="!loading" class="ml-2 text-sm font-normal text-muted-foreground">共 {{ brands.length }} 个品牌</span>
          </h2>
        </div>

        <div v-if="loading" class="grid gap-4">
          <div v-for="i in 6" :key="i" class="h-24 animate-pulse rounded-2xl bg-muted" />
        </div>

        <div v-else-if="brands.length" class="grid gap-4">
          <div v-for="brand in brands" :key="brand" class="rounded-2xl border border-border bg-card shadow-sm overflow-hidden">
            <button @click="toggleBrand(brand)" class="flex w-full items-center justify-between p-4 text-left transition-colors hover:bg-muted/50 sm:p-5">
              <div class="flex items-center gap-3">
                <div class="flex h-9 w-9 items-center justify-center rounded-xl bg-primary/10 text-primary sm:h-10 sm:w-10">
                  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="sm:hidden">
                    <path d="M4 20h16a2 2 0 0 0 2-2V8a2 2 0 0 0-2-2h-7.93a2 2 0 0 1-1.66-.9l-.82-1.2A2 2 0 0 0 7.93 3H4a2 2 0 0 0-2 2v13c0 1.1.9 2 2 2Z" />
                  </svg>
                  <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="hidden sm:block">
                    <path d="M4 20h16a2 2 0 0 0 2-2V8a2 2 0 0 0-2-2h-7.93a2 2 0 0 1-1.66-.9l-.82-1.2A2 2 0 0 0 7.93 3H4a2 2 0 0 0-2 2v13c0 1.1.9 2 2 2Z" />
                  </svg>
                </div>
                <span class="text-lg font-semibold text-foreground sm:text-xl">{{ brand }}</span>
              </div>
              <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="text-muted-foreground transition-transform duration-200" :class="expanded.has(brand) ? 'rotate-180' : ''">
                <polyline points="6 9 12 15 18 9" />
              </svg>
            </button>

            <div v-if="expanded.has(brand)" class="border-t border-border px-4 pb-4 pt-0 sm:px-5 sm:pb-5">
              <div v-if="brandLoading[brand]" class="mt-4 space-y-3">
                <div v-for="i in 3" :key="i" class="h-12 animate-pulse rounded-xl bg-muted" />
              </div>
              <div v-else-if="brandFiles[brand] && brandFiles[brand].length" class="mt-4 space-y-4 sm:space-y-5">
                <div v-for="group in brandFiles[brand]" :key="group.folder">
                  <h4 v-if="group.folder" class="mb-2 text-sm font-semibold uppercase tracking-wider text-muted-foreground sm:text-base">{{ group.folder }}</h4>
                  <div class="grid gap-2 sm:grid-cols-2">
                    <div v-for="(item, idx) in group.files" :key="idx" @click="openPdf(brand, item.path)" class="flex cursor-pointer items-center gap-2 rounded-lg border border-border bg-background p-2 transition-all hover:border-primary/20 hover:shadow-sm sm:p-2.5">
                      <div class="flex h-6 w-6 shrink-0 items-center justify-center rounded bg-primary/5 text-primary">
                        <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                          <path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z" />
                          <polyline points="14 2 14 8 20 8" />
                        </svg>
                      </div>
                      <p class="text-sm font-medium text-foreground line-clamp-2 sm:text-base">{{ item.name }}</p>
                    </div>
                  </div>
                </div>
              </div>
              <div v-else class="mt-4 text-sm text-muted-foreground">暂无文件</div>
            </div>
          </div>
        </div>

        <div v-else class="flex flex-col items-center justify-center rounded-2xl border border-dashed border-border bg-card py-12 text-center sm:py-16">
          <div class="mb-4 rounded-full bg-muted p-4">
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="text-muted-foreground">
              <circle cx="11" cy="11" r="8" />
              <path d="m21 21-4.3-4.3" />
            </svg>
          </div>
          <h3 class="text-base font-medium text-foreground">未找到相关品牌</h3>
          <p class="mt-1 text-sm text-muted-foreground">尝试更换关键词，或检查拼写是否正确</p>
        </div>
      </div>

      <Teleport to="body">
        <div v-if="showPdfModal" class="fixed inset-0 z-50 flex flex-col bg-black/80 backdrop-blur-sm" @click.self="showPdfModal = false">
          <div class="flex items-center justify-between border-b border-border bg-card px-3 py-2.5 sm:px-4 sm:py-3">
            <span class="text-base font-semibold text-foreground sm:text-lg">PDF 预览</span>
            <button @click="showPdfModal = false" class="rounded-lg p-2 text-muted-foreground hover:bg-muted">
              <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <line x1="18" y1="6" x2="6" y2="18" />
                <line x1="6" y1="6" x2="18" y2="18" />
              </svg>
            </button>
          </div>
          <div class="flex-1 overflow-hidden">
            <iframe v-if="currentPdfUrl" :src="currentPdfUrl" class="h-full w-full" frameborder="0"></iframe>
          </div>
        </div>
      </Teleport>

      <footer class="mt-auto pt-8 text-center text-sm text-muted-foreground sm:pt-16">
        <p>汽车说明书检索系统 · 数据来源于各品牌官方用户手册</p>
      </footer>
    </div>
  </div>
</template>

<style scoped>
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>
