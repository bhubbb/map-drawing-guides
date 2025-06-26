# Drawing Guides MCP Server

A Model Context Protocol (MCP) server that provides access to drawing tutorials and guides from easydrawingguides.com, making it easy to find and retrieve step-by-step drawing instructions for artists of all skill levels.

## Overview

This MCP server acts as a bridge between AI assistants and popular drawing tutorial websites, specifically designed to:

- **Comprehensive Search**: Search across Easy Drawing Guides for drawing tutorials
- **Detailed Tutorials**: Retrieve complete drawing guides with step-by-step instructions
- **Content Extraction**: Parse and structure drawing instructions for easy consumption
- **Category Navigation**: Browse available drawing categories and topics
- **Family-Friendly**: Access kid-friendly and beginner-oriented drawing content

## Features

### 🔍 Search Tool
- Search across drawing tutorials from Easy Drawing Guides
- Returns structured metadata and ranked list of relevant guides
- Validates all returned URLs to ensure they are accessible
- Configurable result limits

### 📋 Guide Retrieval Tool
- Retrieve complete drawing tutorial content from URLs as Markdown
- Extract content from the main article section (removes ads)
- Preserve original formatting and structure in Markdown format
- Clean, readable output with metadata

### 📚 Categories Tool
- List available drawing categories from Easy Drawing Guides
- Discover popular drawing topics and themes
- Get suggestions for search terms and ideas

## Installation & Setup

### Prerequisites
- Python 3.12 or higher
- `uv` package manager

### Quick Start

**Run directly with uvx (once published):**
```bash
uvx mcp-drawing-guides
```

**Or run from local directory:**
```bash
uvx --from . mcp-drawing-guides
```

**Or install locally:**
1. **Clone or download this project**
2. **Install dependencies:**
   ```bash
   cd mcp-drawing-guides
   uv sync
   ```

3. **Run the server:**
   ```bash
   uv run python main.py
   ```

### Integration with AI Assistants

This MCP server is designed to work with AI assistants that support the Model Context Protocol. Configure your AI assistant to connect to this server via stdio.

Example configuration for Claude Desktop:
```json
{
  "mcpServers": {
    "drawing-guides": {
      "command": "uvx",
      "args": ["--from", "/path/to/mcp-drawing-guides", "mcp-drawing-guides"]
    }
  }
}
```

Or if using a local installation:
```json
{
  "mcpServers": {
    "drawing-guides": {
      "command": "uv",
      "args": ["run", "python", "/path/to/mcp-drawing-guides/main.py"]
    }
  }
}
```

## Available Tools

### `search`
Search for drawing tutorials across supported sites.

**Parameters:**
- `query` (required): Search terms (e.g., "cat", "anime character", "flower")
- `limit` (optional): Max results to return (1-20, default: 10)
- `source` (optional): Which site to search - "easy" (default: "easy")

**Returns:**
- Search metadata (query, results count, sources searched)
- List of matching drawing guides with titles and validated URLs

**Example:**
```json
{
  "name": "search",
  "arguments": {
    "query": "cute cat",
    "limit": 5,
    "source": "easy"
  }
}
```

### `get_guide`
Retrieve detailed content of a specific drawing guide.

**Parameters:**
- `url` (required): URL of the drawing guide from easydrawingguides.com

**Returns:**
- Guide metadata (title, source, URL, content length)
- Complete tutorial content formatted as Markdown

**Example:**
```json
{
  "name": "get_guide",
  "arguments": {
    "url": "https://easydrawingguides.com/draw-cat/"
  }
}
```

### `list_categories`
List available drawing categories and popular topics.

**Parameters:**
- None required

**Returns:**
- Categories from Easy Drawing Guides
- Popular search terms and suggestions

**Example:**
```json
{
  "name": "list_categories",
  "arguments": {}
}
```

## Supported Sites

### Easy Drawing Guides (easydrawingguides.com)
- **Focus**: Step-by-step drawing tutorials for all skill levels
- **Content**: Animals, people, plants, cartoons, objects, anime, video games
- **Features**: Detailed instructions, printable worksheets, video tutorials
- **Audience**: Kids, beginners, and hobbyists

## How It Works

### Content Extraction Process

1. **Web Scraping**: Uses requests and BeautifulSoup to fetch and parse web content
2. **Content Targeting**: Extracts content specifically from `<div class="inside-article">` 
3. **Ad Removal**: Removes `<div class="mv-ad-box">` elements to clean up content
4. **Markdown Conversion**: Converts HTML content to clean, readable Markdown format
5. **Metadata Generation**: Creates structured metadata for each guide

### Search Algorithm

