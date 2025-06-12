<script setup lang="ts">
// @ts-ignore
type SpeechRecognition = any;
// @ts-ignore
type webkitSpeechRecognition = any;

import { ref } from "vue";
import { Mic } from "lucide-vue-next";
import { useI18n } from "vue-i18n";

const { locale } = useI18n();

const isListening = ref(false);

const emit = defineEmits<{
  (e: "result", text: string): void;
}>();

let recognition: SpeechRecognition | null = null;

function startListening() {
  if (
    !("webkitSpeechRecognition" in window) &&
    !("SpeechRecognition" in window)
  ) {
    alert("Speech recognition is not supported in this browser.");
    return;
  }

  const SpeechRecognitionClass =
    (window as any).SpeechRecognition ||
    (window as any).webkitSpeechRecognition;
  recognition = new SpeechRecognitionClass();

  // Map i18n locale to BCP-47 language tag
  let lang = locale.value;
  if (lang === "vi") lang = "vi-VN";
  else if (lang === "en") lang = "en-US";
  // Add more mappings if you support more languages

  recognition.lang = lang;
  recognition.interimResults = false;
  recognition.maxAlternatives = 1;

  recognition.onstart = () => {
    isListening.value = true;
  };

  recognition.onend = () => {
    isListening.value = false;
  };

  recognition.onerror = (event: any) => {
    isListening.value = false;
    alert("Speech recognition error: " + event.error);
  };

  recognition.onresult = (event: any) => {
    const transcript = event.results[0][0].transcript;
    emit("result", transcript);
  };

  recognition.start();
}
</script>

<template>
  <button
    @click="startListening"
    :class="[
      'rounded-full p-3 shadow transition',
      isListening
        ? 'bg-green-500 text-white animate-pulse'
        : 'bg-gray-200 dark:bg-zinc-700 text-black dark:text-white',
    ]"
    title="Speak"
  >
    <Mic :size="24" />
  </button>
</template>
