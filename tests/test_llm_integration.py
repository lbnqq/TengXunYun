import pytest
import time
import json
import os
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, List, Any

# Import LLM clients
from src.llm_clients.base_llm import BaseLLMClient
from src.llm_clients.xingcheng_llm import XingchengLLMClient
from src.llm_clients.multi_llm import MultiLLMClient

class TestLLMIntegration:
    """Comprehensive test suite for LLM integration functionality."""
    
    @pytest.fixture
    def mock_api_response(self):
        """Mock API response for testing."""
        return {
            "choices": [
                {
                    "message": {
                        "content": "This is a test response from the LLM API."
                    }
                }
            ]
        }
    
    @pytest.fixture
    def mock_xingcheng_client(self):
        """Create a mock Xingcheng LLM client for testing."""
        client = Mock(spec=XingchengLLMClient)
        client.generate.return_value = "Mock Xingcheng response"
        client.api_key = "test_key"
        client.api_secret = "test_secret"
        client.model_name = "x1"
        return client
    
    @pytest.fixture
    def mock_multi_llm_client(self):
        """Create a mock Multi LLM client for testing."""
        client = Mock(spec=MultiLLMClient)
        client.generate.return_value = "Mock Multi LLM response"
        client.chat_completion.return_value = {
            "choices": [{"message": {"content": "Mock response"}}]
        }
        return client

