# 유튜브 업로더 템플릿 관리 프로그램
유튜브 영상 업로드 시 제목, 설명, 태그를 자동으로 채워주는 데스크톱 프로그램입니다.

## 주요 기능
- 제목, 설명, 태그 템플릿 저장 및 관리
- SQLite 데이터베이스를 사용한 데이터 영구 저장
- 템플릿 내용 수정 및 삭제
- 동적 변수( {{게임명}} , {{날짜}} )를 활용한 내용 자동 채우기
- 완성된 내용을 클립보드에 바로 복사

## 스크린샷
<img width="741" height="628" alt="화면 캡처 2025-08-22 023655" src="https://github.com/user-attachments/assets/f58b1359-f8a1-42ae-90a2-42c15752badd" />

## 다운로드 및 사용법
이 프로그램은 파이썬 설치 없이 바로 실행할 수 있습니다.
1. 최신 릴리즈 페이지 에서 uploader_gui.exe 파일과 youtube_uploader.db 파일을 다운로드합니다.
2. 두 파일을 같은 폴더에 두고 uploader_gui.exe 를 실행합니다.
## 개발 정보
- **개발 언어**: Python
- **사용 라이브러리**: tkinter , sqlite3 , pyperclip
- **라이선스**: MIT License
