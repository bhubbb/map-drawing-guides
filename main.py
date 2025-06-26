#!/usr/bin/env python3
"""
Drawing Guides MCP Server

A Model Context Protocol server that provides access to drawing tutorials
from easydrawingguides.com.
"""

import asyncio
import logging
import re
from typing import Any, List, Dict
from urllib.parse import urljoin, quote
import requests
from bs4 import BeautifulSoup

from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
from mcp.types import (
    Tool,
)
import mcp.types as types

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("drawing-guides-mcp")

# Initialize the MCP server
server = Server("drawing-guides")

# Base URLs for the supported sites
EASY_DRAWING_GUIDES_BASE = "https://easydrawingguides.com"

# Headers to mimic browser requests
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

def make_request(url: str) -> requests.Response:
    """Make a web request with error handling."""
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        return response
    except requests.RequestException as e:
        logger.error(f"Request failed for {url}: {e}")
        raise

def search_easy_drawing_guides(query: str, limit: int = 10) -> List[Dict[str, Any]]:
    """Search for drawing guides on easydrawingguides.com."""
    try:
        # Use the site's search functionality
        search_url = f"{EASY_DRAWING_GUIDES_BASE}/?s={quote(query)}"
        response = make_request(search_url)
        soup = BeautifulSoup(response.content, 'html.parser')

        results = []
        # Look for article links in search results
        articles = soup.find_all('article', class_='post') or soup.find_all('h2')

        for article in articles[:limit]:
            title_elem = article.find('h2') or article.find('a')
            if title_elem:
                link_elem = title_elem.find('a') if title_elem.name != 'a' else title_elem
                if link_elem and link_elem.get('href'):
                    title = link_elem.get_text(strip=True)
                    url = urljoin(EASY_DRAWING_GUIDES_BASE, link_elem['href'])

                    # Validate the URL before adding to results
                    try:
                        validate_response = make_request(url)
                        if validate_response.status_code == 200:
                            results.append({
                                'title': title,
                                'url': url,
                                'source': 'Easy Drawing Guides'
                            })
                    except Exception as e:
                        logger.warning(f"Invalid URL skipped: {url} - {e}")
                        continue

        return results
    except Exception as e:
        logger.error(f"Search failed for Easy Drawing Guides: {e}")
        return []

def get_drawing_guide_content(url: str) -> Dict[str, Any]:
    """Extract drawing guide content from a URL."""
    try:
        response = make_request(url)
        soup = BeautifulSoup(response.content, 'html.parser')

        # Extract title
        title = soup.find('h1') or soup.find('title')
        title_text = title.get_text(strip=True) if title else "Unknown Title"

        # Extract main content
        content_selectors = [
            'div.entry-content',
            'article',
            'div.content',
            'main',
            'div.post-content'
        ]

        content_text = ""
        for selector in content_selectors:
            content_elem = soup.select_one(selector)
            if content_elem:
                # Remove script and style elements
                for script in content_elem(["script", "style"]):
                    script.decompose()

                content_text = content_elem.get_text(separator='\n', strip=True)
                break

        # Extract step-by-step instructions if present
        steps = []
        step_elements = soup.find_all(['ol', 'ul']) or soup.find_all('div', class_=re.compile(r'step', re.I))

        for step_elem in step_elements:
            if step_elem.name in ['ol', 'ul']:
                for li in step_elem.find_all('li'):
                    step_text = li.get_text(strip=True)
                    if step_text and len(step_text) > 10:  # Filter out short items
                        steps.append(step_text)
            else:
                step_text = step_elem.get_text(strip=True)
                if step_text and len(step_text) > 10:
                    steps.append(step_text)

        # Extract images (for reference)
        images = []
        img_elements = soup.find_all('img')
        for img in img_elements:
            src = img.get('src')
            if src:
                alt_text = img.get('alt', '') or ''
                images.append({
                    'src': urljoin(url, src),
                    'alt': alt_text
                })

        return {
            'title': title_text,
            'url': url,
            'content': content_text,
            'steps': steps,
            'images': images[:5],  # Limit to first 5 images
            'source': 'Easy Drawing Guides'
        }

    except Exception as e:
        logger.error(f"Failed to extract content from {url}: {e}")
        return {
            'title': 'Error',
            'url': url,
            'content': f'Failed to extract content: {str(e)}',
            'steps': [],
            'images': [],
            'source': 'Unknown'
        }

