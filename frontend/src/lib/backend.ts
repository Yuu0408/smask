import axios from 'axios';
// import { useAzureStore } from '@/stores/azure';
import router from '@/router';

const $backend = axios.create({
    baseURL: import.meta.env.VITE_SERVER_BASE_URL || 'http://localhost:8080',
    headers: {
        'Content-Type': 'application/json',
    },
});

// $backend.interceptors.request.use(async (config) => {
//     const store = useAzureStore();
//     const token = await store.getUserAccessToken();

//     if (token) {
//         config.headers.Authorization = `Bearer ${token}`;
//     }
//     return config;
// });

// Add a response interceptor to handle 401 Unauthorized errors
// $backend.interceptors.response.use(
//     (response) => response,
//     async (error) => {
//         // Handle 401 responses - token expired or invalid
//         if (error.response && error.response.status === 401) {
//             // const store = useAzureStore();

//             try {
//                 // Try to get a fresh token
//                 const token = await store.getUserAccessToken();

//                 if (token) {
//                     // Token refreshed successfully, retry the request
//                     error.config.headers.Authorization = `Bearer ${token}`;
//                     return axios(error.config);
//                 } else {
//                     // Couldn't get a new token, user needs to log in again
//                     store.invalidateAccount();
//                     router.push({ name: 'login' });
//                 }
//             } catch {
//                 // Error refreshing token, redirect to login
//                 store.invalidateAccount();
//                 router.push({ name: 'login' });
//             }
//         }

//         return Promise.reject(error);
//     }
// );

export default $backend;
