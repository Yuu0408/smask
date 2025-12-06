<script setup lang="ts">
import { computed, onMounted, ref, watch, onUnmounted } from 'vue';
import type { SidebarProps } from '@/components/ui/sidebar';
import {
    Sidebar,
    SidebarContent,
    SidebarFooter,
    SidebarRail,
    SidebarMenu,
    SidebarMenuButton,
    SidebarMenuItem,
    SidebarGroup,
    SidebarGroupLabel,
} from '@/components/ui/sidebar';
import { useRouter, useRoute } from 'vue-router';
import { useI18n } from 'vue-i18n';
import { useDialog } from '@/plugins/dialog-manager/use-dialog';
import MedicalRecordDialog from '@/pages/chat/medical-record/MedicalRecordDialog.vue';
import {
    Bot,
    ClipboardList,
    FileHeart,
    History,
    Home,
    Languages,
    LogOut,
    MessageCirclePlus,
    Mic2,
    Settings,
    Sparkles,
    Users2,
    ShieldCheck,
} from 'lucide-vue-next';
import SidebarHeader from './ui/sidebar/SidebarHeader.vue';
import { Separator } from '@/components/ui/separator';
import {
    DropdownMenu,
    DropdownMenuContent,
    DropdownMenuItem,
    DropdownMenuLabel,
    DropdownMenuSeparator,
    DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { useAuthStore } from '@/stores/auth';
import { storeToRefs } from 'pinia';
import { useHistoryStore } from '@/stores/history';

withDefaults(defineProps<SidebarProps>(), {
    collapsible: 'icon',
});

const router = useRouter();
const route = useRoute();
const { t, locale } = useI18n();
const { openDialog } = useDialog();
const auth = useAuthStore();
const { user } = storeToRefs(auth);
const activeTitle = ref<string>('');
const currentRecordId = computed(() => user.value?.currentRecordId || '');
const historyStore = useHistoryStore();

const navPrimary = computed(() => [
    {
        label: t('navbar.breadcrumb.home'),
        icon: Home,
        to: '/home',
        activeMatch: '/home',
    },
    {
        label: t('sidebar.workspace.continueChat'),
        icon: Bot,
        to: '/chat/conversation',
        activeMatch: '/chat',
    },
    {
        label: t('record.title'),
        icon: FileHeart,
        to: '/record',
        activeMatch: '/record',
    },
    {
        label: t('navbar.breadcrumb.todo'),
        icon: ClipboardList,
        to: '/todo',
        activeMatch: '/todo',
    },
    {
        label: t('navbar.breadcrumb.history'),
        icon: History,
        to: '/history',
        activeMatch: '/history',
    },
]);

const navSecondary = computed(() => [
    {
        label: t('navbar.breadcrumb.contact'),
        icon: Users2,
        to: '/contact/doctors',
        activeMatch: '/contact',
    },
]);

const displayName = computed(
    () => user.value?.username || t('sidebar.header.app.name')
);
const recordLabel = computed(
    () => user.value?.currentRecordId || t('medicalRecord.notAvailableShort')
);
const displayIntakeTitle = computed(
    () => activeTitle.value || recordLabel.value
);

async function handleLogout() {
    try {
        await auth.logout();
        await router.push({ name: 'login' });
    } catch (e) {
        console.error('Logout failed', e);
    }
}

function setLanguage(lang: 'en' | 'vi') {
    locale.value = lang;
    try {
        window.localStorage.setItem('locale', lang);
    } catch {}
}

function isActive(match: string) {
    return route.path.startsWith(match);
}

function handleNewChat(mode: 'text' | 'voice' = 'text') {
    openDialog({
        component: MedicalRecordDialog,
        props: { mode: mode === 'voice' ? 'voice' : undefined },
    });
}

async function refreshActiveTitle() {
    if (!user.value?.id) return;
    try {
        const res = await useHistoryStore().getAllChatHistory({
            user_id: user.value.id,
        });
        const histories = res.histories || [];
        const target =
            histories.find((h) => h.sessionId === currentRecordId.value) ||
            histories[0];
        activeTitle.value =
            target?.chiefComplaint ||
            target?.lastMessage ||
            t('history.noMessagesYet');
    } catch {
        activeTitle.value = t('history.noMessagesYet');
    }
}

onMounted(async () => {
    await refreshActiveTitle();
});

onUnmounted(() => {
});

watch(
    () => currentRecordId.value,
    async () => {
        await refreshActiveTitle();
    }
);
</script>

<template>
    <Sidebar collapsible="icon" class="bg-white/80 backdrop-blur-xl">
        <SidebarHeader class="px-3 py-4">
            <div class="flex items-center gap-3 px-1">
                <span
                    class="flex size-9 items-center justify-center rounded-2xl bg-primary/15 text-primary"
                    aria-hidden="true"
                >
                    <Sparkles class="size-4" />
                </span>
                <div class="min-w-0 group-data-[collapsible=icon]:hidden">
                    <p class="truncate text-base font-semibold">
                        {{ displayName }}
                    </p>
                </div>
            </div>
        </SidebarHeader>

        <SidebarContent>
            <div class="px-2 pb-2 group-data-[collapsible=icon]:hidden">
                <div
                    class="relative overflow-hidden rounded-2xl border border-primary/15 bg-gradient-to-br from-primary/10 via-white to-accent/10 p-3 shadow-sm"
                >
                    <div class="absolute right-3 top-3 text-primary/60">
                        <ShieldCheck class="size-4" />
                    </div>
                    <p
                        class="text-[11px] font-semibold uppercase tracking-wide text-muted-foreground"
                    >
                        {{ t('sidebar.activeIntake.title') }}
                    </p>
                    <p class="text-sm font-semibold text-foreground">
                        {{ displayIntakeTitle }}
                    </p>
                    <div class="mt-3 flex gap-2">
                        <button
                            type="button"
                            class="inline-flex items-center gap-2 rounded-xl bg-primary text-primary-foreground px-3 py-2 text-xs font-semibold shadow-sm transition hover:-translate-y-0.5 hover:shadow-md"
                            @click="router.push({ name: 'chat.conversation' })"
                        >
                            <Bot class="size-4" />
                            {{ t('sidebar.activeIntake.continue') }}
                        </button>
                        <button
                            type="button"
                            class="inline-flex items-center gap-2 rounded-xl border border-primary/30 bg-white/70 px-3 py-2 text-xs font-semibold text-foreground shadow-sm transition hover:-translate-y-0.5 hover:shadow-md"
                            @click="handleNewChat('text')"
                        >
                            <MessageCirclePlus class="size-4" />
                            {{ t('sidebar.content.button.new-chat') }}
                        </button>
                    </div>
                </div>
            </div>

            <SidebarMenu>
                <SidebarGroup>
                    <SidebarGroupLabel
                        class="text-xs uppercase tracking-[0.18em] text-muted-foreground"
                    >
                        {{ t('sidebar.group.workspace') }}
                    </SidebarGroupLabel>
                    <SidebarMenuItem
                        v-for="link in navPrimary"
                        :key="link.to"
                        :class="{
                            'bg-primary/10 border-primary/20': isActive(
                                link.activeMatch
                            ),
                        }"
                        class="rounded-xl transition hover:bg-primary/10"
                    >
                        <SidebarMenuButton as-child class="rounded-xl">
                            <router-link
                                :to="link.to"
                                class="flex items-center gap-3"
                            >
                                <component :is="link.icon" class="size-4" />
                                <span class="font-medium truncate">{{
                                    link.label
                                }}</span>
                            </router-link>
                        </SidebarMenuButton>
                    </SidebarMenuItem>
                </SidebarGroup>

                <Separator class="my-2" />

            <SidebarGroup>
                <SidebarGroupLabel
                    class="text-xs uppercase tracking-[0.18em] text-muted-foreground"
                >
                    {{ t('sidebar.group.followUp') }}
                </SidebarGroupLabel>
                <SidebarMenuItem
                    v-for="link in navSecondary"
                    :key="link.to"
                    :class="{
                        'bg-primary/10 border-primary/20': isActive(
                            link.activeMatch
                        ),
                    }"
                    class="rounded-xl transition hover:bg-primary/10"
                >
                    <SidebarMenuButton as-child class="rounded-xl">
                        <router-link
                            :to="link.to"
                            class="flex items-center gap-3"
                        >
                            <component :is="link.icon" class="size-4" />
                            <span class="font-medium truncate">{{
                                link.label
                            }}</span>
                        </router-link>
                    </SidebarMenuButton>
                </SidebarMenuItem>
            </SidebarGroup>

            </SidebarMenu>
        </SidebarContent>

        <Separator class="mt-2" />
        <SidebarFooter class="pt-2">
            <SidebarMenu>
                <SidebarMenuItem>
                    <DropdownMenu>
                        <DropdownMenuTrigger as-child>
                            <SidebarMenuButton class="rounded-xl">
                                <Settings class="size-4" />
                                <span>{{ t('navbar.settings') }}</span>
                            </SidebarMenuButton>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent align="end" class="min-w-56">
                            <DropdownMenuLabel>
                                {{
                                    t('navbar.language.label', {
                                        lang:
                                            locale === 'vi'
                                                ? t('navbar.language.vi')
                                                : t('navbar.language.en'),
                                    })
                                }}
                            </DropdownMenuLabel>
                            <DropdownMenuSeparator />
                            <DropdownMenuItem
                                :class="{ 'font-semibold': locale === 'en' }"
                                @click="setLanguage('en')"
                            >
                                <Languages class="mr-2 size-4" />
                                {{ t('navbar.language.en') }}
                            </DropdownMenuItem>
                            <DropdownMenuItem
                                :class="{ 'font-semibold': locale === 'vi' }"
                                @click="setLanguage('vi')"
                            >
                                <Languages class="mr-2 size-4" />
                                {{ t('navbar.language.vi') }}
                            </DropdownMenuItem>
                        </DropdownMenuContent>
                    </DropdownMenu>
                </SidebarMenuItem>
                <SidebarMenuItem>
                    <SidebarMenuButton
                        class="rounded-xl text-destructive hover:text-destructive"
                        @click="handleLogout"
                    >
                        <LogOut class="size-4" />
                        <span>{{ t('sidebar.footer.logout') }}</span>
                    </SidebarMenuButton>
                </SidebarMenuItem>
            </SidebarMenu>
        </SidebarFooter>

        <SidebarRail />
    </Sidebar>
</template>
