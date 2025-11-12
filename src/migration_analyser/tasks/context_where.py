import sqlglot
from sqlglot import exp


class DangerousQueryError(Exception):
    """Raised when a dangerous query without WHERE clause is detected"""

    pass


# Commands that are dangerous without WHERE clause
DANGEROUS_COMMANDS = {exp.Update, exp.Delete}


def has_where_clause(ast_node):
    """
    Check if an AST node has a WHERE clause.

    Args:
        ast_node: A sqlglot expression node (Update or Delete)

    Returns:
        bool: True if WHERE clause exists and is not empty, False otherwise
    """
    # Check if the node has a 'where' attribute
    if hasattr(ast_node, "args") and "where" in ast_node.args:
        where_clause = ast_node.args["where"]
        # Check if WHERE clause exists and is not None
        return where_clause is not None
    return False


def get_statement_type(ast_node):
    """
    Get the type of SQL statement from AST node.

    Args:
        ast_node: A sqlglot expression node

    Returns:
        str: The command type (e.g., 'UPDATE', 'DELETE', 'SELECT') or None
    """
    if isinstance(ast_node, exp.Update):
        return "UPDATE"
    elif isinstance(ast_node, exp.Delete):
        return "DELETE"
    elif isinstance(ast_node, exp.Select):
        return "SELECT"
    elif isinstance(ast_node, exp.Insert):
        return "INSERT"
    elif isinstance(ast_node, exp.Merge):
        return "MERGE"
    elif isinstance(ast_node, exp.Create):
        return "CREATE"
    elif isinstance(ast_node, exp.Drop):
        return "DROP"
    elif isinstance(ast_node, exp.Alter):
        return "ALTER"
    return type(ast_node).__name__.upper()


def check_ast_for_dangerous_commands(ast_node):
    """
    Recursively check an AST node for dangerous commands without WHERE clause.

    Args:
        ast_node: A sqlglot expression node

    Returns:
        list: List of dictionaries containing analysis results for each dangerous statement
    """
    results = []

    # Check if current node is a dangerous command
    node_type = type(ast_node)
    if node_type in DANGEROUS_COMMANDS:
        statement_type = get_statement_type(ast_node)
        has_where = has_where_clause(ast_node)
        is_dangerous = not has_where

        result = {
            "is_dangerous": is_dangerous,
            "statement_type": statement_type,
            "has_where": has_where,
            "message": "",
            "node": ast_node,
        }

        if is_dangerous:
            result["message"] = (
                f"Dangerous {statement_type} statement without WHERE clause detected!"
            )
        else:
            result["message"] = f"{statement_type} statement has WHERE clause - OK"

        results.append(result)

    # Recursively check child nodes
    if hasattr(ast_node, "args"):
        for value in ast_node.args.values():
            if value is not None:
                if isinstance(value, list):
                    for item in value:
                        if isinstance(item, exp.Expression):
                            results.extend(check_ast_for_dangerous_commands(item))
                elif isinstance(value, exp.Expression):
                    results.extend(check_ast_for_dangerous_commands(value))

    return results


def check_dangerous_query(sql_query, dialect=None):
    """
    Check if an SQL query contains dangerous commands without WHERE clause.

    Args:
        sql_query (str): The SQL query to check
        dialect (str): SQL dialect (e.g., 'postgres', 'mysql', 'sqlite', etc.)

    Returns:
        list: List of dictionaries with analysis results:
            {
                'is_dangerous': bool,
                'statement_type': str,
                'has_where': bool,
                'message': str,
                'node': sqlglot expression node
            }
    """
    try:
        # Parse the SQL query
        parsed = sqlglot.parse(sql_query, read=dialect)

        if not parsed:
            return [
                {
                    "is_dangerous": False,
                    "statement_type": None,
                    "has_where": False,
                    "message": "No valid SQL statement found",
                    "node": None,
                }
            ]

        results = []

        # Check each parsed statement
        for statement in parsed:
            if statement is None:
                continue

            # Check for dangerous commands in this statement and its children
            statement_results = check_ast_for_dangerous_commands(statement)

            # If no dangerous commands found, add a safe result
            if not statement_results:
                statement_type = get_statement_type(statement)
                results.append(
                    {
                        "is_dangerous": False,
                        "statement_type": statement_type,
                        "has_where": None,
                        "message": f"{statement_type} statement is safe",
                        "node": statement,
                    }
                )
            else:
                results.extend(statement_results)

        return results

    except Exception as e:
        return [
            {
                "is_dangerous": False,
                "statement_type": None,
                "has_where": False,
                "message": f"Error parsing SQL: {str(e)}",
                "node": None,
            }
        ]


