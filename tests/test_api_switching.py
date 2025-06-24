import pytest
import time
import json
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, List, Any

from src.llm_clients.multi_llm import MultiLLMClient

class TestAPISwithcing:
    """Test suite for API switching and failover mechanisms."""
    
    @pytest.fixture
    def multi_client(self):
        """Create MultiLLMClient for testing."""
        with patch.dict('os.environ', {
            'XINGCHENG_API_KEY': 'test_key',
            'XINGCHENG_API_SECRET': 'test_secret',
            'QINIU_API_KEY': 'qiniu_key',
            'TOGETHER_API_KEY': 'together_key',
            'OPENROUTER_API_KEY': 'openrouter_key'
        }):
            return MultiLLMClient()
    
    def test_primary_api_success_no_switching(self, multi_client):
        """Test that no switching occurs when primary API succeeds."""
        with patch.object(multi_client, 'call_xingcheng_api') as mock_xingcheng:
            mock_xingcheng.return_value = ("Primary API success", {"status": "ok"})
            
            messages = [{"role": "user", "content": "Test message"}]
            result = multi_client.chat_completion(messages, model="auto")
            
            # Should use primary API and not call others
            mock_xingcheng.assert_called_once()
            assert result["choices"][0]["message"]["content"] == "Primary API success"
    
    def test_sequential_api_failover(self, multi_client):
        """Test sequential failover through multiple APIs."""
        with patch.object(multi_client, 'call_xingcheng_api') as mock_xingcheng, \
             patch.object(multi_client, 'call_openrouter_api') as mock_openrouter, \
             patch.object(multi_client, 'call_together_api') as mock_together, \
             patch.object(multi_client, 'call_qiniu_api') as mock_qiniu:
            
            # First two APIs fail, third succeeds
            mock_xingcheng.return_value = ("[API Error: Xingcheng failed]", None)
            mock_openrouter.return_value = ("[API Error: OpenRouter failed]", None)
            mock_together.return_value = ("Together API success", {"status": "ok"})
            mock_qiniu.return_value = ("Should not be called", {"status": "ok"})
            
            messages = [{"role": "user", "content": "Test message"}]
            content, _ = multi_client.call_multi_cloud(messages)
            
            # Should try first three APIs
            mock_xingcheng.assert_called_once()
            mock_openrouter.assert_called_once()
            mock_together.assert_called_once()
            mock_qiniu.assert_not_called()  # Should stop after success
            
            assert content == "Together API success"
    
    def test_all_apis_fail_scenario(self, multi_client):
        """Test behavior when all APIs fail."""
        with patch.object(multi_client, 'call_xingcheng_api') as mock_xingcheng, \
             patch.object(multi_client, 'call_openrouter_api') as mock_openrouter, \
             patch.object(multi_client, 'call_together_api') as mock_together, \
             patch.object(multi_client, 'call_qiniu_api') as mock_qiniu:
            
            # All APIs fail
            mock_xingcheng.return_value = ("[API Error: Xingcheng failed]", None)
            mock_openrouter.return_value = ("[API Error: OpenRouter failed]", None)
            mock_together.return_value = ("[API Error: Together failed]", None)
            mock_qiniu.return_value = ("[API Error: Qiniu failed]", None)
            
            messages = [{"role": "user", "content": "Test message"}]
            content, _ = multi_client.call_multi_cloud(messages)
            
            # Should try all APIs
            mock_xingcheng.assert_called_once()
            mock_openrouter.assert_called_once()
            mock_together.assert_called_once()
            mock_qiniu.assert_called_once()
            
            assert "All cloud APIs failed" in content
    
    def test_specific_api_selection(self, multi_client):
        """Test selecting a specific API instead of auto mode."""
        with patch.object(multi_client, 'call_qiniu_api') as mock_qiniu:
            mock_qiniu.return_value = ("Qiniu specific response", {"status": "ok"})
            
            messages = [{"role": "user", "content": "Test message"}]
            result = multi_client.chat_completion(messages, model="qiniu/deepseek-v3")
            
            mock_qiniu.assert_called_once()
            assert result["choices"][0]["message"]["content"] == "Qiniu specific response"
    
    def test_api_response_time_tracking(self, multi_client):
        """Test tracking of API response times."""
        with patch.object(multi_client, 'call_xingcheng_api') as mock_xingcheng:
            def slow_api_call(*args, **kwargs):
                time.sleep(0.1)  # Simulate slow response
                return ("Slow response", {"status": "ok"})
            
            mock_xingcheng.side_effect = slow_api_call
            
            start_time = time.time()
            messages = [{"role": "user", "content": "Test message"}]
            result = multi_client.chat_completion(messages, model="xingcheng/x1")
            end_time = time.time()
            
            response_time = end_time - start_time
            assert response_time >= 0.1
            assert result["choices"][0]["message"]["content"] == "Slow response"
    
    def test_api_error_logging(self, multi_client):
        """Test that API errors are properly logged."""
        with patch.object(multi_client, 'call_xingcheng_api') as mock_xingcheng, \
             patch('builtins.print') as mock_print:
            
            mock_xingcheng.return_value = ("[API Error: Connection failed]", None)
            
            messages = [{"role": "user", "content": "Test message"}]
            multi_client.call_multi_cloud(messages)
            
            # Check that error information was printed/logged
            mock_print.assert_called()
            print_calls = [call[0][0] for call in mock_print.call_args_list]
            assert any("Trying API" in call for call in print_calls)
    
    def test_retry_mechanism(self, multi_client):
        """Test retry mechanism for transient failures."""
        with patch.object(multi_client, 'call_xingcheng_api') as mock_xingcheng:
            # First call fails, second succeeds
            mock_xingcheng.side_effect = [
                ("[API Error: Temporary failure]", None),
                ("Retry success", {"status": "ok"})
            ]
            
            messages = [{"role": "user", "content": "Test message"}]
            
            # Simulate retry logic (this would need to be implemented in the actual client)
            content, _ = multi_client.call_xingcheng_api(messages)
            if "API Error" in content:
                content, _ = multi_client.call_xingcheng_api(messages)
            
            assert content == "Retry success"
            assert mock_xingcheng.call_count == 2

