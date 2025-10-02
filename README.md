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

**Important Notes:**
- **URL Input**: Must be a publicly accessible image URL (no authentication required)
- **Base64 Input**: Use `data:image/jpeg;base64,<base64_string>` format
- **Sample Images**: Test images available in [sample_imgs](https://github.com/your-username/exif-extractor/tree/main/sample_imgs) directory

### Resource: `exif://supported-formats`
Information about supported image formats and extracted EXIF data.

## Testing

### Using Public URLs
The server requires publicly accessible image URLs without authentication. You can:

1. **Use sample images** from the [sample_imgs](https://github.com/your-username/exif-extractor/tree/main/sample_imgs) directory
2. **Upload your own images** to services like:
   - [Postimages](https://postimages.org/) - Free, no registration required
   - [ImgBB](https://imgbb.com/) - Free image hosting
   - [GitHub](https://github.com) - Upload to your repository

### Using Base64
For local images, convert to Base64:
```python
import base64

with open("your_image.jpg", "rb") as f:
    base64_string = base64.b64encode(f.read()).decode('utf-8')
    data_url = f"data:image/jpeg;base64,{base64_string}"
```

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
