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

### Basic Usage

1. **Update configuration:** Modify `form_config.json` with your target form's URL and field details
2. **Run the automation:**
   ```bash
   python form_automation.py
   ```

### With Test Data Generation

1. **Configure test data generator:** Update `test_data_config.json` with your test data generator page details
2. **Run with state code for test data generation:**
   ```bash
   python form_automation.py --state CA
   ```
3. **Additional options:**
   ```bash
   # Run in headless mode
   python form_automation.py --state NY --headless
   
   # Use custom configuration files
   python form_automation.py --state TX --config my_form_config.json --test-data-config my_test_config.json
   ```

### Command Line Arguments

- `--state, -s`: State code for test data generation (e.g., CA, NY, TX)
- `--headless`: Run browser in headless mode
- `--config, -c`: Custom form configuration file (default: form_config.json)
- `--test-data-config, -t`: Custom test data configuration file (default: test_data_config.json)

## Environment Variables

Set in `.env` file:
- `CONFIG_FILE`: Path to configuration file (default: form_config.json)
- `HEADLESS`: Run browser in headless mode (true/false)
- `TIMEOUT`: Element wait timeout in seconds

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

## Test Data Generation

The tool supports automatic test data generation by visiting a separate test data generator page before filling the main form.

### Configuration

Update `test_data_config.json` with your test data generator details:

```json
{
  "test_data_generation": {
    "enabled": true,
    "url": "https://your-test-generator.com",
    "state_dropdown": {
      "selector": "state",
      "selector_type": "id"
    },
    "generate_button": {
      "selector": "generateBtn", 
      "selector_type": "id"
    },
    "output_fields": {
      "zipCode": {"selector": "zipCode", "selector_type": "id"},
      "mbi": {"selector": "mbi", "selector_type": "id"},
      "ssn": {"selector": "ssn", "selector_type": "id"}
    }
  }
}
```

### Workflow

1. **Generate Test Data**: Tool visits the test data generator page
2. **Select State**: Chooses the provided state code from dropdown
3. **Generate Values**: Clicks generate button to create random values
4. **Extract Data**: Captures zipCode, mbi, and ssn values
5. **Substitute Values**: Replaces placeholders in form configuration
6. **Fill Form**: Proceeds with form automation using generated data

### Using Placeholders

In your `form_config.json`, use placeholders that will be replaced with generated values:

```json
{
  "type": "text",
  "selector": "zipcode",
  "selector_type": "id", 
  "value": "{{zipCode}}"
}
```

Available placeholders:
- `{{zipCode}}` - Generated ZIP code
- `{{mbi}}` - Generated MBI number  
- `{{ssn}}` - Generated SSN

## Troubleshooting

1. **Element not found**: Check selector and selector_type in your configuration
2. **Timeout errors**: Increase timeout value in .env file
3. **ChromeDriver issues**: The script automatically downloads the correct ChromeDriver version

## Security Notes

- Never commit sensitive data in configuration files
- Use environment variables for sensitive information
- Be respectful of target websites and their terms of service
- Consider rate limiting for multiple form submissions