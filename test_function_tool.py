from agents import function_tool

# Example function with @function_tool decorator
@function_tool
def get_questions_with_no_answer() -> str:
    """
    Get all questions that have no answer from the database.
    """
    return "No questions without answer found"

# Method 1: Access the original function through the FunctionTool object
print("Method 1: Access original function through FunctionTool")
print(f"Type of decorated function: {type(get_questions_with_no_answer)}")
print(f"Original function: {get_questions_with_no_answer.func}")
print(f"Calling original function: {get_questions_with_no_answer.func()}")

# Method 2: Create a separate non-decorated function
def _get_questions_with_no_answer() -> str:
    """
    Get all questions that have no answer from the database.
    """
    return "No questions without answer found"

@function_tool
def get_questions_with_no_answer_tool() -> str:
    """
    Get all questions that have no answer from the database.
    """
    return _get_questions_with_no_answer()

print("\nMethod 2: Separate non-decorated function")
print(f"Calling non-decorated function: {_get_questions_with_no_answer()}")
print(f"Type of tool function: {type(get_questions_with_no_answer_tool)}")

# Method 3: Use the FunctionTool's __call__ method (if available)
print("\nMethod 3: Try to call FunctionTool directly")
try:
    result = get_questions_with_no_answer()
    print(f"Direct call result: {result}")
except Exception as e:
    print(f"Direct call failed: {e}")
    print("FunctionTool objects are not directly callable") 