1. **Site Search**: Queries Easy Drawing Guides for relevant tutorials
2. **Relevance Ranking**: Sorts results by keyword relevance in titles
3. **URL Validation**: Validates each URL to ensure it's accessible before including in results
4. **Content Filtering**: Filters out irrelevant or duplicate results
5. **Source Attribution**: Clearly identifies the source of each result

### Structured Output Format

All tools return structured responses with separate blocks for:
- **Metadata**: Source, URL, content statistics, search parameters
- **Content**: Main tutorial content and descriptions
- **Instructions**: Step-by-step drawing instructions when available
- **References**: Image URLs and alt text for visual reference

## Use Cases

### For Art Students & Beginners
- Find step-by-step tutorials for specific subjects
- Learn fundamental drawing techniques
- Access beginner-friendly instructions with clear steps

### For Parents & Teachers
- Discover family-friendly drawing activities
- Find age-appropriate art projects for children
- Access educational content for art classes

### For Digital Artists & Hobbyists
- Get inspiration for new drawing subjects
- Find reference materials and instruction guides
- Learn new drawing styles and techniques

### For Content Creators
- Source tutorial content for art education
- Find step-by-step processes to reference
- Access structured drawing instruction data

## Quick Start Guide

1. **Clone or download this repository**
2. **Install dependencies:**
   ```bash
   cd mcp-drawing-guides
   uv sync
   ```
3. **Test the server:**
   ```bash
   uv run python main.py
   ```
   Press Ctrl+C to stop the server.

4. **Configure your AI assistant** to use this MCP server

## Examples

### Basic Search
Ask your AI assistant: *"Search for drawing tutorials about dogs"*

The server will:
1. Search Easy Drawing Guides for "dogs"
2. Return structured metadata (query, result count, sources)
3. Provide a list of relevant tutorials with validated URLs
4. Include direct access to full guides

### Retrieve Specific Guide
Ask your AI assistant: *"Get the detailed instructions for this drawing guide: [URL]"*

The server will:
1. Fetch the complete tutorial content from the URL
2. Extract content from the main article section (removes ads)
3. Convert HTML content to clean Markdown format
4. Return structured metadata and formatted content

### Browse Categories
Ask your AI assistant: *"What drawing categories are available?"*

The server will:
1. Return organized lists of categories from Easy Drawing Guides
2. Provide popular search terms and suggestions
3. Help you discover new drawing topics and themes

## Development

### Project Structure
```
mcp-drawing-guides/
├── main.py          # Main MCP server implementation
├── pyproject.toml   # Project dependencies and metadata
├── README.md        # This documentation
└── .venv/           # Virtual environment (created by uv)
```

### Key Dependencies
- `mcp`: Model Context Protocol framework
- `requests`: HTTP library for web scraping
- `beautifulsoup4`: HTML parsing and content extraction
- `lxml`: Fast XML and HTML parser
- `markdownify`: HTML to Markdown conversion

### Customization

The server can be easily customized by modifying `main.py`:

- **Add New Sites**: Extend the search functions to support additional tutorial sites
- **Improve Parsing**: Enhance content extraction for better step identification
- **Content Filtering**: Add custom filters for content quality or appropriateness
- **Caching**: Implement caching to improve performance and reduce server load

### Testing the Server

Test the server directly:
```bash
cd mcp-drawing-guides
uvx --from . mcp-drawing-guides
```

Or with local installation:
```bash
cd mcp-drawing-guides
uv run python main.py
```

The server communicates via JSON-RPC over stdin/stdout, so you'll need an MCP client or AI assistant to interact with it properly.

## Troubleshooting

### Common Issues

1. **Import Errors**: Make sure all dependencies are installed with `uv sync`
2. **Network Issues**: Check internet connectivity for accessing tutorial sites
3. **Parsing Errors**: Some pages may have different structures; the server handles this gracefully
4. **Rate Limiting**: Be respectful of the source sites' server resources

### Debugging

Enable debug logging by modifying the logging level in `main.py`:
```python
logging.basicConfig(level=logging.DEBUG)
```

## Ethical Considerations

- **Respect**: This server respects the robots.txt and terms of service of source sites
- **Attribution**: All content is properly attributed to its original source
- **Non-Commercial**: Intended for educational and personal use
- **Fair Use**: Extracts only necessary content for tutorial purposes

## Contributing

This is a simple, single-file implementation designed for clarity and ease of modification. Feel free to:

- Add support for additional drawing tutorial sites
- Improve content extraction algorithms
- Add caching for better performance
- Extend with additional drawing-related features

## License

This project uses the same license as its dependencies. The drawing tutorial content accessed through this server remains the property of the original sites and creators.

---

*This MCP server makes drawing tutorials more accessible by providing structured access to step-by-step drawing guides from trusted educational sources.*