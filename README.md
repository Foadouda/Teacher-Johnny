<<<<<<< HEAD
# Teacher-Johnny
=======
# Teacher-Johnny Project

A comprehensive system for converting PDF books into summarized PowerPoint presentations using AI. The system extracts chapters, processes content, and generates Google Slides presentations automatically.

## Table of Contents
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Running the Application](#running-the-application)
- [Core Components](#core-components)
- [Detailed Component Breakdown](#detailed-component-breakdown)
- [Advanced Features](#advanced-features)
- [Workflow](#workflow)
- [Configuration](#configuration)
- [Error Handling](#error-handling)
- [License](#license)
- [Support](#support)

## Project Structure

```
Teacher-Johnny/
├── pdf-summarizer/                # Node.js frontend for PDF uploads
│   ├── logs/                      # Application logs
│   │   ├── errors.log            # Error tracking
│   │   ├── gemini.log            # AI processing logs
│   │   ├── process.log           # Execution logs
│   │   └── time.log             # Performance metrics
│   ├── ppt_jsons/                # Generated JSON files for presentations
│   ├── uploads/                  # Temporary PDF storage
│   └── server.js                 # Main server file
└── project_backend/              # Python backend services
    ├── service/
    │   ├── PowerPoint_Generator/
    │   │   ├── ppt.py           # Main PowerPoint generation script
    │   │   ├── Authenticator.py # Google API authentication
    │   │   ├── ppt_creator.py   # Presentation creation
    │   │   ├── EJF.py          # PDF chapter extraction
    │   │   ├── EBN.py          # Book name extraction
    │   │   ├── EJFA.py         # Async chapter processing
    │   │   ├── PresentationHandler.py # Presentation management
    │   │   └── Logging.py      # Logging configuration
    │   └── ElevenLabs_TTS_test/
    │       └── TextToSpeech.py  # Text-to-Speech conversion
    └── core/
        └── settings.py          # Configuration settings
```

## Prerequisites

- Python 3.12+
- Node.js (v14 or higher)
- Google Cloud Service Account credentials
- ElevenLabs API key for TTS
- Virtual environment for Python
- Required Python packages (listed in `requirements.txt`)

## Installation

1. **Clone the Repository**
   ```bash
   git clone <repository-url>
   cd Teacher-Johnny
   ```

2. **Set up Python Environment**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Install Node.js Dependencies**
   ```bash
   cd pdf-summarizer
   npm install
   ```

4. **Configure API Credentials**
   - Place `text-summarization-demo-f74e4d81d2d3.json` in the root directory
   - Configure ElevenLabs API key in settings
   - Ensure Google API permissions for:
     - Google Slides API
     - Google Drive API

## Running the Application

1. **Start the Node.js Server**
   ```bash
   cd pdf-summarizer
   node server.js
   ```
   Server will be available at: http://localhost:3000

2. **Using the Application**
   - Open the web interface in your browser
   - Upload a PDF book
   - Monitor progress through the UI
   - Access generated presentations via provided links

## Core Components

### PDF Summarizer (Node.js)
- **server.js**
  - Handles file uploads
  - Manages WebSocket connections
  - Triggers Python processing
  - Stores files in organized directories

### PowerPoint Generator (Python)
- **ppt.py**
  - Extracts and processes PDF content
  - Manages presentation generation
  - Handles Google Slides integration

### Key Services
| Service | File | Description |
|---------|------|-------------|
| PDF Processing | EJF.py | Extracts chapters from PDFs |
| Book Name Extraction | EBN.py | Determines book titles using AI |
| Chapter Processing | EJFA.py | Handles parallel content processing |
| Google Authentication | Authenticator.py | Manages API connections |
| Presentation Creation | ppt_creator.py | Creates and formats slides |
| TTS Generation | TextToSpeech.py | Converts text to speech |

## Detailed Component Breakdown

### PowerPoint Generator Components

- **[`ppt.py`](project_backend/service/PowerPoint_Generator/ppt.py)**
  - Main orchestration script
  - Manages the complete flow from PDF processing to presentation creation
  - Handles retry logic and progress tracking

- **[`Authenticator.py`](project_backend/service/PowerPoint_Generator/Authenticator.py)**
  - Manages Google API authentication
  - Handles both Slides and Drive API authentication
  - Uses service account credentials for secure access

- **[`ppt_creator.py`](project_backend/service/PowerPoint_Generator/ppt_creator.py)**
  - Creates and formats Google Slides presentations
  - Handles slide layouts, content insertion, and styling
  - Manages presentation templates and formatting

- **[`EJF.py`](project_backend/service/PowerPoint_Generator/EJF.py)** (Extract JSON Format)
  - Extracts text from PDF files
  - Creates structured JSON files for chapters
  - Handles chapter content formatting

- **[`EBN.py`](project_backend/service/PowerPoint_Generator/EBN.py)** (Extract Book Name)
  - Uses Gemini AI to extract book names
  - Handles book title processing and validation
  - Manages book name standardization

- **[`EJFA.py`](project_backend/service/PowerPoint_Generator/EJFA.py)** (Extract JSON Format Async)
  - Implements parallel processing for chapter extraction
  - Uses Ray for distributed processing
  - Manages retry logic for failed extractions

- **[`PresentationHandler.py`](project_backend/service/PowerPoint_Generator/PresentationHandler.py)**
  - Manages presentation sharing and permissions
  - Sets up public access links
  - Handles Google Drive sharing settings

- **[`Logging.py`](project_backend/service/PowerPoint_Generator/Logging.py)**
  - Centralizes logging configuration
  - Manages different log types (error, process, time, Gemini)
  - Handles log file creation and formatting

### Text-to-Speech Service

Located in [`project_backend/service/ElevenLabs_TTS_test/`](project_backend/service/ElevenLabs_TTS_test/):

- **[`TextToSpeech.py`](project_backend/service/ElevenLabs_TTS_test/TextToSpeech.py)**
  - Integrates with ElevenLabs API for high-quality TTS
  - Converts presentation scripts to audio
  - Features:
    - Voice selection (VOICE_ID configuration)
    - Audio playback using pygame
    - JSON script extraction and processing
    - Error handling and retry logic

#### TTS Configuration
```python
VOICE_ID = "pqHfZKP75CvOlQylNhV4"  # ElevenLabs voice ID of Bill
```

## Advanced Features

### Parallel Processing
- Ray framework for distributed processing
- ThreadPoolExecutor for concurrent operations
- Optimized chapter processing with parallel execution

### Error Recovery
- Multiple retry attempts for failed operations
- Exponential backoff strategy
- Comprehensive error logging and tracking

### Performance Monitoring
- Detailed timing logs for each operation
- Process tracking through WebSocket updates
- Performance metrics in time.log

## Workflow

### 1. Upload Phase
- User uploads PDF through web interface
- File saved to `uploads/` directory
- Node.js triggers Python processing

### 2. Processing Phase
- PDF text extraction
- AI-powered book name detection
- Chapter identification and processing
- JSON generation for presentations

### 3. Presentation Creation
- Google API authentication
- Slide generation per chapter
- Public link creation
- Link storage in `presentation_links.json`

## Configuration

### Logging
Located in `pdf-summarizer/logs/`:
- `errors.log`: Error tracking
- `gemini.log`: AI processing logs
- `process.log`: General operations
- `time.log`: Performance metrics

### API Configuration
- Google credentials: `text-summarization-demo-f74e4d81d2d3.json`
- Application settings: `project_backend/core/settings.py`
- Server configuration: `pdf-summarizer/server.js`

## Error Handling

The system implements robust error handling:
- Automatic retry mechanisms for API calls
- Comprehensive error logging
- Real-time process monitoring
- WebSocket status updates

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support, please open an issue in the GitHub repository or contact the maintainers at:
- Email: fouadouda.a@gmail.com
>>>>>>> 505ae3d (Fouad's Version without Rag and STT and TSS)