def get_categories() -> Dict[str, List[str]]:
    """Get available drawing categories from Easy Drawing Guides."""
    categories = {
        'Easy Drawing Guides': [
            'Animals', 'People', 'Plants', 'Cartoons', 'Objects',
            'Anime', 'Video Games', 'Flowers', 'Comics'
        ]
    }
    return categories

@server.list_tools()
async def handle_list_tools() -> list[Tool]:
    """
    List available tools.
    Each tool specifies its arguments using JSON Schema validation.
    """
    return [
        Tool(
            name="search",
            description="Search for drawing tutorials and guides from easydrawingguides.com",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query for drawing tutorials (e.g., 'cat', 'anime character', 'flower')"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of search results to return (default: 10)",
                        "default": 10,
                        "minimum": 1,
                        "maximum": 20
                    },
                    "source": {
                        "type": "string",
                        "description": "Which site to search (only easy is supported)",
                        "enum": ["easy"],
                        "default": "easy"
                    }
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="get_guide",
            description="Get detailed content of a specific drawing guide from a URL",
            inputSchema={
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "URL of the drawing guide to retrieve"
                    }
                },
                "required": ["url"]
            }
        ),
        Tool(
            name="list_categories",
            description="List available drawing categories from Easy Drawing Guides",
            inputSchema={
                "type": "object",
                "properties": {},
                "additionalProperties": False
            }
        )
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: dict[str, Any]) -> list[types.TextContent]:
    """
    Handle tool execution requests.
    """
    if name == "search":
        return await handle_search(arguments)
    elif name == "get_guide":
        return await handle_get_guide(arguments)
    elif name == "list_categories":
        return await handle_list_categories(arguments)
    else:
        raise ValueError(f"Unknown tool: {name}")

async def handle_search(arguments: dict[str, Any]) -> list[types.TextContent]:
    """Handle drawing guide search requests."""
    query = arguments.get("query")
    limit = arguments.get("limit", 10)
    source = arguments.get("source", "both")

    if not query:
        raise ValueError("Query parameter is required")

    results = []
    all_guides = []

    try:
        # Search Easy Drawing Guides
        easy_results = search_easy_drawing_guides(query, limit)
        all_guides.extend(easy_results)

        # Sort by relevance (simple keyword matching)
        query_lower = query.lower()
        all_guides.sort(key=lambda x: query_lower in x['title'].lower(), reverse=True)

        # Limit results
        all_guides = all_guides[:limit]

        if all_guides:
            # Metadata
            results.append(types.TextContent(
                type="text",
                text=f"# Search Metadata\n\n**Query:** {query}\n**Results Count:** {len(all_guides)}\n**Sources:** {source}\n**Sites Searched:** Easy Drawing Guides"
            ))

            # Search Results
            results_text = "# Drawing Guide Search Results\n\n"
            for i, guide in enumerate(all_guides, 1):
                results_text += f"## {i}. {guide['title']}\n"
                results_text += f"**Source:** {guide['source']}\n"
                results_text += f"**URL:** {guide['url']}\n\n"

            results.append(types.TextContent(
                type="text",
                text=results_text
            ))
        else:
            results.append(types.TextContent(
                type="text",
                text=f"# Search Results\n\n**Query:** {query}\n**Results Count:** 0\n**Sources:** {source}\n**Error:** No drawing guides found for your query. Try different keywords like 'animal', 'cartoon', 'flower', or 'character'."
            ))

    except Exception as e:
        logger.error(f"Search error: {e}")
        results.append(types.TextContent(
            type="text",
            text=f"# Search Error\n\n**Query:** {query}\n**Sources:** {source}\n**Error:** {str(e)}"
        ))

    return results

