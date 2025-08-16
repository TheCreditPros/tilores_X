"""
Comprehensive unit tests for utils/function_executor.py
Tests the function executor pattern for Tilores tool management
"""

from unittest.mock import MagicMock, patch

# Import the module under test
from utils.function_executor import (
    FunctionResult,
    TiloresFunctionExecutor,
    initialize_function_executor
)


class TestFunctionResult:
    """Test the FunctionResult dataclass."""

    def test_function_result_creation_minimal(self):
        """Test FunctionResult creation with minimal parameters."""
        result = FunctionResult(success=True)

        assert result.success is True
        assert result.data is None
        assert result.error is None
        assert result.execution_time == 0.0
        assert result.function_name == ""
        assert result.timestamp != ""  # Should be auto-generated

    def test_function_result_creation_complete(self):
        """Test FunctionResult creation with all parameters."""
        test_data = {"key": "value"}
        test_timestamp = "2023-01-01T12:00:00"

        result = FunctionResult(
            success=True,
            data=test_data,
            error=None,
            execution_time=1.5,
            function_name="test_function",
            timestamp=test_timestamp
        )

        assert result.success is True
        assert result.data == test_data
        assert result.error is None
        assert result.execution_time == 1.5
        assert result.function_name == "test_function"
        assert result.timestamp == test_timestamp

    def test_function_result_post_init_timestamp(self):
        """Test that __post_init__ sets timestamp when not provided."""
        with patch('utils.function_executor.datetime') as mock_datetime:
            mock_datetime.now.return_value.isoformat.return_value = "test-timestamp"

            result = FunctionResult(success=True)

            assert result.timestamp == "test-timestamp"
            mock_datetime.now.assert_called_once()

    def test_function_result_post_init_preserves_timestamp(self):
        """Test that __post_init__ preserves existing timestamp."""
        custom_timestamp = "custom-timestamp"
        result = FunctionResult(success=True, timestamp=custom_timestamp)

        assert result.timestamp == custom_timestamp

    def test_function_result_to_dict_success(self):
        """Test to_dict method for successful result."""
        test_data = {"result": "success"}
        result = FunctionResult(
            success=True,
            data=test_data,
            execution_time=2.0,
            function_name="test_func",
            timestamp="2023-01-01T12:00:00"
        )

        dict_result = result.to_dict()

        expected = {
            "success": True,
            "execution_time": 2.0,
            "function_name": "test_func",
            "timestamp": "2023-01-01T12:00:00",
            "data": test_data
        }

        assert dict_result == expected

    def test_function_result_to_dict_error(self):
        """Test to_dict method for error result."""
        result = FunctionResult(
            success=False,
            error="Test error",
            execution_time=1.0,
            function_name="failed_func",
            timestamp="2023-01-01T12:00:00"
        )

        dict_result = result.to_dict()

        expected = {
            "success": False,
            "execution_time": 1.0,
            "function_name": "failed_func",
            "timestamp": "2023-01-01T12:00:00",
            "error": "Test error"
        }

        assert dict_result == expected

    def test_function_result_to_dict_success_no_data(self):
        """Test to_dict method for successful result without data."""
        result = FunctionResult(
            success=True,
            execution_time=1.0,
            function_name="test_func",
            timestamp="2023-01-01T12:00:00"
        )

        dict_result = result.to_dict()

        expected = {
            "success": True,
            "execution_time": 1.0,
            "function_name": "test_func",
            "timestamp": "2023-01-01T12:00:00"
        }

        assert dict_result == expected
        assert "data" not in dict_result

    def test_function_result_to_dict_error_no_message(self):
        """Test to_dict method for error result without error message."""
        result = FunctionResult(
            success=False,
            execution_time=1.0,
            function_name="failed_func",
            timestamp="2023-01-01T12:00:00"
        )

        dict_result = result.to_dict()

        expected = {
            "success": False,
            "execution_time": 1.0,
            "function_name": "failed_func",
            "timestamp": "2023-01-01T12:00:00"
        }

        assert dict_result == expected
        assert "error" not in dict_result


