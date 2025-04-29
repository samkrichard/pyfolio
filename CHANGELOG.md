# Changelog

All notable changes to this project will be documented in this file.

This project adheres to [Semantic Versioning](https://semver.org/).

---

## [1.1.0] — 2025-04-29

### Added
- Input validation for all user commands
- Error handling for API failures and invalid portfolio entries
- Warnings for missing or empty `portfolio.json`
- Cleaner user input parsing via helper function
- Dynamic layout calculations for table width based on column count

### Changed
- Improved user feedback for invalid input and missing data
- Refined pricing command logic to reduce redundancy
- Internal code structure and commenting improved for clarity and maintainability

### Removed
- Removed alias `a` for `all-in` command to prevent future conflicts

---

## [1.0.0] — 2025-04-25

### Added
- Initial release of `pyfolio`
- Basic portfolio tracking with CoinGecko API integration
- Command-line interface for viewing portfolio value
- Configurable display currency
- Support for `help`, `currency`, `price`, `all-in`, and `exit` commands
