# Load-Balancer-Distributed-System
## Project Overview
This project involves implementing a load balancer, which asynchronously routes requests between servers.

## Installation and Setup
### Pre-requisites
- Python 3.9+
- Docker Version 20.10.23 or above
- Ubuntu 20.04 LTS or above

### Setup Instructions
- Clone the repository:
```bash
git clone https://github.com/Twna-Jane/Load-Balancer-Distributed-System.git 
```

- Navigate to the repository:
```bash
cd Load-Balancer-Distributed-System
```

- Create a Python virtual environment:
```bash
python3 -m venv .venv
```

- Activate the virtual environment:
```bash
source .venv/bin/activate
```

- Install the required libraries:
```bash
pip install -r requirements.txt
```

## Basic Usage
### Running Docker Services
- Build images and start the services:
```bash
docker-compose up -d
```

- Verify that the containers are running:
```bash
docker-compose ps
```

- When you're done, you can stop and remove containers:
```bash
docker-compose down
```

### Running Python files
- To run Python files while the virtual environment is active:
```bash
python app.py
```