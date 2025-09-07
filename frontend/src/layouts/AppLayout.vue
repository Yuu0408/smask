<script lang="ts">
export const description = 'A sidebar that collapses to icons.';
export const iframeHeight = '800px';
export const containerClass = 'w-full h-full';
</script>

<script setup lang="ts">
import AppSideBar from '@/components/AppSideBar.vue';
import {
    Breadcrumb,
    BreadcrumbItem,
    BreadcrumbLink,
    BreadcrumbList,
    BreadcrumbPage,
    BreadcrumbSeparator,
} from '@/components/ui/breadcrumb';
import { Separator } from '@/components/ui/separator';
import {
    SidebarInset,
    SidebarProvider,
    SidebarTrigger,
} from '@/components/ui/sidebar';
import { useRoute, RouterView, useRouter } from 'vue-router';
// import { computed } from 'vue';
import { computed, onBeforeMount } from 'vue';
import MainNavBar from '@/components/MainNavBar.vue';

// const route = useRoute();
const route = useRoute();
const router = useRouter();

// TODO: I18n breadcrumbs
const breadcrumbItems = computed(() => {
    const segments = route.path.split('/').filter(Boolean);
    return segments.map((segment, index) => {
        const path = '/' + segments.slice(0, index + 1).join('/');

        if (segment === 'models-n-prompts') {
            return {
                title: 'Models & Prompts',
                path,
            };
        }

        return {
            title: segment.charAt(0).toUpperCase() + segment.slice(1),
            path,
        };
    });
});

onBeforeMount(async () => {
    if (router.currentRoute.value.name === 'home') {
        await router.push({
            name: 'users',
        });
    }
});
</script>
<!-- AppLayout.vue (updated template section) -->
<template>
    <!-- Make the viewport non-scrolling and height-bound -->
    <div class="h-dvh w-full overflow-hidden">
        <!-- Ensure the flex chain allows shrinking -->
        <SidebarProvider class="flex h-full min-h-0">
            <AppSideBar />

            <!-- Main column does NOT scroll -->
            <main class="flex flex-1 min-h-0 flex-col">
                <!-- Stays put; page won't scroll anymore -->
                <MainNavBar
                    class="sticky top-0 z-20 border-b bg-background/80 backdrop-blur supports-[backdrop-filter]:bg-background/60"
                />

                <!-- Only this area scrolls -->
                <main class="flex h-[calc(100vh-3rem)] flex-col bg-background">
                    <RouterView />
                </main>
            </main>
        </SidebarProvider>
    </div>
</template>
