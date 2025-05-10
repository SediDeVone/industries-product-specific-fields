# Product-Specific Fields Analyzer for Salesforce

A Python tool that analyzes Salesforce objects to identify which fields are being used for different products. This tool helps in understanding product-specific field usage patterns in Salesforce objects like QuoteLineItem, OrderItem, and Asset.

## Project Overview

This tool connects to a Salesforce organization and:
- Retrieves records for specified objects (QuoteLineItem, OrderItem, Asset)
- Analyzes which fields are populated for each product
- Outputs a list of fields used per product
- Can also analyze fields by product and action (optional functionality)

This information is valuable for:
- Understanding which fields are relevant for specific products
- Identifying field usage patterns
- Supporting data migration or integration projects
- Optimizing page layouts or validation rules

## Setup

### Prerequisites

1. Python 3.x
2. Salesforce organization with API access

### Installation

1. Clone this repository:
   ```
   git clone <repository-url>
   ```

2. Navigate to the repository folder:
   ```
   cd product-specific-fields
   ```

3. Install required dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Configure your Salesforce connection:
   - Create a copy of the example configuration file in the config directory
   - Update the configuration with your Salesforce credentials
   - Protect your configuration file to prevent leaking access data:
     ```
     git update-index --skip-worktree config/your_config_file.json
     ```

## Configuration

The configuration file (JSON format) should include:
- Salesforce authentication details (username, password, security token, etc.)
- Object configurations
- Field mapping information

Example configuration structure:
```json
{
  "namespace": "",
  "external field name": "Legacy_ID__c",
  "environment_access": [
    {
      "name": "source",
      "username": "your_username",
      "password": "your_password",
      "security_token": "your_security_token",
      "host": "your_instance.salesforce.com",
      "consumer_key": "your_consumer_key",
      "consumer_secret": "your_consumer_secret",
      "is_sandbox": true
    }
  ],
  "objects": [
    {
      "name": "ObjectName",
      "default_retrieve_query": " WHERE isDeleted = false",
      "matching_api_name": "Id",
      "record_type_mapping": [],
      "variants": [],
      "dependencies": []
    }
  ]
}
```

## Usage

Run the main script to analyze fields per product:

```
python getEditableFields.py
```

This will:
1. Connect to your Salesforce organization
2. Retrieve records for QuoteLineItem, OrderItem, and Asset
3. Analyze which fields are populated for each product
4. Output the results to the console

You can modify the script to:
- Analyze different objects
- Change the query conditions
- Enable the product-and-action analysis (uncomment the relevant section)
- Save results to a file instead of console output

## Security Note

The configuration file contains sensitive information (Salesforce credentials). Make sure to:
- Never commit your actual configuration file to version control
- Use the git skip-worktree feature as mentioned in the setup instructions
- Consider using environment variables or a secure vault for credentials in production environments

## Dependencies

- requests: For making HTTP requests to the Salesforce API
- unicodecsv: For handling CSV data with Unicode support
- salesforce_bulk: For interacting with the Salesforce Bulk API
