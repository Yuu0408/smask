<script lang="ts">
export const description = 'Doctor layout with minimal sidebar.';
export const iframeHeight = '800px';
export const containerClass = 'w-full h-full';
</script>

<script setup lang="ts">
import DoctorSideBar from '@/components/DoctorSideBar.vue';
import { SidebarProvider } from '@/components/ui/sidebar';
import MainNavBar from '@/components/MainNavBar.vue';
import { RouterView } from 'vue-router';
</script>

<template>
    <div class="h-dvh w-full overflow-hidden">
        <SidebarProvider class="flex h-full min-h-0">
            <DoctorSideBar />
            <main class="flex flex-1 min-h-0 flex-col">
                <MainNavBar
                    class="sticky top-0 z-20 border-b bg-background/80 backdrop-blur supports-[backdrop-filter]:bg-background/60"
                />
                <main class="flex h-[calc(100vh-3rem)] flex-col bg-background">
                    <RouterView :key="$route.fullPath" />
                </main>
            </main>
        </SidebarProvider>
    </div>
</template>
