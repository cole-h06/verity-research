# Verity

A source reliability system for e-commerce product data.

# The Problem

Product specs conflict across retailers, manufacturers, and government sites. Sources copy each other, so errors propagate. You can't resolve conflicts by majority vote alone.

# The Core Challenge

Sources and claims have a dependency relationship: a source's reliability depends on the accuracy of its claims, and a claim's accuracy depends on the reliability of its sources.

# Stack

- Python (crawler + scraper)
- SQLite (data storage)
- 275+ products scraped across multiple source types (retailers, manufacturers, government sites)

# Status

Data pipeline running. Algorithm design in progress.

