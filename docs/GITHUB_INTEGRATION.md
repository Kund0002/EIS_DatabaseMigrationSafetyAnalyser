# GitHub CI/CD Integration Guide

## Overview

The SQL Migration Safety Analyser is integrated into GitHub's CI/CD pipeline to automatically check SQL files in pull requests for potential safety issues (e.g., DELETE or UPDATE statements without WHERE clauses).

## How It Works

When a pull request is created or updated:

1. **Trigger**: The workflow triggers if any `.sql` files are modified
2. **Detection**: GitHub Actions finds all changed SQL files in the PR
3. **Analysis**: The migration analyser runs on each SQL file
4. **Results**:
   - ✅ **Pass**: If all statements are safe, the check passes (green checkmark)
   - ❌ **Fail**: If dangerous statements are found, the check fails (red X)
5. **Visibility**: Results appear in the PR's "Checks" tab

## Workflow File

The integration is defined in [`.github/workflows/pr-sql-check.yml`](file:///c:/Users/kundj/EIS_DatabaseMigrationAnalyser/.github/workflows/pr-sql-check.yml)

### Key Features

- **Automatic Detection**: Only runs when SQL files are changed
- **Efficient**: Skips if no SQL files in the PR
- **Clear Feedback**: Detailed output in workflow logs
- **Exit Codes**: Returns exit code 1 on failure, 0 on success

## Viewing Results

### In Pull Requests

1. Open your pull request on GitHub
2. Scroll to the "Checks" section at the bottom
3. Look for "SQL Migration Safety Check"
4. Click "Details" to see the full analysis output

### Example Output (Success)

```
✅ All statements are SAFE to execute
```

### Example Output (Failure)

```
⚠️  WARNING: Dangerous statements found in:
  - migrations/001_update_users.sql: 1 dangerous statement(s)

❌ ANALYSIS FAILED - Review these files before merging!
```

## Running Locally

You can run the same checks locally before pushing:

### Single File

```bash
python -m migration_analyser.cli path/to/your/migration.sql
```

### Multiple Files

```bash
python -m migration_analyser.cli migrations/*.sql
```

### Using the Installed Command

After installing the package:

```bash
migration-analyser path/to/your/migration.sql
```

## Configuration Options

### Disable Failure on Dangerous Statements

If you want to run the analyser but not fail the build:

```bash
python -m migration_analyser.cli --no-fail-on-danger migrations/*.sql
```

### Modify Trigger Paths

Edit `.github/workflows/pr-sql-check.yml` to change when the workflow runs:

```yaml
on:
  pull_request:
    branches: [ main ]
    paths:
      - '**.sql'              # All SQL files
      - 'migrations/**'       # Only files in migrations/
      - 'src/**/*.sql'        # SQL files in src/
```

## What Gets Checked

Currently, the analyser checks for:

1. **Missing WHERE Clauses**: DELETE and UPDATE statements without WHERE clauses
2. **Future Checks**: Additional safety checks can be added in `src/migration_analyser/tasks/`

## Troubleshooting

### Check Not Running

- Verify that your PR modifies `.sql` files
- Check that the workflow file exists in `.github/workflows/`
- Ensure the base branch is `main` (or update the workflow)

### False Positives

If the analyser flags a safe statement:
- Review the statement carefully
- Add a comment in the PR explaining why it's safe
- Consider using `--no-fail-on-danger` for exceptional cases

### Workflow Fails to Install

- Ensure `pyproject.toml` has correct dependencies
- Check Python version compatibility (requires Python 3.10+)

## Customization

### Adding New Safety Checks

1. Create a new task file in `src/migration_analyser/tasks/`
2. Implement your check logic
3. Import and call it in `engine.py`
4. The GitHub workflow will automatically use the new check

### Changing Python Version

Edit `.github/workflows/pr-sql-check.yml`:

```yaml
- name: Set up Python
  uses: actions/setup-python@v5
  with:
    python-version: "3.12"  # Change version here
```

## Best Practices

1. **Review Logs**: Always check the detailed logs when a check fails
2. **Run Locally First**: Test your SQL files locally before pushing
3. **Don't Override**: If the check fails, fix the issue rather than bypassing it
4. **Document Exceptions**: If you must merge dangerous SQL, document why in the PR

## Integration with Other Tools

### Pre-commit Hooks

The analyser can also run as a pre-commit hook. Add to `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: local
    hooks:
      - id: sql-safety-check
        name: SQL Migration Safety Check
        entry: python -m migration_analyser.cli
        language: system
        files: \.sql$
        pass_filenames: true
```

### Required Status Checks

To make this check mandatory before merging:

1. Go to your repository Settings
2. Navigate to Branches → Branch protection rules
3. Add or edit a rule for `main`
4. Enable "Require status checks to pass before merging"
5. Select "SQL Migration Safety Check"

## Support

For issues or questions about the analyser:
- Check the workflow logs for detailed error messages
- Review the SQL file flagged as dangerous
- Consult the team if you believe it's a false positive
