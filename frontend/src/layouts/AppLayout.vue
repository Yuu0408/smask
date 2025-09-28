<script lang="ts">
export const description = 'A sidebar that collapses to icons.';
export const iframeHeight = '800px';
export const containerClass = 'w-full h-full';
</script>

<script setup lang="ts">
import AppSideBar from '@/components/AppSideBar.vue';
import { SidebarProvider } from '@/components/ui/sidebar';
import { RouterView } from 'vue-router';
import MainNavBar from '@/components/MainNavBar.vue';
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
