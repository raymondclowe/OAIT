# OAIT Examples

This directory contains example scripts demonstrating how to use OAIT components.

## Basic Usage

Run the basic usage example:

```bash
python examples/basic_usage.py
```

This example demonstrates:
- Creating and managing student models
- Persisting data to SQLite
- Managing session state
- Using the OpenRouter API client (requires API key)

## Setup

Before running examples that use the OpenRouter API, set your API key:

```bash
export OPENROUTER_API_KEY=your_key_here
```

Or add it to your `.env` file:

```
OPENROUTER_API_KEY=your_key_here
```

## Available Examples

### basic_usage.py
Demonstrates the core data models and persistence layer:
- Student model creation and updates
- SQLite persistence
- Session state management
- OpenRouter API integration

More examples will be added as the project develops.
