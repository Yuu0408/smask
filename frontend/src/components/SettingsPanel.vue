<script setup lang="ts">
import { ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
const { locale, t } = useI18n()

const show = ref(false)

function toggleTheme() {
  document.documentElement.classList.toggle('dark')
}
</script>

<template>
  <transition name="slide-fade">
    <div
      v-show="show"
      class="absolute right-12 top-0 w-56 bg-popover dark:bg-zinc-800 p-4 rounded-xl shadow-lg"
      @mouseleave="show = false"
    >
      <h3 class="font-semibold mb-2">{{ t('settings.title') }}</h3>

      <label class="block mb-2">{{ t('settings.language') }}
        <select v-model="locale" class="mt-1 w-full input">
          <option value="en">English</option>
          <option value="vi">Tiếng Việt</option>
        </select>
      </label>

      <button class="btn w-full" @click="toggleTheme">
        {{ t('settings.theme') }}
      </button>
    </div>
  </transition>
</template>

<style scoped>
.slide-fade-enter-from,
.slide-fade-leave-to {
  transform: translateX(20px);
  opacity: 0;
}
.slide-fade-enter-active,
.slide-fade-leave-active {
  transition: all 0.2s ease;
}
</style>
