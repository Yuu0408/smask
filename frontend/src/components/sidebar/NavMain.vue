<script setup lang="ts">
import { ChevronRight, User, type LucideIcon } from 'lucide-vue-next';
import {
    Collapsible,
    CollapsibleContent,
    CollapsibleTrigger,
} from '@/components/ui/collapsible';
import {
    SidebarGroup,
    SidebarMenu,
    SidebarMenuButton,
    SidebarMenuItem,
    SidebarMenuSub,
    SidebarMenuSubButton,
    SidebarMenuSubItem,
    SidebarGroupContent,
    SidebarGroupLabel,
} from '@/components/ui/sidebar';
import { useRoute, useRouter } from 'vue-router';
import { computed } from 'vue';
import { cn } from '@/lib/utils';
import { useDialog } from '@/plugins/dialog-manager/use-dialog';
import MedicalRecordDialog from '@/pages/chat/medical-record/MedicalRecordDialog.vue';
import { useI18n } from 'vue-i18n';
import { Button } from '@/components/ui/button';
import {
    MessageCirclePlus,
    BookText,
    ListTodo,
    History,
} from 'lucide-vue-next';
const route = useRoute();
const router = useRouter();
const { openDialog } = useDialog();
const { t } = useI18n();

type SidebarItemGroup = {
    title: string;
    url: string;
    type: 'group';
    icon?: LucideIcon;
    isActive?: boolean;
    items?: {
        title: string;
        url: string;
        isActive?: boolean;
    }[];
};

type SidebarItemSingle = {
    title: string;
    url: string;
    type: 'single';
    icon?: LucideIcon;
    isActive?: boolean;
};

// const newChatItem: SidebarItemSingle = {
//     title: t('sidebar.main.new-chat'),
//     icon: User,
//     type: 'single',
//     url: '/new-chat',
//     isActive: route.path.startsWith('/new-chat'),
// };
export type SidebarItem = SidebarItemGroup | SidebarItemSingle;

defineProps<{
    items: SidebarItem[];
}>();

// function isActive(url: string) {
//     return computed(() => route.path.startsWith(url));
// }

const handleNewChat = async () => {
    openDialog({
        component: MedicalRecordDialog,
        // optional initial props
    });
};

const handleRecord = async () => {
    await router.push({
        name: 'record',
    });
};

const handleTodo = async () => {
    await router.push({
        name: 'todo',
    });
};

const handleHistory = async () => {
    await router.push({
        name: 'history',
    });
};
</script>

<template>
    <SidebarGroup>
        <SidebarMenu>
            <!-- Flat, non-collapsible mainItems -->

            <SidebarGroupLabel>{{
                t('sidebar.content.label.conversations')
            }}</SidebarGroupLabel
            ><SidebarMenuItem>
                <SidebarMenuButton as-child>
                    <button
                        type="button"
                        class="truncate cursor-pointer hover:bg-muted"
                        @click="handleNewChat"
                    >
                        <MessageCirclePlus />
                        <span>{{ t('sidebar.content.button.new-chat') }}</span>
                    </button>
                </SidebarMenuButton>
            </SidebarMenuItem>
            <SidebarMenuItem>
                <SidebarMenuButton as-child>
                    <button
                        type="button"
                        class="truncate cursor-pointer hover:bg-muted"
                        @click="handleRecord"
                    >
                        <BookText />
                        {{ t('sidebar.content.button.record') }}
                    </button>
                </SidebarMenuButton>
            </SidebarMenuItem>
            <SidebarMenuItem>
                <SidebarMenuButton as-child>
                    <button
                        type="button"
                        class="truncate cursor-pointer hover:bg-muted"
                        @click="handleTodo"
                    >
                        <ListTodo />
                        {{ t('sidebar.content.button.todo-list') }}
                    </button>
                </SidebarMenuButton>
            </SidebarMenuItem>
            <SidebarMenuItem>
                <SidebarMenuButton as-child>
                    <button
                        type="button"
                        class="truncate cursor-pointer hover:bg-muted"
                        @click="handleHistory"
                    >
                        <History />
                        {{ t('sidebar.content.button.history') }}
                    </button>
                </SidebarMenuButton>
            </SidebarMenuItem>
            <SidebarGroup>
                <SidebarGroupLabel>{{
                    t('sidebar.content.label.conversations')
                }}</SidebarGroupLabel>
                <SidebarGroupContent>
                    <SidebarMenu>
                        <SidebarMenuItem>
                            <SidebarMenuButton> Test </SidebarMenuButton>
                        </SidebarMenuItem>
                    </SidebarMenu>
                </SidebarGroupContent>
            </SidebarGroup>
        </SidebarMenu>
    </SidebarGroup>
</template>
