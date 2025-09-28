import type { RouteRecordRaw } from 'vue-router';

const recordRoute: RouteRecordRaw[] = [
    {
        path: 'home',
        component: () => import('./HomePage.vue'),
    },
];

export default recordRoute;
