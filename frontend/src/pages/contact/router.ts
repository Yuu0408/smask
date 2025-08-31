import type { RouteRecordRaw } from 'vue-router';

const contactRoute: RouteRecordRaw[] = [
    {
        path: 'contact',
        name: 'contact.contact',
        component: () => import('./ContactPage.vue'),
    },
];

export default contactRoute;
