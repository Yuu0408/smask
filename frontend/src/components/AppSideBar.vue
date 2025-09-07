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
    SidebarMenu,
    SidebarMenuButton,
    SidebarMenuItem,
    SidebarTrigger,
    SidebarGroupContent,
    SidebarGroupLabel,
    SidebarGroup,
    useSidebar,
} from '@/components/ui/sidebar';

import {
    DropdownMenu,
    DropdownMenuContent,
    DropdownMenuItem,
    DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { ChevronDown } from 'lucide-vue-next';

import { useRoute } from 'vue-router';
import { useI18n } from 'vue-i18n';
import SidebarHeader from './ui/sidebar/SidebarHeader.vue';
import { Separator } from '@/components/ui/separator';
import { useDialog } from '@/plugins/dialog-manager/use-dialog';
import MedicalRecordDialog from '@/pages/chat/medical-record/MedicalRecordDialog.vue';
import { useRouter } from 'vue-router';
import { storeToRefs } from 'pinia';
import { useAuthStore } from '@/stores/auth';

// const store = useMeStore();
// // const azure = useAzureStore();
const router = useRouter();
// const { me: user } = storeToRefs(store);

const logout = async () => {
    try {
        // await azure.logout();
        // store.me = null;
        // await router.push({
        //     name: 'login',
        // });
    } catch (error) {
        console.error('Logout error:', error);
    }
};

const { isMobile } = useSidebar();

const props = withDefaults(defineProps<SidebarProps>(), {
    collapsible: 'icon',
});
const { openDialog } = useDialog();
const { t } = useI18n();

// Create computed navigation items with active state based on current route

const handleNewChat = async () => {
    openDialog({
        component: MedicalRecordDialog,
        // optional initial props
    });
};

const auth = useAuthStore();

async function handleLogout() {
    try {
        await auth.logout();
        await router.push({
            name: 'login',
        });
        // Optional: redirect to login page
        // router.push({ name: 'login' })
    } catch (e) {
        console.error('Logout failed', e);
    }
}
</script>

<template>
    <Sidebar collapsible="icon">
        <SidebarHeader class="px-2 py-4">
            <div class="flex items-center gap-2 px-2">
                <div class="size-8 rounded-md bg-primary/10" />
                <span class="font-semibold">{{
                    t('sidebar.header.app.name')
                }}</span>
            </div>
        </SidebarHeader>

        <SidebarContent>
            <nav class="px-2">
                <SidebarGroup>
                    <SidebarGroupLabel>{{
                        t('sidebar.content.label.conversations')
                    }}</SidebarGroupLabel>
                    <SidebarGroupContent>
                        <SidebarMenu>
                            <SidebarMenuItem>
                                <SidebarMenuButton as-child>
                                    <button
                                        type="button"
                                        class="truncate cursor-pointer hover:bg-muted"
                                        @click="handleNewChat"
                                    >
                                        {{
                                            t('sidebar.content.button.new-chat')
                                        }}
                                    </button>
                                </SidebarMenuButton>
                            </SidebarMenuItem>
                        </SidebarMenu>
                    </SidebarGroupContent>
                </SidebarGroup>
            </nav>
        </SidebarContent>
        <Separator />

        <SidebarFooter>
            <SidebarMenu>
                <SidebarMenuItem>
                    <DropdownMenu>
                        <DropdownMenuTrigger as-child>
                            <SidebarMenuButton
                                size="lg"
                                class="data-[state=open]:bg-sidebar-accent data-[state=open]:text-sidebar-accent-foreground"
                            >
                            </SidebarMenuButton>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent
                            class="w-[--reka-dropdown-menu-trigger-width] min-w-56 rounded-lg"
                            :side="isMobile ? 'bottom' : 'right'"
                            align="end"
                            :side-offset="4"
                        >
                            <DropdownMenuItem
                                @click="logout"
                                class="text-destructive"
                            >
                                <LogOut class="text-destructive" />
                                Log out
                            </DropdownMenuItem>
                        </DropdownMenuContent>
                    </DropdownMenu>
                </SidebarMenuItem>
            </SidebarMenu>
        </SidebarFooter>

        <SidebarRail />
    </Sidebar>
</template>
