"""异步HTTP客户端基础类

提供HTTP请求的通用功能，包括超时、重试和错误处理。
"""

import asyncio
from typing import Dict, Any, Optional
import httpx


class HttpClientError(Exception):
    """HTTP客户端错误"""
    
    def __init__(self, message: str, status_code: Optional[int] = None):
        super().__init__(message)
        self.status_code = status_code


class AsyncHttpClient:
    """异步HTTP客户端基础类"""
    
    def __init__(self, base_url: str, headers: Optional[Dict[str, str]] = None, 
                 timeout: float = 30.0, max_retries: int = 3):
        """初始化HTTP客户端"""
        self.base_url = base_url.rstrip('/')
        self.headers = headers or {}
        self.timeout = timeout
        self.max_retries = max_retries
    
    async def _make_request(
        self,
        method: str,
        endpoint: str,
        json_data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> httpx.Response:
        """发送HTTP请求"""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        request_headers = {**self.headers}
        if headers:
            request_headers.update(headers)
        
        last_exception = None
        
        for attempt in range(self.max_retries + 1):
            try:
                async with httpx.AsyncClient() as client:
                    return await client.request(
                        method=method, url=url, json=json_data,
                        headers=request_headers, timeout=self.timeout
                    )
                    
            except (httpx.TimeoutException, httpx.ConnectError) as e:
                last_exception = e
                if attempt < self.max_retries:
                    await asyncio.sleep(2 ** attempt)
                continue
        
        raise HttpClientError(f"请求失败: {str(last_exception)}")
    
    async def post(
        self,
        endpoint: str,
        json_data: Dict[str, Any],
        headers: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """发送POST请求"""
        response = await self._make_request("POST", endpoint, json_data=json_data, headers=headers)
        
        if response.status_code != 200:
            raise HttpClientError(f"HTTP错误 {response.status_code}", status_code=response.status_code)
        
        try:
            return response.json()
        except Exception as e:
            raise HttpClientError(f"JSON解析失败: {str(e)}")
    
    async def stream_post(
        self,
        endpoint: str,
        json_data: Dict[str, Any],
        headers: Optional[Dict[str, str]] = None
    ):
        """发送流式POST请求"""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        request_headers = {**self.headers}
        if headers:
            request_headers.update(headers)
        
        async with httpx.AsyncClient() as client:
            async with client.stream(
                "POST", url, json=json_data, headers=request_headers, timeout=self.timeout
            ) as response:
                if response.status_code != 200:
                    raise HttpClientError(f"流式请求错误 {response.status_code}")
                
                async for line in response.aiter_lines():
                    yield line 