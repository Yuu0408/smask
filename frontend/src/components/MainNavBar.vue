<!-- src/components/MainNavBar.vue -->
<script setup lang="ts">
import {
    Breadcrumb,
    BreadcrumbItem,
    BreadcrumbLink,
    BreadcrumbList,
    BreadcrumbPage,
    BreadcrumbSeparator,
} from '@/components/ui/breadcrumb';
import { SidebarTrigger } from '@/components/ui/sidebar';
import { computed, ref, watch } from 'vue';
import { useRoute, RouterLink, useRouter } from 'vue-router';
import { useContactStore } from '@/stores/contact';
import { useI18n } from 'vue-i18n';

const route = useRoute();
const router = useRouter();
const contactStore = useContactStore();
const contactName = ref<string | null>(null);
const { t } = useI18n();

async function refreshContactName() {
    try {
        if (
            (route.name === 'contact.detail' ||
                route.name === 'contact.chat') &&
            route.params.id
        ) {
            const id = String(route.params.id);
            const res = await contactStore.getContactDetail(id);
            // Try to get a human-friendly name from medical record
            contactName.value =
                (res as any)?.medical_record?.patient_info?.full_name || null;
        } else {
            contactName.value = null;
        }
    } catch {
        contactName.value = null;
    }
}

watch(
    () => route.fullPath,
    () => {
        void refreshContactName();
    },
    { immediate: true }
);

const breadcrumbItems = computed(() => {
    const segments = route.path.split('/').filter(Boolean);
    return segments.map((segment, index) => {
        const path = '/' + segments.slice(0, index + 1).join('/');

        // Known segments -> i18n keys
        const segmentKeyMap: Record<string, string> = {
            home: 'navbar.breadcrumb.home',
            chat: 'navbar.breadcrumb.chat',
            record: 'navbar.breadcrumb.record',
            diagnosis: 'navbar.breadcrumb.diagnosis',
            todo: 'navbar.breadcrumb.todo',
            history: 'navbar.breadcrumb.history',
            contact: 'navbar.breadcrumb.contact',
            patients: 'navbar.breadcrumb.patients',
            'models-n-prompts': 'navbar.breadcrumb.modelsPrompts',
            'current-conversation': 'navbar.breadcrumb.currentConversation',
            'new-chat': 'navbar.breadcrumb.newChat',
        };

        // Show patient name instead of ID in contact routes
        if (
            segments[0] === 'contact' &&
            segments[1] === 'patients' &&
            index === 2
        ) {
            return { title: contactName.value || segment, path };
        }

        const key = segmentKeyMap[segment];
        if (key) {
            return { title: t(key), path };
        }

        return {
            title: segment.charAt(0).toUpperCase() + segment.slice(1),
            path,
        };
    });
});

function goHome() {
    router.push('/home');
}
</script>

<template>
    <!-- Height matches your design; stays fixed via parent `sticky` -->
    <header class="flex h-16 w-full items-center space-x-4 border-b px-4">
        <div class="flex items-center space-x-4">
            <!-- Mobile-only sidebar trigger (desktop trigger lives in the sidebar) -->
            <SidebarTrigger class="shrink-0" aria-label="Toggle sidebar" />
            <div class="min-w-0">
                <Breadcrumb>
                    <BreadcrumbList class="flex min-w-0">
                        <BreadcrumbItem
                            v-for="(item, index) in breadcrumbItems"
                            :key="item.path"
                            class="truncate"
                        >
                            <template v-if="index < breadcrumbItems.length - 1">
                                <BreadcrumbLink as-child>
                                    <RouterLink
                                        :to="item.path"
                                        class="truncate"
                                        >{{ item.title }}</RouterLink
                                    >
                                </BreadcrumbLink>
                                <BreadcrumbSeparator />
                            </template>
                            <template v-else>
                                <BreadcrumbPage class="truncate">{{
                                    item.title
                                }}</BreadcrumbPage>
                            </template>
                        </BreadcrumbItem>
                    </BreadcrumbList>
                </Breadcrumb>
            </div>
        </div>

        <!-- RIGHT: App logo (clickable) -->
        <div class="ml-auto">
            <button
                class="select-none outline-hidden cursor-pointer"
                aria-label="Go to home"
                @click="goHome"
            >
                <img
                    src="/medee.jpg"
                    alt="Medee"
                    class="h-12 md:h-14 w-auto object-contain"
                    draggable="false"
                />
            </button>
        </div>
    </header>
</template>
