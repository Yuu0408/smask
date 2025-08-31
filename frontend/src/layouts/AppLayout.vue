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

<template>
    <SidebarProvider>
        <AppSideBar />
        <SidebarInset class="overflow-auto">
            <header
                class="flex h-16 shrink-0 items-center gap-2 transition-[width,height] ease-linear group-has-[[data-collapsible=icon]]/sidebar-wrapper:h-12"
            >
                <div class="flex items-center gap-2 px-4">
                    <SidebarTrigger class="-ml-1" />
                    <Separator orientation="vertical" class="mr-2 h-4" />
                    <Breadcrumb>
                        <BreadcrumbList>
                            <BreadcrumbItem
                                v-for="(item, index) in breadcrumbItems"
                                :key="item.path"
                            >
                                <template
                                    v-if="index < breadcrumbItems.length - 1"
                                >
                                    <BreadcrumbLink :href="item.path">
                                        {{ item.title }}
                                    </BreadcrumbLink>
                                    <BreadcrumbSeparator />
                                </template>
                                <template v-else>
                                    <BreadcrumbPage>{{
                                        item.title
                                    }}</BreadcrumbPage>
                                </template>
                            </BreadcrumbItem>
                        </BreadcrumbList>
                    </Breadcrumb>
                </div>
            </header>
            <RouterView />
        </SidebarInset>
    </SidebarProvider>
</template>
