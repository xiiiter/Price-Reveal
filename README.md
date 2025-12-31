# Price Reveal

**Technical Valuation System for Software Projects**

Version 5.0.0

---

## What Is This?

Price Reveal analyzes software projects and estimates their **technical development value** based on code quality, infrastructure maturity, and engineering practices.

This is NOT a business valuation tool. It estimates what it would cost to rebuild the technical components from scratch, adjusted for quality signals.

---

## Installation

```bash
chmod +x price_reveal.py
sudo mv price_reveal.py /usr/local/bin/price_reveal
```

Or run directly:

```bash
python3 price_reveal.py /path/to/project
```

---

## Quick Start

**Analyze a project:**
```bash
price_reveal .
```

**Select specific folders:**
```bash
price_reveal --select .
```

**Configure analysis:**
```bash
price_reveal --config
```

**Save report:**
```bash
price_reveal . --output report.json
```

---

## How It Works

### Base Calculation

```
Base Cost = Lines of Code × Complexity Weight × (Hourly Rate / Lines per Hour)
```

**Complexity weights** vary by language:
- Rust, C++: 1.5x (complex)
- Java, TypeScript: 1.2x (moderate)
- Python, JavaScript: 1.0x (baseline)
- HTML, CSS: 0.5x (simple)
- Config files: 0.2-0.3x (minimal)

**File category multipliers:**
- Entrypoint files (main.py, index.js): 2.5x
- Core business logic: 2.0x
- Infrastructure: 1.5x
- Tests: 0.6x
- Config: 0.4x

### Value Adjustments

After calculating base cost, the system applies adjustments based on detected signals:

**Positive Adjustments (Bonuses):**
- Git History: +18% (if ≥10 commits)
- Docker: +8%
- CI/CD: +12%
- Database: +15%
- API: +20%

**Negative Adjustments (Penalties):**
- Missing Tests: -25%
- Security Issues: -30%

**Example:**
```
Base Cost:              $24,800
Git History Bonus:     +18%  →  +$4,464
Test Coverage Penalty: -25%  →  -$7,316
Docker Bonus:          +8%   →  +$1,838
────────────────────────────────────
Final Technical Value:  $23,786
```

---

## What Gets Valued

### Included (Code Files)
- Source code (.py, .js, .java, .rs, etc.)
- Scripts (.sh, .bash)
- SQL files
- Configuration code (.yml, .json in src/)

### Excluded (Assets)
- Images, fonts, media files
- Build artifacts (dist/, build/)
- Dependencies (node_modules/, vendor/)
- Binary files
- Generated code

**Asset files appear in reports with $0.00 value.**

---

## Detection Systems

### Git Analysis
Detects:
- Total commits
- Number of contributors
- Project age (days)
- Branch count
- Commit frequency

**Requirements:**
- `.git/` directory present
- At least 10 commits for bonus

### Test Detection
Detects:
- pytest, jest, junit, rspec, mocha, xunit, go test
- Test files (test/, spec/ patterns)
- Test coverage ratio (test lines / code lines)

**Penalty applied if:**
- No test framework detected
- Coverage ratio < 30%

### Infrastructure
Detects:
- `Dockerfile`
- `docker-compose.yml`
- CI/CD configs (.github/workflows, .gitlab-ci.yml, etc.)

### Database
Detects in code:
- PostgreSQL
- MySQL
- MongoDB
- Redis
- SQLite
- Oracle
- SQL Server

### API
Detects in code:
- REST (Flask, FastAPI, Express, Gin)
- GraphQL (Apollo, type Query)
- gRPC (.proto files)
- WebSocket

### Security
Detects issues:
- Exposed .env files
- Hardcoded passwords/API keys/tokens in code

---

## Configuration System

Access via:
```bash
price_reveal --config
```

### Menu Options

**1. Base Settings**
- Hourly rate (default: $50)
- Lines per hour (default: 40)

**2. Enable/Disable Checks**
Toggle analysis for:
- Git
- Tests
- Docker
- CI/CD
- Security
- Database
- API

**3. Adjust Weights**
Modify bonus/penalty percentages:
- Git history: ±%
- Test coverage: ±%
- Docker: ±%
- CI/CD: ±%
- Database: ±%
- API: ±%
- Security: ±%

**4. File Category Multipliers**
Adjust multipliers for:
- Entrypoint (default: 2.5x)
- Core (default: 2.0x)
- Infrastructure (default: 1.5x)
- Test (default: 0.6x)
- Config (default: 0.4x)

**5. Reset to Defaults**

**6. Save & Exit**

Configuration saved to: `~/.pricereveal_config.json`

---

## Folder Selection

Use `--select` to choose which directories to analyze:

```bash
price_reveal --select .
```

**Interface:**
```
Select directories to analyze:

1. [x] src/
2. [x] api/
3. [ ] assets/
4. [ ] dist/
5. [x] tests/

Commands:
  a - Select all
  n - Select none
  <number> - Toggle directory
  done - Continue with selection
```

This prevents asset directories, build folders, or irrelevant code from inflating the valuation.

