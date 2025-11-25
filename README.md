# 🖥️ CollaBrix

A **real-time, web-based** collaborative code editor that allows multiple users to write, edit, and execute code together in the same environment. The platform is designed for seamless team collaboration and supports multiple programming languages.

## 🚀 Features
- Real-time collaborative editing  
- Ace Editor with syntax highlighting  
- Multiple language support (C, C++, Java, Python, JavaScript)  
- User cursor tracking  
- File creation & download  
- Shareable room links  
- Docker support for easy deployment  


## 🚀 Getting Started
### 🔹 Setup
1. Clone the repository:
   ```bash
   git clone https://github.com/Naganandhini-R/Collabrix-Code-Editor.git
   cd Collabrix-Code-Editor
   ```
2. Create a Docker image:
   ```bash
   docker build -t collabrix .
   ```

3. Run a container from the `collabrix` image:
   ```bash
   docker run -p 5000:5000 collabrix
   ```

4. Open the app in your browser:
   ```
   http://localhost:5000
   # or replace "privateip" with your private IP address (e.g., 10.12.224.106)
   http://privateip:5000
   ```