class TestTiloresFunctionExecutor:
    """Test the TiloresFunctionExecutor class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_tools = {
            "search": MagicMock(),
            "fetchEntity": MagicMock(),
            "creditReport": MagicMock(),
            "fieldDiscovery": MagicMock()
        }
        self.mock_monitor = MagicMock()

    def test_executor_initialization(self):
        """Test executor initialization with tools and monitor."""
        executor = TiloresFunctionExecutor(self.mock_tools, self.mock_monitor)

        assert executor.tools == self.mock_tools
        assert executor.monitor == self.mock_monitor
        assert isinstance(executor.functions, dict)
        assert len(executor.functions) > 0
        assert isinstance(executor.stats, dict)

        # Check stats initialization
        expected_stats = {
            "total_executions": 0,
            "successful_executions": 0,
            "failed_executions": 0,
            "total_execution_time": 0.0,
            "function_calls": {}
        }
        assert executor.stats == expected_stats

    def test_executor_initialization_no_monitor(self):
        """Test executor initialization without monitor."""
        executor = TiloresFunctionExecutor(self.mock_tools)

        assert executor.tools == self.mock_tools
        assert executor.monitor is None
        assert len(executor.functions) > 0

    def test_register_functions_all_tools(self):
        """Test function registration when all tools are available."""
        executor = TiloresFunctionExecutor(self.mock_tools)

        # Should have search functions
        assert "search_customer" in executor.functions
        assert "search_customer_360" in executor.functions
        assert "search_customer_batch" in executor.functions

        # Should have entity functions
        assert "fetch_entity" in executor.functions
        assert "get_entity_relationships" in executor.functions

        # Should have credit functions
        assert "get_credit_report" in executor.functions
        assert "analyze_credit_score" in executor.functions

        # Should have field discovery functions
        assert "discover_fields" in executor.functions
        assert "get_field_metadata" in executor.functions

    def test_register_functions_partial_tools(self):
        """Test function registration with only some tools available."""
        partial_tools = {"search": MagicMock()}
        executor = TiloresFunctionExecutor(partial_tools)

        # Should have search functions
        assert "search_customer" in executor.functions
        assert "search_customer_360" in executor.functions
        assert "search_customer_batch" in executor.functions

        # Should not have other functions
        assert "fetch_entity" not in executor.functions
        assert "get_credit_report" not in executor.functions
        assert "discover_fields" not in executor.functions

    def test_execute_function_unknown(self):
        """Test executing unknown function."""
        executor = TiloresFunctionExecutor(self.mock_tools, self.mock_monitor)

        result = executor.execute_function("unknown_function", arg1="value1")

        assert result.success is False
        assert result.error is not None
        assert "Unknown function: unknown_function" in result.error
        assert result.function_name == "unknown_function"
        assert result.execution_time > 0
        assert executor.stats["failed_executions"] == 1
        assert executor.stats["total_executions"] == 1

    def test_execute_function_success(self):
        """Test successful function execution."""
        self.mock_tools["search"].run.return_value = {"result": "success"}
        executor = TiloresFunctionExecutor(self.mock_tools, self.mock_monitor)

        result = executor.execute_function("search_customer", query="test")

        assert result.success is True
        assert result.data == {"result": "success"}
        assert result.function_name == "search_customer"
        assert result.execution_time > 0
        assert executor.stats["successful_executions"] == 1
        assert executor.stats["total_executions"] == 1
        assert executor.stats["function_calls"]["search_customer"] == 1

    def test_execute_function_with_error_result(self):
        """Test function execution that returns error in result."""
        self.mock_tools["search"].run.return_value = {"error": "Search failed"}
        executor = TiloresFunctionExecutor(self.mock_tools, self.mock_monitor)

        result = executor.execute_function("search_customer", query="test")

        assert result.success is False
        assert result.error == "Search failed"
        assert result.data == {"error": "Search failed"}
        assert result.function_name == "search_customer"

    def test_execute_function_exception(self):
        """Test function execution with exception."""
        self.mock_tools["search"].run.side_effect = Exception("Test exception")
        executor = TiloresFunctionExecutor(self.mock_tools, self.mock_monitor)

        result = executor.execute_function("search_customer", query="test")

        assert result.success is False
        assert result.error is not None
        assert "Function execution failed: Test exception" in result.error
        assert result.function_name == "search_customer"
        assert result.execution_time > 0
        assert executor.stats["failed_executions"] == 1

    def test_execute_function_monitoring(self):
        """Test function execution with monitoring."""
        self.mock_tools["search"].run.return_value = {"result": "success"}
        executor = TiloresFunctionExecutor(self.mock_tools, self.mock_monitor)

        # Mock timer ID
        self.mock_monitor.start_timer.return_value = "timer-123"

        result = executor.execute_function("search_customer", query="test")

        assert result.success is True

        # Verify monitoring calls
        self.mock_monitor.start_timer.assert_called_once()
        self.mock_monitor.end_timer.assert_called_once_with("timer-123", success=True)

    def test_execute_function_monitoring_error(self):
        """Test function execution monitoring with error."""
        self.mock_tools["search"].run.side_effect = Exception("Test error")
        executor = TiloresFunctionExecutor(self.mock_tools, self.mock_monitor)

        self.mock_monitor.start_timer.return_value = "timer-123"

        result = executor.execute_function("search_customer", query="test")

        assert result.success is False

        # Verify monitoring error handling
        self.mock_monitor.end_timer.assert_called_once_with(
            "timer-123", success=False, error="Test error"
        )

    def test_get_statistics(self):
        """Test getting execution statistics."""
        executor = TiloresFunctionExecutor(self.mock_tools)

        # Execute some functions to generate stats
        self.mock_tools["search"].run.return_value = {"result": "success"}
        executor.execute_function("search_customer", query="test1")
        executor.execute_function("search_customer", query="test2")
        executor.execute_function("unknown_function")

        stats = executor.get_statistics()

        assert stats["total_executions"] == 3
        assert stats["successful_executions"] == 2
        assert stats["failed_executions"] == 1
        assert stats["success_rate"] == 2 / 3
        assert stats["average_execution_time"] > 0
        assert stats["total_execution_time"] > 0
        assert stats["function_calls"]["search_customer"] == 2
        assert "search_customer" in stats["available_functions"]

    def test_get_statistics_no_executions(self):
        """Test getting statistics with no executions."""
        executor = TiloresFunctionExecutor(self.mock_tools)

        stats = executor.get_statistics()

        assert stats["total_executions"] == 0
        assert stats["successful_executions"] == 0
        assert stats["failed_executions"] == 0
        assert stats["success_rate"] == 0
        assert stats["average_execution_time"] == 0.0
        assert stats["total_execution_time"] == 0.0
        assert stats["function_calls"] == {}
        assert len(stats["available_functions"]) > 0


class TestFunctionImplementations:
    """Test specific function implementations."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_tools = {
            "search": MagicMock(),
            "fetchEntity": MagicMock(),
            "creditReport": MagicMock(),
            "fieldDiscovery": MagicMock()
        }
        self.executor = TiloresFunctionExecutor(self.mock_tools)

    def test_execute_search_customer(self):
        """Test search customer function."""
        self.mock_tools["search"].run.return_value = {"customer": "data"}

        result = self.executor._execute_search_customer(query="test query")

        assert result == {"customer": "data"}
        self.mock_tools["search"].run.assert_called_once_with("test query")

    def test_execute_search_customer_no_tool(self):
        """Test search customer without search tool."""
        executor = TiloresFunctionExecutor({})

        result = executor._execute_search_customer(query="test")

        assert result == {"error": "Search tool not available"}

    def test_execute_search_customer_360(self):
        """Test comprehensive customer 360 search."""
        self.mock_tools["search"].run.return_value = {"customer": "data"}

        with patch.object(self.executor, '_format_customer_360_response') as mock_format:
            mock_format.return_value = {"formatted": "data"}

            result = self.executor._execute_search_customer_360(query="test query")

            assert result == {"formatted": "data"}
            self.mock_tools["search"].run.assert_called_once_with("test query")
            mock_format.assert_called_once_with({"customer": "data"}, "test query")

    def test_execute_search_customer_batch(self):
        """Test batch customer search."""
        self.mock_tools["search"].run.side_effect = [
            {"result": "data1"},
            {"result": "data2"}
        ]

        result = self.executor._execute_search_customer_batch(
            queries=["query1", "query2"]
        )

        assert result["batch_results"] == [{"result": "data1"}, {"result": "data2"}]
        assert result["batch_size"] == 2
        assert "timestamp" in result
        assert self.mock_tools["search"].run.call_count == 2

    def test_execute_search_customer_batch_single_query(self):
        """Test batch search with single query parameter."""
        self.mock_tools["search"].run.return_value = {"result": "data"}

        result = self.executor._execute_search_customer_batch(query="single query")

        assert result["batch_results"] == [{"result": "data"}]
        assert result["batch_size"] == 1
        self.mock_tools["search"].run.assert_called_once_with("single query")

    def test_execute_fetch_entity(self):
        """Test entity fetch function."""
        self.mock_tools["fetchEntity"].run.return_value = {"entity": "data"}

        result = self.executor._execute_fetch_entity(entity_id="123")

        assert result == {"entity": "data"}
        self.mock_tools["fetchEntity"].run.assert_called_once_with("123")

    def test_execute_get_entity_relationships(self):
        """Test entity relationships function."""
        entity_data = {
            "entity": "data",
            "relationships": [{"rel1": "data"}, {"rel2": "data"}]
        }
        self.mock_tools["fetchEntity"].run.return_value = entity_data

        result = self.executor._execute_get_entity_relationships(entity_id="123")

        expected = {
            "entity_id": "123",
            "relationships": [{"rel1": "data"}, {"rel2": "data"}],
            "related_count": 2
        }
        assert result == expected

    def test_execute_get_entity_relationships_no_relationships(self):
        """Test entity relationships with no relationships data."""
        self.mock_tools["fetchEntity"].run.return_value = {"entity": "data"}

        result = self.executor._execute_get_entity_relationships(entity_id="123")

        expected = {
            "entity_id": "123",
            "relationships": [],
            "related_count": 0
        }
        assert result == expected

    def test_execute_get_credit_report(self):
        """Test credit report function."""
        self.mock_tools["creditReport"].run.return_value = {"credit": "report"}

        result = self.executor._execute_get_credit_report(customer_id="456")

        assert result == {"credit": "report"}
        self.mock_tools["creditReport"].run.assert_called_once_with("456")

    def test_execute_analyze_credit_score(self):
        """Test credit score analysis function."""
        credit_data = {"credit_score": 750, "other": "data"}
        self.mock_tools["creditReport"].run.return_value = credit_data

        result = self.executor._execute_analyze_credit_score(customer_id="456")

        expected = {
            "customer_id": "456",
            "credit_score": 750,
            "rating": "Very Good",
            "risk_level": "Low Risk"
        }
        assert result == expected

    def test_execute_analyze_credit_score_no_score(self):
        """Test credit score analysis without score in data."""
        self.mock_tools["creditReport"].run.return_value = {"other": "data"}

        result = self.executor._execute_analyze_credit_score(customer_id="456")

        assert result == {"other": "data"}

    def test_execute_discover_fields(self):
        """Test field discovery function."""
        self.mock_tools["fieldDiscovery"].run.return_value = {"fields": "data"}

        result = self.executor._execute_discover_fields()

        assert result == {"fields": "data"}
        self.mock_tools["fieldDiscovery"].run.assert_called_once_with("")

    def test_execute_get_field_metadata(self):
        """Test field metadata function."""
        all_fields = {"field1": {"type": "string"}, "field2": {"type": "int"}}
        self.mock_tools["fieldDiscovery"].run.return_value = all_fields

        result = self.executor._execute_get_field_metadata(field_name="field1")

        expected = {
            "field_name": "field1",
            "metadata": {"type": "string"},
            "exists": True
        }
        assert result == expected

    def test_execute_get_field_metadata_no_field(self):
        """Test field metadata for non-existent field."""
        all_fields = {"field1": {"type": "string"}}
        self.mock_tools["fieldDiscovery"].run.return_value = all_fields

        result = self.executor._execute_get_field_metadata(field_name="nonexistent")

        expected = {
            "field_name": "nonexistent",
            "metadata": {},
            "exists": False
        }
        assert result == expected

    def test_execute_get_field_metadata_no_field_name(self):
        """Test field metadata without field name."""
        all_fields = {"fields": "data"}
        self.mock_tools["fieldDiscovery"].run.return_value = all_fields

        result = self.executor._execute_get_field_metadata()

        assert result == all_fields


