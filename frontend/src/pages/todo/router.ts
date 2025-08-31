import type { RouteRecordRaw } from 'vue-router';

const historyRoute: RouteRecordRaw[] = [
    {
        path: 'todo-list',
        name: 'todo.todo-list',
        component: () => import('./TodoPage.vue'),
    },
];

export default historyRoute;
