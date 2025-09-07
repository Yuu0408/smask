import { inject } from 'vue';

type DialogOptions = {
    component: any;
    props?: Record<string, any>;
    title?: string;
    description?: string;
};

export function useDialog() {
    const openDialog = inject('openDialog') as (options: DialogOptions) => void;
    const closeDialog = inject('closeDialog') as (
        dialogId?: string,
        result?: any
    ) => void;
    const closeLatestDialog = inject('closeLatestDialog') as (
        result?: any
    ) => void;
    const closeAllDialogs = inject('closeAllDialogs') as () => void;

    if (!openDialog || !closeDialog || !closeAllDialogs || !closeLatestDialog) {
        throw new Error(
            'Dialog provider not found. Make sure to use DialogManager in your app.'
        );
    }

    return {
        openDialog,
        closeDialog,
        closeAllDialogs,
        closeLatestDialog,
    };
}
