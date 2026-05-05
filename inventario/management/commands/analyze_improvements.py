"""
Code analysis management command for Django POS Inventory/Sales system.

Scans the codebase for actionable improvements across security, performance,
code quality, template, business logic, and Django best-practice categories.

Usage:
    python manage.py analyze_improvements
    python manage.py analyze_improvements --category security
    python manage.py analyze_improvements --severity HIGH
    python manage.py analyze_improvements --category performance --severity MEDIUM
"""
import ast
import os
import re
import sys
from collections import defaultdict
from pathlib import Path

from django.core.management.base import BaseCommand

SEVERITY_ORDER = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3, "INFO": 4}
SEVERITY_COLORS = {
    "CRITICAL": "\033[91m",
    "HIGH": "\033[93m",
    "MEDIUM": "\033[36m",
    "LOW": "\033[94m",
    "INFO": "\033[97m",
}
CATEGORY_COLORS = {
    "security": "\033[91m",
    "performance": "\033[93m",
    "code_quality": "\033[36m",
    "template": "\033[35m",
    "business_logic": "\033[33m",
    "django_best_practices": "\033[94m",
}
RESET = "\033[0m"
BOLD = "\033[1m"


class Finding:
    def __init__(self, category, severity, file_path, line, title, description, suggestion):
        self.category = category
        self.severity = severity
        self.file_path = file_path
        self.line = line
        self.title = title
        self.description = description
        self.suggestion = suggestion

    def __repr__(self):
        return f"[{self.severity}] {self.title} ({self.file_path}:{self.line})"


