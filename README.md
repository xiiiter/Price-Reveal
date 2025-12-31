# Price Reveal - Technical Valuation System

Professional software project analyzer with advanced valuation capabilities. Goes beyond simple cost estimation to provide technical value assessment based on infrastructure maturity, quality signals, and risk factors.

## Features

### Core Analysis
- **Multi-language support**: Python, JavaScript, TypeScript, Java, C/C++, Go, Rust, and 15+ more
- **Complexity-aware calculation**: Different languages weighted by complexity
- **Flexible scope**: Analyze entire projects or specific folders
- **File-level valuation**: Monetary value calculated per file with category-based multipliers

### Advanced Valuation Signals

#### Infrastructure & History
- **Git Integration**: Analyzes commit history, project age, contributors, and activity
- **Historical Context**: Evaluates project evolution over time

#### Quality & Testing
- **Test Framework Detection**: Identifies pytest, Jest, JUnit, RSpec, and more
- **Coverage Estimation**: Heuristic test coverage calculation
- **Code Quality Signals**: Detects testing infrastructure and practices

#### Architecture & Product
- **API Detection**: Identifies REST, GraphQL, and gRPC implementations
- **Frontend Frameworks**: Detects React, Vue, Angular, Svelte, Next.js
- **Database Integration**: Finds PostgreSQL, MySQL, MongoDB, Redis, and others
- **Docker Support**: Recognizes Dockerfile and docker-compose configurations

#### DevOps & Collaboration
- **CI/CD Detection**: Identifies GitHub Actions, GitLab CI, Jenkins, CircleCI
- **Team Collaboration**: Estimates team size from Git contributors
- **Branch Management**: Analyzes branching strategy

#### Security & Risk
- **Security Scanning**: Heuristic detection of potential security issues
- **Risk Assessment**: Adjusts valuation based on detected risks

## Installation

```bash
chmod +x price_reveal.py
```

### Requirements
- Python 3.7+
- Git (optional, for repository analysis)
- No external dependencies

## Usage

### Basic Analysis

```bash
./price_reveal.py /path/to/project
```

### Interactive Folder Selection

```bash
./price_reveal.py /path/to/project --select-folders
```

Select specific folders to analyze:
- Single folder: `1`
- Multiple folders: `1,3,5`
- Entire project: `0`

### Configuration Mode

```bash
./price_reveal.py --config
```

Allows you to:
- Adjust hourly rates and productivity metrics
- Configure valuation weights for each signal
- Set file value multipliers
- Enable/disable specific features
- Save configuration persistently

### Output Options

```bash
# Save to custom file
./price_reveal.py /path/to/project --output report.json

# Verbose mode
./price_reveal.py /path/to/project --verbose

# Hide file tree
./price_reveal.py /path/to/project --no-tree

# Disable colors
./price_reveal.py /path/to/project --no-color
```

## Valuation Model

### How Value is Calculated

The system uses a multi-factor valuation model:

```
Estimated Technical Value = Base Cost × Maturity Multiplier × Risk Adjustment
```

#### 1. Base Development Cost
Calculated per file based on:
- Lines of code
- Language complexity weight
- File category (entrypoint, core, test, config, documentation)
- Hourly development rate

**File Categories:**
- **Entrypoint** (2.5x): `main.py`, `index.js`, `app.py`, `server.js`
- **Core** (2.0x): Files in `core/`, `engine/`, `kernel/` directories
- **Test** (0.6x): Test and spec files
- **Config** (0.4x): JSON, YAML, TOML files
- **Documentation** (0.3x): Markdown, RST files

#### 2. Maturity Multiplier
Increases value based on detected signals:

| Signal | Weight | Trigger |
|--------|--------|---------|
| Git History | 1.3x | >1000 commits (scaled for fewer) |
| Test Coverage | 1.25x | Tests detected (scaled by coverage %) |
| Docker | 1.15x | Dockerfile present |
| Database | 1.2x | DB integration detected |
| API | 1.3x | REST/GraphQL/gRPC detected |
| Frontend | 1.25x | Modern framework detected |
| CI/CD | 1.15x | Automation configured |
| Documentation | 1.1x | Good/excellent quality |
| Team Collaboration | 1.2x | Multiple contributors |

Multipliers compound for mature projects with multiple signals.

#### 3. Risk Adjustment
Reduces value based on detected issues:

| Risk Factor | Impact | Trigger |
|-------------|--------|---------|
| Security Issues | 0.85x | >10 potential issues detected |
| No Tests | 0.9x | No test framework found |
| No README | 0.95x | No documentation |

### Example Calculation

```
Project: E-commerce Platform
Base Cost: $45,000
Signals Detected:
  - Git: 2,300 commits, 5 contributors → 1.3x
  - Tests: 85% coverage → 1.22x
  - Docker + Compose → 1.15x
  - PostgreSQL → 1.2x
  - REST API → 1.3x
  - React Frontend → 1.25x
  - GitHub Actions → 1.15x
  - Excellent docs → 1.1x
  - Team collaboration → 1.2x

Maturity: 1.3 × 1.22 × 1.15 × 1.2 × 1.3 × 1.25 × 1.15 × 1.1 × 1.2 = 4.87x
Risk: No major issues = 1.0x

Technical Value: $45,000 × 4.87 × 1.0 = $219,150
```

## Configuration System

The configuration system allows full customization without editing code.

### Access Configuration

```bash
./price_reveal.py --config
```

### Configuration Options

#### 1. Base Settings
- Hourly rate (default: $50/hour)
- Lines per hour productivity (default: 40)

