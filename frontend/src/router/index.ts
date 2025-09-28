import chatRoute from '@/pages/chat/router';
import contactRoute from '@/pages/contact/router';
import diagnosisRoute from '@/pages/diagnosis/router';
import historyRoute from '@/pages/history/router';

import {
    createRouter,
    createWebHistory,
    type RouteRecordRaw,
} from 'vue-router';
import { useAuthStore } from '@/stores/auth';

const routes: readonly RouteRecordRaw[] = [
    {
        path: '/login',
        name: 'login',
        component: () => import('@/pages/LoginPage.vue'),
    },
    {
        path: '/',
        name: 'home',
        component: () => import('@/layouts/RoleLayout.vue'),
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
                path: '/current-conversation',
                name: 'current-conversation',
                component: () =>
                    import(
                        '../pages/chat/conversation/CurrentConversationPage.vue'
                    ),
            },
            {
                path: '/record',
                name: 'record',
                component: () => import('../pages/record/RecordPage.vue'),
            },
            {
                path: '/home',
                name: 'home_page',
                component: () => import('../pages/home/HomePage.vue'),
            },
            {
                path: '/contact',
                name: 'contact',
                component: () => import('@/pages/contact/ContactLayout.vue'),
                children: contactRoute,
            },
            {
                path: '/todo',
                name: 'todo',
                component: () => import('@/pages/todo/TodoPage.vue'),
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
                component: () => import('@/pages/history/HistoryPage.vue'),
                children: historyRoute,
            },
        ],
    },
];

const router = createRouter({
    history: createWebHistory(import.meta.env.BASE_URL),
    routes: routes,
});

let initialized = false;

router.beforeEach(async (to) => {
    const auth = useAuthStore();

    if (!initialized) {
        initialized = true;
        try {
            await auth.refresh();
            await auth.getMe();
        } catch (e: unknown | null) {
            if (e && e instanceof Error) {
                console.log('No valid session');
            }
            // no valid session; proceed unauthenticated
        }
    }

    const isLogin = to.name === 'login';

    // Handle root path entry
    if (to.path === '/') {
        if (!auth.isAuthed) return { name: 'login' };
        // Doctors land on patients list; others to home page
        return auth.user?.role === 'doctor'
            ? { name: 'contact.patients' }
            : { name: 'home_page' };
    }

    // Redirect unauthenticated users away from protected routes
    if (!auth.isAuthed && !isLogin) {
        return { name: 'login', query: { redirect: to.fullPath } };
    }

    // Prevent navigating to login when already authenticated
    if (auth.isAuthed && isLogin) {
        return auth.user?.role === 'doctor'
            ? { name: 'contact.patients' }
            : { name: 'home_page' };
    }

    return true;
});

export default router;
