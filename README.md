Forestfit Direct OCR Server
직거래 거래처 표 이미지 + 직거래 베이스 엑셀을 업로드해 입고일정을 자동 매칭하는 FastAPI 서버입니다.

Render 배포
GitHub에 이 폴더 업로드
Render.com → New Web Service
해당 저장소 연결
Build Command: pip install -r requirements.txt
Start Command: uvicorn app:app --host 0.0.0.0 --port $PORT
API
POST /analyze

base_file: 직거래 베이스 엑셀
kdg_image: 케이디지 표 이미지
lizard_image: 리자드 표 이미지
noreunja_image: 노른자 표 이미지
remind_image: 리마인드 표 이미지
응답:

result_rows
cellmate_csv_base64
