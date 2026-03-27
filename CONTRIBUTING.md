# Contributing to PsycheOS

Thank you for your interest in contributing to PsycheOS! This project thrives on diverse contributions from researchers, developers, psychologists, students, and curious minds from all backgrounds.

## 🎯 How to Contribute

### 1. For Researchers and Academics

#### Add Scientific Papers
1. Place PDFs in `data/sources/papers/`
2. Run the ingestion pipeline:
   ```bash
   python -m ingestion.pdf_parser --path "data/sources/papers/your_paper.pdf"
   ```
3. The system will extract text, metadata, and add it to the knowledge graph

#### Add Theory Documentation
1. Create a markdown file in `docs/theories/` following the template:
   ```markdown
   # Theory Name
   
   ## Core Proponents
   - Name (Year)
   
   ## Key Concepts
   - Concept 1: Description
   - Concept 2: Description
   
   ## Evidence
   - Study 1 (Year): Findings
   - Study 2 (Year): Findings
   
   ## Criticisms
   - Criticism 1
   - Criticism 2
   
   ## Connections to Other Theories
   - Extends: [Other Theory]
   - Contradicts: [Other Theory]
   ```

#### Review and Validate
- Check extracted data for accuracy
- Flag papers with poor OCR or extraction errors
- Verify connections in the knowledge graph

### 2. For Developers

#### Code Contributions
1. Fork the repository
2. Create a feature branch:
   ```bash
   git checkout -b feature/amazing-feature
   ```
3. Make your changes
4. Write or update tests
5. Ensure code passes existing tests:
   ```bash
   python -m pytest tests/
   ```
6. Submit a pull request

#### Areas Needing Development
- **Ingestion improvements**: Better PDF parsing, video processing
- **Graph algorithms**: New ways to analyze connections
- **API enhancements**: New endpoints, better performance
- **UI/Visualization**: Better ways to explore the knowledge graph
- **Testing**: More comprehensive test coverage

#### Coding Standards
- Follow PEP 8 for Python code
- Use type hints where appropriate
- Write docstrings for all functions and classes
- Keep functions focused and modular

### 3. For Psychologists and Clinicians

#### Add Clinical Insights
1. Create markdown files in `docs/clinical/` (create the folder if needed)
2. Document:
   - Therapeutic approaches and their theoretical bases
   - Case studies (anonymized)
   - Treatment efficacy data
   - Diagnostic criteria connections to consciousness models

#### Connect Theory to Practice
- Identify which consciousness theories inform which therapies
- Map symptoms to potential underlying mechanisms
- Suggest research questions at the theory-practice interface

### 4. For Students and Learners

#### Improve Documentation
- Clarify complex concepts in existing documentation
- Add examples to make concepts more accessible
- Create tutorials for common tasks
- Translate documentation into other languages

#### Curate Resources
- Find and add high-quality educational content
- Create learning pathways through the knowledge graph
- Develop study guides for specific topics

#### Ask Questions
- Open issues with questions about consciousness theories
- Request clarifications on confusing concepts
- Suggest areas where documentation is lacking

### 5. For Non-Technical Contributors

#### Content Curation
- Find and suggest relevant YouTube videos, podcasts, articles
- Identify important books and papers that should be included
- Tag content with relevant categories and concepts

#### Community Building
- Help welcome new contributors
- Participate in discussions about theories and connections
- Share PsycheOS with relevant communities

#### Ethical Oversight
- Flag potentially harmful content or misinterpretations
- Ensure diverse perspectives are represented
- Monitor for bias in the knowledge graph

## 🚀 Getting Started

### First-Time Setup
1. Set up your development environment (see README.md)
2. Run the tests to ensure everything works:
   ```bash
   python -m pytest tests/ -v
   ```
3. Try ingesting a sample PDF or video

### Good First Issues
Look for issues tagged with:
- `good-first-issue`: Simple tasks for newcomers
- `documentation`: Documentation improvements
- `bug`: Fixing existing problems
- `enhancement`: Adding new features

## 📝 Pull Request Process

1. Ensure your code follows the project standards
2. Update documentation if needed
3. Add tests for new functionality
4. Ensure all tests pass
5. Update the CHANGELOG.md if applicable
6. Submit the PR with a clear description

### PR Description Template
```
## What does this PR do?
[Brief description of changes]

## Related Issue
Fixes # [issue number]

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Performance improvement
- [ ] Code refactoring

## Testing
- [ ] Tests added/updated
- [ ] All tests pass

## Documentation
- [ ] Documentation updated
- [ ] No documentation needed
```

## 🧪 Testing

### Running Tests
```bash
# Run all tests
python -m pytest tests/

# Run specific test file
python -m pytest tests/test_ingestion.py

# Run with coverage
python -m pytest tests/ --cov=ingestion --cov=graph --cov=api
```

### Writing Tests
- Test both success and failure cases
- Mock external dependencies (APIs, file systems)
- Keep tests fast and independent
- Use descriptive test names

## 📊 Data Quality Standards

### For Ingested Content
- **Accuracy**: Extracted text should match source
- **Completeness**: All relevant metadata captured
- **Attribution**: Proper credit to original authors
- **Consistency**: Uniform formatting across sources

### For Knowledge Graph
- **Verifiability**: Connections should cite sources
- **Balance**: Multiple perspectives on controversial topics
- **Clarity**: Clear relationship types and weights
- **Currency**: Regular updates with new research

## 🏷️ Labels and Tags

### Content Tags
Use consistent tags for content:
- `neuroscience`, `philosophy`, `psychology`, `ai`, `clinical`
- `theory`, `evidence`, `criticism`, `application`
- `historical`, `contemporary`, `speculative`

### Relationship Types
Use defined relationship types from `graph/relations.py`:
- `SUPPORTS`, `CONTRADICTS`, `EXTENDS`, `CITES`, `RELATED_TO`

## 🤝 Community Guidelines

### Be Respectful
- Consciousness studies involve deeply held beliefs
- Critique ideas, not people
- Acknowledge the limits of your expertise

### Cite Sources
- Always credit original authors
- Provide references for claims
- Distinguish between established fact and interpretation

### Embrace Diversity
- Welcome perspectives from different cultures, disciplines, and backgrounds
- Recognize that consciousness may be studied through multiple valid approaches
- Avoid dogmatism about any single theory

### Practice Intellectual Humility
- Acknowledge what we don't know
- Be open to revising your views
- Value questions as much as answers

## 🆘 Getting Help

- **GitHub Issues**: For bugs, feature requests, and questions
- **Discussion Forum**: For philosophical and scientific discussions (coming soon)
- **Chat**: Real-time chat for contributors (coming soon)

## 📜 Code of Conduct

### Our Pledge
We pledge to make participation in PsycheOS a harassment-free experience for everyone, regardless of age, body size, disability, ethnicity, gender identity and expression, level of experience, education, socio-economic status, nationality, personal appearance, race, religion, or sexual identity and orientation.

### Our Standards
Examples of behavior that contributes to creating a positive environment include:
- Using welcoming and inclusive language
- Being respectful of differing viewpoints and experiences
- Gracefully accepting constructive criticism
- Focusing on what is best for the community
- Showing empathy towards other community members

### Enforcement
Instances of abusive, harassing, or otherwise unacceptable behavior may be reported to the project maintainers. All complaints will be reviewed and investigated promptly and fairly.

---

*By contributing to PsycheOS, you agree to abide by these guidelines and help create a collaborative, respectful community dedicated to understanding consciousness.*