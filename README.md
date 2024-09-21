# QR Payment System with uAgents

This project simplifies peer-to-peer payments using QR codes, built on the `uAgents` library by Fetch.AI and a basic UI powered by `CustomTkinter`. It allows users to easily scan and pay using QR codes.

## Features

- **QR Code Payments**: Scan others' QR codes to send payments or display your own for receiving payments.
- **User Authentication**: Address exchange bot handles user authentication.
- **Code based Authorization**: Code based transaction authorization.
- **Multiple Users**: Set up bots and UI for multiple users to participate in transactions.
  
## Prerequisites

- Python 3.10 or higher
- Virtual Environment (`venv`)
- Required libraries from `requirements.txt`

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/tejus3131/fetch-pay.git
cd fetch-pay
```

### 2. Set up the virtual environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

## Running the Project

### 1. Start the Processor Bot

The Processor Bot initiates and processes all transactions. You only need to run this once:

```bash
python processor.py
```

### 2. Start the Address Exchange Bot

This bot handles user authentication. Run it once to handle all users:

```bash
python address_exchange.py
```

### 3. Start User Bots and UI

Each user needs their own bot and UI instance. You can run multiple instances, one for each user:

```bash
python user.py
python ui.py  # Starts the UI for the user to preview and scan QR codes
```

## How It Works

- Each user is assigned an agent that manages their funds.
- Upon scanning a QR code or generating their own, the user bot communicates with the Processor Bot to initiate the transaction.
- The Address Exchange Bot ensures that user identities are authenticated.
- Custom authorization logic ensures security for each transaction.

## Contributing

Feel free to submit issues or pull requests to improve the project.
