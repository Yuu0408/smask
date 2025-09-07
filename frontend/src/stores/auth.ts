// src/stores/auth.ts
import { ref, computed } from 'vue';
import { defineStore } from 'pinia';
import axios from 'axios';

import type { User } from '@/types/user'; // define your own type

export const useAuthStore = defineStore('auth', () => {
    const user = ref<User | null>(null);
    const accessToken = ref<string | null>(null);
    const status = ref<'idle' | 'authenticating' | 'authenticated' | 'error'>(
        'idle'
    );

    const isAuthed = computed(() => !!user.value && !!accessToken.value);

    async function login(email: string, password: string) {
        status.value = 'authenticating';
        try {
            const { data } = await axios.post(
                '/auth/login',
                { email, password },
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
        const { data } = await axios.post('/auth/refresh', null, {
            withCredentials: true,
        });
        accessToken.value = data.accessToken;
        user.value = data.user;
    }

    async function getMe() {
        const { data } = await axios.get('/me');
        user.value = data;
    }

    async function logout() {
        try {
            await axios.post('/auth/logout', null, { withCredentials: true });
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
    };
});
