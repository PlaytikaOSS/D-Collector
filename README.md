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
- Install requirements based on requirements.txt
  ```bash
  pip install -r requirements.txt
  ```
- Copy 'config.py.example' to 'config.py'.
  ```bash
  cp config.py.example config.py
  ```
- Fill the relevant variables (empty configs will be ignored).
- Define your company's known internal domain suffixes for the tool to classify as private.
  E.g., `.corp`, `.internal`.
  
---

## Usage
```bash
  dcollector
```

## Output Example
Output Domains file will be in the following format (JSON):
```json
[{"name": "domain name", "record_type": "DNS type (CNAME,A)", "record_value": "value (ip,ec2 domain name)", "is_private": "false/true"}]
```

## Cloud Providers and Tools Support
- Static domains from file
- AWS
- GCP
- Digital Ocean
- Prisma® Cloud (by Palo Alto Networks)

---
## Roadmap
- Support for more cloud providers and DNS registrars.

---
## Contributing
Feel free to fork the repository and submit pull-requests.

---
## License

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
