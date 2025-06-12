<script setup lang="ts">
import SpeechToTextButton from "@/components/SpeechToTextButton.vue";
// import ChatWindow from "@/components/ChatWindow.vue";
// import ChatInputBar from "@/components/ChatInputBar.vue";
import ChatMultipleChoices from "@/components/ChatMultipleChoices.vue";
// import { ScrollArea } from "@/components/ui/scroll-area";
// import type { Message } from "@/types/message";
import { useUserStore } from "@/stores/userStore";
import { computed, ref, watch, onMounted, nextTick } from "vue";
import {
  sendMessageForAudioConversation,
  // sendMessageToServer,
} from "@/api/conversationApi";
import { useRouter } from "vue-router";
import { useI18n } from "vue-i18n";

defineProps<{
  sidebarOpen: boolean;
}>();

const { t } = useI18n();
const { locale } = useI18n();
const userStore = useUserStore();
const messages = computed(() => userStore.messages);

const toastVisible = ref(false);
const router = useRouter();

const filteredChoices = computed(() => {
  const lastMessage = messages.value[messages.value.length - 1];
  if (
    lastMessage?.multiple_choices?.length === 1 &&
    lastMessage.multiple_choices[0] === "%medical_record%"
  ) {
    toastVisible.value = true;
    return [];
  }
  return lastMessage?.multiple_choices || [];
});

watch(toastVisible, (visible) => {
  if (visible) {
    setTimeout(() => {
      toastVisible.value = false;
    }, 4000);
  }
});

function goToDiagnosis() {
  router.push("/diagnosis");
  toastVisible.value = false;
}

const responseText = ref("");

async function sendMessage(text: string) {
  if (!userStore.sessionId) {
    alert(t("chatPage.sessionNotInitialized"));
    return;
  }

  try {
    console.log("Sending message:", text);
    const result = await sendMessageForAudioConversation({
      session_id: userStore.sessionId,
      user_message: text,
    });

    userStore.setMedicalRecord(result.state.medical_record);
    userStore.setTodo(result.state.todo);
    userStore.setDiagnosis(result.state.diagnosis_paper);

    // Set the response text for display
    responseText.value = result.ai_response;

    // Play audio if audio_base64 is present and valid
    if (result.audio_base64 && result.audio_base64.length > 100) {
      const audio = new Audio(`data:audio/mp3;base64,${result.audio_base64}`);
      audio.onerror = (e) => {
        console.error("Audio playback error:", e);
        responseText.value = t("chatPage.error");
      };

      // Wait for DOM update before playing (optional, for UX)
      await nextTick();
      audio.play();
    }
  } catch (error) {
    console.error(error);
    responseText.value = t("chatPage.error");
  }
}

defineExpose({
  sendMessage,
});
</script>

<template>
  <!-- Main centered container -->
  <div class="w-full max-w-2xl flex flex-col flex-1 min-h-[calc(100vh-64px)]">
    <!-- Animated toast -->
    <Transition name="fade">
      <div
        v-if="toastVisible"
        @click="goToDiagnosis"
        class="fixed top-20 right-4 z-40 bg-gray-100 dark:bg-zinc-700 text-black dark:text-white px-4 py-2 rounded-lg shadow-md cursor-pointer transition hover:bg-gray-200 dark:hover:bg-zinc-600"
      >
        📄 {{ t("chatPage.viewDiagnosis") }}
      </div>
    </Transition>

    <!-- Display AI response text -->
    <div
      v-if="responseText"
      class="my-4 p-4 bg-gray-50 dark:bg-zinc-800 rounded shadow"
    >
      {{ responseText }}
    </div>

    <!-- Speech to Text Button -->
    <div class="flex justify-center my-2">
      <SpeechToTextButton @result="sendMessage" />
    </div>

    <ChatMultipleChoices :choices="filteredChoices" @select="sendMessage" />
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