class TestXingchengLLMClient:
    """Test cases for Xingcheng LLM client."""
    
    def test_client_initialization(self):
        """Test proper initialization of Xingcheng client."""
        with patch.dict(os.environ, {
            'XINGCHENG_API_KEY': 'test_key',
            'XINGCHENG_API_SECRET': 'test_secret'
        }):
            client = XingchengLLMClient(
                api_key='test_key',
                api_secret='test_secret',
                model_name='x1'
            )
            assert client.api_key == 'test_key'
            assert client.api_secret == 'test_secret'
            assert client.model_name == 'x1'
    
    @patch('requests.post')
    def test_successful_api_call(self, mock_post):
        """Test successful API call to Xingcheng."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "Test response"}}]
        }
        mock_post.return_value = mock_response
        
        client = XingchengLLMClient('test_key', 'test_secret', 'x1')
        result = client.generate("Test prompt")
        
        assert result == "Test response"
        mock_post.assert_called_once()
    
    @patch('requests.post')
    def test_api_error_handling(self, mock_post):
        """Test API error handling."""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        mock_post.return_value = mock_response
        
        client = XingchengLLMClient('test_key', 'test_secret', 'x1')
        result = client.generate("Test prompt")
        
        assert "Error" in result or "Failed" in result
    
    @patch('requests.post')
    def test_timeout_handling(self, mock_post):
        """Test timeout handling."""
        mock_post.side_effect = Exception("Timeout")
        
        client = XingchengLLMClient('test_key', 'test_secret', 'x1')
        result = client.generate("Test prompt")
        
        assert "Error" in result or "Failed" in result

class TestMultiLLMClient:
    """Test cases for Multi LLM client with API switching."""
    
    @pytest.fixture
    def multi_client_config(self):
        """Configuration for multi LLM client testing."""
        return {
            'xingcheng': {'api_key': 'test_key', 'api_secret': 'test_secret'},
            'qiniu': {'api_key': 'qiniu_key'},
            'together': {'api_key': 'together_key'},
            'openrouter': {'api_key': 'openrouter_key'}
        }
    
    def test_multi_client_initialization(self, multi_client_config):
        """Test Multi LLM client initialization."""
        with patch.dict(os.environ, {
            'XINGCHENG_API_KEY': 'test_key',
            'XINGCHENG_API_SECRET': 'test_secret',
            'QINIU_API_KEY': 'qiniu_key',
            'TOGETHER_API_KEY': 'together_key',
            'OPENROUTER_API_KEY': 'openrouter_key'
        }):
            client = MultiLLMClient()
            assert hasattr(client, 'api_endpoints')
            assert len(client.api_endpoints) > 0
    
    @patch('src.llm_clients.multi_llm.MultiLLMClient.call_xingcheng_api')
    def test_primary_api_success(self, mock_xingcheng):
        """Test successful call to primary API."""
        mock_xingcheng.return_value = ("Success response", {"status": "ok"})
        
        client = MultiLLMClient()
        messages = [{"role": "user", "content": "Test message"}]
        result = client.chat_completion(messages, model="auto")
        
        assert result["choices"][0]["message"]["content"] == "Success response"
    
    @patch('src.llm_clients.multi_llm.MultiLLMClient.call_multi_cloud')
    def test_api_failover_mechanism(self, mock_multi_cloud):
        """Test API failover when primary API fails."""
        # Simulate primary API failure, backup success
        mock_multi_cloud.return_value = ("Backup API response", {"status": "ok"})
        
        client = MultiLLMClient()
        messages = [{"role": "user", "content": "Test message"}]
        result = client.chat_completion(messages, model="auto")
        
        assert result["choices"][0]["message"]["content"] == "Backup API response"
    
    @patch('src.llm_clients.multi_llm.MultiLLMClient.call_multi_cloud')
    def test_all_apis_fail(self, mock_multi_cloud):
        """Test behavior when all APIs fail."""
        mock_multi_cloud.return_value = ("[API Error: All cloud APIs failed]", None)
        
        client = MultiLLMClient()
        messages = [{"role": "user", "content": "Test message"}]
        result = client.chat_completion(messages, model="auto")
        
        assert "API Error" in result["choices"][0]["message"]["content"]

class TestLLMPerformance:
    """Performance tests for LLM integration."""
    
    @pytest.fixture
    def performance_client(self):
        """Create a client for performance testing."""
        return Mock(spec=BaseLLMClient)
    
    def test_response_time_measurement(self, performance_client):
        """Test LLM response time measurement."""
        # Mock a response with delay
        def mock_generate_with_delay(prompt):
            time.sleep(0.1)  # Simulate API delay
            return "Performance test response"
        
        performance_client.generate.side_effect = mock_generate_with_delay
        
        start_time = time.time()
        result = performance_client.generate("Test prompt")
        end_time = time.time()
        
        response_time = end_time - start_time
        assert response_time >= 0.1
        assert result == "Performance test response"
    
    def test_concurrent_requests(self, performance_client):
        """Test handling of concurrent LLM requests."""
        import threading
        
        results = []
        
        def make_request():
            result = performance_client.generate("Concurrent test")
            results.append(result)
        
        performance_client.generate.return_value = "Concurrent response"
        
        # Create multiple threads
        threads = []
        for i in range(5):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        assert len(results) == 5
        assert all(result == "Concurrent response" for result in results)
    
    def test_large_prompt_handling(self, performance_client):
        """Test handling of large prompts."""
        large_prompt = "Test prompt " * 1000  # Create a large prompt
        performance_client.generate.return_value = "Large prompt response"
        
        result = performance_client.generate(large_prompt)
        
        assert result == "Large prompt response"
        performance_client.generate.assert_called_once_with(large_prompt)

class TestLLMErrorHandling:
    """Test error handling scenarios for LLM integration."""
    
    def test_network_error_handling(self):
        """Test handling of network errors."""
        with patch('requests.post') as mock_post:
            mock_post.side_effect = ConnectionError("Network error")
            
            client = XingchengLLMClient('test_key', 'test_secret', 'x1')
            result = client.generate("Test prompt")
            
            assert "Error" in result or "Failed" in result
    
    def test_invalid_api_key_handling(self):
        """Test handling of invalid API keys."""
        with patch('requests.post') as mock_post:
            mock_response = Mock()
            mock_response.status_code = 401
            mock_response.text = "Unauthorized"
            mock_post.return_value = mock_response
            
            client = XingchengLLMClient('invalid_key', 'invalid_secret', 'x1')
            result = client.generate("Test prompt")
            
            assert "Error" in result or "Unauthorized" in result
    
    def test_rate_limit_handling(self):
        """Test handling of rate limits."""
        with patch('requests.post') as mock_post:
            mock_response = Mock()
            mock_response.status_code = 429
            mock_response.text = "Rate limit exceeded"
            mock_post.return_value = mock_response
            
            client = XingchengLLMClient('test_key', 'test_secret', 'x1')
            result = client.generate("Test prompt")
            
            assert "Rate limit" in result or "Error" in result
    
    def test_malformed_response_handling(self):
        """Test handling of malformed API responses."""
        with patch('requests.post') as mock_post:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.side_effect = json.JSONDecodeError("Invalid JSON", "", 0)
            mock_post.return_value = mock_response
            
            client = XingchengLLMClient('test_key', 'test_secret', 'x1')
            result = client.generate("Test prompt")
            
            assert "Error" in result or "Failed" in result

class TestLLMIntegrationWithOrchestrator:
    """Test LLM integration within the orchestrator context."""
    
    @pytest.fixture
    def mock_orchestrator_setup(self):
        """Setup mock orchestrator with LLM client."""
        from src.core.agent.agent_orchestrator import AgentOrchestrator
        
        mock_llm = Mock(spec=BaseLLMClient)
        mock_llm.generate.return_value = json.dumps({
            "inferred_scenario": "Technical Report",
            "supporting_evidence": "Technical keywords found",
            "confidence": 0.9
        })
        
        orchestrator = AgentOrchestrator(
            llm_client=mock_llm,
            kb_path="src/core/knowledge_base"
        )
        
        return orchestrator, mock_llm
    
    def test_orchestrator_llm_integration(self, mock_orchestrator_setup, tmp_path):
        """Test LLM integration within orchestrator workflow."""
        orchestrator, mock_llm = mock_orchestrator_setup
        
        # Create test document
        test_doc = tmp_path / "test_doc.txt"
        test_doc.write_text("This is a technical report with performance metrics.")
        
        # Process document
        result = orchestrator.process_document(str(test_doc))
        
        # Verify LLM was called
        assert mock_llm.generate.called
        assert "error" not in result
        assert result.get("confirmed_scenario") == "Technical Report"
    
    def test_llm_failure_in_orchestrator(self, mock_orchestrator_setup, tmp_path):
        """Test orchestrator behavior when LLM fails."""
        orchestrator, mock_llm = mock_orchestrator_setup
        
        # Make LLM fail
        mock_llm.generate.side_effect = Exception("LLM API failed")
        
        # Create test document
        test_doc = tmp_path / "test_doc.txt"
        test_doc.write_text("This is a test document.")
        
        # Process document - should handle LLM failure gracefully
        result = orchestrator.process_document(str(test_doc))
        
        # Should not crash, might fall back to rule-based inference
        assert isinstance(result, dict)
        # May contain error or use fallback scenario
        assert "confirmed_scenario" in result or "error" in result

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
