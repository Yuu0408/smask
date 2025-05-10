<script setup lang="ts">
import { ref, watch, onMounted, nextTick } from 'vue'
import { Send } from 'lucide-vue-next'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()
const input = ref('')
const textareaRef = ref<HTMLTextAreaElement | null>(null)
const emit = defineEmits(['send'])

defineProps<{ sidebarOpen: boolean }>()

function autoResize(el: HTMLTextAreaElement) {
  el.style.height = 'auto'
  el.style.height = el.scrollHeight + 'px'
}

function send() {
  if (!input.value.trim()) return
  emit('send', input.value.trim())
  input.value = ''

  // Wait until DOM updates (input cleared), then resize
  nextTick(() => {
    if (textareaRef.value) {
      autoResize(textareaRef.value)
    }
  })
}

watch(input, () => {
  if (textareaRef.value) {
    autoResize(textareaRef.value)
  }
})

onMounted(() => {
  if (textareaRef.value) {
    autoResize(textareaRef.value)
  }
})
</script>

<template>
  <form
    @submit.prevent="send"
    class="fixed bottom-0 z-40 px-4 py-5 dark:border-zinc-700 bg-background w-full max-w-2xl flex justify-center transition-all duration-300"
    :style="{
      left: sidebarOpen ? 'calc(50% + 8rem)' : '50%',
      transform: 'translateX(-50%)'
    }"
  >
    <div class="w-full flex gap-2 items-center">
      <textarea
        ref="textareaRef"
        v-model="input"
        :placeholder="t('chatInput.placeholder')"
        rows="1"
        @keydown.enter.exact.prevent="send"
        class="flex-1 resize-none overflow-hidden border rounded-lg px-4 py-2 max-h-40 dark:bg-zinc-800 dark:border-zinc-700"
      />
      <button type="submit" class="h-full btn px-2 rounded-lg flex items-center justify-center group hover:bg-gray-200 dark:hover:bg-zinc-700 transition-colors active:bg-gray-300 dark:active:bg-zinc-600 group">
        <Send class="w-6 h-6"/>
      </button>
    </div>
  </form>
</template>