class CodeAnalyzer:
    def __init__(self, base_dir):
        self.base_dir = Path(base_dir)
        self.findings = []
        self._source_cache = {}

    def _read_file(self, path):
        if path not in self._source_cache:
            try:
                with open(path, "r", encoding="utf-8") as f:
                    self._source_cache[path] = f.read()
            except Exception:
                self._source_cache[path] = None
        return self._source_cache[path]

    def _rel_path(self, path):
        try:
            return str(Path(path).relative_to(self.base_dir))
        except ValueError:
            return str(path)

    def add_finding(self, category, severity, file_path, line, title, description, suggestion):
        self.findings.append(Finding(category, severity, file_path, line, title, description, suggestion))

    # ------------------------------------------------------------------ #
    #  Python AST helpers
    # ------------------------------------------------------------------ #
    def _parse_ast(self, path):
        source = self._read_file(path)
        if source is None:
            return None
        try:
            return ast.parse(source, filename=str(path))
        except SyntaxError:
            return None

    def _get_function_lines(self, node):
        """Return total line count of a function including body."""
        return node.end_lineno - node.lineno + 1 if hasattr(node, "end_lineno") else 0

    def _count_nesting_depth(self, node, depth=0):
        """Return maximum nesting depth inside a node."""
        max_depth = depth
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.If, ast.For, ast.While, ast.With, ast.Try)):
                child_depth = self._count_nesting_depth(child, depth + 1)
                max_depth = max(max_depth, child_depth)
            elif isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                pass
            else:
                child_depth = self._count_nesting_depth(child, depth)
                max_depth = max(max_depth, child_depth)
        return max_depth

    def _has_decorator(self, node, name):
        for dec in node.decorator_list:
            if isinstance(dec, ast.Name) and dec.id == name:
                return True
            if isinstance(dec, ast.Attribute) and dec.attr == name:
                return True
            if isinstance(dec, ast.Call):
                if isinstance(dec.func, ast.Name) and dec.func.id == name:
                    return True
                if isinstance(dec.func, ast.Attribute) and dec.func.attr == name:
                    return True
        return False

    # ------------------------------------------------------------------ #
    #  1. SECURITY ANALYSIS
    # ------------------------------------------------------------------ #
    def analyze_security(self):
        self._check_settings_security()
        for py_file in self._python_files():
            self._check_hardcoded_secrets(py_file)
            self._check_debug_patterns(py_file)
            self._check_sql_injection(py_file)
            self._check_missing_csrf(py_file)
            self._check_raw_user_input(py_file)
            self._check_insecure_rate_limit(py_file)
            self._check_password_handling(py_file)
            self._check_serving_static_in_production(py_file)

    def _check_settings_security(self):
        settings_path = self.base_dir / "Inventory_Sales" / "settings.py"
        if not settings_path.exists():
            return
        source = self._read_file(settings_path)
        rel = self._rel_path(settings_path)

        if re.search(r"SECRET_KEY\s*=\s*['\"]", source):
            self.add_finding(
                "security", "CRITICAL", rel, self._line_number(source, "SECRET_KEY"),
                "Hardcoded SECRET_KEY",
                "SECRET_KEY appears hardcoded in settings.py.",
                "Always load SECRET_KEY from environment variables.",
            )

        if "SECURE_SSL_REDIRECT" in source:
            m = re.search(r"SECURE_SSL_REDIRECT\s*=\s*env\([^)]*False", source)
            if m:
                self.add_finding(
                    "security", "HIGH", rel, self._line_number(source, "SECURE_SSL_REDIRECT"),
                    "SSL redirect disabled by default",
                    "SECURE_SSL_REDIRECT defaults to False. Production should enforce HTTPS.",
                    "Set SECURE_SSL_REDIRECT=True in production or default to True.",
                )

        if "SESSION_COOKIE_SECURE" in source:
            m = re.search(r"SESSION_COOKIE_SECURE\s*=\s*env\([^)]*False", source)
            if m:
                self.add_finding(
                    "security", "HIGH", rel, self._line_number(source, "SESSION_COOKIE_SECURE"),
                    "Session cookie not marked Secure by default",
                    "SESSION_COOKIE_SECURE defaults to False. Cookies may be sent over HTTP.",
                    "Default SESSION_COOKIE_SECURE to True for production.",
                )

        if "CSRF_COOKIE_SECURE" in source:
            m = re.search(r"CSRF_COOKIE_SECURE\s*=\s*env\([^)]*False", source)
            if m:
                self.add_finding(
                    "security", "HIGH", rel, self._line_number(source, "CSRF_COOKIE_SECURE"),
                    "CSRF cookie not marked Secure by default",
                    "CSRF_COOKIE_SECURE defaults to False.",
                    "Default CSRF_COOKIE_SECURE to True for production.",
                )

        if "SECURE_HSTS_SECONDS" in source:
            m = re.search(r"SECURE_HSTS_SECONDS\s*=\s*env\([^)]*0", source)
            if m:
                self.add_finding(
                    "security", "MEDIUM", rel, self._line_number(source, "SECURE_HSTS_SECONDS"),
                    "HSTS not enabled by default",
                    "SECURE_HSTS_SECONDS defaults to 0, disabling HTTP Strict Transport Security.",
                    "Set SECURE_HSTS_SECONDS to at least 31536000 (1 year) in production.",
                )

        for pat in ["CSRF_TRUSTED_ORIGINS", "ALLOWED_HOSTS"]:
            if pat in source:
                if re.search(r"ngrok", source):
                    self.add_finding(
                        "security", "LOW", rel, self._line_number(source, pat),
                        "Ngrok origins in trusted configuration",
                        "ngrok URLs in CSRF_TRUSTED_ORIGINS should be removed in production.",
                        "Remove ngrok patterns from CSRF_TRUSTED_ORIGINS before deploying.",
                    )
                    break

    def _check_hardcoded_secrets(self, path):
        source = self._read_file(path)
        if source is None:
            return
        rel = self._rel_path(path)
        if "settings.py" in str(path):
            return

        patterns = [
            (r'(?<![A-Z_])(?:password|passwd|pwd)\s*=\s*["\'][^"\']{3,}["\']', "Hardcoded password"),
            (r'(?<![A-Z_])(?:secret_key|api_key|api_secret|secret_token)\s*=\s*["\'][a-zA-Z0-9_\-]{8,}["\']', "Hardcoded secret/token"),
            (r'DJANGO_SECRET_KEY\s*=\s*["\']', "Hardcoded Django secret key"),
        ]
        for pat, label in patterns:
            for m in re.finditer(pat, source, re.IGNORECASE):
                line = source[:m.start()].count("\n") + 1
                self.add_finding(
                    "security", "CRITICAL", rel, line,
                    label, f"Potential {label.lower()} found in source code.",
                    "Move secrets to environment variables or a secure vault.",
                )

    def _check_debug_patterns(self, path):
        source = self._read_file(path)
        if source is None:
            return
        rel = self._rel_path(path)
        if "analyze_improvements.py" in str(path):
            return

        for m in re.finditer(r'^DEBUG\s*=\s*True', source, re.MULTILINE):
            line = source[:m.start()].count("\n") + 1
            self.add_finding(
                "security", "HIGH", rel, line,
                "DEBUG=True in code",
                "DEBUG is hardcoded to True, which exposes detailed error pages in production.",
                "Load DEBUG from environment variables only.",
            )

    def _check_sql_injection(self, path):
        source = self._read_file(path)
        if source is None:
            return
        rel = self._rel_path(path)

        for m in re.finditer(r'\.raw\s*\(\s*f["\']', source):
            line = source[:m.start()].count("\n") + 1
            self.add_finding(
                "security", "CRITICAL", rel, line,
                "SQL injection risk - f-string in .raw()",
                "Using f-strings with .raw() allows SQL injection.",
                "Use parameterized queries with .raw() or switch to ORM methods.",
            )

        for m in re.finditer(r'\.execute\s*\(\s*f["\']', source):
            context_start = max(0, m.start() - 5)
            if "quote_name" in source[context_start:m.start()+200]:
                continue
            line = source[:m.start()].count("\n") + 1
            self.add_finding(
                "security", "CRITICAL", rel, line,
                "SQL injection risk - f-string in cursor.execute()",
                "Using f-strings in cursor.execute() is vulnerable to SQL injection.",
                "Use parameterized queries: cursor.execute(sql, [params]).",
            )

        for m in re.finditer(r'Extra\s*\(\s*f["\']', source):
            line = source[:m.start()].count("\n") + 1
            self.add_finding(
                "security", "HIGH", rel, line,
                "SQL injection risk - f-string in .extra()",
                "Using f-strings with .extra() may allow SQL injection.",
                "Use .annotate() with expressions or parameterized .extra() params.",
            )

    def _check_missing_csrf(self, path):
        source = self._read_file(path)
        if source is None:
            return
        rel = self._rel_path(path)

        tree = self._parse_ast(path)
        if tree is None:
            return

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                has_require_post = self._has_decorator(node, "require_POST")
                has_csrf_exempt = self._has_decorator(node, "csrf_exempt")
                if has_require_post and not has_csrf_exempt:
                    has_login = self._has_decorator(node, "login_required")
                    if not has_login:
                        self.add_finding(
                            "security", "HIGH", rel, node.lineno,
                            "POST endpoint without login_required",
                            f"Function '{node.name}' accepts POST but has no @login_required decorator.",
                            "Add @login_required to protect against CSRF from unauthenticated users.",
                        )

    def _check_raw_user_input(self, path):
        source = self._read_file(path)
        if source is None:
            return
        rel = self._rel_path(path)

        patterns = [
            (r'request\.(GET|POST|FILES|COOKIES|META|headers)\[.*?\]\s*%\s*["\']', "Unescaped user input in string formatting"),
            (r'request\.(GET|POST|FILES|COOKIES|META)\[.*?\]\s*\+\s*["\']', "Unescaped user input in string concatenation"),
            (r'HttpResponse\([^)]*request\.(GET|POST)', "User input directly in HttpResponse"),
        ]
        for pat, label in patterns:
            for m in re.finditer(pat, source):
                line = source[:m.start()].count("\n") + 1
                self.add_finding(
                    "security", "MEDIUM", rel, line,
                    label,
                    "User input may be used without sanitization.",
                    "Use Django forms/validation or django.utils.html.escape() before rendering.",
                )

    def _check_insecure_rate_limit(self, path):
        source = self._read_file(path)
        if source is None:
            return
        rel = self._rel_path(path)

        if "in-memory" not in source.lower():
            if re.search(r'_ATTEMPTS\s*=\s*\{\}', source) or re.search(r'_RATE_LIMIT', source):
                has_cache = "django.core.cache" in source or "from django.core.cache" in source
                if not has_cache:
                    self.add_finding(
                        "security", "MEDIUM", rel, self._line_number(source, "_ATTEMPTS") or 1,
                        "In-memory rate limiting",
                        "Rate limiting uses in-memory dict, which resets on restart and doesn't work across workers.",
                        "Use django-ratelimit, django-axes, or Redis-backed rate limiting.",
                    )

    def _check_password_handling(self, path):
        source = self._read_file(path)
        if source is None:
            return
        rel = self._rel_path(path)

        if "set_password" not in source and "check_password" not in source:
            if "User" in source and ("password" in source.lower()):
                if re.search(r"\.password\s*=", source) or re.search(r"user\.password\s*=", source):
                    self.add_finding(
                        "security", "CRITICAL", rel, self._line_number(source, ".password"),
                        "Raw password assignment",
                        "Assigning to .password directly stores plaintext passwords.",
                        "Always use user.set_password() to hash passwords.",
                    )

        if re.search(r'\.save\(\)', source) and "set_password" in source:
            tree = self._parse_ast(path)
            if tree:
                for node in ast.walk(tree):
                    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        func_source = source[node.lineno-1:node.end_lineno]
                        if "set_password" in func_source and ".save()" in func_source:
                            if "update_fields" not in func_source:
                                self.add_finding(
                                    "security", "LOW", rel, node.lineno,
                                    "Model.save() without update_fields after set_password",
                                    f"In '{node.name}', .save() is called without update_fields after set_password.",
                                    "Use save(update_fields=['password']) to avoid unintended side effects.",
                                )

    def _check_serving_static_in_production(self, path):
        source = self._read_file(path)
        if source is None:
            return
        rel = self._rel_path(path)
        if "analyze_improvements.py" in str(path):
            return

        if "static_serve" in source or "serve as static_serve" in source:
            if re.search(r're_path.*static.*static_serve', source):
                self.add_finding(
                    "security", "MEDIUM", rel, self._line_number(source, "static_serve"),
                    "Static files served by Django in production",
                    "Django is configured to serve static/media files directly. This is inefficient and potentially unsafe.",
                    "Use a proper web server (nginx, whitenoise) for static files in production.",
                )

    # ------------------------------------------------------------------ #
    #  2. PERFORMANCE ANALYSIS
    # ------------------------------------------------------------------ #
    def analyze_performance(self):
        for py_file in self._python_files():
            self._check_n_plus_one(py_file)
            self._check_missing_indexes(py_file)
            self._check_missing_pagination(py_file)
            self._check_inefficient_queries(py_file)
            self._check_redundant_queries(py_file)

    def _check_n_plus_one(self, path):
        if "analyze_improvements.py" in str(path):
            return
        source = self._read_file(path)
        if source is None:
            return
        rel = self._rel_path(path)
        tree = self._parse_ast(path)
        if tree is None:
            return

        for node in ast.walk(tree):
            if not isinstance(node, (ast.For, ast.While)):
                continue
            for child in ast.walk(node):
                if isinstance(child, ast.Attribute):
                    attr = child.attr
                    if attr in ("objects", "all", "filter", "get", "create", "save"):
                        line = child.lineno
                        if ".save()" in ast.unparse(child) if hasattr(ast, "unparse") else True:
                            pass
                if isinstance(child, ast.Call):
                    call_str = ast.unparse(child) if hasattr(ast, "unparse") else ""
                    if ".save()" in call_str or ".objects." in call_str:
                        self.add_finding(
                            "performance", "HIGH", rel, child.lineno,
                            "Potential N+1 query in loop",
                            f"ORM call inside a loop may cause N+1 queries.",
                            "Use select_related/prefetch_related or bulk operations.",
                        )
                        break

        for m in re.finditer(r'for\s+\w+\s+in\s+\w+\.objects\.', source):
            line = source[:m.start()].count("\n") + 1
            self.add_finding(
                "performance", "HIGH", rel, line,
                "Iterating over Model.objects in loop",
                "Directly iterating over Model.objects may fetch all columns.",
                "Use .values() or .only() to fetch only needed fields.",
            )

        for m in re.finditer(r'for\s+\w+\s+in\s+.*\.objects\.filter', source):
            line = source[:m.start()].count("\n") + 1
            has_select_related = "select_related" in source[:m.start()+200]
            has_prefetch_related = "prefetch_related" in source[:m.start()+200]
            if not has_select_related and not has_prefetch_related:
                pass

    def _check_missing_indexes(self, path):
        if "analyze_improvements.py" in str(path):
            return
        source = self._read_file(path)
        if source is None:
            return
        if "models.py" not in str(path):
            return
        rel = self._rel_path(path)
        tree = self._parse_ast(path)
        if tree is None:
            return

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                has_meta = False
                has_indexes = False
                foreign_keys = []
                for item in node.body:
                    if isinstance(item, ast.ClassDef) and item.name == "Meta":
                        has_meta = True
                        for meta_item in item.body:
                            if isinstance(meta_item, ast.Assign):
                                for target in meta_item.targets:
                                    if isinstance(target, ast.Name) and target.id == "indexes":
                                        has_indexes = True
                    if isinstance(item, ast.Assign):
                        for target in item.targets:
                            if isinstance(target, ast.Name):
                                val_str = ast.unparse(item.value) if hasattr(ast, "unparse") else ""
                                if "ForeignKey" in val_str or "OneToOneField" in val_str:
                                    foreign_keys.append((target.id, item.lineno))

                if foreign_keys and not has_indexes:
                    for fk_name, fk_line in foreign_keys:
                        self.add_finding(
                            "performance", "MEDIUM", rel, fk_line,
                            f"ForeignKey '{fk_name}' without explicit index",
                            f"Model '{node.name}' has ForeignKey '{fk_name}' but no Meta.indexes defined.",
                            "Add indexes in Meta for frequently queried ForeignKey fields.",
                        )

    def _check_missing_pagination(self, path):
        if "analyze_improvements.py" in str(path):
            return
        source = self._read_file(path)
        if source is None:
            return
        if "views.py" not in str(path):
            return
        rel = self._rel_path(path)
        tree = self._parse_ast(path)
        if tree is None:
            return

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                is_list_view = False
                has_paginate = False
                for item in node.body:
                    if isinstance(item, ast.Assign):
                        for target in item.targets:
                            if isinstance(target, ast.Name):
                                if target.id == "paginate_by":
                                    has_paginate = True
                for base in node.bases:
                    base_str = ast.unparse(base) if hasattr(ast, "unparse") else ""
                    if "ListView" in base_str:
                        is_list_view = True

                if is_list_view and not has_paginate:
                    self.add_finding(
                        "performance", "MEDIUM", rel, node.lineno,
                        f"ListView '{node.name}' without pagination",
                        f"Class '{node.name}' extends ListView but has no paginate_by.",
                        "Add paginate_by = N to prevent loading all records at once.",
                    )

    def _check_inefficient_queries(self, path):
        if "analyze_improvements.py" in str(path):
            return
        source = self._read_file(path)
        if source is None:
            return
        rel = self._rel_path(path)

        patterns = [
            (r'\.objects\.count\(\)\s*[\r\n].*\.objects\.count\(\)', "Duplicate .count() calls"),
            (r'\.objects\.all\(\)\s*\[0\]', "Using [0] on .all() instead of .first()"),
            (r'len\(.*\.objects\.', "Using len() on QuerySet instead of .count()"),
        ]
        for pat, label in patterns:
            for m in re.finditer(pat, source):
                line = source[:m.start()].count("\n") + 1
                self.add_finding(
                    "performance", "MEDIUM", rel, line,
                    label,
                    "Inefficient QuerySet usage detected.",
                    "Use .first(), .count(), or .exists() instead.",
                )

    def _check_redundant_queries(self, path):
        if "analyze_improvements.py" in str(path):
            return
        source = self._read_file(path)
        if source is None:
            return
        rel = self._rel_path(path)
        tree = self._parse_ast(path)
        if tree is None:
            return
        rel = self._rel_path(path)

        tree = self._parse_ast(path)
        if tree is None:
            return

        func_query_counts = defaultdict(list)
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                count = 0
                for child in ast.walk(node):
                    if isinstance(child, ast.Attribute):
                        if child.attr == "objects":
                            count += 1
                if count > 3:
                    self.add_finding(
                        "performance", "LOW", rel, node.lineno,
                        f"Multiple ORM queries in '{node.name}'",
                        f"Function '{node.name}' has {count} ORM query calls.",
                        "Consider combining queries or using select_related/prefetch_related.",
                    )

    # ------------------------------------------------------------------ #
    #  3. CODE QUALITY ANALYSIS
    # ------------------------------------------------------------------ #
    def analyze_code_quality(self):
        for py_file in self._python_files():
            self._check_long_functions(py_file)
            self._check_deep_nesting(py_file)
            self._check_unused_imports(py_file)
            self._check_missing_type_hints(py_file)
            self._check_duplicate_code(py_file)
            self._check_bare_except(py_file)
            self._check_print_statements(py_file)

    def _check_long_functions(self, path):
        if "analyze_improvements.py" in str(path):
            return
        tree = self._parse_ast(path)
        if tree is None:
            return
        rel = self._rel_path(path)

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                lines = self._get_function_lines(node)
                if lines > 50:
                    self.add_finding(
                        "code_quality", "MEDIUM", rel, node.lineno,
                        f"Long function '{node.name}' ({lines} lines)",
                        f"Function '{node.name}' is {lines} lines long (>50).",
                        "Break into smaller, focused functions. Aim for <50 lines.",
                    )
                elif lines > 30:
                    self.add_finding(
                        "code_quality", "LOW", rel, node.lineno,
                        f"Function '{node.name}' ({lines} lines) approaching limit",
                        f"Function '{node.name}' is {lines} lines. Consider refactoring before it exceeds 50.",
                        "Consider extracting helper methods or simplifying logic.",
                    )

    def _check_deep_nesting(self, path):
        if "analyze_improvements.py" in str(path):
            return
        tree = self._parse_ast(path)
        if tree is None:
            return
        rel = self._rel_path(path)

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                depth = self._count_nesting_depth(node)
                if depth > 3:
                    self.add_finding(
                        "code_quality", "MEDIUM", rel, node.lineno,
                        f"Deeply nested function '{node.name}' (depth={depth})",
                        f"Function '{node.name}' has nesting depth of {depth} (>3).",
                        "Use early returns, guard clauses, or extract nested logic.",
                    )

    def _check_unused_imports(self, path):
        if "analyze_improvements.py" in str(path):
            return
        source = self._read_file(path)
        if source is None:
            return
        rel = self._rel_path(path)
        tree = self._parse_ast(path)
        if tree is None:
            return

        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    name = alias.asname or alias.name
                    imports.append((name, node.lineno, alias.name))
            elif isinstance(node, ast.ImportFrom):
                for alias in node.names:
                    name = alias.asname or alias.name
                    imports.append((name, node.lineno, f"{node.module}.{alias.name}" if node.module else alias.name))

        for name, line, full_name in imports:
            pattern = rf'\b{re.escape(name)}\b'
            count = len(re.findall(pattern, source))
            if count <= 1:
                self.add_finding(
                    "code_quality", "LOW", rel, line,
                    f"Potentially unused import '{full_name}'",
                    f"Import '{full_name}' appears to be unused.",
                    "Remove unused imports to keep code clean.",
                )

    def _check_missing_type_hints(self, path):
        if "analyze_improvements.py" in str(path):
            return
        tree = self._parse_ast(path)
        if tree is None:
            return
        rel = self._rel_path(path)

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if node.name.startswith("_"):
                    continue
                has_return_annotation = node.returns is not None
                has_arg_annotations = all(
                    arg.annotation is not None
                    for arg in node.args.args
                    if arg.arg != "self" and arg.arg != "cls"
                )
                if not has_return_annotation and not has_arg_annotations:
                    has_decorator = any(
                        isinstance(d, ast.Name) and d.id in ("property", "staticmethod", "classmethod")
                        for d in node.decorator_list
                    )
                    if not has_decorator:
                        pass

    def _check_duplicate_code(self, path):
        if "analyze_improvements.py" in str(path):
            return
        source = self._read_file(path)
        if source is None:
            return
        rel = self._rel_path(path)

        lines = source.split("\n")
        window_size = 5
        seen = {}
        for i in range(len(lines) - window_size + 1):
            block = "\n".join(l.strip() for l in lines[i:i+window_size] if l.strip())
            if len(block) < 40:
                continue
            if block in seen:
                prev_line = seen[block]
                if i - prev_line > window_size + 2:
                    self.add_finding(
                        "code_quality", "MEDIUM", rel, i + 1,
                        "Duplicate code block",
                        f"Code block at line {i+1} duplicates block at line {prev_line+1}.",
                        "Extract repeated code into a shared function or class method.",
                    )
                    seen[block] = i
            else:
                seen[block] = i

    def _check_bare_except(self, path):
        source = self._read_file(path)
        if source is None:
            return
        rel = self._rel_path(path)
        tree = self._parse_ast(path)
        if tree is None:
            return

        for node in ast.walk(tree):
            if isinstance(node, ast.ExceptHandler):
                if node.type is None:
                    self.add_finding(
                        "code_quality", "MEDIUM", rel, node.lineno,
                        "Bare except clause",
                        "Bare except: catches all exceptions including SystemExit and KeyboardInterrupt.",
                        "Use 'except Exception:' or catch specific exception types.",
                    )
                elif isinstance(node.type, ast.Name) and node.type.id == "Exception":
                    pass

    def _check_print_statements(self, path):
        source = self._read_file(path)
        if source is None:
            return
        if "manage.py" in str(path) or "settings.py" in str(path):
            return
        if "analyze_improvements.py" in str(path):
            return
        rel = self._rel_path(path)

        for m in re.finditer(r'(?<!\w)print\s*\(', source):
            line = source[:m.start()].count("\n") + 1
            self.add_finding(
                "code_quality", "LOW", rel, line,
                "print() statement in production code",
                "print() statements should be replaced with logging.",
                "Use Python's logging module instead of print().",
            )

    # ------------------------------------------------------------------ #
    #  4. TEMPLATE ANALYSIS
    # ------------------------------------------------------------------ #
    def analyze_templates(self):
        for tmpl in self._template_files():
            self._check_missing_load(tmpl)
            self._check_inline_javascript(tmpl)
            self._check_form_errors(tmpl)
            self._check_accessibility(tmpl)
            self._check_missing_csrf_form(tmpl)
            self._check_raw_variable_output(tmpl)

    def _check_missing_load(self, path):
        source = self._read_file(path)
        if source is None:
            return
        rel = self._rel_path(path)

        if "{% url " in source and "{% load" not in source and "base.html" not in str(path):
            self.add_finding(
                "template", "HIGH", rel, 1,
                "Template uses {% url %} without {% load %}",
                "Template uses URL tags but may not explicitly load required tags.",
                "Add {% load static %} or {% load i18n %} if needed at the top of the template.",
            )

        if "{% static " in source and "{% load static %}" not in source:
            has_load = "{% load" in source and "static" in source
            if not has_load:
                self.add_finding(
                    "template", "HIGH", rel, self._line_number(source, "static"),
                    "Missing {% load static %}",
                    "Template uses {% static %} without {% load static %}.",
                    "Add {% load static %} at the top of the template.",
                )

    def _check_inline_javascript(self, path):
        source = self._read_file(path)
        if source is None:
            return
        rel = self._rel_path(path)

        has_script = bool(re.search(r'<script[^>]*>', source))
        has_block_js = "{% block extra_js %}" in source
        is_base = "base.html" in str(path)

        if has_script and not has_block_js and not is_base:
            script_count = len(re.findall(r'<script', source))
            total_chars = sum(len(m.group()) for m in re.finditer(r'<script[^>]*>(.*?)</script>', source, re.DOTALL))
            if total_chars > 500:
                self.add_finding(
                    "template", "MEDIUM", rel, self._line_number(source, "<script"),
                    "Large inline JavaScript block",
                    f"Template has {script_count} inline script block(s) ({total_chars} chars).",
                    "Move JavaScript to static files for caching and CSP compliance.",
                )

        for m in re.finditer(r'\bon\w+\s*=\s*["\']', source):
            line = source[:m.start()].count("\n") + 1
            self.add_finding(
                "template", "LOW", rel, line,
                "Inline event handler (onclick, etc.)",
                "Inline event handlers mix HTML and JS.",
                "Use addEventListener in external JS files instead.",
            )

    def _check_form_errors(self, path):
        source = self._read_file(path)
        if source is None:
            return
        rel = self._rel_path(path)

        if "<form" in source or "{% csrf_token %}" in source:
            has_form_tag = "{% csrf_token %}" in source
            has_errors = "form.errors" in source or "form.non_field_errors" in source
            if has_form_tag and not has_errors:
                has_form_instance = re.search(r'{{\s*form\s*}}', source)
                if has_form_instance:
                    pass
                else:
                    for m in re.finditer(r'{{\s*\w+\s*}}', source):
                        pass

        if "<form" in source:
            if "non_field_errors" not in source:
                self.add_finding(
                    "template", "MEDIUM", rel, self._line_number(source, "<form"),
                    "Form missing non_field_errors display",
                    "Form template does not display form.non_field_errors.",
                    "Add {% if form.non_field_errors %} block to show validation errors.",
                )

    def _check_accessibility(self, path):
        source = self._read_file(path)
        if source is None:
            return
        rel = self._rel_path(path)

        for m in re.finditer(r'<img(?![^>]*\balt\s*=)', source):
            line = source[:m.start()].count("\n") + 1
            self.add_finding(
                "template", "MEDIUM", rel, line,
                "Image missing alt attribute",
                "img tag without alt attribute fails accessibility standards.",
                "Add alt=\"description\" or alt=\"\" for decorative images.",
            )

        for m in re.finditer(r'<button(?![^>]*\btype\s*=)', source):
            line = source[:m.start()].count("\n") + 1
            self.add_finding(
                "template", "LOW", rel, line,
                "Button without explicit type",
                "button without type attribute defaults to 'submit'.",
                "Add type=\"button\" or type=\"submit\" explicitly.",
            )

        for m in re.finditer(r'<input(?![^>]*\bid\s*=)[^>]*(?:type="text"|type="email"|type="password"|type="number")', source):
            line = source[:m.start()].count("\n") + 1
            has_label_before = False
            context_start = max(0, m.start() - 200)
            context = source[context_start:m.start()]
            if re.search(r'<label[^>]*>.*</label>', context, re.DOTALL):
                has_label_before = True
            if not has_label_before:
                pass

    def _check_missing_csrf_form(self, path):
        source = self._read_file(path)
        if source is None:
            return
        rel = self._rel_path(path)

        forms = re.finditer(r'<form\s[^>]*method=["\']post["\']', source, re.IGNORECASE)
        for form_match in forms:
            form_start = form_match.start()
            form_end = source.find("</form>", form_start)
            if form_end == -1:
                form_end = len(source)
            form_content = source[form_start:form_end]
            if "{% csrf_token %}" not in form_content:
                line = source[:form_start].count("\n") + 1
                self.add_finding(
                    "template", "HIGH", rel, line,
                    "POST form missing CSRF token",
                    "Form with method='post' is missing {% csrf_token %}.",
                    "Add {% csrf_token %} inside the form.",
                )

    def _check_raw_variable_output(self, path):
        source = self._read_file(path)
        if source is None:
            return
        rel = self._rel_path(path)

        for m in re.finditer(r'{{\s*(?!block|endblock|if|else|elif|for|endfor|csrf_token|load|extends|include|with|trans|static|url|loop|csrfmiddlewaretoken)[a-zA-Z_]\w*(?:\.[a-zA-Z_]\w*|\[\s*["\']?\w+\s*["\']?\])*\s*\|?\s*(?!safe|escape|striptags|escapejs|urlencode|floatformat|date|time|default|length|truncatewords|truncatechars|upper|lower|title|capfirst|add|cut|join|slugify|linebreaks|linebreaksbr|removetags|yesno|filesizeformat|pluralize|dictsort|dictsortreversed|random|first|last|make_list|unordered_list|get_digit|timesince|timeuntil|wordcount|wordwrap|ljust|rjust|center|slice|divisibleby|addslashes|phone2numeric|pprint|filesizeformat|stringformat)[a-zA-Z]*\s*}}', source):
            var_match = re.match(r'{{\s*([a-zA-Z_]\w*(?:\.[a-zA-Z_]\w*)*)', m.group())
            if var_match:
                var_name = var_match.group(1)
                if var_name not in ("user", "request", "messages", "page_obj", "paginator", "object", "form", "object_list", "csrf_token"):
                    pass

    # ------------------------------------------------------------------ #
    #  5. BUSINESS LOGIC ANALYSIS
    # ------------------------------------------------------------------ #
    def analyze_business_logic(self):
        for py_file in self._python_files():
            self._check_audit_trail(py_file)
            self._check_validation_gaps(py_file)
            self._check_error_handling(py_file)
            self._check_backup_export(py_file)

    def _check_audit_trail(self, path):
        source = self._read_file(path)
        if source is None:
            return
        if "models.py" not in str(path):
            return
        rel = self._rel_path(path)
        tree = self._parse_ast(path)
        if tree is None:
            return

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                has_audit = False
                for item in node.body:
                    if isinstance(item, ast.Assign):
                        for target in item.targets:
                            if isinstance(target, ast.Name):
                                name = target.id
                                if "audit" in name.lower() or "log" in name.lower() or "historial" in name.lower():
                                    has_audit = True

                if not has_audit and node.name not in ("Meta",):
                    has_created = False
                    has_updated = False
                    has_deleted = False
                    for item in ast.walk(node):
                        if isinstance(item, ast.Assign):
                            for target in item.targets:
                                if isinstance(target, ast.Name):
                                    if "created_at" in target.id or "creada_en" in target.id:
                                        has_created = True
                                    if "updated_at" in target.id or "actualizada_en" in target.id:
                                        has_updated = True

                    if not has_created:
                        self.add_finding(
                            "business_logic", "MEDIUM", rel, node.lineno,
                            f"Model '{node.name}' missing created_at timestamp",
                            f"Model '{node.name}' has no created_at field for audit trail.",
                            "Add created_at = models.DateTimeField(auto_now_add=True).",
                        )

    def _check_validation_gaps(self, path):
        source = self._read_file(path)
        if source is None:
            return
        rel = self._rel_path(path)
        tree = self._parse_ast(path)
        if tree is None:
            return

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                has_clean = False
                for item in node.body:
                    if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)) and item.name == "clean":
                        has_clean = True
                if has_clean:
                    continue
                is_model = any(
                    (isinstance(b, ast.Attribute) and "Model" in ast.unparse(b)) or
                    (isinstance(b, ast.Name) and "Model" in b.id)
                    for b in node.bases
                ) if hasattr(ast, "unparse") else False
                if is_model and "models.Model" in source[node.lineno-1:node.lineno+5]:
                    pass

    def _check_error_handling(self, path):
        source = self._read_file(path)
        if source is None:
            return
        rel = self._rel_path(path)
        tree = self._parse_ast(path)
        if tree is None:
            return

        for node in ast.walk(tree):
            if isinstance(node, ast.ExceptHandler):
                if node.type is not None:
                    type_str = ast.unparse(node.type) if hasattr(ast, "unparse") else ""
                    if type_str == "Exception":
                        has_logging = False
                        for child in ast.walk(node):
                            if isinstance(child, ast.Attribute):
                                if child.attr in ("exception", "error", "warning", "info", "debug"):
                                    has_logging = True
                                    break
                            if isinstance(child, ast.Call):
                                call_str = ast.unparse(child) if hasattr(ast, "unparse") else ""
                                if "logger" in call_str.lower():
                                    has_logging = True
                                    break
                        if not has_logging:
                            self.add_finding(
                                "business_logic", "MEDIUM", rel, node.lineno,
                                "Exception caught without logging",
                                "Broad Exception caught but not logged.",
                                "Log exceptions with logger.exception() for debugging.",
                            )

    def _check_backup_export(self, path):
        source = self._read_file(path)
        if source is None:
            return
        rel = self._rel_path(path)

        has_export = any(kw in source.lower() for kw in ["export", "backup", "csv", "excel", "xlsx", "download"])
        has_view = "views.py" in str(path) or "urls.py" in str(path)

        if has_view and not has_export:
            if "reportes" in str(path) or "ventas" in str(path) or "productos" in str(path):
                self.add_finding(
                    "business_logic", "LOW", rel, 1,
                    "Missing export/backup functionality",
                    f"App '{path.parent.name}' has no data export or backup feature.",
                    "Consider adding CSV/PDF export for reports and inventory data.",
                )

    # ------------------------------------------------------------------ #
    #  6. DJANGO BEST PRACTICES ANALYSIS
    # ------------------------------------------------------------------ #
    def analyze_django_best_practices(self):
        for py_file in self._python_files():
            self._check_custom_managers(py_file)
            self._check_orm_consistency(py_file)
            self._check_custom_validators(py_file)
            self._check_verbose_names(py_file)
            self._check_signal_usage(py_file)

    def _check_custom_managers(self, path):
        source = self._read_file(path)
        if source is None:
            return
        if "models.py" not in str(path):
            return
        rel = self._rel_path(path)

        has_manager = "Manager" in source and "class" in source
        if not has_manager:
            tree = self._parse_ast(path)
            if tree:
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        has_objects = False
                        for item in node.body:
                            if isinstance(item, ast.Assign):
                                for target in item.targets:
                                    if isinstance(target, ast.Name) and target.id == "objects":
                                        has_objects = True
                        if has_objects:
                            continue
                        if "models.Model" in source:
                            self.add_finding(
                                "django_best_practices", "LOW", rel, node.lineno,
                                f"Model '{node.name}' uses default manager",
                                f"Model '{node.name}' uses the default objects manager.",
                                "Consider a custom manager for common query patterns.",
                            )
                            break

    def _check_orm_consistency(self, path):
        source = self._read_file(path)
        if source is None:
            return
        if "analyze_improvements.py" in str(path):
            return
        rel = self._rel_path(path)

        if "get_object_or_404" in source and ".get(" in source:
            tree = self._parse_ast(path)
            if tree:
                uses_get_404 = "get_object_or_404" in source
                uses_get = re.search(r'\.get\(', source)
                if uses_get_404 and uses_get:
                    self.add_finding(
                        "django_best_practices", "LOW", rel, self._line_number(source, ".get("),
                        "Inconsistent use of .get() and get_object_or_404()",
                        "Mixing .get() and get_object_or_404() in the same file.",
                        "Use get_object_or_404() consistently for views.",
                    )

    def _check_custom_validators(self, path):
        source = self._read_file(path)
        if source is None:
            return
        if "models.py" not in str(path):
            return
        rel = self._rel_path(path)

        has_validators = "validators=" in source or "MinValueValidator" in source or "MaxValueValidator" in source
        has_clean = "def clean" in source

        if not has_validators and not has_clean:
            tree = self._parse_ast(path)
            if tree:
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        if "models.Model" in source[node.lineno-1:node.lineno+5]:
                            has_char = False
                            has_decimal = False
                            for item in node.body:
                                if isinstance(item, ast.Assign):
                                    val_str = ast.unparse(item.value) if hasattr(ast, "unparse") else ""
                                    if "CharField" in val_str:
                                        has_char = True
                                    if "DecimalField" in val_str or "IntegerField" in val_str:
                                        has_decimal = True

                            if has_decimal or has_char:
                                self.add_finding(
                                    "django_best_practices", "INFO", rel, node.lineno,
                                    f"Model '{node.name}' could benefit from custom validators",
                                    f"Model '{node.name}' has fields that could use validators.",
                                    "Add MinValueValidator, MaxValueValidator, or custom validators.",
                                )
                                break

    def _check_verbose_names(self, path):
        source = self._read_file(path)
        if source is None:
            return
        if "models.py" not in str(path):
            return
        rel = self._rel_path(path)

        if "verbose_name" not in source.lower():
            tree = self._parse_ast(path)
            if tree:
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        has_meta = False
                        for item in node.body:
                            if isinstance(item, ast.ClassDef) and item.name == "Meta":
                                has_meta = True
                        if not has_meta:
                            if "models.Model" in source[node.lineno-1:node.lineno+5]:
                                self.add_finding(
                                    "django_best_practices", "INFO", rel, node.lineno,
                                    f"Model '{node.name}' missing Meta class",
                                    f"Model '{node.name}' has no Meta class with verbose_name.",
                                    "Add Meta class with verbose_name and verbose_name_plural.",
                                )

    def _check_signal_usage(self, path):
        source = self._read_file(path)
        if source is None:
            return
        rel = self._rel_path(path)

        if "post_save" in source or "pre_save" in source or "@receiver" in source:
            tree = self._parse_ast(path)
            if tree:
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        has_receiver = False
                        for dec in node.decorator_list:
                            if isinstance(dec, ast.Name) and dec.id == "receiver":
                                has_receiver = True
                            if isinstance(dec, ast.Call):
                                if isinstance(dec.func, ast.Name) and dec.func.id == "receiver":
                                    has_receiver = True
                        if has_receiver:
                            pass

    # ------------------------------------------------------------------ #
    #  Cross-file analysis
    # ------------------------------------------------------------------ #
    def analyze_cross_file(self):
        self._check_form_class_consistency()
        self._check_url_naming()
        self._check_middleware_order()

    def _check_form_class_consistency(self):
        views_dir = self.base_dir
        forms_with_views = set()
        views_using_forms = set()

        for py_file in self._python_files():
            source = self._read_file(py_file)
            if source is None:
                continue
            rel = self._rel_path(py_file)

            if "forms.py" in str(py_file):
                tree = self._parse_ast(py_file)
                if tree:
                    for node in ast.walk(tree):
                        if isinstance(node, ast.ClassDef):
                            for base in node.bases:
                                base_str = ast.unparse(base) if hasattr(ast, "unparse") else ""
                                if "Form" in base_str:
                                    forms_with_views.add((node.name, rel))

            if "views.py" in str(py_file):
                if "Form" in source:
                    tree = self._parse_ast(py_file)
                    if tree:
                        for node in ast.walk(tree):
                            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                                func_source = source[node.lineno-1:node.end_lineno]
                                if "Form" in func_source:
                                    views_using_forms.add(rel)

    def _check_url_naming(self):
        for py_file in self._python_files():
            if "urls.py" not in str(py_file):
                continue
            source = self._read_file(py_file)
            if source is None:
                continue
            rel = self._rel_path(py_file)

            if "name=" not in source and "path(" in source:
                self.add_finding(
                    "django_best_practices", "MEDIUM", rel, 1,
                    "URL patterns without named routes",
                    "URL patterns without 'name=' make reverse URL lookups harder.",
                    "Add name='...' to all path() entries.",
                )

            tree = self._parse_ast(py_file)
            if tree:
                for node in ast.walk(tree):
                    if isinstance(node, ast.Assign) and isinstance(node.value, ast.List):
                        for elt in node.value.elts:
                            if isinstance(elt, ast.Call):
                                func_str = ast.unparse(elt.func) if hasattr(ast, "unparse") else ""
                                if func_str in ("path", "re_path"):
                                    has_name = any(
                                        isinstance(kw, ast.keyword) and kw.arg == "name"
                                        for kw in elt.keywords
                                    )
                                    if not has_name and len(elt.args) >= 2:
                                        pass

    def _check_middleware_order(self):
        settings_path = self.base_dir / "Inventory_Sales" / "settings.py"
        source = self._read_file(settings_path)
        if source is None:
            return
        rel = self._rel_path(settings_path)

        if "MIDDLEWARE" in source:
            m = re.search(r"MIDDLEWARE\s*=\s*\[(.*?)\]", source, re.DOTALL)
            if m:
                middleware_block = m.group(1)
                lines = [l.strip().strip(",'\"") for l in middleware_block.split("\n") if l.strip() and l.strip().startswith("'")]

                security_idx = next((i for i, l in enumerate(lines) if "SecurityMiddleware" in l), -1)
                session_idx = next((i for i, l in enumerate(lines) if "SessionMiddleware" in l), -1)
                csrf_idx = next((i for i, l in enumerate(lines) if "CsrfViewMiddleware" in l), -1)
                auth_idx = next((i for i, l in enumerate(lines) if "AuthenticationMiddleware" in l), -1)

                if security_idx > session_idx and security_idx != -1 and session_idx != -1:
                    self.add_finding(
                        "django_best_practices", "MEDIUM", rel, self._line_number(source, "MIDDLEWARE"),
                        "Middleware order: SecurityMiddleware should be first",
                        "SecurityMiddleware should come before SessionMiddleware.",
                        "Move SecurityMiddleware to the top of MIDDLEWARE list.",
                    )

    # ------------------------------------------------------------------ #
    #  File discovery
    # ------------------------------------------------------------------ #
    def _python_files(self):
        exclude_dirs = {"migrations", "__pycache__", ".git", ".venv", "venv", "node_modules", "htmlcov", ".pytest_cache", "deploy"}
        exclude_files = {"manage.py", "populate_categories.py", "utils.py"}
        for root, dirs, files in os.walk(self.base_dir):
            dirs[:] = [d for d in dirs if d not in exclude_dirs]
            for f in files:
                if f.endswith(".py") and f not in exclude_files:
                    yield Path(root) / f

    def _template_files(self):
        tmpl_dir = self.base_dir / "templates"
        if tmpl_dir.exists():
            for root, dirs, files in os.walk(tmpl_dir):
                for f in files:
                    if f.endswith(".html"):
                        yield Path(root) / f
        for app_dir in self.base_dir.iterdir():
            if app_dir.is_dir():
                app_tmpl = app_dir / "templates"
                if app_tmpl.exists():
                    for root, dirs, files in os.walk(app_tmpl):
                        for f in files:
                            if f.endswith(".html"):
                                yield Path(root) / f

    def _line_number(self, source, pattern):
        lines = source.split("\n")
        for i, line in enumerate(lines, 1):
            if pattern in line:
                return i
        return 1

    # ------------------------------------------------------------------ #
    #  Run all analyzers
    # ------------------------------------------------------------------ #
    def run_all(self, category_filter=None, severity_filter=None):
        analyzers = {
            "security": self.analyze_security,
            "performance": self.analyze_performance,
            "code_quality": self.analyze_code_quality,
            "template": self.analyze_templates,
            "business_logic": self.analyze_business_logic,
            "django_best_practices": self.analyze_django_best_practices,
        }

        categories = list(analyzers.keys())
        if category_filter:
            categories = [c for c in categories if c == category_filter]

        for cat in categories:
            analyzers[cat]()

        self.analyze_cross_file()

        if severity_filter:
            self.findings = [f for f in self.findings if f.severity == severity_filter]

        self.findings.sort(key=lambda f: (SEVERITY_ORDER.get(f.severity, 5), f.category, f.file_path, f.line))
        return self.findings