---

## Output Format

### Terminal Report

Shows:
1. **Value Calculation** - Breakdown with adjustments
2. **What Increased Value** - Detected positive signals
3. **What Reduced Value** - Detected negative signals
4. **What Was Ignored** - Asset files, builds
5. **How This Was Calculated** - Methodology explanation
6. **Known Limitations** - Honesty about accuracy
7. **Top Value Files** - Highest-value code files
8. **Top Value Directories** - Highest-value folders

### JSON Report

Saved automatically to: `pricereveal_<project>_<timestamp>.json`

Contains:
- Metadata (project name, timestamp, version)
- Summary (file counts, lines, hours)
- Complete valuation breakdown
- All detected metrics
- Top 50 code files
- Top 20 directories
- Limitations list

---

## Command-Line Options

```
price_reveal [path] [options]

Arguments:
  path                  Project directory (default: interactive prompt)

Options:
  --config              Open configuration menu
  --select              Interactive folder selection
  --output, -o FILE     Save JSON report to FILE
  --no-tree             Hide file/directory tree
  --no-color            Disable colored output
  --version             Show version
  -h, --help            Show help
```

---

## Methodology

This tool uses a **heuristic model** inspired by software engineering economics research.

**Not machine learning.** Not real market data.

The model combines:
1. Development cost estimation (COCOMO-inspired)
2. Infrastructure maturity signals
3. Quality indicators
4. Risk factors

**Assumptions:**
- Code complexity correlates with development time
- Mature infrastructure indicates professional development
- Tests indicate quality investment
- Security issues indicate technical debt

**This is conservative by design.** When uncertain, the tool undervalues rather than overvalues.

---

## Known Limitations

1. **No Git = Limited Maturity Assessment**
   Without Git history, project age and collaboration can't be measured.

2. **Heuristic Detection**
   Test frameworks, databases, and APIs are detected via pattern matching, not static analysis.

3. **Coverage Estimation**
   Test coverage is estimated from line ratios, not actual coverage tools.

4. **No Business Value**
   Does NOT include:
   - Revenue
   - Market position
   - Intellectual property value
   - Brand value
   - Customer base
   - Contracts or partnerships

5. **No Human Factors**
   Does NOT include:
   - Team experience
   - Onboarding time
   - Knowledge transfer costs
   - Maintainability (beyond tests)

6. **Language-Agnostic Complexity**
   Complexity weights are rough approximations, not precise measurements.

---

## Use Cases

### ✅ Good For

- Internal cost estimation
- Due diligence screening
- Technical debt assessment
- Comparing similar projects
- Prioritizing refactoring
- Demonstrating technical maturity

### ❌ Not For

- M&A valuations (use business valuation experts)
- Investment decisions (technical value ≠ market value)
- Pricing SaaS products (business model is separate)
- Legal disputes (not expert testimony)

---

## Philosophy

**Transparency over complexity.**

This tool could use neural networks, complex ML models, or opaque formulas. It doesn't.

Every adjustment is explainable. Every weight is configurable. Every calculation is auditable.

**Conservative over optimistic.**

When in doubt, undervalue. Better to be pleasantly surprised than disappointed.

**Technical, not commercial.**

This measures what was built, not what it's worth in the market.

A brilliant technical solution for a dying market has high technical value but low commercial value.

A mediocre technical solution for a thriving market has low technical value but high commercial value.

This tool only measures the first.

---

## Contributing

This is a commercial tool. For enterprise features, support, or customization:

Contact: [Your contact information]

---

## License

Proprietary. For personal and internal business use only.

Redistribution, resale, or offering as a service requires written permission.

---

## Version History

**5.0.0** - Complete rebuild
- Folder selection system
- Interactive configuration
- Transparent valuation breakdown
- Asset file handling ($0.00)
- Professional report format
- Conservative methodology

**4.0.0** - Previous version (replaced)

---

## FAQ

**Q: Why do my asset files show $0.00?**
A: Assets (images, fonts, videos) aren't code. They don't require software engineering to create. Only code files are valued.

**Q: Why is my value lower than expected?**
A: The tool is conservative. Missing tests, no Git history, or security issues reduce value significantly. This is intentional.

**Q: Can I adjust the weights?**
A: Yes. Use `price_reveal --config` to customize all weights and multipliers.

**Q: Why doesn't it detect my API/database?**
A: Detection uses pattern matching. If your code doesn't match common patterns, it won't be detected. This is a known limitation.

**Q: Is this legally defensible?**
A: No. This is a heuristic tool for internal estimation. For legal or financial purposes, hire experts.

**Q: What's the difference between this and business valuation?**
A: This values the **technical implementation**. Business valuation includes revenue, market, IP, customers, etc. They're completely different.

**Q: Can I use this for M&A?**
A: Only as one input among many. Technical value is a small part of overall business value.

**Q: Why not use ML?**
A: Transparency. A neural network can't explain why it gave a particular value. This tool can explain every adjustment.

---

**Built for engineers who value honesty over hype.**
