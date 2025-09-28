export interface GetCurrentTodoRequest {
    user_id: string;
    record_id?: string;
}

export interface TodoItem {
    text: string;
    is_check: boolean;
}

export interface GetCurrentTodoResponse {
    user_id: string;
    record_id: string;
    items: TodoItem[];
}

export interface UpdateTodoItemRequest {
    user_id: string;
    record_id?: string;
    index: number;
    is_check: boolean;
}

export type UpdateTodoItemResponse = GetCurrentTodoResponse;
