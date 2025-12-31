#!/usr/bin/env python3
import os
import sys
import json
import argparse
import subprocess
import re
from pathlib import Path
from collections import defaultdict
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, asdict, field

__version__ = "5.0.0"

CONFIG_FILE = Path.home() / ".pricereveal_config.json"

DEFAULT_CONFIG = {
    "hourly_rate": 50.0,
    "lines_per_hour": 40,
    "checks": {
        "git": True,
        "tests": True,
        "docker": True,
        "ci_cd": True,
        "security": True,
        "database": True,
        "api": True
    },
    "weights": {
        "git_history_bonus": 0.18,
        "test_coverage_penalty": -0.25,
        "docker_bonus": 0.08,
        "ci_cd_bonus": 0.12,
        "database_bonus": 0.15,
        "api_bonus": 0.20,
        "security_penalty": -0.30
    },
    "file_multipliers": {
        "entrypoint": 2.5,
        "core": 2.0,
        "infrastructure": 1.5,
        "test": 0.6,
        "config": 0.4
    },
    "complexity_weights": {
        ".rs": 1.5, ".cpp": 1.5, ".c": 1.4, ".go": 1.3, ".scala": 1.4,
        ".java": 1.2, ".cs": 1.2, ".ts": 1.2, ".tsx": 1.2, ".swift": 1.3,
        ".py": 1.0, ".js": 1.0, ".jsx": 1.0, ".php": 1.0, ".rb": 1.0,
        ".kt": 1.1, ".ex": 1.2, ".html": 0.5, ".css": 0.5, ".vue": 0.8,
        ".json": 0.3, ".yml": 0.3, ".yaml": 0.3, ".md": 0.2
    },
    "code_extensions": [
        ".py", ".js", ".jsx", ".ts", ".tsx", ".java", ".c", ".cpp", ".cc",
        ".h", ".hpp", ".cs", ".php", ".rb", ".go", ".rs", ".swift", ".kt",
        ".scala", ".ex", ".exs", ".sh", ".bash", ".sql", ".r", ".m", ".mm",
        ".dart", ".lua", ".pl", ".vim", ".asm"
    ],
    "asset_extensions": [
        ".png", ".jpg", ".jpeg", ".gif", ".svg", ".ico", ".webp", ".bmp",
        ".ttf", ".otf", ".woff", ".woff2", ".eot", ".mp3", ".mp4", ".wav",
        ".avi", ".mov", ".pdf", ".zip", ".tar", ".gz", ".7z", ".rar"
    ],
    "ignore_dirs": [
        ".git", "node_modules", "__pycache__", "venv", ".venv", "dist",
        "build", ".idea", ".vscode", "coverage", ".mypy_cache", ".pytest_cache",
        "target", "bin", "obj", ".next", "out", "vendor", "bower_components"
    ],
    "ignore_files": [
        ".DS_Store", "Thumbs.db", ".gitignore", "package-lock.json",
        "yarn.lock", "pnpm-lock.yaml"
    ]
}

class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    END = '\033[0m'
    
    @staticmethod
    def disable():
        for attr in dir(Colors):
            if not attr.startswith('_') and attr != 'disable':
                setattr(Colors, attr, '')

@dataclass
class FileValue:
    path: str
    lines: int
    language: str
    extension: str
    is_code: bool
    base_value: float
    multiplier: float
    final_value: float
    category: str
    reason: str

@dataclass
class GitMetrics:
    detected: bool = False
    commits: int = 0
    age_days: int = 0
    contributors: int = 0
    branches: int = 0
    avg_commit_frequency: float = 0.0

@dataclass
class TestMetrics:
    framework_detected: bool = False
    framework_name: str = ""
    test_files: int = 0
    test_lines: int = 0
    code_lines: int = 0
    coverage_ratio: float = 0.0

@dataclass
class InfraMetrics:
    docker: bool = False
    docker_compose: bool = False
    ci_cd: bool = False
    ci_platforms: List[str] = field(default_factory=list)

@dataclass
class DatabaseMetrics:
    detected: bool = False
    types: List[str] = field(default_factory=list)

@dataclass
class APIMetrics:
    detected: bool = False
    types: List[str] = field(default_factory=list)

@dataclass
class SecurityMetrics:
    env_files_exposed: int = 0
    hardcoded_secrets: int = 0
    total_issues: int = 0

@dataclass
class ValuationBreakdown:
    base_cost: float
    git_bonus: float
    git_bonus_pct: float
    test_penalty: float
    test_penalty_pct: float
    docker_bonus: float
    docker_bonus_pct: float
    ci_cd_bonus: float
    ci_cd_bonus_pct: float
    database_bonus: float
    database_bonus_pct: float
    api_bonus: float
    api_bonus_pct: float
    security_penalty: float
    security_penalty_pct: float
    final_value: float

