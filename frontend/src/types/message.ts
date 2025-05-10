export interface Message {
    from: 'user' | 'bot'
    text: string
    isPlaceholder?: boolean
    multiple_choices?: string[]
  }
  