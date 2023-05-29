EXCLUDE_DIRS = ['__pycache__', '.venv', '.git', '.idea', 'venv', 'env', 'node_modules', 'dist', 'build', '.vscode',
                '.github', '.gitlab']
ALLOW_FILES = ['.txt', '.js', '.mjs', '.ts', '.tsx', '.css', '.scss', '.less', '.html', '.htm', '.json', '.py',
               '.java', '.c', '.cpp', '.cs', '.go', '.php', '.rb', '.rs', '.swift', '.kt', '.scala', '.m', '.h',
               '.sh', '.pl', '.pm', '.lua', '.sql']
EXCLUDE_FILES = ['requirements.txt', 'package.json', 'package-lock.json', 'yarn.lock']
DEFAULT_MODEL_PATH = "models/ggml-gpt4all-j-v1.3-groovy.bin"
DEFAULT_CONFIG = {
    "max_tokens": "1048",
    "chunk_size": "500",
    "chunk_overlap": "50",
    "k": "4",
    "model_name": "gpt-3.5-turbo",
    "model_path": "models/ggml-gpt4all-j-v1.3-groovy.bin",
    "model_type": "openai",
}
