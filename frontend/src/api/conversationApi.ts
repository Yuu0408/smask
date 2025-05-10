export interface ConversationResponse {
    ai_response: string
    state: any,
    multiple_choices: string[],
  }

export interface ConversationRequest {
  session_id: string
  user_message: string
}
  
export async function sendMessageToServer(payload: ConversationRequest): Promise<ConversationResponse> {
  const response = await fetch('http://localhost:8000/conversation', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(payload)
  })

  if (!response.ok) {
    throw new Error('Failed to communicate with server')
  }

  return await response.json()
}
  