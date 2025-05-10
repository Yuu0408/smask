<script setup lang="ts">
import ChatWindow from '@/components/ChatWindow.vue'
import ChatInputBar from '@/components/ChatInputBar.vue'
import ChatMultipleChoices from '@/components/ChatMultipleChoices.vue'
import { ScrollArea } from '@/components/ui/scroll-area'
import type { Message } from '@/types/message'
import { useUserStore } from '@/stores/userStore'
import { computed, ref, watch } from 'vue'
import { sendMessageToServer } from '@/api/conversationApi'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'

defineProps<{
  sidebarOpen: boolean
}>()

const { t } = useI18n()
const userStore = useUserStore()
const messages = computed(() => userStore.messages)

const toastVisible = ref(false)
const router = useRouter()

const filteredChoices = computed(() => {
  const lastMessage = messages.value[messages.value.length - 1]
  if (lastMessage?.multiple_choices?.length === 1 && lastMessage.multiple_choices[0] === '%medical_record%') {
    toastVisible.value = true
    return []
  }
  return lastMessage?.multiple_choices || []
})

watch(toastVisible, (visible) => {
  if (visible) {
    setTimeout(() => {
      toastVisible.value = false
    }, 4000)
  }
})

function goToDiagnosis() {
  router.push('/diagnosis')
  toastVisible.value = false
}

async function sendMessage(text: string) {
  if (!userStore.sessionId) {
    alert(t('chatPage.sessionNotInitialized'))
    return
  }

  userStore.addMessage({ from: 'user', text })

  const placeholder: Message = {
    from: 'bot',
    text: t('chatPage.typing'),
    isPlaceholder: true,
  }
  userStore.addMessage(placeholder)

  const placeholderIndex = messages.value.length - 1

  try {
    const result = await sendMessageToServer({
      user_message: text,
      session_id: userStore.sessionId
    })

    userStore.setMedicalRecord(result.state.medical_record)
    userStore.setTodo(result.state.todo)
    userStore.setDiagnosis(result.state.diagnosis_paper)
    messages.value[placeholderIndex] = {
      from: 'bot',
      text: result.ai_response,
      multiple_choices: result.multiple_choices || [],
    }
  } catch (error) {
    console.error(error)
    messages.value[placeholderIndex] = {
      from: 'bot',
      text: t('chatPage.error'),
    }
  }
}

defineExpose({
  sendMessage
})
</script>

<template>
  <!-- Main centered container -->
  <div class="w-full max-w-2xl flex flex-col flex-1 min-h-[calc(100vh-64px)]">
    <ScrollArea class="flex-1">
      <ChatWindow :messages="messages" class="flex-1" />
    </ScrollArea>

    <!-- Animated toast -->
    <Transition name="fade">
      <div
        v-if="toastVisible"
        @click="goToDiagnosis"
        class="fixed top-20 right-4 z-40 bg-gray-100 dark:bg-zinc-700 text-black dark:text-white px-4 py-2 rounded-lg shadow-md cursor-pointer transition hover:bg-gray-200 dark:hover:bg-zinc-600"
      >
        📄 {{ t('chatPage.viewDiagnosis') }}
      </div>
    </Transition>

    <ChatMultipleChoices
      :choices="filteredChoices"
      @select="sendMessage"
    />
    <ChatInputBar @send="sendMessage" :sidebar-open="sidebarOpen" />
  </div>
</template>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.5s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
