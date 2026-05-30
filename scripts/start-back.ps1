$env:PYTHONPATH = "D:\Project\weread\weread-review-web\.python-deps;D:\Project\weread\weread-review-web\back"
Set-Location -LiteralPath "D:\Project\weread\weread-review-web\back"
& "C:\Users\23533\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe" -m uvicorn app.main:app --host 127.0.0.1 --port 8000

