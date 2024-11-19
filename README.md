# D-Collector

**TLDR; D-Collector is a tool that fetches DNS records from various DNS management and cloud providers and
normalize all records to a unified format.**

---

## Description

Most of the enterprises nowadays are using multiple different cloud providers and DNS registrars.
That creates a fertile ground for shadow IT to grow and makes it extremely hard for information security
teams to map, manage and scan their attack surface.

The above led us to create *D-Collector*. Now, we can continuously scan our infrastructure for
security vulnerabilities and drastically reduce the risk of shadow IT.

### Who is this tool for?
This tool has been created for IT and information security practitioners to easily automate their
domains management and attack surface management.

### How it works?

- Provide D-Collector with your cloud providers API tokens/keys.
- D-Collector to fetch all DNS records from the given cloud providers. 
- D-Collector to create a unified structured "domains.json" file with all the DNS records.
- Harness the magic for your needs.

--- 

## Installation
### Prerequisites
- Fill the relevant providers' environment variables (empty variables will be ignored):
  ```bash
  # Prisma® Cloud (by Palo Alto Networks)
  export PRISMA_API_KEYID = your-value-here
  export PRISMA_API_SECRET = your-value-here
  export PRISMA_URL = your-value-here
  
  # Cycognito (ASM product)
  export CY_KEY = your-value-here
  export CY_REALM = your-value-here
  
  # AWS (Route53)
  export AWS_ACCESS_KEY_ID = your-value-here
  export AWS_SECRET_ACCESS_KEY = your-value-here
  # (Optional) If needed to assume a primary role for Route53 access
  export AWS_ARN=your-value-here
  # (Optional) JSON file containing additional roles to assume
  # This file should contain a list of role ARNs for additional Route53 accounts or permissions. Example:
  #
  # [
  #   "arn:aws:iam::123456789012:role/Role1",
  #   "arn:aws:iam::123456789012:role/Role2"
  # ]
  export AWS_ARN_EXTRA_ROLES_FILE=/path/to/roles.json
  
  # GCP
  export GCP_PRIVATE_KEY_FILE = your-value-here
  export GCP_PROJECT = your-value-here
  
  # Digital Ocean
  export DG_TOKEN = your-value-here
  
  # A JSON file contains DNS records in domains fetcher's output format
  export STATIC_DOMAINS_FILE = your-value-here
  ```
- Define your company's known internal domain suffixes for the tool to classify as private.
  E.g., `.corp`, `.internal`.
  ```bash
  # Internal domain suffixes list, e.g., ".corp", ".internal"
  # Example:
  # INTERNAL_DOMAIN_SUFFIXES = "['.internal','corp']"
  export INTERNAL_DOMAIN_SUFFIXES = your-value-here
  ```

### PIP (recommended)
```bash
pip install d-collector
```

### Manual
```bash
git clone https://github.com/Playtika/D-Collector.git
cd D-Collector
pip install .
```
---

## Usage
Short Form    | Long Form            | Description
------------- | -------------------- |-------------
-h            | --help               | Show this help message and exit
-lp            | --list-providers            | Listing loaded providers

### Examples
- List loaded providers\
```dcollector -lp```
- Pull domain names from providers\
```dcollector```

## Output Example
Output domains file will be in the following format (JSON):
```json
[{"name": "domain name", "record_type": "DNS type (CNAME,A)", "record_value": "value (ip,ec2 domain name)", "is_private": "false/true", "source": "provider/dns management tool"}]
```

## Cloud Providers and Tools Support
- Static domains from file
- AWS (Supports primary role and additional roles via JSON file)
- GCP
- Digital Ocean
- Prisma® Cloud (by Palo Alto Networks)
- Cycognito (EASM product)

---
## Roadmap
- Support for more cloud providers and DNS registrars.

---
## Contributing
Feel free to fork the repository and submit pull-requests.

---
## License

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
