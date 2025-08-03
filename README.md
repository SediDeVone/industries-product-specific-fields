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
2. Salesforce org with API access and Salesforce CLI (sf) installed and authenticated

### Installation

1. Clone this repository:
   ```
   git clone <repository-url>
   ```

2. Navigate to the repository folder:
   ```
   cd product-specific-fields
   ```

3. Install required Python dependencies:
   ```
   pip install -r requirements.txt
   ```
   Note: If you encounter an ImportError for simple_salesforce, install it explicitly:
   ```
   pip install simple-salesforce
   ```

4. Authenticate to your Salesforce org using Salesforce CLI and set an alias (example alias: org-qa):
  - Interactive/Web login (recommended):
    ```
    sf org login web --alias org-qa
    ```
  - Or JWT-based login (for CI/automation). Ensure you have server.key and set environment variables.
    Important: The script derives env var names from the alias using `alias.capitalize()`. For an alias `org-qa`, it will look for:
    - Org-qa_CLIENT_ID: Connected App client id
    - Org-qa_USERNAME: Username of the target org
    Then run:
    ```
    sf org login jwt --client-id $Org-qa_CLIENT_ID --jwt-key-file server.key --username $Org-qa_USERNAME --alias org-qa
    ```

Note: You can specify the Salesforce org alias and domain at runtime using command-line parameters. The --org parameter is required; --domain defaults to 'test' if not provided. The alias is case-insensitive for CLI lookup but the JWT env vars are case-sensitive as described above.

## Usage

Run the main script to analyze fields per product:

```
python getEditableFields.py --org <your-org-alias> --domain <login-domain>
```

Examples:
- Using a sandbox alias and default domain:
```
python getEditableFields.py --org org-qa
```
- Using a production alias and login domain:
```
python getEditableFields.py --org org-prod --domain login
```

This will:
1. Connect to your Salesforce organization via the Salesforce CLI token
2. Retrieve records for QuoteLineItem, OrderItem, and Asset
3. Analyze which fields are populated for each product
4. Output the results to the console

You can modify the script to:
- Analyze different objects (change object names and product id field in get_editable_field_per_product calls)
- Change the query conditions (default_retrieve_query)
- Enable the product-and-action analysis (uncomment the "PER PRODUCT AND ACTION" section at the bottom)

## Configuration

No JSON configuration file is required. Authentication is handled via Salesforce CLI. For JWT re-auth fallback, the script looks for the following environment variables based on your alias (example alias 'org-qa'):
- org-qa_CLIENT_ID
- org-qa_USERNAME

Additionally, ensure a private key file named server.key is present if you use JWT login.

## Security Note

- Do not commit any credentials or private keys to version control.
- Prefer using Salesforce CLI auth mechanisms; for JWT, store client id and username in environment variables and server.key securely.

## Dependencies

Python packages (installed via requirements.txt):
- requests: For making HTTP requests to the Salesforce REST API
- unicodecsv: For handling CSV data with Unicode support (required by some environments)
- salesforce_bulk: For interacting with the Salesforce Bulk API
- simple_salesforce: Imported by the connector module (ensure it's available even if not directly used at runtime)

Other tools:
- Salesforce CLI (sf): Used to obtain access tokens and instance URL
