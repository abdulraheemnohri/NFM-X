#!/usr/bin/env python3
"""
NFM-X Validation Test Script
Run this script to validate all fixes and ensure the project is working correctly.

Usage:
    python test_nfm_x.py
"""

import sys
import subprocess
from pathlib import Path
from typing import List


class TestResult:
    def __init__(self, name: str, passed: bool, message: str = ""):
        self.name = name
        self.passed = passed
        self.message = message
    
    def __str__(self):
        status = "PASS" if self.passed else "FAIL"
        emoji = "✅" if self.passed else "❌"
        return f"{emoji} {status}: {self.name}{f' - {self.message}' if self.message else ''}"


class NFMXValidator:
    def __init__(self):
        self.results: List[TestResult] = []
        self.project_root = Path.cwd()
    
    def add_result(self, result: TestResult):
        self.results.append(result)
    
    def run_all_tests(self):
        print("🚀 NFM-X Project Validation")
        print("=" * 60)
        
        self.test_python_version()
        self.test_required_files()
        self.test_no_urdu_content()
        self.test_no_utcnow_violations()
        self.test_import_statements()
        self.test_configuration()
        self.test_documentation()
        
        self.print_results()
        return all(r.passed for r in self.results)
    
    def test_python_version(self):
        try:
            version = sys.version_info
            if version >= (3, 10):
                self.add_result(TestResult("Python Version", True, f"Python {version.major}.{version.minor}.{version.micro}"))
            else:
                self.add_result(TestResult("Python Version", False, f"Python {version.major}.{version.minor} - Requires 3.10+"))
        except Exception as e:
            self.add_result(TestResult("Python Version", False, str(e)))
    
    def test_required_files(self):
        required_files = [
            "backend/app/main.py", "backend/app/config.py", "backend/app/api/conflicts.py",
            "backend/app/memory/capture.py", "backend/app/embeddings/vector_store.py",
            "backend/app/health.py", "backend/app/predictions/engine.py",
            "backend/app/api/memory.py", "backend/tests/test_memory_api.py",
            "backend/app/api/search.py", "backend/app/compression/engine.py",
            "backend/app/memory/models.py", "backend/app/world_model/engine.py",
            "backend/app/middleware/auth.py", "backend/app/middleware/rate_limit.py",
            "DEPLOYMENT.md", "CONTRIBUTING.md", "CODE_OF_CONDUCT.md",
            "requirements.txt", "requirements-dev.txt", "Dockerfile",
            "docker-compose.yml", "pytest.ini", "LICENSE"
        ]
        
        missing_files = []
        for file_path in required_files:
            full_path = self.project_root / file_path
            if not full_path.exists():
                missing_files.append(file_path)
        
        if missing_files:
            self.add_result(TestResult("Required Files", False, f"Missing: {', '.join(missing_files[:5])}"))
        else:
            self.add_result(TestResult("Required Files", True, f"All {len(required_files)} files present"))
    
    def test_no_urdu_content(self):
        urdu_keywords = ["اردو", "پاکستان", "میں", "ہے"]
        code_dirs = ["backend"]
        urdu_found = []
        
        for code_dir in code_dirs:
            dir_path = self.project_root / code_dir
            if dir_path.exists():
                for py_file in dir_path.rglob("*.py"):
                    try:
                        with open(py_file, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                            for keyword in urdu_keywords:
                                if keyword in content:
                                    urdu_found.append(str(py_file.relative_to(self.project_root)))
                                    break
                    except Exception:
                        continue
        
        if urdu_found:
            self.add_result(TestResult("No Urdu Content", False, f"Found in: {', '.join(urdu_found[:3])}"))
        else:
            self.add_result(TestResult("No Urdu Content", True, "No Urdu content found"))
    
    def test_no_utcnow_violations(self):
        violations = []
        for code_dir in ["backend"]:
            dir_path = self.project_root / code_dir
            if dir_path.exists():
                for py_file in dir_path.rglob("*.py"):
                    try:
                        with open(py_file, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                            if 'datetime.utcnow' in content:
                                violations.append(str(py_file.relative_to(self.project_root)))
                    except Exception:
                        continue
        
        if violations:
            self.add_result(TestResult("No datetime.utcnow()", False, f"Found in: {', '.join(violations[:3])}"))
        else:
            self.add_result(TestResult("No datetime.utcnow()", True, "No violations found"))
    
    def test_import_statements(self):
        issues = []
        for code_dir in ["backend/app"]:
            dir_path = self.project_root / code_dir
            if dir_path.exists():
                for py_file in dir_path.rglob("*.py"):
                    try:
                        with open(py_file, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                            if 'from backend.app.database import' in content:
                                issues.append(str(py_file.relative_to(self.project_root)))
                    except Exception:
                        continue
        
        if issues:
            self.add_result(TestResult("Import Statements", False, f"Old imports in: {', '.join(issues[:3])}"))
        else:
            self.add_result(TestResult("Import Statements", True, "All imports correct"))
    
    def test_configuration(self):
        config_files = ["requirements.txt", "requirements-dev.txt", "Dockerfile", "docker-compose.yml", "pytest.ini", ".env.example", ".gitignore"]
        missing = [f for f in config_files if not (self.project_root / f).exists()]
        
        if missing:
            self.add_result(TestResult("Configuration Files", False, f"Missing: {', '.join(missing)}"))
        else:
            self.add_result(TestResult("Configuration Files", True, "All config files present"))
    
    def test_documentation(self):
        doc_files = ["README.md", "DEPLOYMENT.md", "CONTRIBUTING.md", "CODE_OF_CONDUCT.md", "LICENSE"]
        missing = [f for f in doc_files if not (self.project_root / f).exists()]
        
        if missing:
            self.add_result(TestResult("Documentation", False, f"Missing: {', '.join(missing)}"))
        else:
            self.add_result(TestResult("Documentation", True, "All documentation present"))
    
    def print_results(self):
        print("
📊 Validation Results:")
        print("-" * 60)
        
        passed = sum(1 for r in self.results if r.passed)
        failed = sum(1 for r in self.results if not r.passed)
        total = len(self.results)
        
        for result in self.results:
            print(result)
        
        print("-" * 60)
        print(f"📈 Summary: {passed}/{total} validation checks passed")
        
        if failed == 0:
            print("🎉 All validation checks passed!")
        else:
            print(f"⚠️  {failed} validation check(s) failed.")
        print("=" * 60)


def run_pytest():
    try:
        result = subprocess.run(
            ["pytest", "--cov=backend", "--cov-report=term", "--cov-fail-under=80", "-v", "--tb=short"],
            cwd=str(Path.cwd()),
            capture_output=True,
            text=True,
            timeout=300
        )
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)


def main():
    print("🔍 NFM-X Project Validator")
    print("=" * 60)
    
    validator = NFMXValidator()
    all_passed = validator.run_all_tests()
    
    print("
🧪 Running pytest...")
    try:
        pytest_passed, stdout, stderr = run_pytest()
        
        if pytest_passed:
            print("✅ pytest: All tests passed")
            if stdout:
                lines = stdout.split('
')
                for line in lines[-10:]:
                    if line.strip():
                        print(f"  {line}")
        else:
            print("❌ pytest: Some tests failed")
            if stderr:
                lines = stderr.split('
')
                for line in lines[-10:]:
                    if line.strip():
                        print(f"  {line}")
    except Exception as e:
        print(f"⚠️  pytest not available: {e}")
        pytest_passed = False
    
    print("
" + "=" * 60)
    if all_passed and pytest_passed:
        print("🎉 PROJECT VALIDATION: PASSED")
        print("✅ All validation checks passed")
        print("✅ All pytest tests passed")
        print("🚀 Project is ready for production!")
    else:
        print("⚠️  PROJECT VALIDATION: PARTIAL")
        if not all_passed:
            print("❌ Some validation checks failed")
        if not pytest_passed:
            print("❌ pytest not available or tests failed")
        print("🔧 Please review and fix the issues above.")
    print("=" * 60)
    
    return 0 if (all_passed and pytest_passed) else 1


if __name__ == "__main__":
    sys.exit(main())