# Copyright (C) 2025 AIDC-AI
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#     http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
LLM (Large Language Model) Service - Triển khai trực tiếp bằng OpenAI SDK

Hỗ trợ structured output thông qua tham số response_type (model Pydantic).
"""

import json
import re
from typing import Optional, Type, TypeVar, Union

from openai import AsyncOpenAI
from pydantic import BaseModel
from loguru import logger


T = TypeVar("T", bound=BaseModel)


class LLMService:
    """
    Service LLM (Large Language Model)

    Triển khai trực tiếp bằng OpenAI SDK. Không cần lớp capability.

    Hỗ trợ tất cả các nhà cung cấp tương thích OpenAI SDK:
    - OpenAI (gpt-4o, gpt-4o-mini, gpt-3.5-turbo)
    - Alibaba Qwen (qwen-max, qwen-plus, qwen-turbo)
    - Anthropic Claude (claude-sonnet-4-5, claude-opus-4, claude-haiku-4)
    - DeepSeek (deepseek-chat)
    - Moonshot Kimi (moonshot-v1-8k, moonshot-v1-32k, moonshot-v1-128k)
    - Ollama (llama3.2, qwen2.5, mistral, codellama) - MIỄN PHÍ & LOCAL!
    - Bất kỳ provider tùy chỉnh nào có API tương thích OpenAI

    Cách dùng:
        # Gọi trực tiếp
        answer = await pixelle_video.llm("Giải thích về atomic habits")

        # Có tham số
        answer = await pixelle_video.llm(
            prompt="Giải thích atomic habits trong 3 câu",
            temperature=0.7,
            max_tokens=2000
        )
    """
    
    def __init__(self, config: dict):
        """
        Khởi tạo service LLM

        Args:
            config: Dict cấu hình đầy đủ của ứng dụng (giữ lại để tương thích ngược)
        """
        # Lưu ý: Không cache config ở đây nữa để hỗ trợ hot reload
        # Config được đọc động từ config_manager trong _get_config_value()
        self._client: Optional[AsyncOpenAI] = None

    def _get_config_value(self, key: str, default=None):
        """
        Lấy giá trị config động từ config_manager (hỗ trợ hot reload)

        Args:
            key: Tên key config
            default: Giá trị mặc định nếu không tìm thấy

        Returns:
            Giá trị config
        """
        from pixelle_video.config import config_manager
        return getattr(config_manager.config.llm, key, default)
    
    def _create_client(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
    ) -> AsyncOpenAI:
        """
        Tạo client OpenAI

        Args:
            api_key: API Key (tùy chọn, dùng config nếu không truyền)
            base_url: Base URL (tùy chọn, dùng config nếu không truyền)

        Returns:
            Instance AsyncOpenAI client
        """
        # Lấy API Key (ưu tiên: tham số > config)
        final_api_key = (
            api_key
            or self._get_config_value("api_key")
            or "dummy-key"  # Ollama không cần key thật
        )

        # Lấy base URL (ưu tiên: tham số > config)
        final_base_url = (
            base_url
            or self._get_config_value("base_url")
        )

        # Tạo client
        client_kwargs = {"api_key": final_api_key}
        if final_base_url:
            client_kwargs["base_url"] = final_base_url

        return AsyncOpenAI(**client_kwargs)
    
    async def __call__(
        self,
        prompt: str,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        response_type: Optional[Type[T]] = None,
        **kwargs
    ) -> Union[str, T]:
        """
        Sinh văn bản bằng LLM

        Args:
            prompt: Prompt để sinh văn bản
            api_key: API Key (tùy chọn, dùng config nếu không truyền)
            base_url: Base URL (tùy chọn, dùng config nếu không truyền)
            model: Tên model (tùy chọn, dùng config nếu không truyền)
            temperature: Nhiệt độ sampling (0.0-2.0). Thấp hơn = tất định hơn.
            max_tokens: Số token tối đa được sinh
            response_type: Lớp Pydantic model tùy chọn cho structured output.
                          Nếu được cung cấp, trả về instance model đã parse thay vì chuỗi.
            **kwargs: Tham số bổ sung tùy theo provider

        Returns:
            Văn bản đã sinh (str) hoặc instance Pydantic model đã parse (nếu có response_type)

        Ví dụ:
            # Sinh văn bản cơ bản
            answer = await pixelle_video.llm("Giải thích atomic habits")

            # Structured output với Pydantic model
            class MovieReview(BaseModel):
                title: str
                rating: int
                summary: str

            review = await pixelle_video.llm(
                prompt="Đánh giá phim Inception",
                response_type=MovieReview
            )
            print(review.title)  # Truy cập có cấu trúc
        """
        # Tạo client (instance mới mỗi lần để hỗ trợ ghi đè tham số)
        client = self._create_client(api_key=api_key, base_url=base_url)

        # Lấy model (ưu tiên: tham số > config)
        final_model = (
            model
            or self._get_config_value("model")
            or "gpt-3.5-turbo"  # Mặc định dự phòng
        )

        logger.debug(f"Gọi LLM: model={final_model}, base_url={client.base_url}, response_type={response_type}")

        try:
            if response_type is not None:
                # Chế độ structured output - thử beta.chat.completions.parse trước
                return await self._call_with_structured_output(
                    client=client,
                    model=final_model,
                    prompt=prompt,
                    response_type=response_type,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    **kwargs
                )
            else:
                # Chế độ output văn bản thông thường
                response = await client.chat.completions.create(
                    model=final_model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=temperature,
                    max_tokens=max_tokens,
                    **kwargs
                )

                result = response.choices[0].message.content
                logger.debug(f"Độ dài phản hồi LLM: {len(result)} ký tự")

                return result

        except Exception as e:
            logger.error(f"Lỗi khi gọi LLM (model={final_model}, base_url={client.base_url}): {e}")
            raise
    
    async def _call_with_structured_output(
        self,
        client: AsyncOpenAI,
        model: str,
        prompt: str,
        response_type: Type[T],
        temperature: float,
        max_tokens: int,
        **kwargs
    ) -> T:
        """
        Gọi LLM với hỗ trợ structured output

        Sử dụng cách nhồi chỉ thị JSON schema vào cuối prompt để tương thích tối đa
        với tất cả các provider tương thích OpenAI (Qwen, DeepSeek, v.v.).

        Args:
            client: Client OpenAI
            model: Tên model
            prompt: Prompt
            response_type: Lớp Pydantic model
            temperature: Nhiệt độ sampling
            max_tokens: Số token tối đa
            **kwargs: Tham số bổ sung

        Returns:
            Instance Pydantic model đã parse
        """
        # Xây dựng chỉ thị JSON schema và nối vào cuối prompt
        json_schema_instruction = self._get_json_schema_instruction(response_type)
        enhanced_prompt = f"{prompt}\n\n{json_schema_instruction}"

        # Gọi LLM với prompt đã được tăng cường
        response = await client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": enhanced_prompt}],
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )
        content = response.choices[0].message.content

        logger.debug(f"Độ dài phản hồi structured output: {len(content)} ký tự")

        # Parse JSON từ nội dung phản hồi
        return self._parse_response_as_model(content, response_type)
    
    def _get_json_schema_instruction(self, response_type: Type[T]) -> str:
        """
        Sinh chỉ thị JSON schema cho chế độ fallback của LLM

        Args:
            response_type: Lớp Pydantic model

        Returns:
            Chuỗi chỉ thị đã định dạng kèm JSON schema
        """
        try:
            # Lấy JSON schema từ Pydantic model
            schema = response_type.model_json_schema()
            schema_str = json.dumps(schema, indent=2, ensure_ascii=False)

            return f"""## QUAN TRỌNG: Bắt buộc định dạng output JSON