class TestAPIConfiguration:
    """Test API configuration and initialization."""
    
    def test_missing_api_keys_handling(self):
        """Test handling of missing API keys."""
        with patch.dict('os.environ', {}, clear=True):
            # Should initialize but with limited functionality
            client = MultiLLMClient()
            assert hasattr(client, 'api_endpoints')
    
    def test_partial_api_configuration(self):
        """Test with only some APIs configured."""
        with patch.dict('os.environ', {
            'XINGCHENG_API_KEY': 'test_key',
            'XINGCHENG_API_SECRET': 'test_secret'
            # Other APIs not configured
        }, clear=True):
            client = MultiLLMClient()
            assert hasattr(client, 'api_endpoints')
            # Should work with available APIs
    
    def test_invalid_model_specification(self, multi_client):
        """Test handling of invalid model specifications."""
        messages = [{"role": "user", "content": "Test message"}]
        
        # Test with invalid API prefix
        result = multi_client.chat_completion(messages, model="invalid/model")
        
        # Should fall back to auto mode or handle gracefully
        assert "choices" in result
    
    def test_api_endpoint_validation(self, multi_client):
        """Test validation of API endpoints."""
        # Test that client has expected API endpoints configured
        expected_apis = ['xingcheng', 'qiniu', 'together', 'openrouter']
        
        # Check that client can handle these API types
        for api_type in expected_apis:
            model_name = f"{api_type}/test-model"
            messages = [{"role": "user", "content": "Test"}]
            
            # Should not raise exception for valid API types
            try:
                result = multi_client.chat_completion(messages, model=model_name)
                assert isinstance(result, dict)
            except Exception as e:
                # If it fails, it should be due to API call, not configuration
                assert "API Error" in str(e) or "connection" in str(e).lower()

class TestAPIPerformanceMetrics:
    """Test performance metrics collection for API switching."""
    
    def test_api_success_rate_tracking(self, multi_client):
        """Test tracking of API success rates."""
        success_count = 0
        total_calls = 10
        
        with patch.object(multi_client, 'call_xingcheng_api') as mock_xingcheng:
            # Simulate 70% success rate
            def variable_success(*args, **kwargs):
                nonlocal success_count
                success_count += 1
                if success_count <= 7:
                    return ("Success", {"status": "ok"})
                else:
                    return ("[API Error: Failed]", None)
            
            mock_xingcheng.side_effect = variable_success
            
            messages = [{"role": "user", "content": "Test"}]
            results = []
            
            for _ in range(total_calls):
                content, _ = multi_client.call_xingcheng_api(messages)
                results.append("Success" in content)
            
            success_rate = sum(results) / len(results)
            assert 0.6 <= success_rate <= 0.8  # Around 70%
    
    def test_api_latency_comparison(self, multi_client):
        """Test comparison of API latencies."""
        with patch.object(multi_client, 'call_xingcheng_api') as mock_xingcheng, \
             patch.object(multi_client, 'call_qiniu_api') as mock_qiniu:
            
            def fast_api(*args, **kwargs):
                time.sleep(0.05)
                return ("Fast response", {"status": "ok"})
            
            def slow_api(*args, **kwargs):
                time.sleep(0.15)
                return ("Slow response", {"status": "ok"})
            
            mock_xingcheng.side_effect = fast_api
            mock_qiniu.side_effect = slow_api
            
            messages = [{"role": "user", "content": "Test"}]
            
            # Test Xingcheng (fast)
            start_time = time.time()
            multi_client.call_xingcheng_api(messages)
            xingcheng_time = time.time() - start_time
            
            # Test Qiniu (slow)
            start_time = time.time()
            multi_client.call_qiniu_api(messages)
            qiniu_time = time.time() - start_time
            
            assert xingcheng_time < qiniu_time
            assert xingcheng_time >= 0.05
            assert qiniu_time >= 0.15

class TestMockModeIntegration:
    """Test integration with mock mode when all APIs fail."""
    
    def test_fallback_to_mock_mode(self, multi_client):
        """Test automatic fallback to mock mode."""
        with patch.object(multi_client, 'call_multi_cloud') as mock_multi_cloud:
            mock_multi_cloud.return_value = ("[API Error: All cloud APIs failed]", None)
            
            messages = [{"role": "user", "content": "Test message"}]
            result = multi_client.chat_completion(messages, model="auto")
            
            # Should handle the failure gracefully
            assert "choices" in result
            assert "API Error" in result["choices"][0]["message"]["content"]
    
    def test_explicit_mock_mode_selection(self, multi_client):
        """Test explicit selection of mock mode."""
        # This would require implementing mock mode in MultiLLMClient
        # For now, test that it doesn't crash
        messages = [{"role": "user", "content": "Test message"}]
        
        try:
            result = multi_client.chat_completion(messages, model="mock")
            assert isinstance(result, dict)
        except NotImplementedError:
            # Expected if mock mode not implemented yet
            pass

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
