<script setup lang="ts">
import type { SidebarProps } from '@/components/ui/sidebar';

import { LogOut, UserRound, Settings } from 'lucide-vue-next';
import NavMain, { type SidebarItem } from '@/components/sidebar/NavMain.vue';

import {
    Sidebar,
    SidebarContent,
    SidebarFooter,
    SidebarRail,
    SidebarMenu,
    SidebarMenuButton,
    SidebarMenuItem,
} from '@/components/ui/sidebar';

import { MessageCirclePlus } from 'lucide-vue-next';

import { useRoute } from 'vue-router';
import { useI18n } from 'vue-i18n';
import {
    DropdownMenu,
    DropdownMenuTrigger,
    DropdownMenuContent,
    DropdownMenuLabel,
    DropdownMenuItem,
    DropdownMenuSeparator,
} from '@/components/ui/dropdown-menu';
import SidebarHeader from './ui/sidebar/SidebarHeader.vue';
import { Separator } from '@/components/ui/separator';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/auth';
import { computed } from 'vue';

// const store = useMeStore();
// // const azure = useAzureStore();
const router = useRouter();
const route = useRoute();
// const { me: user } = storeToRefs(store);

withDefaults(defineProps<SidebarProps>(), {
    collapsible: 'icon',
});

const { t, locale } = useI18n();

// Create computed navigation items with active state based on current route

const auth = useAuthStore();
const displayName = computed(
    () => auth.user?.username || t('sidebar.header.app.name')
);

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

function setLanguage(lang: 'en' | 'vi') {
    locale.value = lang;
    try {
        window.localStorage.setItem('locale', lang);
    } catch {}
}

const navMain = [
    {
        title: t('sidebar.main.conversation.button.new-chat'),
        icon: MessageCirclePlus,
        type: 'single',
        url: '/chat/new-chat',
        isActive: route.path.startsWith('/chat/new-chat'),
    },
] satisfies SidebarItem[];
</script>

<template>
    <Sidebar collapsible="icon">
        <SidebarHeader class="px-2 py-4">
            <div class="flex items-center gap-2 px-2">
                <UserRound />
                <span
                    class="font-semibold group-data-[collapsible=icon]:hidden"
                    >{{ displayName }}</span
                >
            </div>
        </SidebarHeader>

        <SidebarContent>
            <NavMain :items="navMain" />
        </SidebarContent>

        <Separator />

        <SidebarFooter>
            <SidebarMenu>
                <SidebarMenuItem>
                    <DropdownMenu>
                        <DropdownMenuTrigger as-child>
                            <SidebarMenuButton>
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
                                {{ t('navbar.language.en') }}
                            </DropdownMenuItem>
                            <DropdownMenuItem
                                :class="{ 'font-semibold': locale === 'vi' }"
                                @click="setLanguage('vi')"
                            >
                                {{ t('navbar.language.vi') }}
                            </DropdownMenuItem>
                        </DropdownMenuContent>
                    </DropdownMenu>
                </SidebarMenuItem>
                <SidebarMenuItem>
                    <SidebarMenuButton
                        class="text-destructive"
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
