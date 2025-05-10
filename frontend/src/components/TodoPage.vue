<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { useUserStore } from '@/stores/userStore'
import { Checkbox } from '@/components/ui/checkbox'
import { Label } from '@/components/ui/label'

const store = useUserStore()
const todos = computed(() => store.todo ?? [])

const checked = ref<boolean[]>([])

watch(
  todos,
  (newTodos) => {
    checked.value = newTodos.map((_, idx) => checked.value[idx] ?? false)
  },
  { immediate: true }
)

function toggle(index: number) {
  checked.value[index] = !checked.value[index]
}
</script>

<template>
  <div class="max-w-2xl mx-auto p-6 pb-32">
    <h1 class="text-3xl font-bold mb-6 text-center">{{ $t("todo.title") }}</h1>

    <div v-if="todos.length" class="space-y-4">
      <button
        v-for="(item, index) in todos"
        :key="index"
        @click="toggle(index)"
        class="flex items-center gap-4 w-full text-left bg-white p-4 rounded-lg shadow border transition hover:bg-gray-50 active:scale-[0.99] focus:outline-none"
      >
        <Label class="flex items-center gap-4 cursor-pointer w-full">
          <Checkbox
            :checked="checked[index]"
            class="pointer-events-none"
          />
          <span class="text-base">
            {{ item }}
          </span>
        </Label>
      </button>
    </div>

    <div v-else class="text-center text-gray-500">
      {{ $t("todo.noTasks") }}
    </div>
  </div>
</template>
