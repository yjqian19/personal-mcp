# EXIF Extractor MCP Server

A simple MCP server for extracting EXIF information from JPG and PNG images.

## Features

- Extract EXIF data from image URLs or Base64 data
- Support for JPG and PNG formats
- Extract camera information, technical parameters, and image details

## Installation

```bash
uv sync
```

## Running

```bash
# Development mode
uv run dev

# Production mode
uv run start

# Interactive testing
uv run playground
```

## Usage

### Tool: `extract_exif`
Extract EXIF information from image URL or Base64 data.

**Parameters:**
- `image_input` (string): Image URL or Base64 encoded image data

### Resource: `exif://supported-formats`
Information about supported image formats and extracted EXIF data.

## Configuration

- `timeout` (int): Request timeout in seconds (default: 30)
- `max_file_size` (int): Maximum file size in bytes (default: 50MB)
- `include_technical` (bool): Include technical parameters (default: true)
- `include_location` (bool): Include location information (default: false)

## Project Structure

```
exif-extractor/
├── pyproject.toml         # Project config
├── smithery.yaml          # Runtime specification
├── src/
│   └── exif_extractor/    # Server module
│       ├── __init__.py
│       └── server.py      # Main server implementation
└── README.md
```

## Resources

- [Smithery Documentation](https://smithery.ai/docs)
- [MCP Protocol](https://modelcontextprotocol.io)