#### 2. Valuation Weights
Adjust impact of each signal:
- `git_history_weight`: Default 1.3
- `test_coverage_weight`: Default 1.25
- `docker_weight`: Default 1.15
- `database_weight`: Default 1.2
- `api_weight`: Default 1.3
- `frontend_weight`: Default 1.25
- `ci_weight`: Default 1.15
- `documentation_weight`: Default 1.1
- `team_collaboration_weight`: Default 1.2

#### 3. Risk Factors
- `security_penalty`: Default 0.85
- Applies when >10 security issues detected

#### 4. File Value Multipliers
- `entrypoint_multiplier`: Default 2.5
- `core_multiplier`: Default 2.0
- `test_multiplier`: Default 0.6
- `config_multiplier`: Default 0.4
- `documentation_multiplier`: Default 0.3

#### 5. Feature Toggles
Enable/disable specific valuation signals:
- `git_history_enabled`
- `test_coverage_enabled`
- `docker_enabled`
- `database_enabled`
- `api_enabled`
- `frontend_enabled`
- `ci_enabled`
- `security_enabled`
- `documentation_enabled`
- `team_collaboration_enabled`

### Configuration Storage

Configuration is saved to `~/.pricereveal_config.json` and persists across sessions.

## Output Format

### Terminal Report

Shows:
- Project overview (files, lines, size)
- Value calculation breakdown
- All detected signals with details
- Methodology explanation

### File Tree with Values

```
src/
├── api/
│   ├── users.py          $1,240.00
│   ├── auth.py           $2,180.00
├── core/
│   ├── engine.py         $4,960.00
│   ├── processor.py      $3,420.00
├── main.py               $2,050.00  (entrypoint)

📂 Directory Values:
  src/core: $8,380.00
  src/api: $3,420.00
  src/utils: $1,850.00
```

### JSON Report

Complete machine-readable output including:
- All metrics and calculations
- Full signal detection results
- Per-file valuations
- Directory-level aggregations
- Value breakdown and methodology

## Limitations

### What This Tool Does
- Provides technical value estimation based on code analysis
- Identifies infrastructure maturity signals
- Assesses development investment
- Highlights quality and risk factors

### What This Tool Does NOT Do
- Financial or business valuation
- Market value assessment
- Revenue or profit estimation
- Legal or accounting analysis
- CVE-based vulnerability scanning
- Actual code execution or testing

### Important Notes

**This is a heuristic model**: All calculations are estimates based on detectable patterns in code. The "value" represents accumulated technical investment and infrastructure maturity, not market value or business worth.

**Not a replacement for**: 
- Professional software audits
- Financial valuations
- Security assessments
- Code reviews

**Best used for**:
- Project scoping and estimation
- Portfolio analysis
- Technology stack assessment
- Development investment tracking
- Team productivity benchmarking

## Detection Methods

### Git Analysis
- Uses `git` command-line interface
- Analyzes commit history, contributors, branches
- Requires Git repository to be present

### Test Detection
Searches for:
- Test file naming patterns (`test_*.py`, `*.test.js`, `*_spec.rb`)
- Test framework imports (pytest, jest, junit, rspec, etc.)
- Test directories

### Infrastructure Detection
Checks for:
- Configuration files (Dockerfile, docker-compose.yml)
- CI/CD configs (.github/workflows, .gitlab-ci.yml, etc.)
- Package managers and dependencies
- Database clients in code

### Security Scanning
Heuristic pattern matching for:
- Hardcoded credentials
- Dangerous function usage (eval, exec)
- Injection vulnerabilities patterns
- XSS patterns in frontend code

**Note**: This is NOT a comprehensive security audit. Use dedicated security tools for production systems.

## Examples

### Analyze Full Project
```bash
./price_reveal.py ~/projects/my-app
```

### Analyze Specific Folders
```bash
./price_reveal.py ~/projects/my-app --select-folders
# Then select: 1,3,5 for src, api, and core folders
```

### Custom Configuration
```bash
./price_reveal.py --config
# Set hourly rate to $100
# Increase git_history_weight to 1.5
# Save and exit

./price_reveal.py ~/projects/my-app
```

### Generate Report
```bash
./price_reveal.py ~/projects/my-app --output valuation_report.json
```

## Methodology

Price Reveal uses a research-informed approach combining:

1. **Industry Standards**: Typical development productivity metrics
2. **Complexity Science**: Language-specific complexity weights
3. **Infrastructure Patterns**: Common architectural signals
4. **Quality Metrics**: Testing and documentation standards
5. **Risk Assessment**: Security and maintenance indicators

The model is designed to be:
- **Transparent**: All factors are visible and explainable
- **Configurable**: Weights can be adjusted for your context
- **Consistent**: Same inputs produce same outputs
- **Conservative**: Prefers underestimation to overestimation

## Version History

### 4.0.0 (Current)
- Complete valuation system with maturity and risk factors
- Per-file value calculation with category multipliers
- Interactive configuration system
- Folder selection capability
- Git history analysis
- Test coverage estimation
- Infrastructure detection (Docker, databases, APIs)
- Frontend framework detection
- CI/CD platform detection
- Security heuristics
- Documentation quality assessment
- Team collaboration signals

### 3.0.0
- Basic cost estimation
- Multi-language support
- Complexity weights

## License

This tool is provided as-is for project analysis purposes. Use professional services for financial decisions.

## Support

For issues or questions, review the documentation or examine the source code. The tool is designed to be self-explanatory and configurable.
