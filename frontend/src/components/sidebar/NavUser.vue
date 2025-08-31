<script setup lang="ts">
import { ChevronsUpDown } from 'lucide-vue-next';

import {
    DropdownMenu,
    DropdownMenuContent,
    // DropdownMenuItem,
    DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import {
    SidebarMenu,
    SidebarMenuButton,
    SidebarMenuItem,
    useSidebar,
} from '@/components/ui/sidebar';
// import { useMeStore } from '@/stores/me';
// import { storeToRefs } from 'pinia';
// import UserAvatar from '../common/UserAvatar.vue';
// import { useAzureStore } from '@/stores/azure';
import { useRouter } from 'vue-router';

// const store = useMeStore();
// const azure = useAzureStore();
// const router = useRouter();
// const { me: user } = storeToRefs(store);

// const logout = async () => {
//     try {
//         await azure.logout();
//         store.me = null;

//         await router.push({
//             name: 'login',
//         });
//     } catch (error) {
//         console.error('Logout error:', error);
//     }
// };

const { isMobile } = useSidebar();
</script>

<template>
    <SidebarMenu>
        <SidebarMenuItem>
            <DropdownMenu>
                <DropdownMenuTrigger as-child>
                    <SidebarMenuButton
                        size="lg"
                        class="data-[state=open]:bg-sidebar-accent data-[state=open]:text-sidebar-accent-foreground"
                    >
                        <!-- <UserAvatar :name="user.name" /> -->
                        <div
                            class="grid flex-1 text-left text-sm leading-tight"
                        >
                            <!-- <span class="truncate font-semibold">{{
                                user.name
                            }}</span>
                            <span class="truncate text-xs">{{
                                user.email
                            }}</span> -->
                        </div>
                        <ChevronsUpDown class="ml-auto size-4" />
                    </SidebarMenuButton>
                </DropdownMenuTrigger>
                <DropdownMenuContent
                    class="w-[--reka-dropdown-menu-trigger-width] min-w-56 rounded-lg"
                    :side="isMobile ? 'bottom' : 'right'"
                    :align="end"
                    :side-offset="4"
                >
                    <!-- <DropdownMenuItem @click="logout" class="text-destructive">
                        <LogOut class="text-destructive" />
                        Log out
                    </DropdownMenuItem> -->
                </DropdownMenuContent>
            </DropdownMenu>
        </SidebarMenuItem>
    </SidebarMenu>
</template>