def validate_sql_safety(sql_query, raise_on_danger=False, dialect=None):
    """
    Validate if an SQL query is safe to execute.

    Args:
        sql_query (str): The SQL query to validate
        raise_on_danger (bool): If True, raises exception on dangerous queries
        dialect (str): SQL dialect (e.g., 'postgres', 'mysql', 'sqlite', etc.)

    Returns:
        bool: True if safe, False if dangerous

    Raises:
        DangerousQueryError: If raise_on_danger is True and dangerous query detected
    """
    results = check_dangerous_query(sql_query, dialect=dialect)

    for result in results:
        if result["is_dangerous"]:
            if raise_on_danger:
                raise DangerousQueryError(result["message"])
            return False

    return True


class WhereClauseResult:
    """Result object for WHERE clause detection task"""

    def __init__(self, statement_num, results):
        self.statement_num = statement_num
        self.results = results
        self.is_safe = all(not r["is_dangerous"] for r in results)
        self.dangerous_count = sum(1 for r in results if r["is_dangerous"])
        self.statement_type = results[0]["statement_type"] if results else "UNKNOWN"

    def __str__(self):
        if self.is_safe:
            return (
                f"WhereClauseResult(statement={self.statement_num}, "
                f"type={self.statement_type}, status='SAFE')"
            )
        else:
            return (
                f"WhereClauseResult(statement={self.statement_num}, "
                f"type={self.statement_type}, status='DANGEROUS', "
                f"issues={self.dangerous_count})"
            )


def run_task(parsed_stmt, statement_num=1):
    """
    Run WHERE clause safety check on a single parsed SQL statement.

    Args:
        parsed_stmt: A sqlglot expression node (parsed SQL statement)
        statement_num: The statement number (for display purposes)

    Returns:
        WhereClauseResult: Object containing analysis results
    """
    # Check the parsed statement for dangerous commands
    results = check_ast_for_dangerous_commands(parsed_stmt)

    # If no dangerous commands found in the statement itself, check if it's safe
    if not results:
        statement_type = get_statement_type(parsed_stmt)
        results = [
            {
                "is_dangerous": False,
                "statement_type": statement_type,
                "has_where": None,
                "message": f"{statement_type} statement is safe",
                "node": parsed_stmt,
            }
        ]

    print(parsed_stmt)

    return WhereClauseResult(statement_num, results)


# Example usage
if __name__ == "__main__":
    test_queries = [
        "UPDATE users SET status = 'inactive'",  # Dangerous
        "UPDATE users SET status = 'inactive' WHERE user_id = 123",  # Safe
        "DELETE FROM logs",  # Dangerous
        "DELETE FROM logs WHERE created_at < '2023-01-01'",  # Safe
        "SELECT * FROM users",  # Safe
        "INSERT INTO users (name) VALUES ('John')",  # Safe
    ]

    for query in test_queries:
        print(f"Query: {query}")
        results = check_dangerous_query(query)
        for result in results:
            print(f"  - Dangerous: {result['is_dangerous']}")
            print(f"  - Type: {result['statement_type']}")
            print(f"  - Has WHERE: {result['has_where']}")
            print(f"  - Message: {result['message']}")
        print()
