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
import { Button } from '@/components/ui/button';
import { SidebarTrigger } from '@/components/ui/sidebar';
import { Settings } from 'lucide-vue-next';
import { computed } from 'vue';
import { useRoute, RouterLink } from 'vue-router';

const route = useRoute();

const breadcrumbItems = computed(() => {
    const segments = route.path.split('/').filter(Boolean);
    return segments.map((segment, index) => {
        const path = '/' + segments.slice(0, index + 1).join('/');
        if (segment === 'models-n-prompts')
            return { title: 'Models & Prompts', path };
        return {
            title: segment.charAt(0).toUpperCase() + segment.slice(1),
            path,
        };
    });
});
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

        <!-- LEFT: Breadcrumb -->

        <!-- RIGHT: Settings icon -->
        <div class="ml-auto">
            <Button variant="ghost" size="icon" aria-label="Settings">
                <Settings class="size-5" />
            </Button>
        </div>
    </header>
</template>
