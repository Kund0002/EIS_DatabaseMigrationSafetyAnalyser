import sqlglot
from sqlglot import exp


class DropOperationError(Exception):
    """Raised when an unsafe DROP TABLE or DROP COLUMN operation is detected"""
    pass


def check_ast_for_drop_operations(ast_node):
    """
    Recursively check for unsafe DROP TABLE or ALTER TABLE DROP COLUMN operations.

    Args:
        ast_node: A sqlglot expression node

    Returns:
        list of dict: each dict represents a detection result
    """
    results = []

    # Case 1: DROP TABLE detected
    if isinstance(ast_node, exp.Drop):
        obj_type = ast_node.args.get("kind")
        if obj_type and obj_type.name.upper() == "TABLE":
            results.append({
                "is_dangerous": True,
                "statement_type": "DROP TABLE",
                "message": "DROP TABLE detected — this may cause irreversible data loss.",
                "node": ast_node,
            })

    # Case 2: ALTER TABLE ... DROP COLUMN detected
    if isinstance(ast_node, exp.Alter):
        actions = ast_node.args.get("actions")
        if actions:
            for action in actions:
                if isinstance(action, exp.Drop):
                    obj_type = action.args.get("kind")
                    if obj_type and obj_type.name.upper() == "COLUMN":
                        results.append({
                            "is_dangerous": True,
                            "statement_type": "ALTER TABLE DROP COLUMN",
                            "message": "ALTER TABLE DROP COLUMN detected — this may cause data loss or migration inconsistency.",
                            "node": ast_node,
                        })

    # Recursively traverse children
    if hasattr(ast_node, "args"):
        for value in ast_node.args.values():
            if value is not None:
                if isinstance(value, list):
                    for item in value:
                        if isinstance(item, exp.Expression):
                            results.extend(check_ast_for_drop_operations(item))
                elif isinstance(value, exp.Expression):
                    results.extend(check_ast_for_drop_operations(value))

    return results


class DropOperationResult:
    """Encapsulates results for DROP operation safety checks"""

    def __init__(self, statement_num, results):
        self.statement_num = statement_num
        self.results = results
        self.is_safe = all(not r["is_dangerous"] for r in results)
        self.dangerous_count = sum(1 for r in results if r["is_dangerous"])
        self.statement_type = (
            results[0]["statement_type"] if results else "UNKNOWN"
        )

    def __str__(self):
        if self.is_safe:
            return (
                f"DropOperationResult(statement={self.statement_num}, "
                f"type={self.statement_type}, status='SAFE')"
            )
        else:
            return (
                f"DropOperationResult(statement={self.statement_num}, "
                f"type={self.statement_type}, status='DANGEROUS', "
                f"issues={self.dangerous_count})"
            )


def run_task(parsed_stmt, statement_num=1):
    """
    Run the DROP operation safety check on a parsed SQL statement.

    Args:
        parsed_stmt: sqlglot expression node
        statement_num: integer, for display

    Returns:
        DropOperationResult
    """
    results = check_ast_for_drop_operations(parsed_stmt)

    if not results:
        # Mark safe if no DROP statements found
        results = [{
            "is_dangerous": False,
            "statement_type": "OTHER",
            "message": "No destructive DROP operations detected.",
            "node": parsed_stmt,
        }]

    return DropOperationResult(statement_num, results)
