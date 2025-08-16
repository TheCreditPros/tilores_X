"""
Function Executor Pattern for Tilores Tool Management
Provides centralized execution, monitoring, and error handling
"""

import logging
import time
from dataclasses import dataclass
from typing import Any, Callable, Dict, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class FunctionResult:
    """Standardized function execution result"""

    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    execution_time: float = 0.0
    function_name: str = ""
    timestamp: str = ""

    def __post_init__(self):
        """Set timestamp if not provided"""
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API response"""
        result = {
            "success": self.success,
            "execution_time": self.execution_time,
            "function_name": self.function_name,
            "timestamp": self.timestamp,
        }

        if self.success and self.data:
            result["data"] = self.data
        elif not self.success and self.error:
            result["error"] = self.error

        return result


class TiloresFunctionExecutor:
    """
    Centralized function execution for Tilores tools
    Provides consistent execution patterns, monitoring, and error handling
    """

    def __init__(self, tilores_tools: Dict[str, Any], monitor: Optional[Any] = None):
        """
        Initialize the function executor

        Args:
            tilores_tools: Dictionary of Tilores tool instances
            monitor: Optional monitoring instance
        """
        self.tools = tilores_tools
        self.monitor = monitor

        # Function registry mapping names to methods
        self.functions: Dict[str, Callable] = {}
        self._register_functions()

        # Execution statistics
        self.stats = {
            "total_executions": 0,
            "successful_executions": 0,
            "failed_executions": 0,
            "total_execution_time": 0.0,
            "function_calls": {},
        }

        logger.info(f"🔧 Function executor initialized with {len(self.functions)} functions")

    def _register_functions(self):
        """Register available Tilores functions"""
        # Register search functions
        if "search" in self.tools:
            self.functions["search_customer"] = self._execute_search_customer
            self.functions["search_customer_360"] = self._execute_search_customer_360
            self.functions["search_customer_batch"] = self._execute_search_customer_batch

        # Register entity functions
        if "fetchEntity" in self.tools:
            self.functions["fetch_entity"] = self._execute_fetch_entity
            self.functions["get_entity_relationships"] = self._execute_get_entity_relationships

        # Register credit functions
        if "creditReport" in self.tools:
            self.functions["get_credit_report"] = self._execute_get_credit_report
            self.functions["analyze_credit_score"] = self._execute_analyze_credit_score

        # Register field discovery
        if "fieldDiscovery" in self.tools:
            self.functions["discover_fields"] = self._execute_discover_fields
            self.functions["get_field_metadata"] = self._execute_get_field_metadata

    def execute_function(self, function_name: str, **kwargs) -> FunctionResult:
        """
        Execute a function with comprehensive error handling and monitoring

        Args:
            function_name: Name of function to execute
            **kwargs: Function arguments

        Returns:
            FunctionResult with execution details
        """
        start_time = time.time()
        self.stats["total_executions"] += 1

        # Track function-specific calls
        if function_name not in self.stats["function_calls"]:
            self.stats["function_calls"][function_name] = 0
        self.stats["function_calls"][function_name] += 1

        # Start monitoring if available
        timer_id = None
        if self.monitor:
            timer_id = self.monitor.start_timer(
                f"tilores_function_{function_name}", {"function": function_name, "args_count": len(kwargs)}
            )

        try:
            logger.info(f"🚀 Executing Tilores function: {function_name}")
            logger.debug(f"   Arguments: {list(kwargs.keys())}")

            # Check if function exists
            if function_name not in self.functions:
                error_msg = f"Unknown function: {function_name}. Available: {list(self.functions.keys())}"
                logger.error(f"❌ {error_msg}")
                self.stats["failed_executions"] += 1

                if self.monitor and timer_id:
                    self.monitor.end_timer(timer_id, success=False, error=error_msg)

                return FunctionResult(
                    success=False, error=error_msg, execution_time=time.time() - start_time, function_name=function_name
                )

            # Execute the function
            function = self.functions[function_name]
            result_data = function(**kwargs)

            execution_time = time.time() - start_time
            self.stats["successful_executions"] += 1
            self.stats["total_execution_time"] += execution_time

            # End monitoring timer
            if self.monitor and timer_id:
                self.monitor.end_timer(timer_id, success=True)

            # Check if result indicates an error
            if isinstance(result_data, dict) and "error" in result_data:
                logger.warning(f"⚠️ Function {function_name} returned error: {result_data['error']}")
                return FunctionResult(
                    success=False,
                    error=result_data["error"],
                    data=result_data,
                    execution_time=execution_time,
                    function_name=function_name,
                )

            logger.info(f"✅ Function {function_name} executed successfully in {execution_time:.2f}s")

            return FunctionResult(
                success=True, data=result_data, execution_time=execution_time, function_name=function_name
            )

        except Exception as e:
            execution_time = time.time() - start_time
            self.stats["failed_executions"] += 1
            self.stats["total_execution_time"] += execution_time

            error_msg = f"Function execution failed: {str(e)}"
            logger.error(f"❌ {error_msg}", exc_info=True)

            # End monitoring timer with error
            if self.monitor and timer_id:
                self.monitor.end_timer(timer_id, success=False, error=str(e))

            return FunctionResult(
                success=False, error=error_msg, execution_time=execution_time, function_name=function_name
            )

    def get_statistics(self) -> Dict[str, Any]:
        """Get execution statistics"""
        avg_time = 0.0
        if self.stats["successful_executions"] > 0:
            avg_time = self.stats["total_execution_time"] / self.stats["successful_executions"]

        return {
            "total_executions": self.stats["total_executions"],
            "successful_executions": self.stats["successful_executions"],
            "failed_executions": self.stats["failed_executions"],
            "success_rate": self.stats["successful_executions"] / max(1, self.stats["total_executions"]),
            "average_execution_time": avg_time,
            "total_execution_time": self.stats["total_execution_time"],
            "function_calls": self.stats["function_calls"],
            "available_functions": list(self.functions.keys()),
        }

    # Function implementations
    def _execute_search_customer(self, **kwargs) -> Dict[str, Any]:
        """Execute customer search"""
        search_tool = self.tools.get("search")
        if not search_tool:
            return {"error": "Search tool not available"}

        return search_tool.run(kwargs.get("query", ""))

    def _execute_search_customer_360(self, **kwargs) -> Dict[str, Any]:
        """Execute comprehensive customer 360 search"""
        search_tool = self.tools.get("search")
        if not search_tool:
            return {"error": "Search tool not available"}

        # Get basic search results
        base_results = search_tool.run(kwargs.get("query", ""))

        # Format for optimal LLM consumption
        return self._format_customer_360_response(base_results, kwargs.get("query", ""))

    def _execute_search_customer_batch(self, **kwargs) -> Dict[str, Any]:
        """Execute batch customer search with parallel processing"""
        search_tool = self.tools.get("search")
        if not search_tool:
            return {"error": "Search tool not available"}

        queries = kwargs.get("queries", [])
        if not queries:
            queries = [kwargs.get("query", "")]

        results = []
        for query in queries:
            result = search_tool.run(query)
            results.append(result)

        return {"batch_results": results, "batch_size": len(results), "timestamp": datetime.now().isoformat()}

    def _execute_fetch_entity(self, **kwargs) -> Dict[str, Any]:
        """Execute entity fetch"""
        fetch_tool = self.tools.get("fetchEntity")
        if not fetch_tool:
            return {"error": "Fetch entity tool not available"}

        return fetch_tool.run(kwargs.get("entity_id", ""))

    def _execute_get_entity_relationships(self, **kwargs) -> Dict[str, Any]:
        """Get entity relationships"""
        fetch_tool = self.tools.get("fetchEntity")
        if not fetch_tool:
            return {"error": "Fetch entity tool not available"}

        entity_data = fetch_tool.run(kwargs.get("entity_id", ""))

        # Extract relationships if available
        if isinstance(entity_data, dict):
            return {
                "entity_id": kwargs.get("entity_id", ""),
                "relationships": entity_data.get("relationships", []),
                "related_count": len(entity_data.get("relationships", [])),
            }

        return entity_data

    def _execute_get_credit_report(self, **kwargs) -> Dict[str, Any]:
        """Execute credit report retrieval"""
        credit_tool = self.tools.get("creditReport")
        if not credit_tool:
            return {"error": "Credit report tool not available"}

        return credit_tool.run(kwargs.get("customer_id", ""))

    def _execute_analyze_credit_score(self, **kwargs) -> Dict[str, Any]:
        """Analyze credit score from report"""
        credit_tool = self.tools.get("creditReport")
        if not credit_tool:
            return {"error": "Credit report tool not available"}

        report = credit_tool.run(kwargs.get("customer_id", ""))

        # Extract and analyze credit score
        if isinstance(report, dict) and "credit_score" in report:
            score = report.get("credit_score", 0)
            return {
                "customer_id": kwargs.get("customer_id", ""),
                "credit_score": score,
                "rating": self._get_credit_rating(score),
                "risk_level": self._get_risk_level(score),
            }

        return report

    def _execute_discover_fields(self, **kwargs) -> Dict[str, Any]:
        """Execute field discovery"""
        discovery_tool = self.tools.get("fieldDiscovery")
        if not discovery_tool:
            return {"error": "Field discovery tool not available"}

        return discovery_tool.run("")

    def _execute_get_field_metadata(self, **kwargs) -> Dict[str, Any]:
        """Get field metadata"""
        discovery_tool = self.tools.get("fieldDiscovery")
        if not discovery_tool:
            return {"error": "Field discovery tool not available"}

        all_fields = discovery_tool.run("")
        field_name = kwargs.get("field_name", "")

        # Extract metadata for specific field if provided
        if field_name and isinstance(all_fields, dict):
            field_info = all_fields.get(field_name, {})
            return {"field_name": field_name, "metadata": field_info, "exists": bool(field_info)}

        return all_fields

    def _format_customer_360_response(self, data: Any, query: str) -> Dict[str, Any]:
        """
        Format response for optimal LLM consumption
        Structures data to make it easier for LLMs to understand and process
        """
        if not isinstance(data, dict):
            return {"raw_data": data}

        formatted = {
            "query": query,
            "timestamp": datetime.now().isoformat(),
            "customer_summary": {},
            "data_sections": {},
            "metadata": {"source": "tilores", "format_version": "1.0"},
        }

        # Extract customer summary if available
        if "entity" in data or "customer" in data:
            customer_data = data.get("entity") or data.get("customer", {})
            if isinstance(customer_data, dict):
                formatted["customer_summary"] = {
                    "id": customer_data.get("id", ""),
                    "name": customer_data.get("name", ""),
                    "email": customer_data.get("email", ""),
                    "phone": customer_data.get("phone", ""),
                    "status": customer_data.get("status", "active"),
                }

        # Organize data into sections
        for key, value in data.items():
            if key not in ["entity", "customer"] and value:
                formatted["data_sections"][key] = value

        # Add response instruction for LLM
        formatted["llm_instruction"] = self._create_llm_instruction(formatted, query)

        return formatted

    def _create_llm_instruction(self, data: Dict[str, Any], query: str) -> str:
        """Create instruction for LLM on how to use the data"""
        sections = list(data.get("data_sections", {}).keys())

        if not sections:
            return "Use the customer summary to answer the query."

        instruction = f"To answer '{query}', reference the following data sections: "
        instruction += ", ".join(sections)
        instruction += ". Provide specific details from the relevant sections."

        return instruction

    def _get_credit_rating(self, score: int) -> str:
        """Get credit rating from score"""
        if score >= 800:
            return "Excellent"
        elif score >= 740:
            return "Very Good"
        elif score >= 670:
            return "Good"
        elif score >= 580:
            return "Fair"
        else:
            return "Poor"

    def _get_risk_level(self, score: int) -> str:
        """Get risk level from credit score"""
        if score >= 740:
            return "Low Risk"
        elif score >= 670:
            return "Medium Risk"
        else:
            return "High Risk"


# Global instance placeholder
function_executor: Optional[TiloresFunctionExecutor] = None


def initialize_function_executor(tilores_tools: Dict[str, Any], monitor: Optional[Any] = None):
    """
    Initialize the global function executor

    Args:
        tilores_tools: Dictionary of Tilores tools
        monitor: Optional monitoring instance
    """
    global function_executor
    function_executor = TiloresFunctionExecutor(tilores_tools, monitor)
    return function_executor
