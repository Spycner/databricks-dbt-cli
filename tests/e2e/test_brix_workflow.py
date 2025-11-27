"""End-to-end tests for full brix CLI workflow.

These tests exercise the complete brix workflow from scratch:
1. Create a profiles.yml using brix dbt profile commands
2. Create a dbt project using brix dbt project init
3. Run dbt via brix dbt run
4. Validate the results
"""

import pytest
from typer.testing import CliRunner

from brix.main import app

runner = CliRunner()


@pytest.mark.e2e
class TestBrixDuckDbWorkflow:
    """E2E test: create profile + project from scratch, run dbt with DuckDB in-memory."""

    def test_full_duckdb_workflow(self, tmp_path):
        """Test complete brix workflow with DuckDB in-memory."""
        profiles_dir = tmp_path / "profiles"
        profiles_dir.mkdir()
        profiles_path = profiles_dir / "profiles.yml"

        # 1. Initialize profiles.yml from template
        result = runner.invoke(app, ["dbt", "profile", "init", "-p", str(profiles_path)])
        assert result.exit_code == 0, f"profile init failed: {result.output}"
        assert profiles_path.exists(), "profiles.yml was not created"

        # 2. Add DuckDB in-memory profile
        result = runner.invoke(
            app,
            [
                "dbt",
                "profile",
                "edit",
                "-p",
                str(profiles_path),
                "--action",
                "add-profile",
                "--profile",
                "e2e_test",
                "--target",
                "dev",
                "--path",
                ":memory:",
            ],
        )
        assert result.exit_code == 0, f"profile edit failed: {result.output}"

        # Verify profile was added
        profiles_content = profiles_path.read_text()
        assert "e2e_test:" in profiles_content
        assert "type: duckdb" in profiles_content

        # 3. Create dbt project (no packages to avoid needing dbt deps)
        result = runner.invoke(
            app,
            [
                "dbt",
                "project",
                "init",
                "-n",
                "e2e_project",
                "-p",
                "e2e_test",
                "-b",
                str(tmp_path),
                "--with-example",
                "--no-packages",
            ],
        )
        assert result.exit_code == 0, f"project init failed: {result.output}"

        project_dir = tmp_path / "e2e_project"
        assert project_dir.exists(), "Project directory was not created"
        assert (project_dir / "dbt_project.yml").exists(), "dbt_project.yml was not created"
        assert (project_dir / "models").exists(), "models directory was not created"

        # 4. Run dbt
        result = runner.invoke(
            app,
            ["dbt", "run", "--project-dir", str(project_dir), "--profiles-dir", str(profiles_dir)],
        )
        assert result.exit_code == 0, f"dbt run failed: {result.output}"

        # 5. Validate target directory was created (dbt ran successfully)
        assert (project_dir / "target").exists(), "target directory was not created by dbt run"
