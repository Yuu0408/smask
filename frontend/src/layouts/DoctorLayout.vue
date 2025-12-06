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
    <div class="relative min-h-dvh w-full overflow-hidden bg-background">
        <div
            class="pointer-events-none absolute inset-0 opacity-70"
            aria-hidden="true"
        >
            <div
                class="absolute -left-16 top-10 size-80 rounded-full bg-primary/15 blur-3xl"
            />
            <div
                class="absolute right-4 top-32 size-96 rounded-full bg-accent/12 blur-3xl"
            />
            <div
                class="absolute -right-10 bottom-10 size-72 rounded-full bg-primary/18 blur-[120px]"
            />
        </div>

        <SidebarProvider
            class="relative z-10 flex min-h-dvh min-h-0 bg-gradient-to-br from-background/80 via-white/70 to-accent/5 backdrop-blur"
        >
            <DoctorSideBar />
            <main class="flex flex-1 min-h-0 flex-col">
                <MainNavBar
                    class="sticky top-0 z-20 border-b bg-white/80 backdrop-blur-xl supports-[backdrop-filter]:bg-background/70"
                />
                <main class="flex min-h-0 flex-1 flex-col bg-transparent">
                    <RouterView :key="$route.fullPath" />
                </main>
            </main>
        </SidebarProvider>
    </div>
</template>
