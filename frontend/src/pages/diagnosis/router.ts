import type { RouteRecordRaw } from 'vue-router';

const diagnosisRoute: RouteRecordRaw[] = [
    {
        path: 'record',
        name: 'diagnosis.record',
        component: () => import('./record/RecordDetailPage.vue'),
    },
];

export default diagnosisRoute;
