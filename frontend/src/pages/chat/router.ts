import type { RouteRecordRaw } from 'vue-router';

const chatRoute: RouteRecordRaw[] = [
    {
        path: 'new-chat',
        name: 'chat.new-chat',
        component: () => import('./conversation/ConversationPage.vue'),
    },
    {
        path: 'conversation',
        name: 'chat.conversation',
        component: () => import('./conversation/ConversationPage.vue'),
    },
    {
        path: 'current-conversation',
        name: 'chat.current-conversation',
        component: () => import('./conversation/CurrentConversationPage.vue'),
    },
];

export default chatRoute;
