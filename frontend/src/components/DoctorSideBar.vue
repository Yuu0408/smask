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
import { LogOut, Users, MessageSquare, Stethoscope } from 'lucide-vue-next';
import { Separator } from '@/components/ui/separator';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/auth';
import { useContactStore } from '@/stores/contact';
import { storeToRefs } from 'pinia';
import { onMounted, ref } from 'vue';
import { useI18n } from 'vue-i18n';

withDefaults(defineProps<SidebarProps>(), {
    collapsible: 'icon',
});
const router = useRouter();
const auth = useAuthStore();
const contact = useContactStore();
const { user } = storeToRefs(auth);

const patients = ref<{ contact_id: string; name: string }[]>([]);
const { t } = useI18n();

onMounted(async () => {
    if (!user.value?.id) return;
    try {
        const res = await contact.listPatients(user.value.id);
        patients.value = (res.patients || []).map((p) => ({
            contact_id: p.contact_id,
            name: p.full_name,
        }));
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
</script>

<template>
    <Sidebar collapsible="icon">
        <SidebarHeader class="px-3 py-3">
            <div class="flex items-center gap-2 text-sm font-medium">
                <Stethoscope class="size-4" />
                <span class="group-data-[collapsible=icon]:hidden">{{
                    t('doctor.sidebar.header.title')
                }}</span>
            </div>
            <div
                class="mt-1 text-xs text-muted-foreground truncate group-data-[collapsible=icon]:hidden"
            >
                {{ user?.username }}
            </div>
        </SidebarHeader>

        <Separator />

        <SidebarContent>
            <SidebarGroup>
                <SidebarGroupLabel>{{
                    t('doctor.sidebar.group.patients')
                }}</SidebarGroupLabel>
                <SidebarMenu>
                    <SidebarMenuItem>
                        <SidebarMenuButton as-child>
                            <router-link :to="{ name: 'contact.patients' }">
                                <Users class="size-4" />
                                <span>{{
                                    t('doctor.sidebar.allPatients')
                                }}</span>
                            </router-link>
                        </SidebarMenuButton>
                    </SidebarMenuItem>
                    <SidebarMenuItem v-for="p in patients" :key="p.contact_id">
                        <SidebarMenuButton as-child>
                            <router-link
                                :to="{
                                    name: 'contact.detail',
                                    params: { id: p.contact_id },
                                }"
                            >
                                <MessageSquare class="size-4" />
                                <span class="truncate">{{ p.name }}</span>
                            </router-link>
                        </SidebarMenuButton>
                    </SidebarMenuItem>
                </SidebarMenu>
            </SidebarGroup>
        </SidebarContent>

        <Separator />

        <SidebarFooter>
            <SidebarMenu>
                <SidebarMenuItem>
                    <SidebarMenuButton
                        @click="handleLogout"
                        class="text-destructive"
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
