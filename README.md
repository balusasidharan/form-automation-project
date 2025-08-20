# Form Automation Project

A Python-based web form automation tool that can fill out and submit application forms automatically using Selenium WebDriver.

## Features

- Automated form filling with text inputs, dropdowns, checkboxes
- File upload support
- Configurable field selectors and values
- Screenshot capture for verification
- Headless browser support
- Comprehensive logging
- Error handling and retry mechanisms

## Installation

1. **Activate the virtual environment:**
   ```bash
   source venv/bin/activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## Configuration

Edit `form_config.json` to configure your form automation:

```json
{
  "url": "https://your-target-form-url.com",
  "fields": [
    {
      "type": "text",
      "selector": "field_id",
      "selector_type": "id",
      "value": "Your Value"
    }
  ],
  "submit": {
    "selector": "submit_button_id",
    "selector_type": "id"
  }
}
```

### Field Types

- **text**: Text inputs, textareas
- **dropdown**: Select dropdowns
- **click**: Buttons, checkboxes, radio buttons
- **file**: File upload inputs

### Selector Types

- **id**: Find by ID attribute
- **class_name**: Find by class name
- **xpath**: Find by XPath
- **css_selector**: Find by CSS selector
- **name**: Find by name attribute
- **tag_name**: Find by tag name

## Usage

1. **Update configuration:** Modify `form_config.json` with your target form's URL and field details
2. **Run the automation:**
   ```bash
   python form_automation.py
   ```

## Environment Variables

Set in `.env` file:
- `CONFIG_FILE`: Path to configuration file (default: form_config.json)
- `HEADLESS`: Run browser in headless mode (true/false)
- `TIMEOUT`: Element wait timeout in seconds
- `CHROMEDRIVER_PATH`: Custom path to ChromeDriver executable (optional - avoids downloading every time)

## Examples

### Basic Text Form
```json
{
  "url": "https://example.com/contact-form",
  "fields": [
    {
      "type": "text",
      "selector": "name",
      "selector_type": "id",
      "value": "John Doe"
    },
    {
      "type": "text",
      "selector": "email",
      "selector_type": "id", 
      "value": "john@example.com"
    }
  ],
  "submit": {
    "selector": "submit",
    "selector_type": "id"
  }
}
```

### Job Application Form
```json
{
  "url": "https://company.com/careers/apply",
  "fields": [
    {
      "type": "text",
      "selector": "applicant_name",
      "selector_type": "id",
      "value": "Jane Smith"
    },
    {
      "type": "file",
      "selector": "resume_upload",
      "selector_type": "id",
      "value": "/path/to/resume.pdf"
    },
    {
      "type": "dropdown",
      "selector": "position",
      "selector_type": "id",
      "value": "Software Engineer"
    }
  ]
}
```

## Using Custom ChromeDriver Path

To avoid downloading ChromeDriver every time you run the script:

1. **Download ChromeDriver manually:**
   - Visit https://chromedriver.chromium.org/
   - Download the version matching your Chrome browser
   - Extract the executable

2. **Set the path in .env file:**
   ```bash
   CHROMEDRIVER_PATH=/path/to/your/chromedriver
   ```
   
   Example paths:
   - macOS: `CHROMEDRIVER_PATH=/usr/local/bin/chromedriver`
   - Linux: `CHROMEDRIVER_PATH=/usr/local/bin/chromedriver`
   - Windows: `CHROMEDRIVER_PATH=C:\chromedriver\chromedriver.exe`

3. **Make executable (macOS/Linux):**
   ```bash
   chmod +x /path/to/your/chromedriver
   ```

## Troubleshooting

1. **Element not found**: Check selector and selector_type in your configuration
2. **Timeout errors**: Increase timeout value in .env file
3. **ChromeDriver issues**: The script automatically downloads the correct ChromeDriver version, or set `CHROMEDRIVER_PATH` for custom path
4. **Permission errors**: Make sure ChromeDriver executable has proper permissions (`chmod +x`)

## Security Notes

- Never commit sensitive data in configuration files
- Use environment variables for sensitive information
- Be respectful of target websites and their terms of service
- Consider rate limiting for multiple form submissions