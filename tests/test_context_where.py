import sys
import unittest
from pathlib import Path

import sqlglot

# Add src directory to path to import the module
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from migration_analyser.tasks.context_where import (  # noqa: E402
    DangerousQueryError,
    check_dangerous_query,
    get_statement_type,
    has_where_clause,
    validate_sql_safety,
)


class TestContextWhere(unittest.TestCase):
    """Test suite for contextWhere module"""

    def test_dangerous_update_without_where(self):
        """Test that UPDATE without WHERE is detected as dangerous"""
        query = "UPDATE users SET status = 'inactive'"
        results = check_dangerous_query(query)

        self.assertEqual(len(results), 1)
        self.assertTrue(results[0]["is_dangerous"])
        self.assertEqual(results[0]["statement_type"], "UPDATE")
        self.assertFalse(results[0]["has_where"])
        self.assertIn("Dangerous", results[0]["message"])

    def test_safe_update_with_where(self):
        """Test that UPDATE with WHERE is detected as safe"""
        query = "UPDATE users SET status = 'inactive' WHERE user_id = 123"
        results = check_dangerous_query(query)

        self.assertEqual(len(results), 1)
        self.assertFalse(results[0]["is_dangerous"])
        self.assertEqual(results[0]["statement_type"], "UPDATE")
        self.assertTrue(results[0]["has_where"])
        self.assertIn("OK", results[0]["message"])

    def test_dangerous_delete_without_where(self):
        """Test that DELETE without WHERE is detected as dangerous"""
        query = "DELETE FROM logs"
        results = check_dangerous_query(query)

        self.assertEqual(len(results), 1)
        self.assertTrue(results[0]["is_dangerous"])
        self.assertEqual(results[0]["statement_type"], "DELETE")
        self.assertFalse(results[0]["has_where"])
        self.assertIn("Dangerous", results[0]["message"])

    def test_safe_delete_with_where(self):
        """Test that DELETE with WHERE is detected as safe"""
        query = "DELETE FROM logs WHERE created_at < '2023-01-01'"
        results = check_dangerous_query(query)

        self.assertEqual(len(results), 1)
        self.assertFalse(results[0]["is_dangerous"])
        self.assertEqual(results[0]["statement_type"], "DELETE")
        self.assertTrue(results[0]["has_where"])
        self.assertIn("OK", results[0]["message"])

    def test_safe_select_statement(self):
        """Test that SELECT statements are safe"""
        query = "SELECT * FROM users"
        results = check_dangerous_query(query)

        self.assertEqual(len(results), 1)
        self.assertFalse(results[0]["is_dangerous"])
        self.assertEqual(results[0]["statement_type"], "SELECT")
        self.assertIn("safe", results[0]["message"])

    def test_safe_insert_statement(self):
        """Test that INSERT statements are safe"""
        query = "INSERT INTO users (name) VALUES ('John')"
        results = check_dangerous_query(query)

        self.assertEqual(len(results), 1)
        self.assertFalse(results[0]["is_dangerous"])
        self.assertEqual(results[0]["statement_type"], "INSERT")
        self.assertIn("safe", results[0]["message"])

    def test_validate_sql_safety_returns_false_for_dangerous(self):
        """Test that validate_sql_safety returns False for dangerous queries"""
        query = "UPDATE users SET status = 'inactive'"
        result = validate_sql_safety(query, raise_on_danger=False)

        self.assertFalse(result)

    def test_validate_sql_safety_returns_true_for_safe(self):
        """Test that validate_sql_safety returns True for safe queries"""
        query = "UPDATE users SET status = 'inactive' WHERE user_id = 123"
        result = validate_sql_safety(query, raise_on_danger=False)

        self.assertTrue(result)

    def test_validate_sql_safety_raises_exception(self):
        """Test that validate_sql_safety raises exception when raise_on_danger=True"""
        query = "DELETE FROM logs"

        with self.assertRaises(DangerousQueryError) as context:
            validate_sql_safety(query, raise_on_danger=True)

        self.assertIn("Dangerous", str(context.exception))

    def test_multiple_statements(self):
        """Test handling of multiple SQL statements"""
        query = """
            UPDATE users SET status = 'active' WHERE user_id = 1;
            DELETE FROM logs WHERE created_at < '2023-01-01';
            SELECT * FROM users;
        """
        results = check_dangerous_query(query)

        # Should have 3 results
        self.assertEqual(len(results), 3)

        # All should be safe
        for result in results:
            self.assertFalse(result["is_dangerous"])

    def test_mixed_dangerous_and_safe_statements(self):
        """Test mix of dangerous and safe statements"""
        query = """
            UPDATE users SET status = 'active';
            DELETE FROM logs WHERE created_at < '2023-01-01';
        """
        results = check_dangerous_query(query)

        # Should have 2 results
        self.assertEqual(len(results), 2)

        # First should be dangerous (UPDATE without WHERE)
        self.assertTrue(results[0]["is_dangerous"])
        self.assertEqual(results[0]["statement_type"], "UPDATE")

        # Second should be safe (DELETE with WHERE)
        self.assertFalse(results[1]["is_dangerous"])
        self.assertEqual(results[1]["statement_type"], "DELETE")

    def test_has_where_clause_function(self):
        """Test the has_where_clause helper function"""
        query_with_where = "UPDATE users SET status = 'inactive' WHERE user_id = 123"
        query_without_where = "UPDATE users SET status = 'inactive'"

        ast_with_where = sqlglot.parse_one(query_with_where)
        ast_without_where = sqlglot.parse_one(query_without_where)

        self.assertTrue(has_where_clause(ast_with_where))
        self.assertFalse(has_where_clause(ast_without_where))

    def test_get_statement_type_function(self):
        """Test the get_statement_type helper function"""
        test_cases = [
            ("UPDATE users SET status = 'inactive'", "UPDATE"),
            ("DELETE FROM logs", "DELETE"),
            ("SELECT * FROM users", "SELECT"),
            ("INSERT INTO users (name) VALUES ('John')", "INSERT"),
        ]

        for query, expected_type in test_cases:
            ast = sqlglot.parse_one(query)
            result = get_statement_type(ast)
            self.assertEqual(result, expected_type)


if __name__ == "__main__":
    unittest.main()
