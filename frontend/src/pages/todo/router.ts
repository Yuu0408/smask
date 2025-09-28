import type { RouteRecordRaw } from 'vue-router';

const todoRoute: RouteRecordRaw[] = [
    {
        path: 'todo',
        name: 'todo',
        component: () => import('./TodoPage.vue'),
    },
];

export default todoRoute;