Bạn PHẢI phản hồi CHỈ bằng một đối tượng JSON hợp lệ (không markdown, không có văn bản thừa).
JSON phải tuân thủ NGHIÊM NGẶT schema sau:

```json
{schema_str}
```

Chỉ xuất ra đối tượng JSON, không gì khác. Mọi nội dung văn bản tự nhiên phải bằng tiếng Việt."""
        except Exception as e:
            logger.warning(f"Không sinh được JSON schema: {e}")
            return """## QUAN TRỌNG: Bắt buộc định dạng output JSON
Bạn PHẢI phản hồi CHỈ bằng một đối tượng JSON hợp lệ (không markdown, không có văn bản thừa). Mọi nội dung văn bản tự nhiên phải bằng tiếng Việt."""
    
    def _parse_response_as_model(self, content: str, response_type: Type[T]) -> T:
        """
        Parse nội dung phản hồi LLM thành Pydantic model

        Args:
            content: Văn bản phản hồi LLM thô
            response_type: Lớp Pydantic model đích

        Returns:
            Instance model đã parse
        """
        # Thử parse JSON trực tiếp trước
        try:
            data = json.loads(content)
            return response_type.model_validate(data)
        except json.JSONDecodeError:
            pass

        # Thử trích xuất từ khối code markdown
        json_pattern = r'```(?:json)?\s*([\s\S]+?)\s*```'
        match = re.search(json_pattern, content, re.DOTALL)
        if match:
            try:
                data = json.loads(match.group(1))
                return response_type.model_validate(data)
            except json.JSONDecodeError:
                pass

        # Thử tìm bất kỳ đối tượng JSON nào trong văn bản
        brace_start = content.find('{')
        brace_end = content.rfind('}')
        if brace_start != -1 and brace_end > brace_start:
            try:
                json_str = content[brace_start:brace_end + 1]
                data = json.loads(json_str)
                return response_type.model_validate(data)
            except json.JSONDecodeError:
                pass

        raise ValueError(f"Không parse được phản hồi LLM thành {response_type.__name__}: {content[:200]}...")

    @property
    def active(self) -> str:
        """
        Lấy tên model đang hoạt động

        Returns:
            Tên model đang hoạt động

        Ví dụ:
            print(f"Đang dùng model: {pixelle_video.llm.active}")
        """
        return self._get_config_value("model", "gpt-3.5-turbo")

    def __repr__(self) -> str:
        """Chuỗi đại diện"""
        model = self.active
        base_url = self._get_config_value("base_url", "default")
        return f"<LLMService model={model!r} base_url={base_url!r}>"

