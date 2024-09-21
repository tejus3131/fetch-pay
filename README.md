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

### 1. Start the Address Exchange Bot

This bot handles user authentication. Run it once to handle all users:

```bash
python address_exchange.py
```

### 2. Start User Bots

Each user needs their own bot instance. You can run multiple instances, one for each user:

```bash
python user.py
```

> This will ask for a `name` and a `code`(use for uthorization while paying) and will provide a `UID` for each user.
> This `UID` will be used in login while interacting with UI.

### 3. Start User UI

Each user needs their UI instance. You can run multiple instances, one for each user:

```bash
python ui.py  # Starts the UI for the user to preview and scan QR codes
```

> Here you have to enter the `UID` of the user to login.
> You will get the user's QR code that can be used to recieve the payment.
> Or you can scan another QR to send funds to them.

## How It Works

- Each user is assigned an agent that manages their funds.
- Upon scanning a QR code or generating their own, the user bot communicates with the Processor Bot to initiate the transaction.
- The Address Exchange Bot ensures that user identities are authenticated.
- Custom authorization logic ensures security for each transaction.

## Contributing

Feel free to submit issues or pull requests to improve the project.

## Collabration

This project is created with support of `Fetch.ai Innovation Lab`, Meerut Institute of Engineering and Technology, Meerut, Uttar Pradesh, India.
