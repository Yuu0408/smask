import type { RouteRecordRaw } from 'vue-router';

const recordRoute: RouteRecordRaw[] = [
    {
        path: 'record',
        component: () => import('./RecordPage.vue'),
    },
];

export default recordRoute;
