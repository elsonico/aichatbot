# AI Chatbot

A Flask-based AI chatbot application that uses OpenAI's GPT-4 model to provide intelligent responses while maintaining a knowledge base of previous interactions. The application includes features for user feedback and response streaming.

## Features

- Interactive chat interface
- Integration with OpenAI's GPT-4 model
- PostgreSQL database for storing chat history and knowledge base
- Real-time response streaming
- User feedback system
- Docker support for easy deployment
- Custom data enrichment for API requests

## Prerequisites

- Python 3.x
- PostgreSQL database
- OpenAI API key
- Docker (optional, for containerized deployment)

## Environment Variables

The following environment variables need to be set:

```
DB_HOST=localhost
DB_NAME=chatdb
DB_USER=chatuser
DB_PASS=yourpassword
DB_PORT=5432
OPENAI_API_KEY=your_openai_api_key
```

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd aichatbot
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up the PostgreSQL database and create the required tables:
```bash
# The tables will be automatically created when the application starts
```

## Running the Application

### Local Development

```bash
python app.py
```

### Using Docker

```bash
docker build -t aichatbot .
docker run -p 5000:5000 aichatbot
```

### Using Gunicorn (Production)

```bash
gunicorn -c gunicorn.conf.py app:app
```

## API Endpoints

- `GET /`: Main chat interface
- `POST /chat`: Send a message and receive a response
- `GET /chat`: Stream response for a given question
- `POST /feedback`: Submit feedback for a chat response

## Project Structure

```
.
├── app.py              # Main application file
├── Dockerfile          # Docker configuration
├── gunicorn.conf.py    # Gunicorn configuration
├── requirements.txt    # Python dependencies
├── static/            # Static files
└── templates/         # HTML templates
```

## Database Models

### Chat
- Stores chat history with questions, answers, and user feedback
- Fields: id, question, answer, feedback

### KnowledgeBase
- Maintains a knowledge base of previous Q&A pairs
- Fields: id, question, answer

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details. 