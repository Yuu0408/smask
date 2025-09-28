// src/stores/auth.ts
import { ref, computed } from 'vue';
import { defineStore } from 'pinia';
import type { User } from '@/types/user'; // define your own type
import $backend from '@/lib/backend';
import type { loginRequest, registerRequest } from '@/types/auth';

const URL_PREFIX = '/auth';
export const useAuthStore = defineStore('auth', () => {
    const user = ref<User | null>(null);
    const accessToken = ref<string | null>(null);
    const status = ref<'idle' | 'authenticating' | 'authenticated' | 'error'>(
        'idle'
    );

    const isAuthed = computed(() => !!user.value && !!accessToken.value);

    async function login(payload: loginRequest) {
        status.value = 'authenticating';
        const username = payload.username;
        const password = payload.password;
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
        if (!accessToken.value) throw new Error('No access token');
        const { data } = await $backend.get(`${URL_PREFIX}/me`, {
            headers: {
                Authorization: `Bearer ${accessToken.value}`,
            },
        });
        if (user.value) {
            user.value.id = data.id;
            user.value.currentRecordId = data.record_id;
            user.value.username = data.username;
            user.value.is_active = data.is_active;
            user.value.role = data.role;
        }
    }

    async function register(payload: registerRequest) {
        const username = payload.username;
        const password = payload.password;
        const role = payload.role;
        const metadata = payload.metadata ?? {};
        const { data } = await $backend.post(
            `${URL_PREFIX}/register`,
            { username, password, role, metadata },
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
