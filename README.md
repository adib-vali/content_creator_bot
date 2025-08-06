# Content Creator Bot 🤖

A Telegram chatbot for automated content creation using AI. This bot can generate product images and text content based on user-uploaded product images.

## Features

- **Product Image Generation**: Generate different types of product shots:
  - The On-Model Portrait
  - The In-Context Lifestyle Shot
  - The Product-Only "Hero Shot"
  - The Creative Flat Lay

- **Text Content Generation**: Create various types of text content:
  - Product Description
  - Marketing Copy
  - Social Media Post
  - Blog Post
  - Email Campaign
  - Other custom content

## Setup Instructions

### 1. Prerequisites

- Python 3.8 or higher
- Telegram Bot Token (from @BotFather)
- Fal AI API Key (from https://fal.ai/)

### 2. Installation

1. Clone this repository:
```bash
git clone <repository-url>
cd content_creator_bot
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp env_example.txt .env
```

Edit the `.env` file and add your API keys:
```
TELEGRAM_TOKEN=your_telegram_bot_token_here
FAL_KEY=your_fal_ai_key_here
```

### 3. Getting API Keys

#### Telegram Bot Token
1. Message @BotFather on Telegram
2. Send `/newbot` command
3. Follow the instructions to create your bot
4. Copy the token provided

#### Fal AI API Key
1. Go to https://fal.ai/
2. Sign up or log in
3. Navigate to your account settings
4. Generate an API key

### 4. Running the Bot

```bash
python bot.py
```

The bot will start and you can interact with it on Telegram.

## Usage

1. **Start the bot**: Send `/start` to begin
2. **Upload product image**: Send a photo of your product
3. **Choose content type**: Select either:
   - تولید تصویر محصول (Generate Product Image)
   - تولید محتوا متنی (Generate Text Content)
4. **Select specific type**: Choose from the available options
5. **For text content**: Provide additional context about your requirements
6. **Receive results**: Get your generated content!

## Bot Workflow

```
User sends product image
         ↓
    Choose content type
         ↓
┌─────────────────┬─────────────────┐
│ Product Image   │ Text Content    │
│ Generation      │ Generation      │
│                 │                 │
│ • On-Model      │ • Product Desc  │
│ • Lifestyle     │ • Marketing     │
│ • Hero Shot     │ • Social Media  │
│ • Flat Lay      │ • Blog Post     │
│                 │ • Email         │
└─────────────────┴─────────────────┘
         ↓
    API Processing
         ↓
    Return Results
```

## API Integration

The bot integrates with two Fal AI workflows:

1. **Content Creator Workflow** (`workflows/adib-vali/contentcreator`)
   - Used for product image generation
   - Parameters: `image_url`, `prompt`, `reasoning`, `model`

2. **Vision Specialist Workflow** (`workflows/adib-vali/vision-speccialist`)
   - Used for text content generation
   - Parameters: `image_url`, `prompt`

## File Structure

```
content_creator_bot/
├── bot.py              # Main bot application
├── api_client.py       # Fal AI API client
├── config.py           # Configuration and constants
├── requirements.txt    # Python dependencies
├── env_example.txt     # Environment variables example
└── README.md          # This file
```

## Error Handling

The bot includes comprehensive error handling for:
- Missing API keys
- Network connectivity issues
- Invalid image uploads
- API response errors
- User input validation

## Contributing

Feel free to submit issues and enhancement requests!

## License

This project is licensed under the MIT License.