class TestHelperMethods:
    """Test helper methods."""

    def setup_method(self):
        """Set up test fixtures."""
        self.executor = TiloresFunctionExecutor({})

    def test_format_customer_360_response_non_dict(self):
        """Test formatting non-dict data."""
        result = self.executor._format_customer_360_response("string data", "query")

        assert result == {"raw_data": "string data"}

    def test_format_customer_360_response_with_entity(self):
        """Test formatting data with entity information."""
        data = {
            "entity": {
                "id": "123",
                "name": "John Doe",
                "email": "john@example.com",
                "phone": "123-456-7890",
                "status": "active"
            },
            "other_data": {"key": "value"}
        }

        result = self.executor._format_customer_360_response(data, "test query")

        assert result["query"] == "test query"
        assert "timestamp" in result
        assert result["customer_summary"]["id"] == "123"
        assert result["customer_summary"]["name"] == "John Doe"
        assert result["customer_summary"]["email"] == "john@example.com"
        assert result["data_sections"]["other_data"] == {"key": "value"}
        assert "llm_instruction" in result

    def test_format_customer_360_response_with_customer(self):
        """Test formatting data with customer information."""
        data = {
            "customer": {
                "id": "456",
                "name": "Jane Smith"
            },
            "transactions": [{"txn": "data"}]
        }

        result = self.executor._format_customer_360_response(data, "test query")

        assert result["customer_summary"]["id"] == "456"
        assert result["customer_summary"]["name"] == "Jane Smith"
        assert result["data_sections"]["transactions"] == [{"txn": "data"}]

    def test_create_llm_instruction_no_sections(self):
        """Test LLM instruction creation with no data sections."""
        data = {"customer_summary": {}, "data_sections": {}}

        instruction = self.executor._create_llm_instruction(data, "test query")

        assert instruction == "Use the customer summary to answer the query."

    def test_create_llm_instruction_with_sections(self):
        """Test LLM instruction creation with data sections."""
        data = {
            "data_sections": {
                "transactions": [],
                "credit_info": {}
            }
        }

        instruction = self.executor._create_llm_instruction(data, "test query")

        expected = ("To answer 'test query', reference the following data sections: "
                   "transactions, credit_info. Provide specific details from the relevant sections.")
        assert instruction == expected

    def test_get_credit_rating_excellent(self):
        """Test credit rating for excellent score."""
        assert self.executor._get_credit_rating(850) == "Excellent"
        assert self.executor._get_credit_rating(800) == "Excellent"

    def test_get_credit_rating_very_good(self):
        """Test credit rating for very good score."""
        assert self.executor._get_credit_rating(799) == "Very Good"
        assert self.executor._get_credit_rating(740) == "Very Good"

    def test_get_credit_rating_good(self):
        """Test credit rating for good score."""
        assert self.executor._get_credit_rating(739) == "Good"
        assert self.executor._get_credit_rating(670) == "Good"

    def test_get_credit_rating_fair(self):
        """Test credit rating for fair score."""
        assert self.executor._get_credit_rating(669) == "Fair"
        assert self.executor._get_credit_rating(580) == "Fair"

    def test_get_credit_rating_poor(self):
        """Test credit rating for poor score."""
        assert self.executor._get_credit_rating(579) == "Poor"
        assert self.executor._get_credit_rating(300) == "Poor"

    def test_get_risk_level_low(self):
        """Test risk level for low risk scores."""
        assert self.executor._get_risk_level(800) == "Low Risk"
        assert self.executor._get_risk_level(740) == "Low Risk"

    def test_get_risk_level_medium(self):
        """Test risk level for medium risk scores."""
        assert self.executor._get_risk_level(739) == "Medium Risk"
        assert self.executor._get_risk_level(670) == "Medium Risk"

    def test_get_risk_level_high(self):
        """Test risk level for high risk scores."""
        assert self.executor._get_risk_level(669) == "High Risk"
        assert self.executor._get_risk_level(300) == "High Risk"


