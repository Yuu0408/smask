<script setup lang="ts">
import { Phone, MessageSquareDot, type LucideIcon } from 'lucide-vue-next';
import {
    SidebarGroup,
    SidebarMenu,
    SidebarMenuButton,
    SidebarMenuItem,
    SidebarGroupLabel,
} from '@/components/ui/sidebar';
import { useRouter } from 'vue-router';
import { useDialog } from '@/plugins/dialog-manager/use-dialog';
import MedicalRecordDialog from '@/pages/chat/medical-record/MedicalRecordDialog.vue';
import { useI18n } from 'vue-i18n';
import {
    MessageCirclePlus,
    BookText,
    ListTodo,
    History,
} from 'lucide-vue-next';
import Separator from '../ui/separator/Separator.vue';
import { onMounted, onUnmounted, ref } from 'vue';
import { useContactStore } from '@/stores/contact';
import { useAuthStore } from '@/stores/auth';
import { storeToRefs } from 'pinia';

const router = useRouter();
const { openDialog } = useDialog();
const { t } = useI18n();

const contactStore = useContactStore();
const { user } = storeToRefs(useAuthStore());
const myDoctors = ref<
    { doctor_id: string; contact_id: string; username: string }[]
>([]);
let _timer: number | null = null;

async function refreshDoctors() {
    if (!user.value?.id) return;
    try {
        const res = await contactStore.listMyDoctors(user.value.id);
        myDoctors.value = res.doctors || [];
    } catch {}
}

onMounted(async () => {
    await refreshDoctors();
    _timer = window.setInterval(refreshDoctors, 8000);
});

onUnmounted(() => {
    if (_timer) clearInterval(_timer);
});

type SidebarItemGroup = {
    title: string;
    url: string;
    type: 'group';
    icon?: LucideIcon;
    isActive?: boolean;
    items?: { title: string; url: string; isActive?: boolean }[];
};

type SidebarItemSingle = {
    title: string;
    url: string;
    type: 'single';
    icon?: LucideIcon;
    isActive?: boolean;
};
export type SidebarItem = SidebarItemGroup | SidebarItemSingle;

defineProps<{ items: SidebarItem[] }>();

const handleNewChat = async () => {
    openDialog({ component: MedicalRecordDialog });
};
const handleNewCall = async () => {
    openDialog({ component: MedicalRecordDialog, props: { mode: 'voice' } });
};
const handleRecord = async () => {
    await router.push({ name: 'record' });
};
const handleTodo = async () => {
    await router.push({ name: 'todo' });
};
const handleHistory = async () => {
    await router.push({ name: 'history' });
};
const handleCurrentConversation = async () => {
    await router.push({ name: 'current-conversation' });
};
</script>

<template>
    <SidebarGroup>
        <SidebarMenu>
            <!-- Flat, non-collapsible mainItems -->

            <SidebarMenuItem>
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
                        @click="handleNewCall"
                    >
                        <Phone />
                        <span>{{ t('sidebar.content.button.new-call') }}</span>
                        <!-- <Badge variant="outline" class="ml-2">{{ t('badge.beta') }}</Badge> -->
                    </button>
                </SidebarMenuButton>
            </SidebarMenuItem>
            <Separator />
            <SidebarGroupLabel>{{
                t('sidebar.content.label.conversations')
            }}</SidebarGroupLabel>
            <SidebarMenuItem>
                <SidebarMenuButton as-child>
                    <button
                        type="button"
                        class="truncate cursor-pointer hover:bg-muted"
                        @click="handleCurrentConversation"
                    >
                        <MessageSquareDot />
                        {{ t('sidebar.content.button.current-conversation') }}
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
            <Separator />
            <SidebarGroupLabel>{{
                t('sidebar.content.label.contacts')
            }}</SidebarGroupLabel>
            <SidebarMenuItem v-for="d in myDoctors" :key="d.contact_id">
                <SidebarMenuButton as-child>
                    <router-link
                        :to="{
                            name: 'contact.chat',
                            params: { id: d.contact_id },
                        }"
                    >
                        {{ d.username }}
                    </router-link>
                </SidebarMenuButton>
            </SidebarMenuItem>
        </SidebarMenu>
    </SidebarGroup>
</template>
