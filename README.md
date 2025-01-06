# Payment Manager System

## Overview
The Payment Manager System is a desktop application designed to manage client payments. It allows users to add, edit, delete, and filter payments and clients. The system also provides functionality to send payment reminders via WhatsApp.

## Features
- Add, edit, and delete clients and payments.
- Filter payments by client.
- Toggle the display of paid payments.
- Send payment reminders via WhatsApp.
- Log actions in a backlog for auditing purposes.

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/Payment-Manager-System.git
   ```
2. Navigate to the project directory:
   ```bash
   cd Payment-Manager-System
   ```
3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Set up environment variables:
   - Create a `.env` file in the root directory.
   - Add your Supabase URL and key to the `.env` file:
     ```
     SUPABASE_URL=your_supabase_url
     SUPABASE_KEY=your_supabase_key
     ```

## Usage
1. Run the application:
   ```bash
   python src/app.py
   ```
2. The main window will open, allowing you to manage clients and payments.

## Modules
- `paymentapp.py`: Main application class for managing the main window and its components.
- `clientcrud.py`: Class for managing client CRUD operations.
- `paymentcrud.py`: Class for managing payment CRUD operations.
- `send_reminder.py`: Functions for sending payment reminders via WhatsApp.
- `supabase_client.py`: Supabase client setup.

## Contributing
1. Fork the repository.
2. Create a new branch:
   ```bash
   git checkout -b feature-branch
   ```
3. Make your changes and commit them:
   ```bash
   git commit -m "Description of changes"
   ```
4. Push to the branch:
   ```bash
   git push origin feature-branch
   ```
5. Open a pull request.

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
