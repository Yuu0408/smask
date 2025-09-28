import { defineStore } from 'pinia';
import $backend from '@/lib/backend';
import type {
    GetCurrentTodoRequest,
    GetCurrentTodoResponse,
    UpdateTodoItemRequest,
    UpdateTodoItemResponse,
} from '@/types/todo';

const URL_PREFIX = '/v1/todo';

export const useTodoStore = defineStore('todo', () => {
    async function getCurrentTodo(params: GetCurrentTodoRequest) {
        const { data } = await $backend.get<GetCurrentTodoResponse>(
            URL_PREFIX,
            {
                params,
            }
        );
        return data;
    }
    async function checkTodoItem(payload: UpdateTodoItemRequest) {
        const { data } = await $backend.patch<UpdateTodoItemResponse>(
            `${URL_PREFIX}/check`,
            payload
        );
        return data;
    }

    return { getCurrentTodo, checkTodoItem };
});
