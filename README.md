# Knowledge Base API

A sophisticated document processing API built with FastAPI and Docling, designed for extracting structured information from documents. This project serves as a foundation for building AI-powered document understanding systems.

## Features

- 🚀 **FastAPI Framework** - Modern, fast, and production-ready API framework
- 📄 **Document Processing** - Advanced document parsing using Docling (supports PDFs, images, and more)
- 🔄 **Async/Await** - Full async support for high-performance operations
- 📋 **RESTful API** - Well-structured v1 API endpoints
- ⚙️ **Configuration Management** - Environment-based configuration with Pydantic
- 🔗 **CORS Support** - Cross-Origin Resource Sharing enabled
- 📊 **Health Checks** - Built-in system health monitoring
- 🧠 **LLM Ready** - Pre-configured for OpenAI integration (Phase 2)
- 📝 **Logging** - Comprehensive logging with Loguru

## Tech Stack

- **Python 3.12+**
- **FastAPI** - Web framework
- **Docling** - Document processing and extraction
- **Pydantic** - Data validation
- **Uvicorn** - ASGI server
- **Loguru** - Logging library
- **Pytest** - Testing framework

## Project Structure

```
knowledge-base-api/
├── app/
│   ├── main.py              # FastAPI application entry point
│   ├── __init__.py
│   ├── api/
│   │   └── v1/
│   │       └── router.py    # API v1 routes
│   ├── core/
│   │   ├── config.py        # Configuration settings
│   │   └── logging.py       # Logging setup
│   ├── schemas/
│   │   ├── base.py          # Base Pydantic schemas
│   │   └── document.py      # Document-related schemas
│   └── services/
│       └── document.py      # Document processing service
├── pyproject.toml           # Project dependencies and metadata
└── README.md                # This file
```

## Installation

### Prerequisites
- Python 3.12 or higher
- pip or uv package manager

### Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Knowledge-base-api
   ```

2. **Create a virtual environment** (optional but recommended)
   ```bash
   python3.12 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -e .
   ```

4. **Create a .env file** (optional)
   ```bash
   cp .env.example .env
   ```
   Configure environment variables as needed:
   ```env
   DEBUG=False
   PROJECT_NAME=Knowledge API
   VERSION=0.1.0
   OPENAI_API_KEY=your_key_here  # Optional, for Phase 2
   ```

## Running the Application

### Development Server
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

### Running with Docker

> Note: the Dockerfile in this repo is named `DockerFile` (capital **F**).

1. **Build the image**
   ```bash
   docker build -f DockerFile -t knowledge-api .
   ```

2. **Run the container**
   ```bash
   docker run --rm -p 8000:8000 --name knowledge-api knowledge-api
   ```

   The API will be available at `http://localhost:8000`.

3. **(Optional) Use a custom .env**
   ```bash
   docker run --rm -p 8000:8000 \
     --env-file .env \
     --name knowledge-api \
     knowledge-api
   ```

### Interactive API Documentation
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Health Check
```bash
curl http://localhost:8000/health
```

## API Endpoints

### Health Check
- **GET** `/health` - System health status

### API v1
- **Base path**: `/api/v1`
- **Document upload**: `POST /api/v1/documents/upload` (multipart form, field name: `file`, accepts `.pdf`)
- See [Interactive API Documentation](#interactive-api-documentation) for full schema and response details.

## Usage Examples

### Basic Health Check
```bash
curl -X GET http://localhost:8000/health
```

### Document Upload (PDF)
```bash
curl -X POST "http://localhost:8000/api/v1/documents/upload" \
  -F "file=@/path/to/document.pdf;type=application/pdf"

# Example 202 Accepted response
# {
#   "message": "File uploaded successfully. Processing has started in the background.",
#   "filename": "document.pdf"
# }
```

## Configuration

Configuration is managed via `app/core/config.py` using Pydantic Settings. You can override settings through:

1. Environment variables
2. `.env` file
3. Default values in the Settings class

### Available Settings
- `PROJECT_NAME` - Application name (default: "Knowledge API")
- `VERSION` - API version (default: "0.1.0")
- `API_V1_STR` - API v1 prefix (default: "/api/v1")
- `DEBUG` - Debug mode (default: False)
- `OPENAI_API_KEY` - OpenAI API key for LLM features (optional)

## Development

### Running Tests
```bash
pytest
```

### Code Quality
```bash
ruff check .
```

### Code Formatting
```bash
ruff format .
```

## Logging

The application uses Loguru for comprehensive logging. Configure logging in `app/core/logging.py`.

Key startup messages:
- `🚀 Initializing Heavy AI Models (Docling)...` - Heavy models are being loaded
- `🛑 Cleaning up resources...` - Application shutdown

## Architecture

### Lifespan Management
The application uses FastAPI's lifespan context manager to handle:
- **Startup**: Initializing the DocumentProcessor with Docling models
- **Shutdown**: Cleaning up resources

This ensures efficient resource management and graceful shutdown.

### Middleware
- **CORS Middleware** - Configured to accept requests from any origin in development. Update `allow_origins` in production.

## Roadmap

- **Phase 1** ✅ Document processing pipeline with Docling
- **Phase 2** 🔄 LLM integration with OpenAI for document understanding
- **Phase 3** 📅 Knowledge graph generation
- **Phase 4** 📅 Vector embeddings and semantic search

## Best Practices

1. Always use async operations for I/O-bound tasks
2. Keep API schemas in `schemas/` directory
3. Use dependency injection for services
4. Configure CORS properly for production
5. Set `DEBUG=False` in production
6. Use environment variables for sensitive data (API keys, etc.)

## Troubleshooting

### Models Not Loading
If the Docling models fail to load:
- Ensure you have sufficient disk space
- Check internet connection (models are downloaded on first run)
- Review logs for specific error messages

### CORS Issues
If you encounter CORS errors:
- Update `allow_origins` in `main.py` with your frontend domain
- Restart the application

## Contributing

1. Create a new branch for your feature
2. Follow the coding style (use Ruff for formatting)
3. Write tests for new functionality
4. Update documentation as needed
5. Submit a pull request

## License

This project is provided as-is for development and learning purposes.

## Support

For issues, questions, or contributions, please open an issue or contact the project maintainer.

---

**Last Updated**: February 2026
