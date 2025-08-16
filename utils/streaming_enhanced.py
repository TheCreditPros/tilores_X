"""
Enhanced Streaming Utilities for Better User Experience
Intelligent chunking and error handling for streaming responses
"""

import asyncio
import json
import re
from datetime import datetime
from typing import AsyncGenerator


class EnhancedStreamingHandler:
    """Sophisticated streaming with sentence-aware chunking and error recovery"""

    def __init__(self, chunk_delay: float = 0.05):
        """
        Initialize enhanced streaming handler

        Args:
            chunk_delay: Delay between chunks in seconds (default 0.05)
        """
        self.chunk_delay = chunk_delay

    def chunk_by_sentences(self, content: str, target_chunks: int = 10) -> list:
        """
        Split content into chunks at sentence boundaries

        Args:
            content: Text to chunk
            target_chunks: Target number of chunks (will adjust for sentence boundaries)

        Returns:
            List of content chunks
        """
        # Split by sentence boundaries
        sentence_pattern = r"(?<=[.!?])\s+"
        sentences = re.split(sentence_pattern, content)

        if not sentences:
            return [content]

        # If we have fewer sentences than target chunks, return sentences
        if len(sentences) <= target_chunks:
            return sentences

        # Otherwise, group sentences into chunks
        sentences_per_chunk = max(1, len(sentences) // target_chunks)
        chunks = []

        for i in range(0, len(sentences), sentences_per_chunk):
            chunk = " ".join(sentences[i : i + sentences_per_chunk])
            if chunk:  # Don't add empty chunks
                chunks.append(chunk)

        return chunks

    async def generate_enhanced_stream(
        self, request_data: dict, content: str, include_usage: bool = True
    ) -> AsyncGenerator[str, None]:
        """
        Generate enhanced streaming response with better chunking and error handling

        Args:
            request_data: Original request data including model
            content: Response content to stream
            include_usage: Whether to include usage statistics

        Yields:
            SSE formatted chunks
        """
        try:
            # Generate metadata
            response_id = f"chatcmpl-{datetime.now().strftime('%Y%m%d%H%M%S')}"
            created = int(datetime.utcnow().timestamp())
            model = request_data.get("model", "gpt-4")

            # Send opening chunk with role
            opening_chunk = {
                "id": response_id,
                "object": "chat.completion.chunk",
                "created": created,
                "model": model,
                "system_fingerprint": f"fp_enhanced_{created % 1000000}",
                "choices": [{"index": 0, "delta": {"role": "assistant"}, "logprobs": None, "finish_reason": None}],
            }
            yield f"data: {json.dumps(opening_chunk)}\n\n"

            # Chunk content intelligently
            chunks = self.chunk_by_sentences(content, target_chunks=10)

            # Stream content chunks
            for i, chunk in enumerate(chunks):
                # Add space before non-first chunks if needed
                if i > 0 and not chunk.startswith(" "):
                    chunk = " " + chunk

                content_chunk = {
                    "id": response_id,
                    "object": "chat.completion.chunk",
                    "created": created,
                    "model": model,
                    "choices": [{"index": 0, "delta": {"content": chunk}, "logprobs": None, "finish_reason": None}],
                }

                yield f"data: {json.dumps(content_chunk)}\n\n"
                await asyncio.sleep(self.chunk_delay)

            # Calculate usage if requested
            if include_usage:
                # Simple token estimation (4 chars per token)
                prompt_text = str(request_data.get("messages", []))
                prompt_tokens = max(1, len(prompt_text) // 4)
                completion_tokens = max(1, len(content) // 4)

                # Send final chunk with usage
                final_chunk = {
                    "id": response_id,
                    "object": "chat.completion.chunk",
                    "created": created,
                    "model": model,
                    "choices": [{"index": 0, "delta": {}, "logprobs": None, "finish_reason": "stop"}],
                    "usage": {
                        "prompt_tokens": prompt_tokens,
                        "completion_tokens": completion_tokens,
                        "total_tokens": prompt_tokens + completion_tokens,
                    },
                }
            else:
                # Simple final chunk without usage
                final_chunk = {
                    "id": response_id,
                    "object": "chat.completion.chunk",
                    "created": created,
                    "model": model,
                    "choices": [{"index": 0, "delta": {}, "logprobs": None, "finish_reason": "stop"}],
                }

            yield f"data: {json.dumps(final_chunk)}\n\n"
            yield "data: [DONE]\n\n"

        except Exception as e:
            # Error recovery - send error in stream
            error_chunk = {
                "id": f"chatcmpl-error-{int(datetime.utcnow().timestamp())}",
                "object": "chat.completion.chunk",
                "created": int(datetime.utcnow().timestamp()),
                "model": request_data.get("model", "gpt-4"),
                "choices": [
                    {
                        "index": 0,
                        "delta": {"content": f"\n\n[Streaming error: {str(e)}]"},
                        "logprobs": None,
                        "finish_reason": "stop",
                    }
                ],
            }
            yield f"data: {json.dumps(error_chunk)}\n\n"
            yield "data: [DONE]\n\n"


# Global instance for convenience
enhanced_streamer = EnhancedStreamingHandler()
