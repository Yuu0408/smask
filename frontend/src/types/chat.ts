export interface sendChatMessageRequest {
    user_id: string;
    record_id: string;
    message: string;
}

export interface sendChatMessageResponse {
    message: string;
    multiple_choices?: string[];
    decision?: ChatStage;
    action?: 'NONE' | 'SEND_CONTACT';
    send_contact?: {
        include_conversation: boolean;
        address: string;
        facility: string;
    } | null;
    todos?: TodoItem[];
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

export type ChatStage =
    | 'FORM_CLARIFICATION'
    | 'BASIC_QUESTIONING'
    | 'REASONING'
    | 'RULE_OUT'
    | 'CLOSING'
    | 'NEXT_STEP'
    | 'LEGACY_DIAGNOSIS';

export interface TodoItem {
    text: string;
    is_check: boolean;
}