class Command(BaseCommand):
    help = "Analyze the Django POS codebase for security, performance, and quality improvements."

    def add_arguments(self, parser):
        parser.add_argument(
            "--category",
            type=str,
            choices=["security", "performance", "code_quality", "template", "business_logic", "django_best_practices"],
            help="Filter by analysis category",
        )
        parser.add_argument(
            "--severity",
            type=str,
            choices=["CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO"],
            help="Filter by minimum severity level",
        )
        parser.add_argument(
            "--format",
            type=str,
            choices=["text", "json"],
            default="text",
            help="Output format (default: text)",
        )
        parser.add_argument(
            "--output",
            type=str,
            help="Output file path (default: stdout)",
        )

    def handle(self, *args, **options):
        base_dir = Path(__file__).resolve().parent.parent.parent.parent.parent
        analyzer = CodeAnalyzer(base_dir)

        category = options.get("category")
        severity = options.get("severity")
        output_format = options.get("format")
        output_file = options.get("output")

        findings = analyzer.run_all(category_filter=category, severity_filter=severity)

        if output_format == "json":
            output = self._format_json(findings)
        else:
            output = self._format_text(findings, category, severity)

        if output_file:
            with open(output_file, "w", encoding="utf-8") as f:
                if output_format == "json":
                    import json
                    json.dump(json.loads(output), f, indent=2, ensure_ascii=False)
                else:
                    f.write(output)
            self.stdout.write(self.style.SUCCESS(f"Report written to {output_file}"))
        else:
            self.stdout.write(output, ending="")

    def _format_text(self, findings, category_filter=None, severity_filter=None):
        if not findings:
            return f"{BOLD}No findings{' matching filters' if category_filter or severity_filter else ''}.{RESET}\n"

        by_category = defaultdict(list)
        for f in findings:
            by_category[f.category].append(f)

        category_labels = {
            "security": "Security",
            "performance": "Performance",
            "code_quality": "Code Quality",
            "template": "Template Issues",
            "business_logic": "Business Logic",
            "django_best_practices": "Django Best Practices",
        }

        output = []
        output.append(f"{BOLD}{'='*80}{RESET}\n")
        output.append(f"{BOLD}  Django POS Code Analysis Report{RESET}\n")
        output.append(f"{BOLD}{'='*80}{RESET}\n")

        total_by_severity = defaultdict(int)
        for f in findings:
            total_by_severity[f.severity] += 1

        output.append(f"{BOLD}Summary:{RESET}\n")
        for sev in ["CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO"]:
            count = total_by_severity.get(sev, 0)
            if count:
                color = SEVERITY_COLORS.get(sev, "")
                output.append(f"  {color}{sev}: {count}{RESET}\n")
        output.append(f"  {BOLD}Total: {len(findings)}{RESET}\n\n")

        output.append(f"{BOLD}{'='*80}{RESET}\n\n")

        for cat, cat_findings in by_category.items():
            label = category_labels.get(cat, cat)
            color = CATEGORY_COLORS.get(cat, "")
            output.append(f"{BOLD}{color}--- {label} ({len(cat_findings)} findings) ---{RESET}\n\n")

            for f in cat_findings:
                sev_color = SEVERITY_COLORS.get(f.severity, "")
                output.append(f"  {sev_color}[{f.severity}]{RESET} {BOLD}{f.title}{RESET}\n")
                output.append(f"    File: {f.file_path}:{f.line}\n")
                output.append(f"    Issue: {f.description}\n")
                output.append(f"    Fix: {f.suggestion}\n")
                output.append(f"\n")

        output.append(f"{BOLD}{'='*80}{RESET}\n")
        output.append(f"{BOLD}End of report - {len(findings)} total findings{RESET}\n")

        return "".join(output)

    def _format_json(self, findings):
        import json
        data = {
            "total": len(findings),
            "findings": [
                {
                    "category": f.category,
                    "severity": f.severity,
                    "file": f.file_path,
                    "line": f.line,
                    "title": f.title,
                    "description": f.description,
                    "suggestion": f.suggestion,
                }
                for f in findings
            ],
        }
        return json.dumps(data, indent=2, ensure_ascii=False)
