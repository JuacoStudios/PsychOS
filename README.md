# PsycheOS 🌌

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

**A collaborative knowledge system to build an updated, living model of human consciousness and mental health.**

PsycheOS synthesizes scientific papers, YouTube videos, books, historical texts, and clinical data into a dynamic knowledge graph. It's an open-source platform where researchers, psychologists, developers, and curious minds can collaboratively map the landscape of consciousness studies.

## 🎯 Why PsycheOS?

The study of consciousness is fragmented across disciplines: neuroscience, psychology, philosophy, AI research, and spiritual traditions. PsycheOS aims to bridge these silos by creating a unified, computable model that evolves with new research and insights.

## ✨ Features

- **Multi-source ingestion**: Parse PDFs, transcribe videos, scrape web articles
- **Knowledge graph**: Connect theories, concepts, evidence, and contradictions
- **Semantic search**: Find connections across disciplines
- **Open API**: Build your own tools on top of the consciousness graph
- **Community-driven**: Anyone can contribute papers, theories, or code

## 🚀 Quick Start

### Prerequisites
- Python 3.9 or higher
- pip (Python package manager)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/PsycheOS.git
cd PsycheOS
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Install additional system dependencies (for audio processing):
```bash
# On Ubuntu/Debian
sudo apt-get install ffmpeg

# On macOS
brew install ffmpeg

# On Windows (using Chocolatey)
choco install ffmpeg
```

### Basic Usage

1. **Ingest a PDF paper**:
```bash
python -m ingestion.pdf_parser --path "data/sources/your_paper.pdf"
```

2. **Ingest a YouTube video**:
```bash
python -m ingestion.video_ingestion --url "https://www.youtube.com/watch?v=example"
```

3. **Start the API server**:
```bash
uvicorn api.main:app --reload
```

4. **Explore the API**:
- Open http://localhost:8000/docs for interactive API documentation
- Visit http://localhost:8000/api/v1/theories to see pre-loaded consciousness theories

## 📁 Project Structure

```
PsycheOS/
├── ingestion/          # Data ingestion from various sources
├── graph/             # Knowledge graph construction and visualization
├── models/            # Data models for consciousness and mental health
├── api/               # FastAPI REST API
├── data/              # Raw and processed data
├── docs/              # Documentation and theory files
└── tests/             # Test suite
```

## 🤝 How to Contribute

PsycheOS thrives on community contributions! Whether you're a:
- **Researcher** with papers to add
- **Developer** who can improve the code
- **Psychologist** with clinical insights
- **Student** curious about consciousness
- **Writer** who can improve documentation

...your contributions are welcome!

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

### Ways to Contribute:
1. **Add a paper**: Place PDFs in `data/sources/` and run the ingestion pipeline
2. **Add a theory**: Create a markdown file in `docs/theories/`
3. **Improve code**: Fix bugs, add features, optimize performance
4. **Improve documentation**: Clarify concepts, add examples
5. **Share insights**: Open an issue with your thoughts on consciousness models

## 📚 Learn More

- [VISION.md](VISION.md) - The philosophical and scientific vision behind PsycheOS
- [ROADMAP.md](ROADMAP.md) - Development roadmap and future plans
- [CONTRIBUTING.md](CONTRIBUTING.md) - How to contribute to the project

## 🧠 Pre-loaded Theories

PsycheOS comes with several foundational theories already modeled:
- **Integrated Information Theory (IIT)** - Giulio Tononi
- **Global Workspace Theory** - Bernard Baars
- **Predictive Processing** - Karl Friston
- **Attention Schema Theory** - Michael Graziano
- **Higher-Order Thought Theory** - David Rosenthal

## 🔗 Connect

- **GitHub Issues**: For bug reports and feature requests
- **Discussions**: For philosophical and scientific conversations
- **Wiki**: For detailed documentation (coming soon)

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- All the researchers and thinkers whose work forms the foundation of consciousness studies
- The open-source community for building the tools that make this project possible
- Every contributor who helps map the territory of the mind

---

*"The mind is not a vessel to be filled, but a fire to be kindled." - Plutarch*