// src/stores/auth.ts
import { ref, computed } from 'vue';
import { defineStore } from 'pinia';
import type { User } from '@/types/user'; // define your own type
import $backend from '@/lib/backend';

const URL_PREFIX = '/auth';
export const useAuthStore = defineStore('auth', () => {
    const user = ref<User | null>(null);
    const accessToken = ref<string | null>(null);
    const status = ref<'idle' | 'authenticating' | 'authenticated' | 'error'>(
        'idle'
    );

    const isAuthed = computed(() => !!user.value && !!accessToken.value);

    async function login(username: string, password: string) {
        status.value = 'authenticating';
        try {
            const { data } = await $backend.post(
                `${URL_PREFIX}/login`,
                { username, password },
                { withCredentials: true }
            );
            accessToken.value = data.accessToken;
            user.value = data.user;
            status.value = 'authenticated';
        } catch (e) {
            logout();
            status.value = 'error';
            throw e;
        }
    }

    async function refresh() {
        const { data } = await $backend.post(`${URL_PREFIX}/refresh`, null, {
            withCredentials: true,
        });
        accessToken.value = data.accessToken;
        user.value = data.user;
    }

    async function getMe() {
        const { data } = await $backend.get('/me');
        user.value = data;
    }

    async function register(username: string, password: string) {
        const { data } = await $backend.post(
            `${URL_PREFIX}/register`,
            { username, password },
            { withCredentials: true }
        );
        accessToken.value = data.accessToken;
        user.value = data.user;
        status.value = 'authenticated';
    }

    async function logout() {
        try {
            await $backend.post(`${URL_PREFIX}/logout`, null, {
                withCredentials: true,
            });
        } finally {
            user.value = null;
            accessToken.value = null;
            status.value = 'idle';
        }
    }

    return {
        user,
        accessToken,
        status,
        isAuthed,
        login,
        refresh,
        getMe,
        logout,
        register,
    };
});