class TestGlobalFunctions:
    """Test global initialization functions."""

    def test_initialize_function_executor(self):
        """Test global function executor initialization."""
        mock_tools = {"search": MagicMock()}
        mock_monitor = MagicMock()

        # Clear global state
        import utils.function_executor
        utils.function_executor.function_executor = None

        result = initialize_function_executor(mock_tools, mock_monitor)

        assert result is not None
        assert isinstance(result, TiloresFunctionExecutor)
        assert result.tools == mock_tools
        assert result.monitor == mock_monitor

        # Check global state
        from utils.function_executor import function_executor as global_executor
        assert global_executor is result

    def test_initialize_function_executor_no_monitor(self):
        """Test global function executor initialization without monitor."""
        mock_tools = {"search": MagicMock()}

        # Clear global state
        import utils.function_executor
        utils.function_executor.function_executor = None

        result = initialize_function_executor(mock_tools)

        assert result is not None
        assert result.tools == mock_tools
        assert result.monitor is None


class TestIntegration:
    """Test integration scenarios."""

    def test_full_execution_workflow(self):
        """Test complete execution workflow with all components."""
        mock_tools = {
            "search": MagicMock(),
            "creditReport": MagicMock()
        }
        mock_monitor = MagicMock()

        # Set up tool responses
        mock_tools["search"].run.return_value = {"customer": "found"}
        mock_tools["creditReport"].run.return_value = {"credit_score": 720}

        # Set up monitor
        mock_monitor.start_timer.return_value = "timer-id"

        executor = TiloresFunctionExecutor(mock_tools, mock_monitor)

        # Execute search
        search_result = executor.execute_function("search_customer", query="test")
        assert search_result.success is True
        assert search_result.data == {"customer": "found"}

        # Execute credit analysis
        credit_result = executor.execute_function("analyze_credit_score", customer_id="123")
        assert credit_result.success is True
        assert credit_result.data is not None
        assert credit_result.data["credit_score"] == 720
        assert credit_result.data["rating"] == "Good"
        assert credit_result.data["risk_level"] == "Medium Risk"

        # Check statistics
        stats = executor.get_statistics()
        assert stats["total_executions"] == 2
        assert stats["successful_executions"] == 2
        assert stats["failed_executions"] == 0
        assert stats["success_rate"] == 1.0

        # Verify monitoring calls
        assert mock_monitor.start_timer.call_count == 2
        assert mock_monitor.end_timer.call_count == 2
