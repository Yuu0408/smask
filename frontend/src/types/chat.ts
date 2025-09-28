export interface sendChatMessageRequest {
    user_id: string;
    record_id: string;
    message: string;
}

export interface sendChatMessageResponse {
    message: string;
    multiple_choices?: string[];
    decision?: string;
}

export interface getChatHistoryRequest {
    user_id: string;
    record_id: string;
}

export interface ChatMessage {
    id: string;
    role: 'ai' | 'human';
    content: string;
    created_at: string;
}

export interface GetChatHistoryResponse {
    history: ChatMessage[];
}
