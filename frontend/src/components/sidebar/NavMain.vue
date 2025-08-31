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
} from '@/components/ui/sidebar';
import { useRoute } from 'vue-router';
import { computed } from 'vue';
import { cn } from '@/lib/utils';
import { useDialog } from '@/plugins/dialog-manager/use-dialog';
import MedicalRecordDialog from '@/pages/chat/medical-record/MedicalRecordDialog.vue';
import { useI18n } from 'vue-i18n';
import { Button } from '@/components/ui/button';
import { MessageCirclePlus } from 'lucide-vue-next';
const route = useRoute();
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

const newChatItem: SidebarItemSingle = {
    title: t('sidebar.main.new-chat'),
    icon: User,
    type: 'single',
    url: '/new-chat',
    isActive: route.path.startsWith('/new-chat'),
};
export type SidebarItem = SidebarItemGroup | SidebarItemSingle;

defineProps<{
    items: SidebarItem[];
    mainItems: SidebarItem[];
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
</script>

<template>
    <SidebarGroup>
        <SidebarMenu>
            <!-- Flat, non-collapsible mainItems -->
            <SidebarMenuItem
                :tooltip="newChatItem.title"
                :class="
                    cn(
                        'transition-colors overflow-hidden',
                        'hover:bg-sidebar-accent hover:text-sidebar-accent-foreground'
                    )
                "
            >
                <SidebarMenuButton
                    @click="handleNewChat"
                    class="cursor-pointer"
                >
                    <MessageCirclePlus />
                    <span>New chat</span>
                </SidebarMenuButton>
            </SidebarMenuItem>
            <!-- <SidebarMenuItem
                :tooltip="newChatItem.title"
                :class="
                    cn(
                        'transition-colors overflow-hidden',
                        'hover:bg-sidebar-accent hover:text-sidebar-accent-foreground'
                    )
                "
            >
                <SidebarMenuButton>
                    <RouterLink
                        :to="newChatItem.url"
                        :class="
                            cn(
                                'p-2 flex w-full items-center gap-2 text-left h-8 text-sm rounded-md',
                                '[&>svg]:size-4 [&>svg]:shrink-0',
                                isActive(newChatItem.url).value
                                    ? 'text-primary font-medium'
                                    : 'text-muted-foreground'
                            )
                        "
                    >
                        <component
                            :is="newChatItem.icon"
                            v-if="newChatItem.icon"
                        />
                        <span>{{ newChatItem.title }}</span>
                    </RouterLink>
                </SidebarMenuButton>
            </SidebarMenuItem> -->

            <!-- <template v-for="item in mainItems" :key="'main-' + item.title">
                
                <SidebarMenuItem
                    v-if="item.type === 'single'"
                    :tooltip="item.title"
                    :class="
                        cn(
                            'transition-colors overflow-hidden',
                            'hover:bg-sidebar-accent hover:text-sidebar-accent-foreground'
                        )
                    "
                >
                    <SidebarMenuButton as-child>
                        <RouterLink
                            :to="item.url"
                            :class="
                                cn(
                                    'p-2 flex w-full items-center gap-2 text-left h-8 text-sm rounded-md',
                                    '[&>svg]:size-4 [&>svg]:shrink-0',
                                    isActive(item.url).value
                                        ? 'text-primary font-medium'
                                        : 'text-muted-foreground'
                                )
                            "
                        >
                            <component :is="item.icon" v-if="item.icon" />
                            <span>{{ item.title }}</span>
                        </RouterLink>
                    </SidebarMenuButton>
                </SidebarMenuItem>

                <template v-else>
  
                    <SidebarMenuItem
                        :class="
                            cn(
                                'px-2 py-1 text-xs font-medium text-muted-foreground',
                                'mt-2'
                            )
                        "
                    >
                        <div class="truncate">{{ item.title }}</div>
                    </SidebarMenuItem>

                    <SidebarMenuItem
                        v-for="sub in item.items"
                        :key="'main-sub-' + item.title + '-' + sub.title"
                        :tooltip="sub.title"
                        :class="
                            cn(
                                'transition-colors overflow-hidden',
                                'hover:bg-sidebar-accent hover:text-sidebar-accent-foreground'
                            )
                        "
                    >
                        <SidebarMenuButton as-child>
                            <RouterLink
                                :to="sub.url"
                                :class="
                                    cn(
                                        'p-2 pl-7 flex w-full items-center gap-2 text-left h-8 text-sm rounded-md',
                                        isActive(sub.url).value
                                            ? 'text-primary font-medium'
                                            : 'text-muted-foreground'
                                    )
                                "
                            >
                                <span class="truncate">{{ sub.title }}</span>
                            </RouterLink>
                        </SidebarMenuButton>
                    </SidebarMenuItem>
                </template>
            </template>

            <template v-for="item in items">
                <Collapsible
                    v-if="item.type === 'group'"
                    :key="'group' + item.title"
                    as-child
                    :default-open="item.isActive"
                    class="group/collapsible"
                >
                    <SidebarMenuItem>
                        <CollapsibleTrigger as-child>
                            <SidebarMenuButton :tooltip="item.title">
                                <component :is="item.icon" v-if="item.icon" />
                                <span>{{ item.title }}</span>
                                <ChevronRight
                                    class="ml-auto transition-transform duration-200 group-data-[state=open]/collapsible:rotate-90"
                                />
                            </SidebarMenuButton>
                        </CollapsibleTrigger>
                        <CollapsibleContent>
                            <SidebarMenuSub>
                                <SidebarMenuSubItem
                                    v-for="subItem in item.items"
                                    :key="subItem.title"
                                >
                                    <SidebarMenuSubButton
                                        as-child
                                        :href="subItem.url"
                                        :class="
                                            cn(
                                                'transition-colors hover:text-primary',
                                                isActive(subItem.url).value
                                                    ? 'text-primary font-medium'
                                                    : 'text-muted-foreground'
                                            )
                                        "
                                    >
                                        <a :href="subItem.url">
                                            <span>{{ subItem.title }}</span>
                                        </a>
                                    </SidebarMenuSubButton>
                                </SidebarMenuSubItem>
                            </SidebarMenuSub>
                        </CollapsibleContent>
                    </SidebarMenuItem>
                </Collapsible>
                <SidebarMenuItem
                    v-else
                    :key="'single' + item.title"
                    :tooltip="item.title"
                    :class="
                        cn(
                            'transition-colors overflow-hidden',
                            'hover:bg-sidebar-accent hover:text-sidebar-accent-foreground'
                        )
                    "
                >
                    <a
                        :href="item.url"
                        :class="
                            cn(
                                'p-2 flex w-full items-center gap-2 text-left h-8 text-sm rounded-md',
                                '[&>svg]:size-4 [&>svg]:shrink-0',
                                isActive(item.url)
                                    ? 'text-primary font-medium'
                                    : 'text-muted-foreground'
                            )
                        "
                    >
                        <component :is="item.icon" v-if="item.icon" />

                        <span>{{ item.title }}</span>
                    </a>
                </SidebarMenuItem>
            </template> -->
        </SidebarMenu>
    </SidebarGroup>
</template>
