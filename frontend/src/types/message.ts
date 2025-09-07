export interface Message {
    id: string;
    role: 'ai' | 'human';
    content: string;
    multiple_choices?: string[];
}
export interface Conversation {
    id: string;
    title: string;
    messages: Message[];
}
