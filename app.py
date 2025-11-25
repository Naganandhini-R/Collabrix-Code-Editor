from flask import Flask, render_template, url_for, request, jsonify, redirect
from flask_socketio import SocketIO, emit, join_room
import os
import shutil
import subprocess
import uuid
import re

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)


@app.route('/')
def index():
    room_id = request.args.get('room_id', '')
    return render_template('home.html', room_id=room_id)


@app.route('/compile', methods=['POST', 'GET'])
def compile():
    if request.method == 'POST':
        code = request.get_json().get('codeVal')
        inputVal = request.get_json().get('inputVal')
        langType = request.get_json().get('langType')

        output = code_exe(langType, code, inputVal)
        data = {'result': output}
        return jsonify(data)
    else:
        return jsonify({'error': 'invalid access'})


@app.route('/editor/<string:room_id>', methods=['GET', 'POST'])
def editor(room_id):
    if request.method == 'POST':
        username = request.form.get('username')
        return render_template('editor.html', room_id=room_id, userName=username)
    else:
        return redirect((url_for("index", room_id=room_id)))


@socketio.on('join')
def handle_join(data):
    print("join")
    room = data['room']
    userName = data['userName']
    join_room(room)
    emit('request_users', {'room': room, 'userName': userName}, to=room, skip_sid=True)
    emit('request_editors', {'room': room}, to=room, skip_sid=True)


@socketio.on('requested_users')
def requested_users(data):
    room = data['room']
    users = data['users']
    emit('create_users', {'room': room, 'users': users}, to=room, skip_sid=True)


@socketio.on('requested_editors')
def requested_editors(data):
    print("render_editors")
    room = data['room']
    currentEditors = data['currentEditors']
    fileCount = data['fileCount']
    print(currentEditors)
    emit('create_editors', {'room': room, 'currentEditors': currentEditors, 'fileCount': fileCount}, to=room, skip_sid=True)


@socketio.on('update_text')
def handle_update(data):
    room = data['room']
    text = data['text']
    currentTextEditorName = data['currentTextEditorName']
    userName = data['userName']
    cursor = data['cursor']
    emit('update_text', {'text': text, 'currentTextEditorName': currentTextEditorName, 'userName': userName, 'cursor': cursor}, to=room, skip_sid=True)


@socketio.on('create_new_file')
def create_new_file(data):
    print("create_new_file in app.py")
    room = data['room']
    fileCount = data['fileCount']
    fileName = data['fileName']
    emit('create_new_file', {'room': room, 'fileCount': fileCount, 'fileName': fileName}, to=room, skip_sid=True)


@socketio.on('delete_file')
def delete_file(data):
    room = data['room']
    fileId = data['fileId']
    emit('delete_file', {'room': room, 'fileId': fileId}, to=room, skip_sid=True)


@socketio.on('rename_file')
def rename_file(data):
    room = data['room']
    fileId = data['fileId']
    newFileName = data['newFileName']
    emit('rename_file', {'room': room, 'fileId': fileId, 'newFileName': newFileName}, to=room, skip_sid=True)


# ====================== CODE EXECUTION FUNCTION ======================
def code_exe(language, code, inputVal):
    if language not in ["cpp", "py", "java", "c", "js"]:
        return "error: Invalid File Extension\nUse cpp, c, java, py or js File Extensions."

    sessionId = str(uuid.uuid4())
    folderPath = os.path.join("temp", sessionId)
    os.makedirs(folderPath, exist_ok=True)

    fileName = f"code.{language}"
    filePath = os.path.join(folderPath, fileName)

    with open(filePath, "w") as f:
        f.write(code)

    try:
        # -------------------- PYTHON --------------------
        if language == "py":
            execute = subprocess.run(
                ["python3", filePath],
                timeout=10,
                input=inputVal,
                capture_output=True,
                text=True
            )
            shutil.rmtree(folderPath)
            return execute.stderr if execute.returncode != 0 else execute.stdout

        # -------------------- CPP --------------------
        elif language == "cpp":
            outputFile = f"{folderPath}/a.out"
            compileCode = subprocess.run(
                ["g++", "-o", outputFile, filePath],
                capture_output=True,
                text=True
            )
            if compileCode.returncode != 0:
                shutil.rmtree(folderPath)
                return compileCode.stderr

            execute = subprocess.run(
                [outputFile],
                timeout=10,
                input=inputVal,
                capture_output=True,
                text=True
            )
            shutil.rmtree(folderPath)
            return execute.stderr if execute.returncode != 0 else execute.stdout

        # -------------------- C --------------------
        elif language == "c":
            outputFile = f"{folderPath}/a.out"
            compileCode = subprocess.run(
                ["gcc", "-o", outputFile, filePath],
                capture_output=True,
                text=True
            )
            if compileCode.returncode != 0:
                shutil.rmtree(folderPath)
                return compileCode.stderr

            execute = subprocess.run(
                [outputFile],
                timeout=10,
                input=inputVal,
                capture_output=True,
                text=True
            )
            shutil.rmtree(folderPath)
            return execute.stderr if execute.returncode != 0 else execute.stdout

        # -------------------- JAVA --------------------
        elif language == "java":
            match = re.search(r'public\s+class\s+([A-Za-z_]\w*)', code)
            class_name = match.group(1) if match else "Main"
            javaFilePath = os.path.join(folderPath, f"{class_name}.java")

            with open(javaFilePath, "w") as f:
                f.write(code)

            compileCode = subprocess.run(
                ["javac", javaFilePath],
                capture_output=True,
                text=True
            )
            if compileCode.returncode != 0:
                shutil.rmtree(folderPath)
                return compileCode.stderr

            execute = subprocess.run(
                ["java", "-cp", folderPath, class_name],
                timeout=10,
                input=inputVal,
                capture_output=True,
                text=True
            )
            shutil.rmtree(folderPath)
            return execute.stderr if execute.returncode != 0 else execute.stdout

        # -------------------- JAVASCRIPT --------------------
        elif language == "js":
            modified_code = re.sub(
                r'prompt\s*\(\s*["\'].*?["\']\s*\)',
                f'"{inputVal.strip()}"',
                code
            )

            with open(filePath, "w") as f:
                f.write(modified_code)

            execute = subprocess.run(
                ["node", filePath],
                timeout=10,
                input=inputVal,
                capture_output=True,
                text=True
            )
            shutil.rmtree(folderPath)
            return execute.stderr if execute.returncode != 0 else execute.stdout

    except subprocess.TimeoutExpired:
        shutil.rmtree(folderPath)
        return "Timeout expired. The code execution took too long."


# ====================== MAIN APP RUN ======================
if __name__ == '__main__':
     socketio.run(app, host='0.0.0.0', port=5000, debug=True, allow_unsafe_werkzeug=True)




