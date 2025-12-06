<script setup lang="ts">
import type { SidebarProps } from '@/components/ui/sidebar';
import {
    Sidebar,
    SidebarHeader,
    SidebarContent,
    SidebarFooter,
    SidebarMenu,
    SidebarMenuItem,
    SidebarMenuButton,
    SidebarGroup,
    SidebarGroupLabel,
    SidebarRail,
} from '@/components/ui/sidebar';
import {
    LogOut,
    Users,
    MessageSquare,
    Stethoscope,
    UserRound,
} from 'lucide-vue-next';
import { Separator } from '@/components/ui/separator';
import { useRouter, useRoute } from 'vue-router';
import { useAuthStore } from '@/stores/auth';
import { useContactStore } from '@/stores/contact';
import { storeToRefs } from 'pinia';
import { onMounted, ref } from 'vue';
import { useI18n } from 'vue-i18n';
import { computed } from 'vue';
import {
    DropdownMenu,
    DropdownMenuContent,
    DropdownMenuItem,
    DropdownMenuLabel,
    DropdownMenuSeparator,
    DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { Languages, Settings } from 'lucide-vue-next';

withDefaults(defineProps<SidebarProps>(), {
    collapsible: 'icon',
});
const router = useRouter();
const auth = useAuthStore();
const contact = useContactStore();
const { user } = storeToRefs(auth);
const route = useRoute();

const patients = ref<{ contact_id: string; name: string }[]>([]);
const { t, locale } = useI18n();
const displayName = computed(
    () => user.value?.username || t('doctor.sidebar.header.title')
);
const doctorFacility = computed(
    () =>
        (user.value as any)?.metadata?.facility ||
        (user.value as any)?.user_metadata?.facility ||
        (user.value as any)?.facility ||
        ''
);
const doctorAddress = computed(
    () =>
        (user.value as any)?.metadata?.address ||
        (user.value as any)?.user_metadata?.address ||
        (user.value as any)?.address ||
        ''
);
const doctorLocation = computed(() => {
    const parts = [doctorAddress.value, doctorFacility.value].filter(
        (p) => p && String(p).trim() !== ''
    );
    return parts.join(', ');
});

onMounted(async () => {
    if (!user.value?.id) return;
    try {
        const res = await contact.listPatients(user.value.id);
        patients.value = (res.patients || []).map((p) => ({
            contact_id: p.contact_id,
            name: p.full_name,
        }));
        if (!doctorAddress.value && !doctorFacility.value) {
            await auth.getMe().catch(() => {});
        }
        console.log('Doctor metadata', {
            address: doctorAddress.value,
            facility: doctorFacility.value,
            metadata: (user.value as any)?.metadata,
        });
    } catch {}
});

async function handleLogout() {
    try {
        await auth.logout();
        await router.push({ name: 'login' });
    } catch (e) {
        console.error('Logout failed', e);
    }
}

const isActive = (path: string) =>
    route.path === path || route.path.startsWith(`${path}/`);

function setLanguage(lang: 'en' | 'vi') {
    locale.value = lang;
    try {
        window.localStorage.setItem('locale', lang);
    } catch {}
}
</script>

<template>
    <Sidebar collapsible="icon" class="bg-white/80 backdrop-blur-xl">
        <SidebarHeader class="px-3 py-4">
            <div class="flex items-center gap-3 px-1">
                <span
                    class="flex size-9 items-center justify-center rounded-2xl bg-primary/15 text-primary"
                    aria-hidden="true"
                >
                    <UserRound class="size-4" />
                </span>
                <div class="min-w-0 group-data-[collapsible=icon]:hidden">
                    <p class="truncate text-base font-semibold">
                        {{ displayName }}
                    </p>
                    <p class="text-xs text-muted-foreground flex items-center gap-1">
                        <Stethoscope class="size-3 text-primary" />
                        {{ doctorLocation }}
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
                        <Shield class="size-4" />
                    </div>
                    <p
                        class="text-[11px] font-semibold uppercase tracking-wide text-muted-foreground"
                    >
                        {{ t('doctor.sidebar.group.patients') }}
                    </p>
                    <p class="text-sm font-semibold text-foreground">
                        {{ patients.length }} {{ t('doctor.sidebar.allPatients') }}
                    </p>
                    <div class="mt-3 flex gap-2">
                        <button
                            type="button"
                            class="inline-flex items-center gap-2 rounded-xl bg-primary text-primary-foreground px-3 py-2 text-xs font-semibold shadow-sm transition hover:-translate-y-0.5 hover:shadow-md"
                            @click="router.push({ name: 'contact.patients' })"
                        >
                            <Users class="size-4" />
                            {{ t('doctor.sidebar.allPatients') }}
                        </button>
                    </div>
                </div>
            </div>

            <SidebarMenu>
                <SidebarGroup>
                    <SidebarGroupLabel
                        class="text-xs uppercase tracking-[0.18em] text-muted-foreground"
                    >{{ t('doctor.sidebar.group.patients') }}</SidebarGroupLabel>

                    <SidebarMenuItem
                        v-for="p in patients"
                        :key="p.contact_id"
                        class="rounded-xl transition hover:bg-primary/10"
                        :class="{
                            'bg-primary/10 border-primary/20':
                                route.params.id === p.contact_id,
                        }"
                    >
                        <SidebarMenuButton as-child class="rounded-xl">
                            <router-link
                                :to="{
                                    name: 'contact.detail',
                                    params: { id: p.contact_id },
                                }"
                                class="flex items-center gap-3"
                            >
                                <MessageSquare class="size-4" />
                                <span class="truncate">{{ p.name }}</span>
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
                        @click="handleLogout"
                        class="rounded-xl text-destructive hover:text-destructive"
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
