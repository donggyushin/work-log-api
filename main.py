import os
import uvicorn
from src.presentation.api import app


if __name__ == "__main__":
    # Railway는 PORT 환경 변수를 동적으로 할당
    # 로컬 개발에서는 기본값 8000 사용
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