@dataclass
class ProjectMetrics:
    project_name: str
    root_path: str
    analyzed_paths: List[str]
    total_files: int
    code_files: int
    asset_files: int
    total_lines: int
    code_lines: int
    estimated_hours: float
    languages: Dict[str, int]
    file_values: List[FileValue]
    directory_values: Dict[str, float]
    git_metrics: GitMetrics
    test_metrics: TestMetrics
    infra_metrics: InfraMetrics
    database_metrics: DatabaseMetrics
    api_metrics: APIMetrics
    security_metrics: SecurityMetrics
    valuation: ValuationBreakdown
    analysis_timestamp: str
    limitations: List[str]

def load_config() -> Dict:
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, 'r') as f:
                saved = json.load(f)
                config = DEFAULT_CONFIG.copy()
                config.update(saved)
                return config
        except:
            pass
    return DEFAULT_CONFIG.copy()

def save_config(config: Dict):
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=2)
        print(f"{Colors.GREEN}✓ Configuration saved{Colors.END}")
    except Exception as e:
        print(f"{Colors.RED}✗ Failed to save: {e}{Colors.END}")

def config_menu():
    config = load_config()
    
    while True:
        print(f"\n{Colors.BOLD}{Colors.CYAN}╔═══════════════════════════════════════╗{Colors.END}")
        print(f"{Colors.BOLD}{Colors.CYAN}║  Price Reveal Configuration System    ║{Colors.END}")
        print(f"{Colors.BOLD}{Colors.CYAN}╚═══════════════════════════════════════╝{Colors.END}\n")
        
        print(f"{Colors.BOLD}1.{Colors.END} Base Settings")
        print(f"{Colors.BOLD}2.{Colors.END} Enable/Disable Checks")
        print(f"{Colors.BOLD}3.{Colors.END} Adjust Weights & Multipliers")
        print(f"{Colors.BOLD}4.{Colors.END} File Category Multipliers")
        print(f"{Colors.BOLD}5.{Colors.END} Reset to Defaults")
        print(f"{Colors.BOLD}6.{Colors.END} Save & Exit")
        print(f"{Colors.BOLD}0.{Colors.END} Exit Without Saving\n")
        
        choice = input(f"{Colors.CYAN}Select option: {Colors.END}").strip()
        
        if choice == "1":
            config_base_settings(config)
        elif choice == "2":
            config_checks(config)
        elif choice == "3":
            config_weights(config)
        elif choice == "4":
            config_multipliers(config)
        elif choice == "5":
            if input("Reset to defaults? (yes/no): ").lower() == "yes":
                config = DEFAULT_CONFIG.copy()
                print(f"{Colors.GREEN}✓ Reset to defaults{Colors.END}")
        elif choice == "6":
            save_config(config)
            break
        elif choice == "0":
            break

def config_base_settings(config: Dict):
    print(f"\n{Colors.BOLD}Base Settings:{Colors.END}\n")
    print(f"Current hourly rate: ${config['hourly_rate']:.2f}")
    print(f"Current lines per hour: {config['lines_per_hour']}")
    
    rate = input(f"\nNew hourly rate (Enter to keep): $").strip()
    if rate:
        try:
            config['hourly_rate'] = float(rate)
        except:
            print(f"{Colors.RED}Invalid value{Colors.END}")
    
    lines = input(f"New lines per hour (Enter to keep): ").strip()
    if lines:
        try:
            config['lines_per_hour'] = int(lines)
        except:
            print(f"{Colors.RED}Invalid value{Colors.END}")

def config_checks(config: Dict):
    checks = config['checks']
    
    while True:
        print(f"\n{Colors.BOLD}Enable/Disable Checks:{Colors.END}\n")
        for i, (name, enabled) in enumerate(checks.items(), 1):
            status = f"{Colors.GREEN}ON{Colors.END}" if enabled else f"{Colors.DIM}OFF{Colors.END}"
            print(f"{i}. {name.replace('_', ' ').title()}: {status}")
        print(f"0. Back\n")
        
        choice = input(f"{Colors.CYAN}Toggle option (number): {Colors.END}").strip()
        
        if choice == "0":
            break
        
        try:
            idx = int(choice) - 1
            keys = list(checks.keys())
            if 0 <= idx < len(keys):
                key = keys[idx]
                checks[key] = not checks[key]
        except:
            pass

def config_weights(config: Dict):
    weights = config['weights']
    
    while True:
        print(f"\n{Colors.BOLD}Adjustment Weights:{Colors.END}\n")
        for i, (name, weight) in enumerate(weights.items(), 1):
            pct = weight * 100
            sign = "+" if weight > 0 else ""
            print(f"{i}. {name.replace('_', ' ').title()}: {sign}{pct:.0f}%")
        print(f"0. Back\n")
        
        choice = input(f"{Colors.CYAN}Edit option (number): {Colors.END}").strip()
        
        if choice == "0":
            break
        
        try:
            idx = int(choice) - 1
            keys = list(weights.keys())
            if 0 <= idx < len(keys):
                key = keys[idx]
                new_val = input(f"New value for {key} (as percentage, e.g., 18 for +18%): ").strip()
                if new_val:
                    weights[key] = float(new_val) / 100.0
        except:
            print(f"{Colors.RED}Invalid input{Colors.END}")

