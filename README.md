# Google Sheets Product Recommendations

A Google Sheets application that fetches product recommendations from e-commerce websites (AliExpress and Ishtari) using their internal APIs, and finds relevant YouTube videos. The system uses FastAPI for the backend, Playwright for cookie management, and Google Apps Script for the frontend integration.

[Video Demo Coming Soon]

## Features

- Fetch product recommendations from multiple e-commerce platforms
- Smart product similarity scoring algorithm
- YouTube video recommendations integration
- Asynchronous processing with cancellation support
- Cookie-based authentication for e-commerce APIs
- Real-time status updates
- Containerized deployment using Docker
- Automated data collection and organization in Google Sheets

## Technical Architecture

### Backend (FastAPI)
- Built with FastAPI for high-performance async operations
- Four main endpoints:
  1. `/health`: Health check endpoint
  2. `/trigger_product_fetch`: Initiates async product fetching
  3. `/cancel_product_fetch`: Cancels ongoing fetch operations
  4. `/fetch_status`: Retrieves current fetch status
- Uses Playwright for cookie management on startup
- Direct integration with e-commerce internal APIs
- Implements gspread for Google Sheets updates
- Smart similarity scoring for product relevance

### Frontend (Google Apps Script)
- Handles user interactions in Google Sheets
- Manages API calls to the backend
- Integrates with YouTube Data API v3 for video recommendations
- Orchestrates the product fetch workflow

## Product Similarity Scoring

The application uses a sophisticated algorithm to score product relevance:

1. **Base Score**: Calculates the ratio of matched keywords
2. **Phrase Bonus**: 50% bonus for exact phrase matches
3. **Position Weighting**: Higher scores for keywords appearing earlier in product titles
4. **Normalized Scoring**: Final scores are normalized and presented as percentages

Example:
```python
"black shoes" matching "Black Running Shoes" would consider:
- Keyword presence
- Position of keywords in title
- Exact phrase matching
```

## Setup Instructions

### 1. Environment Variables

Required environment variables:
```bash
SHARED_SECRET=<your-hex-secret>        # Authentication secret
GOOGLE_SHEET_ID=<sheet-id>            # ID of your Google Sheet
LOG_LEVEL=INFO                        # Optional, default: INFO. Use DEBUG for extra verbosity
```

Set these in:
- Local development: `.env` file
- Production: render.com secrets

### 2. Google Cloud Console Setup

1. Create a new project in the [Google Cloud Console](https://console.cloud.google.com/)
2. Enable required APIs:
   - Google Sheets API
   - YouTube Data API v3
3. Set up credentials:
   - Navigate to the Google Sheets API section
   - Go to Credentials
   - Create a Service Account
   - Create a new key for this service account (JSON format)
   - Download the JSON file and rename it to `credentials.json`
   - Place this file in your project root directory
   - Share your Google Sheet with the service account email address found in the credentials file
4. **Important**: The `credentials.json` file is required in both:
   - Local development environment
   - Production deployment environment

### 3. Google Sheet Setup

1. Create a new Google Sheet with three sheets:
   - Sheet1: "User Input" (First column for keywords)
   - Sheet2: "Product Recommendations" (Locked)
   - Sheet3: "YouTube Videos" (Locked)

2. Share the sheet with the service account email from your credentials

3. Configure Apps Script:
   - Open Apps Script editor from Google Sheets (Extensions > Apps Script)
   - Set up the YouTube Data API v3 in Services
   - Add SHARED_SECRET in Script Properties
   - Copy and paste the AppsScriptCode/Code.gs in the repo into the Code.gs file in the Apps Script editor
   - Draw the boxes for the buttons in sheet1 (User Input) and 'Assign a Script' to each one of them corresponding to their Apps Script function: OnButtonPress and OnCancelRetrieval for the 'Fetch Product Recommendations' and 'Cancel Product Fetch' boxes respectively 
   - Save the changes. No need to deploy independently, this Apps Script will run in the context of the Google Sheet

### 4. Local Development Setup

```bash
# Clone the repository
git clone https://github.com/ZaherAmasha/Google-sheets-project.git

# Create .env file and edit it with your actual values
cp .env.example .env

# Ensure credentials.json is in the project's root

# Start the application using Docker Compose
docker-compose up
```

### 5. Production Deployment (render.com)
The backend can be deployed to any platform that supports Docker containers. This guide uses render.com as an example due to its simplicity, but you can adapt these instructions for any deployment platform:

#### Using [render.com](https://render.com):
1. Connect your repository to render.com
2. Add environment variables in Secrets section:
   - `SHARED_SECRET`
   - `GOOGLE_SHEET_ID`
   - `LOG_LEVEL` (optional)
3. Add `credentials.json` as a secret file
4. Deploy using the Dockerfile provided

#### Using other platforms:
- Ensure the platform supports Docker
- Configure the required environment variables
- Provide the `credentials.json` file securely
- Set up the deployment process according to the platform's specifications


## Implementation Details

### Backend Processing
- Asynchronous processing using FastAPI and Python's asyncio
- Cookie management:
  - Fetches cookies from e-commerce sites on server startup using Playwright
  - Stores cookies in memory for subsequent API requests
- Direct integration with e-commerce internal APIs
- Comprehensive error handling and logging
- Smart product similarity scoring
- Basic data validation for incoming requests

### YouTube Integration
- Implemented in Apps Script for simplified authentication
- Fetches relevant videos based on keywords
- Populates Sheet3 with video recommendations
- Uses YouTube Data API v3

### Security
- Endpoint authentication using SHARED_SECRET
- Secure cookie management
- Protected Google Sheets endpoints
- Environment-based configuration

## Usage

1. Enter keywords in the first column of Sheet1
2. Click the 'Fetch Product Recommendations' button
3. The system will:
   - Trigger an async task to fetch products
   - Score products based on relevance
   - Fetch related YouTube videos
   - Update sheets in real-time
   - Allow cancellation of the fetch operation

## Development

### Prerequisites
- Docker and Docker Compose
- Google Cloud Console account
- Google Sheets API access
- Basic understanding of web scraping with web drivers (like Selenium and Playwright) and fetching data from the backend internal APIs of websites to be scraped
- Basic understanding of FastAPI and Google Apps Script

## Contributing

Feel free to submit issues and enhancement requests!
Contributions are what make the open source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

If you have a suggestion that would make this better, please fork the repo and create a pull request. You can also simply open an issue with the tag "enhancement".
Don't forget to give the project a star! Thanks again!

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

Distributed under the Apache-2.0 License. See `LICENSE` file for more information.

