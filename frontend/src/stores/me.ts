import type { Me } from '@/types/me';
import { defineStore, storeToRefs } from 'pinia';
import { ref, watch } from 'vue';
import { useAzureStore } from './azure';

export const useMeStore = defineStore('me', () => {
    const me = ref<Me | null>(null);
    const azure = useAzureStore();
    const { currentActiveAccount } = storeToRefs(azure);

    const initializeFromAzure = () => {
        if (currentActiveAccount.value && !me.value) {
            me.value = {
                name:
                    currentActiveAccount.value.name ??
                    currentActiveAccount.value.username,
                email: currentActiveAccount.value.username,
                username: currentActiveAccount.value.username.split('@')[0],
            };
        }
    };

    watch(
        () => currentActiveAccount,
        (account) => {
            if (account.value) {
                me.value = {
                    name: account.value.name ?? account.value.username,
                    email: account.value.username,
                    username: account.value.username.split('@')[0],
                };
            } else if (me.value) {
                me.value = null;
            }
        }
    );
    return {
        me,
        initializeFromAzure,
    };
});
