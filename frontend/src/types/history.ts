export interface ChatHistoryPreview {
    sessionId: string;
    // Last activity time for the conversation (ISO string from backend)
    updatedAt: string;
    // First 100 chars of the last message in the conversation
    lastMessage: string;
    // Chief complaint extracted from the medical record for this session
    chiefComplaint?: string;
}

export interface GetAllChatHistoryRequest {
    user_id: string;
}

export interface GetAllChatHistoryResponse {
    histories: ChatHistoryPreview[];
}
