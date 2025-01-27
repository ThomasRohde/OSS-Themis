# Themis

![Themis](./bcm-client/src/assets/themis_small.png)

Themis is a powerful collaborative tool for creating, managing and visualizing hierarchical concept models, with a primary focus on Business Capability Models (BCM). Drawing inspiration from the Greek goddess of divine order, Themis helps organizations bring structure and clarity to complex organizational hierarchies.

The tool excels at breaking down large organizational concepts into well-defined, hierarchical structures using MECE principles (Mutually Exclusive, Collectively Exhaustive). Whether you're mapping business capabilities, creating taxonomies, organizing knowledge hierarchies, or building mind maps, Themis provides an intuitive interface for:

- Building multi-level capability models with AI-assisted concept generation
- Smart copy-paste functionality for easy integration with AI chat platforms
- Collaborating in real-time with multiple stakeholders
- Visualizing complex hierarchies with optimized layouts
- Exporting to various enterprise formats including Confluence, ArchiMate, and Microsoft Office
- Managing model evolution through comprehensive audit logging
- Categorizing and organizing software systems that support business capabilities

Perfect for enterprise architects, business analysts, and organizational designers who need to create clear, well-structured models of business functions, processes, or knowledge domains. The smart copy-paste feature makes it easy to leverage AI platforms like ChatGPT for capability generation and refinement while maintaining model integrity.

## Features

- **Business Capability Modeling**
  - Interactive capability model editor
  - Hierarchical capability visualization
  - Drag-and-drop capability reorganization
  - Context menu for quick actions

- **Collaboration**
  - Real-time multi-user collaboration
  - Audit logging of all changes
  - User presence indicators
  - Change synchronization

- **Export Options**
  - SVG export for vector graphics
  - PowerPoint (PPTX) export
  - Word document export
  - HTML export
  - Markdown export
  - PlantUML diagrams
  - Mermaid diagrams
  - Confluence integration

- **Layout & Visualization**
  - Optimized layout algorithms
  - Automatic grid arrangement
  - Aspect ratio optimization
  - Interactive tooltips
  - Responsive design

- **Enterprise Integration**
  - Confluence publishing support
  - ArchiMate export
  - Database persistence
  - REST API access

## Prerequisites

- Python 3.11 or higher
- Node.js 18 or higher
- npm 9 or higher

## Installation

```bash
# Clone the repository
git clone https://github.com/ThomasRohde/themis.git
cd themis

# Create and activate virtual environment
python -m venv .venv
.venv\Scripts\activate

# Install backend dependencies
pip install -e .

# Install frontend dependencies
cd bcm-client
npm install
npm run build

# Run Themis
themis
```

## Development

```bash
# Start the backend server
uvicorn bcm.main:app --reload --port 8000

# In another terminal, start the frontend
cd bcm-client
npm start
```

The application will be available at `http://localhost:3000`

## Project Structure

```
themis/
├── bcm/                    # Backend package
│   ├── api/               # API endpoints
│   ├── models/            # Data models
│   ├── static/            # Static assets
│   └── templates/         # Jinja2 templates
├── bcm-client/            # Frontend React application
│   ├── src/              # Source files
│   └── public/           # Public assets
└── tests/                 # Test suites
```

## API Documentation

API documentation is available at `http://localhost/docs` when running the development server.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- FastAPI for the backend framework
- React for the frontend framework
- SQLAlchemy for database operations
