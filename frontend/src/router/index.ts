import chatRoute from '@/pages/chat/router';
import contactRoute from '@/pages/contact/router';
import diagnosisRoute from '@/pages/diagnosis/router';
import historyRoute from '@/pages/history/router';

import {
    createRouter,
    createWebHistory,
    type RouteRecordRaw,
} from 'vue-router';

const routes: readonly RouteRecordRaw[] = [
    {
        path: '/login',
        name: 'login',
        component: () => import('@/pages/LoginPage.vue'),
    },
    {
        path: '/',
        name: 'home',
        component: () => import('@/layouts/AppLayout.vue'),
        children: [
            {
                path: '/chat',
                name: 'chat',
                component: () => import('@/pages/chat/ChatLayout.vue'),
                children: chatRoute,
            },
            {
                path: '/new-chat',
                name: 'new-chat',
                component: () =>
                    import('../pages/chat/conversation/ConversationPage.vue'),
            },
            {
                path: '/contact',
                name: 'contact',
                component: () => import('@/pages/contact/ContactLayout.vue'),
                children: contactRoute,
            },
            {
                path: '/diagnosis',
                name: 'diagnosis',
                component: () =>
                    import('@/pages/diagnosis/DiagnosisLayout.vue'),
                children: diagnosisRoute,
            },
            {
                path: '/history',
                name: 'history',
                component: () => import('@/pages/history/HistoryLayout.vue'),
                children: historyRoute,
            },
        ],
    },
];

const router = createRouter({
    history: createWebHistory(import.meta.env.BASE_URL),
    routes: routes,
});

export default router;
