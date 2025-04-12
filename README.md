# NerdDash: AI Thought Network Visualization

A streamlit-based visualization tool for analyzing and exploring AI thought patterns through concept clustering, topic modeling, and sentiment analysis.

## Overview

NerdDash is a data visualization dashboard that analyzes text data from AI thought patterns stored in MongoDB. It provides insights through various visualizations:

- Concept clustering and embedding visualization using t-SNE
- Topic modeling with BERTopic
- Sentiment and emotion analysis over time
- Interactive charts for concept exploration

## Features

- **Data Overview**: View key metrics about your AI thought network
- **Timeline Analysis**: Track how concepts evolve over time  
- **Popular Concepts**: Identify frequently occurring concepts
- **Semantic Clustering**: Group related concepts using embeddings
- **Topic Modeling**: Discover underlying themes in your data
- **Sentiment Analysis**: Track emotional patterns in AI thoughts

## Requirements

- Python 3.11+
- MongoDB database with card data
- Docker (optional for containerized deployment)

## Installation

### Option 1: Local Development

1. Clone the repository:
   ```bash
   git clone https://github.com/rquintero93/nerDash.git
   cd nerdbot
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows, use: .venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install uv
   uv sync
   ```

4. Create a `.env` file in the `src` directory with your MongoDB connection details:
   ```
   MONGO_URI=mongodb://username:password@hostname:port/
   ```

5. Run the application:
   ```bash
   task run
   ```

### Option 2: Docker Deployment

1. Build and run with Docker Compose:
   ```bash
   docker-compose up -d
   ```

2. Access the application at http://localhost:8051

## Development

This project uses `taskipy` to simplify common development tasks:

- `task lint` - Check code style with Ruff
- `task format` - Format code with Ruff
- `task typecheck` - Run static type checking
- `task test` - Run pytest tests
- `task check` - Run full suite of checks
- `task docs_serve` - Serve documentation locally

## Architecture

- **MVC Pattern**:
  - **Models**: Connect to MongoDB and retrieve data
  - **Views**: Visualization components for different chart types
  - **Controllers**: Process and transform data for visualization