def config_multipliers(config: Dict):
    mults = config['file_multipliers']
    
    while True:
        print(f"\n{Colors.BOLD}File Category Multipliers:{Colors.END}\n")
        for i, (name, mult) in enumerate(mults.items(), 1):
            print(f"{i}. {name.title()}: {mult:.1f}x")
        print(f"0. Back\n")
        
        choice = input(f"{Colors.CYAN}Edit option (number): {Colors.END}").strip()
        
        if choice == "0":
            break
        
        try:
            idx = int(choice) - 1
            keys = list(mults.keys())
            if 0 <= idx < len(keys):
                key = keys[idx]
                new_val = input(f"New multiplier for {key}: ").strip()
                if new_val:
                    mults[key] = float(new_val)
        except:
            print(f"{Colors.RED}Invalid input{Colors.END}")

def select_folders(root_path: Path) -> List[Path]:
    subdirs = [d for d in root_path.iterdir() if d.is_dir() and d.name not in DEFAULT_CONFIG['ignore_dirs']]
    
    if not subdirs:
        return [root_path]
    
    subdirs.sort(key=lambda x: x.name.lower())
    selected = {i: True for i in range(len(subdirs))}
    
    while True:
        print(f"\n{Colors.BOLD}Select directories to analyze:{Colors.END}\n")
        
        for i, d in enumerate(subdirs):
            mark = f"{Colors.GREEN}[x]{Colors.END}" if selected[i] else f"{Colors.DIM}[ ]{Colors.END}"
            print(f"{i+1}. {mark} {d.name}/")
        
        print(f"\n{Colors.BOLD}Commands:{Colors.END}")
        print("  a - Select all")
        print("  n - Select none")
        print("  <number> - Toggle directory")
        print("  done - Continue with selection\n")
        
        choice = input(f"{Colors.CYAN}Command: {Colors.END}").strip().lower()
        
        if choice == "done":
            break
        elif choice == "a":
            selected = {i: True for i in range(len(subdirs))}
        elif choice == "n":
            selected = {i: False for i in range(len(subdirs))}
        else:
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(subdirs):
                    selected[idx] = not selected[idx]
            except:
                pass
    
    result = [subdirs[i] for i, sel in selected.items() if sel]
    
    if not result:
        print(f"{Colors.YELLOW}No directories selected, analyzing root{Colors.END}")
        return [root_path]
    
    return result

