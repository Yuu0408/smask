<script setup lang="ts">
import type { SidebarProps } from '@/components/ui/sidebar';

import { AudioLines, Sparkles, User } from 'lucide-vue-next';
import NavMain, { type SidebarItem } from '@/components/sidebar/NavMain.vue';
import NavUser from '@/components/sidebar/NavUser.vue';

import {
    Sidebar,
    SidebarContent,
    SidebarFooter,
    SidebarRail,
} from '@/components/ui/sidebar';

import { useRoute } from 'vue-router';
import { useI18n } from 'vue-i18n';

const props = withDefaults(defineProps<SidebarProps>(), {
    collapsible: 'icon',
});
const { t } = useI18n();

const route = useRoute();
// Create computed navigation items with active state based on current route
const navMainItem = [
    {
        title: t('sidebar.main.new-chat'),
        icon: User,
        type: 'single',
        url: '/new-chat',
        isActive: route.path.startsWith('/new-chat'),
    },
] satisfies SidebarItem[];
const navMain = [
    {
        title: t('sidebar.group.users'),
        icon: User,
        type: 'group',
        url: '/chat',
        isActive: route.path.startsWith('/chat'),
        items: [
            {
                title: t('sidebar.group.users.members'),
                url: '/chat/medical-record',
                isActive: route.path.includes('/chat/medical-record'),
            },
            {
                title: t('sidebar.group.users.admins'),
                url: '/users/admins',
                isActive: route.path.includes('/users/admins'),
            },
        ],
    },
    {
        title: t('sidebar.group.models-n-prompts'),
        icon: Sparkles,
        type: 'group',
        url: '/models-n-prompts/',
        isActive: route.path.startsWith('/models-n-prompts'),
        items: [
            {
                title: t('sidebar.group.models-n-prompts.models'),
                url: '/models-n-prompts/models',
                isActive: route.path.includes('/models-n-prompts/models'),
            },
            {
                title: t('sidebar.group.models-n-prompts.prompts'),
                url: '/models-n-prompts/prompts',
                isActive: route.path.includes('/models-n-prompts/prompts'),
            },
            {
                title: t('sidebar.group.models-n-prompts.prompt-templates'),
                url: '/models-n-prompts/prompt-templates',
                isActive: route.path.includes(
                    '/models-n-prompts/prompt-templates'
                ),
            },
        ],
    },
    {
        title: t('sidebar.group.kaigi'),
        icon: AudioLines,
        type: 'group',
        url: '/kaigi',
        isActive: route.path.startsWith('/kaigi'),
        items: [
            {
                title: t('sidebar.group.kaigi.app-prompts'),
                url: '/kaigi/app-prompts',
                isActive: route.path.includes('/kaigi/app-prompts'),
            },
            {
                title: t('sidebar.group.kaigi.summary-templates'),
                url: '/kaigi/summary-templates',
                isActive: route.path.includes('/kaigi/summary-templates'),
            },
            // {
            //     title: t('sidebar.group.kaigi.summary-templates.messages'),
            //     url: '/kaigi/summary-messages',
            //     isActive: route.path.includes('/kaigi/summary-messages'),
            // },
        ],
    },
] satisfies SidebarItem[];
</script>

<template>
    <Sidebar v-bind="props">
        <SidebarContent>
            <NavMain :items="navMain" :main-items="navMainItem" />
        </SidebarContent>
        <SidebarFooter>
            <NavUser />
        </SidebarFooter>
        <SidebarRail />
    </Sidebar>
</template>
