# FlashAPI ⚡

**An ultra-fast, modern web framework for Python**

[![PyPI version](https://img.shields.io/pypi/v/flashapi.svg)](https://pypi.org/project/flashapi/)
[![Python Versions](https://img.shields.io/pypi/pyversions/flashapi.svg)](https://pypi.org/project/flashapi/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Downloads](https://img.shields.io/pypi/dm/flashapi.svg)](https://pypi.org/project/flashapi/)

FlashAPI is a high-performance, lightweight web framework designed for building fast APIs with minimal overhead. Built on modern ASGI standards with performance optimizations out of the box.

## 🚀 Features

- **⚡ Ultra Fast**: Optimized routing and request handling
- **🛠️ Type-Safe**: Runtime type validation for path parameters
- **💾 Built-in Caching**: Decorator-based caching system
- **📊 Performance Monitoring**: Real-time request statistics
- **🔧 Middleware Ready**: CORS, compression, timing middleware included
- **🎯 Developer Friendly**: Excellent error messages and debugging
- **📦 Lightweight**: Minimal dependencies, fast startup

## 📦 Installation

```bash
pip install flashapi

# With Redis caching support
pip install flashapi[redis]

# Full installation with all features
pip install flashapi[full]

# Development dependencies
pip install flashapi[dev]