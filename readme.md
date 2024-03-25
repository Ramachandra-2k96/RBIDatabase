# RBIDatabase Project Installation Guide

Welcome to our RBIdatabase project! In this guide, we'll walk you through the steps to install and run our project from GitHub. Let's get started!

## Prerequisites

Before you begin, ensure you have the following installed on your system:

- Python (version 3.6 or later)
- pip (Python package installer)
- Git

## Installation

1. Clone the repository to your local machine:

   ```bash
   git clone https://github.com/Ramachandra-2k96/RBIDatabase
   ```

2. Navigate to the project directory:

   ```bash
   cd RBIDatabase
   ```

3. Create a virtual environment to isolate project dependencies:

   ```bash
   python -m venv env
   ```

4. Activate the virtual environment:

   - **Windows:**

     ```bash
     .\env\Scripts\activate
     ```

   - **Linux/macOS:**

     ```bash
     source env/bin/activate
     ```

5. Install project dependencies:

   ```bash
   pip install -r requirements.txt
   ```

6. Perform migrations:

   ```bash
   python manage.py migrate
   ```

## Running the Server

Now that you have installed the project and set up dependencies, you can run the development server:

```bash
python manage.py runserver
```

You should see output indicating that the server is running. Open your web browser and navigate to `http://localhost:8000` to view the project(user) .
`http://localhost:8000/admin/login` for main admin

`http://localhost:8000/bank_login/` for bank admin 
## Contributing

If you would like to contribute to this project, please follow these steps:

1. Fork the repository.
2. Create a new branch (`git checkout -b feature/yourfeature`).
3. Make your changes.
4. Commit your changes (`git commit -am 'Add some feature'`).
5. Push to the branch (`git push origin feature/yourfeature`).
6. Create a new Pull Request.

## Support

If you encounter any issues or have questions, feel free to [create an issue](https://github.com/Ramachandra-2k96/RBIDatabase/issues) on GitHub.

Happy coding! 🚀
