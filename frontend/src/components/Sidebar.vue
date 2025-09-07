<template>
    <aside
        class="bg-gray-200 dark:bg-gray-800 text-black dark:text-white w-64 h-full fixed top-0 left-0 z-30 transition-transform duration-300 ease-in-out overflow-hidden flex flex-col justify-between"
        :class="{ '-translate-x-full': !isOpen }"
    >
        <!-- Navigation -->
        <div class="p-4 mt-16">
            <ul class="space-y-1">
                <li>
                    <button
                        @click="navigateTo('/chat')"
                        :class="[
                            'w-full flex items-center gap-2 text-left px-4 py-2 rounded-md transition-colors duration-200 font-medium active:scale-[0.98]',
                            currentRoute === '/chat'
                                ? 'bg-gray-300 dark:bg-gray-600'
                                : 'hover:bg-gray-300 dark:hover:bg-gray-700',
                        ]"
                    >
                        <MessageSquare class="w-5 h-5" />
                        {{ $t('sidebar.chat') }}
                    </button>
                </li>
                <li>
                    <button
                        @click="navigateTo('/record')"
                        :class="[
                            'w-full flex items-center gap-2 text-left px-4 py-2 rounded-md transition-colors duration-200 font-medium active:scale-[0.98]',
                            currentRoute === '/record'
                                ? 'bg-gray-300 dark:bg-gray-600'
                                : 'hover:bg-gray-300 dark:hover:bg-gray-700',
                        ]"
                    >
                        <FileText class="w-5 h-5" />
                        {{ $t('sidebar.medicalRecord') }}
                    </button>
                </li>
                <li>
                    <button
                        @click="navigateTo('/diagnosis')"
                        :class="[
                            'w-full flex items-center gap-2 text-left px-4 py-2 rounded-md transition-colors duration-200 font-medium active:scale-[0.98]',
                            currentRoute === '/diagnosis'
                                ? 'bg-gray-300 dark:bg-gray-600'
                                : 'hover:bg-gray-300 dark:hover:bg-gray-700',
                        ]"
                    >
                        <HeartPulse class="w-5 h-5" />
                        {{ $t('sidebar.diagnosis') }}
                    </button>
                </li>
                <li>
                    <button
                        @click="navigateTo('/todo')"
                        :class="[
                            'w-full flex items-center gap-2 text-left px-4 py-2 rounded-md transition-colors duration-200 font-medium active:scale-[0.98]',
                            currentRoute === '/todo'
                                ? 'bg-gray-300 dark:bg-gray-600'
                                : 'hover:bg-gray-300 dark:hover:bg-gray-700',
                        ]"
                    >
                        <ListTodo class="w-5 h-5" />
                        {{ $t('sidebar.todoList') }}
                    </button>
                </li>
            </ul>
        </div>

        <!-- Language Select at Bottom -->
        <div class="p-4 border-t border-gray-300 dark:border-gray-700">
            <Select v-model="selectedLanguage">
                <SelectTrigger class="w-full">
                    <SelectValue :placeholder="$t('sidebar.selectLanguage')" />
                </SelectTrigger>
                <SelectContent>
                    <SelectItem value="en">English</SelectItem>
                    <SelectItem value="vi">Tiếng Việt</SelectItem>
                </SelectContent>
            </Select>
        </div>
    </aside>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { MessageSquare, FileText, HeartPulse, ListTodo } from 'lucide-vue-next';

import {
    Select,
    SelectTrigger,
    SelectValue,
    SelectContent,
    SelectItem,
} from '@/components/ui/select';
import { useI18n } from 'vue-i18n';

defineProps<{ isOpen: boolean }>();

const router = useRouter();
const route = useRoute();
const { locale } = useI18n();

function navigateTo(path: string) {
    router.push(path);
}

const currentRoute = computed(() => route.path);

const selectedLanguage = ref<'en' | 'vi'>(
    (localStorage.getItem('lang') as 'en' | 'vi') ||
        (locale.value as 'en' | 'vi')
);

watch(selectedLanguage, (newLang) => {
    locale.value = newLang;
    localStorage.setItem('lang', newLang);
});
</script>
