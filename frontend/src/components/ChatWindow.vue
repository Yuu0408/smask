<script setup lang="ts">
import { ScrollArea } from '@/components/ui/scroll-area'
import { ref, watch, nextTick } from 'vue'
import markdownit from 'markdown-it'
import type { Message } from '@/types/message'
import type { PropType } from 'vue'

const props = defineProps({
  messages: {
    type: Array as PropType<Message[]>,
    required: true,
  }
})

const bottomRef = ref<HTMLElement | null>(null)

const md = markdownit({
  breaks: true,
  html: false,
})

watch(
  () => props.messages,
  async () => {
    await nextTick()
    bottomRef.value?.scrollIntoView({ behavior: 'smooth' })
  },
  { deep: true }
)
</script>

<template>
  <ScrollArea class="flex-1">
    <div class="p-4 space-y-4 pb-16">
      <div
        v-for="(m, i) in messages"
        :key="i"
        class="w-full flex"
        :class="m.from === 'user' ? 'justify-end' : 'justify-start'"
      >
        <div
          :class="[
            m.isPlaceholder
              ? 'bg-muted text-muted-foreground opacity-60 italic animate-pulse px-4 py-2 rounded-lg text-sm sm:text-base max-w-[75%] break-words'
              : m.from === 'user'
              ? 'bg-primary text-primary-foreground text-left px-4 py-2 rounded-lg text-sm sm:text-base max-w-[75%] break-words'
              : 'bg-muted text-muted-foreground text-left max-w-[80%] prose prose-sm sm:prose-base dark:prose-invert p-4 rounded-xl'
          ]"
          v-html="m.from === 'bot' && !m.isPlaceholder ? md.render(m.text) : m.text"
        />
      </div>

      <div ref="bottomRef" />
    </div>
  </ScrollArea>
</template>

<style scoped>
.prose :is(h1, h2, h3, h4, h5, h6) {
  margin-top: 0.5rem;
  margin-bottom: 0.25rem;
}
.prose ul {
  padding-left: 1.25rem;
  margin-top: 0.25rem;
  margin-bottom: 0.25rem;
}
.prose li {
  margin-bottom: 0.25rem;
}
</style>