def detect_git_metrics(root_path: Path, config: Dict) -> GitMetrics:
    if not config['checks']['git']:
        return GitMetrics()
    
    git_dir = root_path / ".git"
    if not git_dir.exists():
        return GitMetrics()
    
    metrics = GitMetrics(detected=True)
    
    try:
        result = subprocess.run(
            ["git", "rev-list", "--all", "--count"],
            cwd=root_path, capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0:
            metrics.commits = int(result.stdout.strip())
    except:
        pass
    
    try:
        result = subprocess.run(
            ["git", "log", "--format=%an", "--all"],
            cwd=root_path, capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0:
            contributors = set(result.stdout.strip().split('\n'))
            metrics.contributors = len(contributors)
    except:
        pass
    
    try:
        result = subprocess.run(
            ["git", "log", "--format=%ct", "--reverse"],
            cwd=root_path, capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0:
            timestamps = result.stdout.strip().split('\n')
            if timestamps and timestamps[0]:
                first_ts = int(timestamps[0])
                age_seconds = datetime.now().timestamp() - first_ts
                metrics.age_days = int(age_seconds / 86400)
                
                if metrics.commits > 1 and metrics.age_days > 0:
                    metrics.avg_commit_frequency = metrics.commits / (metrics.age_days / 30.0)
    except:
        pass
    
    try:
        result = subprocess.run(
            ["git", "branch", "-a"],
            cwd=root_path, capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0:
            branches = [b.strip() for b in result.stdout.split('\n') if b.strip()]
            metrics.branches = len(branches)
    except:
        pass
    
    return metrics

def detect_test_metrics(files: List[FileValue], config: Dict) -> TestMetrics:
    if not config['checks']['tests']:
        return TestMetrics()
    
    metrics = TestMetrics()
    
    test_patterns = [
        r'test[_/]', r'[_/]test\.', r'spec[_/]', r'[_/]spec\.',
        r'__tests__', r'\.test\.', r'\.spec\.'
    ]
    
    test_frameworks = {
        'pytest': ['.py'],
        'jest': ['.js', '.jsx', '.ts', '.tsx'],
        'junit': ['.java'],
        'rspec': ['.rb'],
        'mocha': ['.js'],
        'xunit': ['.cs'],
        'go test': ['.go']
    }
    
    for fv in files:
        if fv.is_code:
            for pattern in test_patterns:
                if re.search(pattern, fv.path.lower()):
                    metrics.test_files += 1
                    metrics.test_lines += fv.lines
                    break
    
    code_lines = sum(fv.lines for fv in files if fv.is_code and fv.category != "test")
    metrics.code_lines = code_lines
    
    if code_lines > 0:
        metrics.coverage_ratio = metrics.test_lines / code_lines
    
    for framework, exts in test_frameworks.items():
        if any(fv.extension in exts for fv in files if fv.is_code):
            metrics.framework_detected = True
            metrics.framework_name = framework
            break
    
    return metrics

def detect_infra_metrics(root_path: Path, config: Dict) -> InfraMetrics:
    metrics = InfraMetrics()
    
    if config['checks']['docker']:
        if (root_path / "Dockerfile").exists():
            metrics.docker = True
        if (root_path / "docker-compose.yml").exists() or (root_path / "docker-compose.yaml").exists():
            metrics.docker_compose = True
    
    if config['checks']['ci_cd']:
        ci_files = {
            '.github/workflows': 'GitHub Actions',
            '.gitlab-ci.yml': 'GitLab CI',
            '.circleci/config.yml': 'CircleCI',
            'Jenkinsfile': 'Jenkins',
            '.travis.yml': 'Travis CI',
            'azure-pipelines.yml': 'Azure Pipelines'
        }
        
        for file, platform in ci_files.items():
            if (root_path / file).exists():
                metrics.ci_cd = True
                metrics.ci_platforms.append(platform)
    
    return metrics

def detect_database_metrics(files: List[FileValue], config: Dict) -> DatabaseMetrics:
    if not config['checks']['database']:
        return DatabaseMetrics()
    
    metrics = DatabaseMetrics()
    
    db_patterns = {
        'PostgreSQL': [r'psycopg2', r'postgresql://', r'postgres://'],
        'MySQL': [r'mysql', r'pymysql', r'mysql://'],
        'MongoDB': [r'mongodb://', r'pymongo', r'mongoose'],
        'Redis': [r'redis://', r'redis\.'],
        'SQLite': [r'sqlite3', r'\.db$', r'\.sqlite$'],
        'Oracle': [r'oracle', r'cx_Oracle'],
        'SQL Server': [r'mssql', r'pyodbc']
    }
    
    all_text = ""
    for fv in files[:100]:
        if fv.is_code:
            try:
                with open(fv.path, 'r', encoding='utf-8', errors='ignore') as f:
                    all_text += f.read(10000) + "\n"
            except:
                pass
    
    for db_name, patterns in db_patterns.items():
        for pattern in patterns:
            if re.search(pattern, all_text, re.IGNORECASE):
                metrics.detected = True
                if db_name not in metrics.types:
                    metrics.types.append(db_name)
                break
    
    return metrics

def detect_api_metrics(files: List[FileValue], config: Dict) -> APIMetrics:
    if not config['checks']['api']:
        return APIMetrics()
    
    metrics = APIMetrics()
    
    api_patterns = {
        'REST API': [r'@app\.route', r'@router\.',  r'express\(\)', r'FastAPI', r'flask', r'gin\.'],
        'GraphQL': [r'graphql', r'apollo', r'type Query'],
        'gRPC': [r'grpc', r'\.proto$'],
        'WebSocket': [r'websocket', r'socket\.io']
    }
    
    all_text = ""
    for fv in files[:100]:
        if fv.is_code:
            try:
                with open(fv.path, 'r', encoding='utf-8', errors='ignore') as f:
                    all_text += f.read(10000) + "\n"
            except:
                pass
    
    for api_type, patterns in api_patterns.items():
        for pattern in patterns:
            if re.search(pattern, all_text, re.IGNORECASE):
                metrics.detected = True
                if api_type not in metrics.types:
                    metrics.types.append(api_type)
                break
    
    return metrics

def detect_security_issues(root_path: Path, files: List[FileValue], config: Dict) -> SecurityMetrics:
    if not config['checks']['security']:
        return SecurityMetrics()
    
    metrics = SecurityMetrics()
    
    env_files = ['.env', 'env', '.env.local', '.env.production']
    for env_file in env_files:
        if (root_path / env_file).exists():
            metrics.env_files_exposed += 1
    
    secret_patterns = [
        r'password\s*=\s*["\'][^"\']+["\']',
        r'api_key\s*=\s*["\'][^"\']+["\']',
        r'secret\s*=\s*["\'][^"\']+["\']',
        r'token\s*=\s*["\'][^"\']+["\']'
    ]
    
    for fv in files[:50]:
        if fv.is_code:
            try:
                with open(fv.path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read(50000)
                    for pattern in secret_patterns:
                        if re.search(pattern, content, re.IGNORECASE):
                            metrics.hardcoded_secrets += 1
                            break
            except:
                pass
    
    metrics.total_issues = metrics.env_files_exposed + metrics.hardcoded_secrets
    
    return metrics

def categorize_file(path: str, lines: int) -> Tuple[str, str]:
    path_lower = path.lower()
    
    entrypoint_patterns = [
        'main.py', 'app.py', 'index.js', 'index.ts', 'main.go',
        'main.rs', 'main.java', 'program.cs', '__init__.py'
    ]
    
    for pattern in entrypoint_patterns:
        if path_lower.endswith(pattern):
            return "entrypoint", "Main application entry point"
    
    core_patterns = [
        r'/core/', r'/engine/', r'/kernel/', r'/lib/', r'/src/[^/]+\.py$',
        r'/models/', r'/controllers/', r'/services/', r'/handlers/'
    ]
    
    for pattern in core_patterns:
        if re.search(pattern, path_lower):
            return "core", "Core business logic"
    
    if re.search(r'test[_/]|[_/]test\.|spec[_/]|[_/]spec\.', path_lower):
        return "test", "Test code"
    
    infra_patterns = [
        r'/infra/', r'/infrastructure/', r'/deployment/', r'/scripts/',
        r'/config/', r'/settings/', r'docker', r'\.yml$', r'\.yaml$'
    ]
    
    for pattern in infra_patterns:
        if re.search(pattern, path_lower):
            return "infrastructure", "Infrastructure code"
    
    if re.search(r'\.json$|\.xml$|\.toml$|\.ini$|\.env', path_lower):
        return "config", "Configuration file"
    
    return "standard", "Standard code file"

def calculate_file_value(path: str, lines: int, extension: str, is_code: bool, config: Dict) -> FileValue:
    language = "Unknown"
    
    if not is_code:
        return FileValue(
            path=path, lines=lines, language="Asset", extension=extension,
            is_code=False, base_value=0.0, multiplier=0.0, final_value=0.0,
            category="asset", reason="Non-code file (excluded from valuation)"
        )
    
    complexity = config['complexity_weights'].get(extension, 1.0)
    cost_per_line = config['hourly_rate'] / config['lines_per_hour']
    base_value = lines * complexity * cost_per_line
    
    category, reason = categorize_file(path, lines)
    multiplier = config['file_multipliers'].get(category, 1.0)
    final_value = base_value * multiplier
    
    return FileValue(
        path=path, lines=lines, language=language, extension=extension,
        is_code=True, base_value=base_value, multiplier=multiplier,
        final_value=final_value, category=category, reason=reason
    )

def analyze_files(paths: List[Path], config: Dict) -> Tuple[List[FileValue], Dict[str, float]]:
    file_values = []
    dir_values = defaultdict(float)
    
    for root_path in paths:
        for file_path in root_path.rglob("*"):
            if not file_path.is_file():
                continue
            
            if file_path.name in config['ignore_files']:
                continue
            
            rel_path = str(file_path.relative_to(root_path))
            
            if any(ignored in rel_path.split(os.sep) for ignored in config['ignore_dirs']):
                continue
            
            extension = file_path.suffix.lower()
            is_code = extension in config['code_extensions']
            
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = sum(1 for _ in f)
            except:
                lines = 0
            
            if lines == 0:
                continue
            
            fv = calculate_file_value(str(file_path), lines, extension, is_code, config)
            file_values.append(fv)
            
            dir_path = str(file_path.parent)
            dir_values[dir_path] += fv.final_value
    
    return file_values, dict(dir_values)

def calculate_valuation(file_values: List[FileValue], git: GitMetrics, 
                       test: TestMetrics, infra: InfraMetrics,
                       db: DatabaseMetrics, api: APIMetrics,
                       security: SecurityMetrics, config: Dict) -> ValuationBreakdown:
    
    base_cost = sum(fv.final_value for fv in file_values if fv.is_code)
    
    adjustments = []
    current_value = base_cost
    
    git_bonus = 0.0
    git_bonus_pct = 0.0
    if config['checks']['git'] and git.detected and git.commits >= 10:
        git_bonus_pct = config['weights']['git_history_bonus']
        git_bonus = current_value * git_bonus_pct
        current_value += git_bonus
    
    test_penalty = 0.0
    test_penalty_pct = 0.0
    if config['checks']['tests'] and test.code_lines > 0:
        if not test.framework_detected or test.coverage_ratio < 0.3:
            test_penalty_pct = config['weights']['test_coverage_penalty']
            test_penalty = current_value * test_penalty_pct
            current_value += test_penalty
    
    docker_bonus = 0.0
    docker_bonus_pct = 0.0
    if config['checks']['docker'] and infra.docker:
        docker_bonus_pct = config['weights']['docker_bonus']
        docker_bonus = current_value * docker_bonus_pct
        current_value += docker_bonus
    
    ci_cd_bonus = 0.0
    ci_cd_bonus_pct = 0.0
    if config['checks']['ci_cd'] and infra.ci_cd:
        ci_cd_bonus_pct = config['weights']['ci_cd_bonus']
        ci_cd_bonus = current_value * ci_cd_bonus_pct
        current_value += ci_cd_bonus
    
    database_bonus = 0.0
    database_bonus_pct = 0.0
    if config['checks']['database'] and db.detected:
        database_bonus_pct = config['weights']['database_bonus']
        database_bonus = current_value * database_bonus_pct
        current_value += database_bonus
    
    api_bonus = 0.0
    api_bonus_pct = 0.0
    if config['checks']['api'] and api.detected:
        api_bonus_pct = config['weights']['api_bonus']
        api_bonus = current_value * api_bonus_pct
        current_value += api_bonus
    
    security_penalty = 0.0
    security_penalty_pct = 0.0
    if config['checks']['security'] and security.total_issues > 0:
        security_penalty_pct = config['weights']['security_penalty']
        security_penalty = current_value * security_penalty_pct
        current_value += security_penalty
    
    return ValuationBreakdown(
        base_cost=base_cost,
        git_bonus=git_bonus,
        git_bonus_pct=git_bonus_pct,
        test_penalty=test_penalty,
        test_penalty_pct=test_penalty_pct,
        docker_bonus=docker_bonus,
        docker_bonus_pct=docker_bonus_pct,
        ci_cd_bonus=ci_cd_bonus,
        ci_cd_bonus_pct=ci_cd_bonus_pct,
        database_bonus=database_bonus,
        database_bonus_pct=database_bonus_pct,
        api_bonus=api_bonus,
        api_bonus_pct=api_bonus_pct,
        security_penalty=security_penalty,
        security_penalty_pct=security_penalty_pct,
        final_value=current_value
    )

def analyze_project(paths: List[Path], root_path: Path, config: Dict) -> ProjectMetrics:
    file_values, dir_values = analyze_files(paths, config)
    
    code_files = [fv for fv in file_values if fv.is_code]
    asset_files = [fv for fv in file_values if not fv.is_code]
    
    total_lines = sum(fv.lines for fv in file_values)
    code_lines = sum(fv.lines for fv in code_files)
    
    languages = defaultdict(int)
    for fv in code_files:
        languages[fv.extension] += fv.lines
    
    estimated_hours = sum(fv.lines for fv in code_files) / config['lines_per_hour']
    
    git = detect_git_metrics(root_path, config)
    test = detect_test_metrics(file_values, config)
    infra = detect_infra_metrics(root_path, config)
    db = detect_database_metrics(file_values, config)
    api = detect_api_metrics(file_values, config)
    security = detect_security_issues(root_path, file_values, config)
    
    valuation = calculate_valuation(file_values, git, test, infra, db, api, security, config)
    
    limitations = []
    if not git.detected:
        limitations.append("No Git history detected - maturity cannot be accurately assessed")
    if not test.framework_detected:
        limitations.append("No test framework detected - quality assurance level unknown")
    if not infra.ci_cd:
        limitations.append("No CI/CD detected - deployment maturity unknown")
    limitations.append("Valuation is based on heuristic model, not actual market data")
    limitations.append("Business value, IP, and market factors not included")
    
    return ProjectMetrics(
        project_name=root_path.name,
        root_path=str(root_path),
        analyzed_paths=[str(p) for p in paths],
        total_files=len(file_values),
        code_files=len(code_files),
        asset_files=len(asset_files),
        total_lines=total_lines,
        code_lines=code_lines,
        estimated_hours=estimated_hours,
        languages=dict(languages),
        file_values=sorted(file_values, key=lambda x: x.final_value, reverse=True),
        directory_values=dir_values,
        git_metrics=git,
        test_metrics=test,
        infra_metrics=infra,
        database_metrics=db,
        api_metrics=api,
        security_metrics=security,
        valuation=valuation,
        analysis_timestamp=datetime.now().isoformat(),
        limitations=limitations
    )

def format_currency(value: float) -> str:
    return f"${value:,.2f}"

def format_pct(value: float) -> str:
    pct = value * 100
    sign = "+" if value > 0 else ""
    return f"{sign}{pct:.0f}%"

def print_report(metrics: ProjectMetrics, show_tree: bool):
    v = metrics.valuation
    
    print(f"\n{Colors.BOLD}{Colors.CYAN}═══════════════════════════════════════════════════════════════{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}    TECHNICAL VALUATION REPORT{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}═══════════════════════════════════════════════════════════════{Colors.END}\n")
    
    print(f"{Colors.BOLD}PROJECT: {metrics.project_name}{Colors.END}")
    print(f"Analyzed: {len(metrics.analyzed_paths)} directories")
    print(f"Files: {metrics.code_files} code, {metrics.asset_files} assets")
    print(f"Lines: {metrics.code_lines:,} (code only)\n")
    
    print(f"{Colors.BOLD}───────────────────────────────────────────────────────────────{Colors.END}")
    print(f"{Colors.BOLD}VALUE CALCULATION{Colors.END}")
    print(f"{Colors.BOLD}───────────────────────────────────────────────────────────────{Colors.END}\n")
    
    print(f"Base Development Cost:        {format_currency(v.base_cost)}")
    
    if v.git_bonus != 0:
        print(f"Git History Bonus:            {format_pct(v.git_bonus_pct):>6}  →  +{format_currency(v.git_bonus)}")
    
    if v.test_penalty != 0:
        print(f"Test Coverage Penalty:        {format_pct(v.test_penalty_pct):>6}  →  {format_currency(v.test_penalty)}")
    
    if v.docker_bonus != 0:
        print(f"Docker Bonus:                 {format_pct(v.docker_bonus_pct):>6}  →  +{format_currency(v.docker_bonus)}")
    
    if v.ci_cd_bonus != 0:
        print(f"CI/CD Bonus:                  {format_pct(v.ci_cd_bonus_pct):>6}  →  +{format_currency(v.ci_cd_bonus)}")
    
    if v.database_bonus != 0:
        print(f"Database Bonus:               {format_pct(v.database_bonus_pct):>6}  →  +{format_currency(v.database_bonus)}")
    
    if v.api_bonus != 0:
        print(f"API Bonus:                    {format_pct(v.api_bonus_pct):>6}  →  +{format_currency(v.api_bonus)}")
    
    if v.security_penalty != 0:
        print(f"Security Penalty:             {format_pct(v.security_penalty_pct):>6}  →  {format_currency(v.security_penalty)}")
    
    print(f"\n{Colors.BOLD}Final Technical Value:        {Colors.GREEN}{format_currency(v.final_value)}{Colors.END}\n")
    
    print(f"{Colors.BOLD}───────────────────────────────────────────────────────────────{Colors.END}")
    print(f"{Colors.BOLD}WHAT INCREASED VALUE{Colors.END}")
    print(f"{Colors.BOLD}───────────────────────────────────────────────────────────────{Colors.END}\n")
    
    increased = []
    if metrics.git_metrics.detected:
        increased.append(f"✓ Git history with {metrics.git_metrics.commits} commits")
    if metrics.infra_metrics.docker:
        increased.append(f"✓ Docker containerization")
    if metrics.infra_metrics.ci_cd:
        increased.append(f"✓ CI/CD pipeline ({', '.join(metrics.infra_metrics.ci_platforms)})")
    if metrics.database_metrics.detected:
        increased.append(f"✓ Database integration ({', '.join(metrics.database_metrics.types)})")
    if metrics.api_metrics.detected:
        increased.append(f"✓ API implementation ({', '.join(metrics.api_metrics.types)})")
    
    if increased:
        for item in increased:
            print(f"  {item}")
    else:
        print(f"  {Colors.DIM}No major value increasers detected{Colors.END}")
    
    print(f"\n{Colors.BOLD}───────────────────────────────────────────────────────────────{Colors.END}")
    print(f"{Colors.BOLD}WHAT REDUCED VALUE{Colors.END}")
    print(f"{Colors.BOLD}───────────────────────────────────────────────────────────────{Colors.END}\n")
    
    reduced = []
    if not metrics.test_metrics.framework_detected:
        reduced.append(f"✗ No test framework detected")
    elif metrics.test_metrics.coverage_ratio < 0.3:
        reduced.append(f"✗ Low test coverage ({metrics.test_metrics.coverage_ratio*100:.0f}%)")
    
    if metrics.security_metrics.total_issues > 0:
        reduced.append(f"✗ {metrics.security_metrics.total_issues} security issues detected")
    
    if reduced:
        for item in reduced:
            print(f"  {item}")
    else:
        print(f"  {Colors.GREEN}No major value reducers detected{Colors.END}")
    
    print(f"\n{Colors.BOLD}───────────────────────────────────────────────────────────────{Colors.END}")
    print(f"{Colors.BOLD}WHAT WAS IGNORED{Colors.END}")
    print(f"{Colors.BOLD}───────────────────────────────────────────────────────────────{Colors.END}\n")
    
    print(f"  • Asset files ({metrics.asset_files} files) - $0.00")
    print(f"  • Build artifacts and dependencies")
    print(f"  • Binary files and media")
    print(f"  • Generated code")
    
    print(f"\n{Colors.BOLD}───────────────────────────────────────────────────────────────{Colors.END}")
    print(f"{Colors.BOLD}HOW THIS VALUE WAS CALCULATED{Colors.END}")
    print(f"{Colors.BOLD}───────────────────────────────────────────────────────────────{Colors.END}\n")
    
    print(f"  Base Cost Calculation:")
    print(f"    Lines of code × Complexity weight × (Hourly rate / Lines per hour)")
    print(f"    Applied file category multipliers (entrypoint, core, test, etc.)")
    print(f"\n  Adjustments Applied:")
    print(f"    • Git history: Project age and commit frequency")
    print(f"    • Tests: Framework detection and coverage ratio")
    print(f"    • Infrastructure: Docker, CI/CD presence")
    print(f"    • Database & API: Technology stack maturity")
    print(f"    • Security: Issues reduce value")
    
    print(f"\n{Colors.BOLD}───────────────────────────────────────────────────────────────{Colors.END}")
    print(f"{Colors.BOLD}KNOWN LIMITATIONS{Colors.END}")
    print(f"{Colors.BOLD}───────────────────────────────────────────────────────────────{Colors.END}\n")
    
    for limitation in metrics.limitations:
        print(f"  • {limitation}")
    
    print(f"\n{Colors.DIM}This is a technical development cost estimate using heuristic")
    print(f"analysis. It does NOT include business value, intellectual property,")
    print(f"market position, revenue, or other commercial factors.{Colors.END}\n")
    
    if show_tree:
        print(f"{Colors.BOLD}───────────────────────────────────────────────────────────────{Colors.END}")
        print(f"{Colors.BOLD}TOP VALUE FILES{Colors.END}")
        print(f"{Colors.BOLD}───────────────────────────────────────────────────────────────{Colors.END}\n")
        
        top_files = [fv for fv in metrics.file_values if fv.is_code][:20]
        for fv in top_files:
            rel_path = Path(fv.path).name
            if fv.category == "entrypoint":
                color = Colors.GREEN
                marker = "⚡"
            elif fv.category == "core":
                color = Colors.YELLOW
                marker = "●"
            else:
                color = Colors.END
                marker = "○"
            
            print(f"  {marker} {rel_path:<40} {color}{format_currency(fv.final_value)}{Colors.END}")
        
        print(f"\n{Colors.BOLD}TOP VALUE DIRECTORIES{Colors.END}\n")
        
        sorted_dirs = sorted(metrics.directory_values.items(), key=lambda x: x[1], reverse=True)[:10]
        for dir_path, value in sorted_dirs:
            dir_name = Path(dir_path).name or "root"
            print(f"  {dir_name:<40} {Colors.GREEN}{format_currency(value)}{Colors.END}")

def save_report(metrics: ProjectMetrics, output_path: Path):
    report = {
        'metadata': {
            'project_name': metrics.project_name,
            'analysis_timestamp': metrics.analysis_timestamp,
            'analyzed_paths': metrics.analyzed_paths,
            'tool_version': __version__
        },
        'summary': {
            'total_files': metrics.total_files,
            'code_files': metrics.code_files,
            'asset_files': metrics.asset_files,
            'total_lines': metrics.total_lines,
            'code_lines': metrics.code_lines,
            'estimated_hours': metrics.estimated_hours
        },
        'valuation': asdict(metrics.valuation),
        'git_metrics': asdict(metrics.git_metrics),
        'test_metrics': asdict(metrics.test_metrics),
        'infra_metrics': asdict(metrics.infra_metrics),
        'database_metrics': asdict(metrics.database_metrics),
        'api_metrics': asdict(metrics.api_metrics),
        'security_metrics': asdict(metrics.security_metrics),
        'languages': metrics.languages,
        'top_files': [asdict(fv) for fv in metrics.file_values[:50] if fv.is_code],
        'top_directories': dict(sorted(metrics.directory_values.items(), key=lambda x: x[1], reverse=True)[:20]),
        'limitations': metrics.limitations
    }
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"\n{Colors.GREEN}✓ Report saved: {output_path}{Colors.END}")

def main():
    config = load_config()
    
    parser = argparse.ArgumentParser(
        description="Price Reveal - Technical Valuation System",
        epilog="Use --config to customize analysis parameters"
    )
    
    parser.add_argument("path", nargs="?", help="Project path to analyze")
    parser.add_argument("--config", action="store_true", help="Open configuration menu")
    parser.add_argument("--select", action="store_true", help="Select specific folders")
    parser.add_argument("--output", "-o", type=str, help="Output JSON file")
    parser.add_argument("--no-tree", action="store_true", help="Hide file tree")
    parser.add_argument("--no-color", action="store_true", help="Disable colors")
    parser.add_argument("--version", action="version", version=f"Price Reveal v{__version__}")
    
    args = parser.parse_args()
    
    if args.no_color:
        Colors.disable()
    
    if args.config:
        config_menu()
        return
    
    if not args.path:
        print(f"\n{Colors.CYAN}{Colors.BOLD}Price Reveal v{__version__}{Colors.END}")
        print(f"{Colors.DIM}Technical Valuation System{Colors.END}\n")
        path_input = input(f"Project path: ").strip()
        if not path_input:
            print(f"{Colors.RED}No path provided{Colors.END}")
            sys.exit(1)
        args.path = path_input
    
    try:
        project_path = Path(args.path).resolve()
        if not project_path.exists():
            raise FileNotFoundError(f"Path not found: {args.path}")
        if not project_path.is_dir():
            raise NotADirectoryError(f"Not a directory: {args.path}")
    except Exception as e:
        print(f"{Colors.RED}✗ {e}{Colors.END}")
        sys.exit(1)
    
    if args.select:
        selected = select_folders(project_path)
    else:
        selected = [project_path]
    
    print(f"\n{Colors.CYAN}Analyzing project...{Colors.END}")
    
    try:
        metrics = analyze_project(selected, project_path, config)
    except Exception as e:
        print(f"{Colors.RED}✗ Analysis failed: {e}{Colors.END}")
        sys.exit(1)
    
    print_report(metrics, not args.no_tree)
    
    if args.output:
        output_path = Path(args.output)
    else:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_path = Path(f"pricereveal_{metrics.project_name}_{timestamp}.json")
    
    save_report(metrics, output_path)
    
    print(f"\n{Colors.GREEN}✓ Analysis complete{Colors.END}\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Interrupted{Colors.END}\n")
        sys.exit(0)
    except Exception as e:
        print(f"\n{Colors.RED}Fatal error: {e}{Colors.END}\n")
        sys.exit(1)
