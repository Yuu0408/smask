import type { RouteRecordRaw } from 'vue-router';

const contactRoute: RouteRecordRaw[] = [
    {
        path: 'patients',
        name: 'contact.patients',
        component: () => import('./ContactPage.vue'),
    },
    {
        path: 'patients/:id',
        name: 'contact.detail',
        component: () => import('./PatientDetailPage.vue'),
    },
    {
        path: 'patients/:id/chat',
        name: 'contact.chat',
        component: () => import('./DirectChatPage.vue'),
    },
];

export default contactRoute;
