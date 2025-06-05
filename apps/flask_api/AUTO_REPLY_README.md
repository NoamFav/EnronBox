# Ollama Auto-Reply Feature

This feature uses Ollama to generate automatic replies to emails. It integrates with the existing Flask API to provide a seamless experience.

## Prerequisites

1. **Ollama**: You need to have Ollama installed and running on your system.
   - Download from [Ollama's website](https://ollama.ai/)
   - Start the Ollama server: `ollama serve`

2. **Model**: You need to pull at least one model to use with Ollama.
   - Pull the default model: `ollama pull llama3`
   - Or any other model you prefer: `ollama pull mistral` or `ollama pull gemma`

3. **Flask API**: The Flask API needs to be running.
   - Run with Docker: `docker compose up --build`
   - Or natively: `./bin/flask-api.sh`

## API Usage

### Endpoint

```
POST /api/respond
```

### Request Body

```json
{
  "content": "Email content here",
  "subject": "Email subject (optional)",
  "sender": "Sender name (optional)",
  "model": "Ollama model to use (optional, default: llama3)",
  "temperature": 0.7 // Optional, controls randomness
}
```

### Response

```json
{
  "success": true,
  "reply": "Generated reply text",
  "metadata": {
    "model": "llama3",
    "total_duration": 1234,
    "load_duration": 123,
    "prompt_eval_count": 12,
    "eval_count": 123,
    "eval_duration": 1000
  }
}
```

## Testing the Feature

We've included a test script to help you try out the auto-reply feature:

```bash
# Run with default sample email
python apps/flask_api/test_auto_reply.py

# Try different sample emails (0, 1, or 2)
python apps/flask_api/test_auto_reply.py 1
```

## Integration with Frontend

To integrate with the frontend, send a POST request to the `/api/respond` endpoint with the email content and optional parameters. The API will return a generated reply that you can display or use in your application.

### Example JavaScript/TypeScript Integration

```typescript
async function generateAutoReply(emailContent: string, subject?: string) {
  const response = await fetch('http://localhost:5050/api/respond', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      content: emailContent,
      subject: subject,
      model: 'llama3',
      temperature: 0.7
    }),
  });
  
  const data = await response.json();
  
  if (data.success) {
    return data.reply;
  } else {
    throw new Error(data.error || 'Failed to generate reply');
  }
}
```

## Customization

### System Prompts

You can modify the system prompts in `app/services/responder.py` to customize the tone and style of the generated replies.

### Models

You can use any model available in Ollama. Just make sure to pull the model first:

```bash
ollama pull <model_name>
```

Then specify the model name in your API request.

### Performance Considerations

- Larger models will provide better quality replies but will be slower.
- First-time model loading may take longer; subsequent requests will be faster.
- If you're experiencing slow responses, consider using a smaller model or adjusting the temperature parameter.

## Troubleshooting

1. **Ollama not running**: Ensure Ollama is running with `ollama serve`
2. **Model not found**: Make sure you've pulled the model with `ollama pull <model_name>`
3. **API connection issues**: Check that the Flask API is running on port 5050
4. **Slow responses**: This is normal for the first request as the model loads into memory 