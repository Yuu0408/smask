export interface Message {
    from: 'ai' | 'human';
    text: string;
    isPlaceholder?: boolean;
    multiple_choices?: string[];
}
