# 🔗 URL Shortener Project 🔗
### Web Address :  [Click this link](https://myshortener.netlify.app)

This project is a simple yet effective URL shortener that allows users to convert long URLs into shorter, more manageable links. It consists of a React-based frontend for user interaction and a Flask-based backend with a MongoDB database for storing URL mappings. The system provides a seamless experience for shortening URLs and redirecting users to the original links.

🚀 **Key Features**

- 🌐 **URL Shortening:** Converts long URLs into shorter, unique links.
- 🖱️ **Copy to Clipboard:** Easily copy the shortened URL with a single click.
- ♻️ **Redirection:** Redirects users from the shortened URL to the original URL.
- 💾 **MongoDB Storage:** Stores URL mappings in a MongoDB database for persistence.
- 🛡️ **Error Handling:** Provides informative error messages for invalid URLs or API issues.
- ⏳ **Loading Indicator:** Displays a loading indicator during API requests.
- ✨ **Client-Side Validation:** Validates URL input on the client-side before submission.
- 🔑 **Unique Key Generation:** Generates unique short keys using SHA-256 hashing with collision resolution.

🛠️ **Tech Stack**

| Category    | Technology      | Description                                                                 |
|-------------|-----------------|-----------------------------------------------------------------------------|
| Frontend    | React           | JavaScript library for building user interfaces.                            |
| Frontend    | lucide-react    | Icon library for React applications.                                        |
| Backend     | Flask           | Micro web framework for Python.                                             |
| Database    | MongoDB         | NoSQL database for storing URL mappings.                                    |
| Backend     | pymongo         | Python driver for MongoDB.                                                  |
| Other       | hashlib         | Python module for hashing algorithms (SHA-256).                               |
| Other       | urllib.parse    | Python module for parsing URLs.                                             |
| Other       | flask_cors      | Flask extension for handling Cross-Origin Resource Sharing (CORS).            |
| Build Tools | npm             | Node package manager for frontend dependencies.                             |
| Build Tools | pip             | Package installer for Python.                                               |

📦 **Getting Started**

### Prerequisites

- Node.js and npm (for the frontend)
- Python 3.x and pip (for the backend)
- MongoDB installed and running

### Installation

**Frontend:**

```bash
cd frontend
npm install
```

**Backend:**

```bash
cd backend
pip install -r requirements.txt
```

### Running Locally

**Frontend:**

```bash
cd frontend
npm start
```

**Backend:**

```bash
cd backend
python app.py
```

Make sure your MongoDB instance is running and accessible.  You may need to configure the connection string in `backend/shortener.py` if your MongoDB instance is not running on the default host and port.

💻 **Project Structure**

```
📂 url-shortener
├── 📂 backend
│   ├── 📄 shortener.py
│   ├── 📄 requirements.txt
│   └── 📄 .env (optional - for environment variables)
├── 📂 frontend
│   ├── 📂 src
│   │   ├── 📄 App.js
│   │   ├── 📄 index.js
│   │   └── 📄 ... (other frontend files)
│   ├── 📄 package.json
│   ├── 📄 public
│   └── 📄 ... (other frontend files)
├── 📄 README.md
└── 📄 ... (other project files)
```

📸 **Screenshots**



🤝 **Contributing**

Contributions are welcome! Please feel free to submit pull requests or open issues to suggest improvements or report bugs.

📝 **License**

This project is licensed under the [MIT License](LICENSE) - see the [LICENSE](LICENSE) file for details.

📬 **Contact**

If you have any questions or suggestions, feel free to contact me at [dpatel0698@gmail.com](mailto:your-email@example.com).

💖 **Thanks**

Thank you for checking out this URL Shortener project! I hope it's helpful.