async def handle_get_guide(arguments: dict[str, Any]) -> list[types.TextContent]:
    """Handle drawing guide content retrieval."""
    url = arguments.get("url")

    if not url:
        raise ValueError("URL parameter is required")

    # Validate URL is from supported sites
    if not (EASY_DRAWING_GUIDES_BASE in url):
        raise ValueError("URL must be from easydrawingguides.com")

    results = []

    try:
        guide_content = get_drawing_guide_content(url)

        # Metadata
        results.append(types.TextContent(
            type="text",
            text=f"# Guide Metadata\n\n**Title:** {guide_content['title']}\n**Source:** {guide_content['source']}\n**URL:** {guide_content['url']}\n**Content Length:** {len(guide_content['content'])} characters\n**Steps Found:** {len(guide_content['steps'])}\n**Images Found:** {len(guide_content['images'])}"
        ))

        # Main Content
        if guide_content['content']:
            results.append(types.TextContent(
                type="text",
                text=f"# Drawing Guide Content\n\n{guide_content['content']}"
            ))

        # Step-by-step instructions if available
        if guide_content['steps']:
            steps_text = "# Step-by-Step Instructions\n\n"
            for i, step in enumerate(guide_content['steps'], 1):
                steps_text += f"**Step {i}:** {step}\n\n"

            results.append(types.TextContent(
                type="text",
                text=steps_text
            ))

        # Images reference if available
        if guide_content['images']:
            images_text = "# Reference Images\n\n"
            for i, img in enumerate(guide_content['images'], 1):
                images_text += f"**Image {i}:** {img['src']}\n"
                if img['alt']:
                    images_text += f"**Alt Text:** {img['alt']}\n"
                images_text += "\n"

            results.append(types.TextContent(
                type="text",
                text=images_text
            ))

    except Exception as e:
        logger.error(f"Guide retrieval error: {e}")
        results.append(types.TextContent(
            type="text",
            text=f"# Guide Retrieval Error\n\n**URL:** {url}\n**Error:** {str(e)}"
        ))

    return results

async def handle_list_categories(arguments: dict[str, Any]) -> list[types.TextContent]:
    """Handle listing of available drawing categories."""
    results = []
    try:
        categories = get_categories()

        # Metadata
        results.append(types.TextContent(
            type="text",
            text=f"# Drawing Categories\n\n**Total Sources:** {len(categories)}\n**Last Updated:** Available categories from supported sites"
        ))

        # Categories by source
        categories_text = "# Available Drawing Categories\n\n"

        for source, cats in categories.items():
            categories_text += f"## {source}\n\n"
            for category in cats:
                categories_text += f"- {category}\n"
            categories_text += "\n"

        categories_text += "## Popular Search Terms\n\n"
        categories_text += "- Animals (cat, dog, lion, elephant, etc.)\n"
        categories_text += "- Cartoon Characters (Mickey Mouse, Pikachu, etc.)\n"
        categories_text += "- Anime Characters (Naruto, Goku, etc.)\n"
        categories_text += "- Flowers (rose, tulip, sunflower, etc.)\n"
        categories_text += "- Objects (house, car, tree, etc.)\n"
        categories_text += "- People (face, body, girl, boy, etc.)\n"

        results.append(types.TextContent(
            type="text",
            text=categories_text
        ))

    except Exception as e:
        logger.error(f"Categories listing error: {e}")
        results.append(types.TextContent(
            type="text",
            text=f"# Categories Error\n\n**Error:** {str(e)}"
        ))

    return results

async def main():
    # Run the server using stdin/stdout streams
    from mcp.server.stdio import stdio_server

    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="drawing-guides",
                server_version="0.1.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )

def cli():
    """Entry point for the mcp-drawing-guides command."""
    asyncio.run(main())

if __name__ == "__main__":
    cli()
