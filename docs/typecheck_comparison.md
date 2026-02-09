# Typechecker Comparison and Recommendation

This document provides a comparison of the Python typecheckers tested for this project and includes a recommendation for the best tool(s) to use.

## Tools Tested

The following typecheckers were evaluated:

1. **pytype** (version 2024.10.11)
2. **mypy** (version 1.19.1)
3. **pyright** (version 1.1.408)
4. **basedpyright** (version 1.37.4)

## Comparison Criteria

### 1. Runtime Performance

Performance was measured by running each typechecker 3 times on the entire codebase and calculating the average runtime:

| Tool | Average Runtime (ms) | Relative Speed |
|------|---------------------|----------------|
| mypy | 201 | **Fastest** |
| pytype | 1695 | 8.4x slower |
| pyright | 1531 | 7.6x slower |
| basedpyright | 1561 | 7.8x slower |

**Winner: mypy** - Significantly faster than all other tools, making it ideal for rapid development feedback.

### 2. Strictness and Type Coverage

- **pytype**: Moderate strictness. Uses inference to fill in missing types. Does not support Python 3.13+.
- **mypy**: Configurable strictness. Industry standard with extensive configuration options. Can be very strict or lenient based on configuration.
- **pyright**: High strictness by default. Microsoft-backed tool with excellent IDE integration (VS Code). More strict than mypy in default configuration.
- **basedpyright**: Fork of pyright with enhanced features and community-driven development. Similar strictness to pyright but with additional community-requested features.

**Winner: pyright/basedpyright** - Most comprehensive type checking with highest strictness. basedpyright offers additional community features.

### 3. Maintainer Support and Community Adoption

- **pytype**: Maintained by Google. Limited Python version support (no 3.13+). Smaller community.
- **mypy**: The original and most widely adopted Python type checker. Large community, extensive documentation, and plugins. Actively maintained by Dropbox and the Python community.
- **pyright**: Maintained by Microsoft. Excellent integration with VS Code. Growing community adoption. Very active development.
- **basedpyright**: Community-driven fork of pyright. Active development with rapid feature additions. Smaller but dedicated community.

**Winner: mypy** - Largest community, most extensive ecosystem, and longest track record of stability.

### 4. Configuration and Ease of Use

- **pytype**: Minimal configuration required. Simple `pytype.cfg` file.
- **mypy**: Extensive configuration options via `mypy.ini` or `pyproject.toml`. Well-documented.
- **pyright**: JSON-based configuration (`pyrightconfig.json`). Clean and well-structured.
- **basedpyright**: Inherits pyright's configuration. Additional options for community features.

**Winner: mypy** - Most mature configuration options with the best documentation.

### 5. Python Version Support

- **pytype**: Does not support Python 3.13+ (critical limitation).
- **mypy**: Supports all modern Python versions including 3.13+.
- **pyright**: Supports all modern Python versions including 3.13+.
- **basedpyright**: Supports all modern Python versions including 3.13+.

**Winner: mypy, pyright, basedpyright** - All support current Python versions. pytype is disqualified for this project's future needs.

## Recommendation

### Primary Recommendation: mypy

**mypy** is recommended as the primary typechecker for this project for the following reasons:

1. **Performance**: 7-8x faster than alternatives, providing rapid feedback during development.
2. **Community**: Largest ecosystem, best documentation, and most extensive plugin support.
3. **Stability**: Longest track record and most mature tool.
4. **Python 3.13+ Support**: Unlike pytype, mypy will continue to work as the project upgrades Python versions.
5. **Configurability**: Extensive options allow the project to start lenient and gradually increase strictness.

### Secondary Recommendation: basedpyright

**basedpyright** is recommended as a secondary typechecker for the following reasons:

1. **Strictness**: Catches more potential issues than mypy in default configuration.
2. **Community Features**: Benefits from community-driven enhancements over base pyright.
3. **Complementary**: Finds different categories of issues than mypy, providing additional coverage.
4. **Active Development**: Rapid feature additions and bug fixes.

### Ranked List

1. **mypy** - Primary tool, fast and reliable
2. **basedpyright** - Secondary tool, strictest checking
3. **pyright** - Alternative to basedpyright if community fork is undesirable
4. **pytype** - To be phased out due to Python 3.13+ incompatibility

## Configuration Notes

All tools have been configured with minimal, local configuration files:

- `mypy.ini` - Basic configuration with lenient test file checking
- `basedpyright.json` - Basic configuration with reasonable strictness
- `pyrightconfig.json` - Basic configuration matching basedpyright

The local `Makefile` enables the recommended tools:

```makefile
RUN_MYPY := 1
RUN_PYRIGHT := 1
RUN_BASEDPYRIGHT := 1
```

## Migration Path

1. **Current state**: All four typecheckers enabled and passing.
2. **Short term**: Continue running all tools to maximize coverage.
3. **Medium term** (Python 3.13 upgrade): Disable pytype by setting `RUN_PYTYPE := 0` in Makefile.
4. **Long term**: Consider disabling pyright if basedpyright provides sufficient coverage, or vice versa.

## Conclusion

This project now has comprehensive type checking with multiple tools. The combination of mypy (for speed) and basedpyright (for strictness) provides excellent coverage while maintaining fast development cycles. The phasing out of pytype is necessary for Python 3.13+ compatibility.
