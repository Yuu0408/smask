import type { RouteRecordRaw } from 'vue-router';

const historyRoute: RouteRecordRaw[] = [
    {
        path: 'history-list',
        name: 'history.history-list',
        component: () => import('./history-list/HistoryListPage.vue'),
    },
];

export default historyRoute;
