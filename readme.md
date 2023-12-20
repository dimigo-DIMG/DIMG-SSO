
## DIMG-SSO (codename: `somang`)

### 1. 개요

- DIMG-SSO는 한국디지털미디어고등학교 학생들을 위한 SSO(Single Sign On) 서비스입니다.
- DIMG 계정으로 로그인하여 DIMG 동아리의 서비스를 이용할 수 있습니다.
- 한국디지털미디어고등학교 학생들은 학교의 Google 계정을 사용하여 학생 인증과 동시에 회원가입할 수 있으며, 추후 로그인을 위한 이메일/비밀번호를 설정할 수 있습니다.
- DIMG-SSO는 인증과 각 서비스의 편의성을 위한 최소한의 정보만을 수집합니다.
- kaist의 sparcs 동아리의 [sparcssso](https://github.com/sparcs-kaist/sparcssso)를 참고하여 제작되었습니다. (MIT License)

### 2. 목표 기능 (route)

- [x] `/` - 메인 페이지
- [x] `/account` - 계정 페이지
  - [x] `/account/register` - 회원가입
  - [x] `/account/login` - 로그인
  - [x] `/account/logout` - 로그아웃
  - [x] '/account/modify' - 계정 정보 수정 (전체)
    - [X] `/account/modify/email` - 이메일 변경 (프로필 메뉴)
    - [X] `/account/modify/password` - 비밀번호 변경 (프로필 메뉴)
    - [X] `/account/modify/profile` - 프로필 변경 (프로필 메뉴)
  - [x] `/account/forgot-password` - 비밀번호 찾기 (인증 전)
  - [x] `/account/reset-password` - 비밀번호 재설정 (인증 후)
  - [x] `/account/verify` - 이메일 인증
  - [ ] `/account/delete` - 계정 삭제
  
- [x] `/manage` - 관리자 페이지
  - [X] `/manage/dashboard` - 대시보드
  - [ ] `/manage/users` - 사용자 관리
  - [ ] `/manage/users/<user_id>` - 사용자 관리
    - [ ] `/manage/users/<user_id>/edit` - 사용자 수정
    - [ ] `/manage/users/<user_id>/delete` - 사용자 삭제
  - [x] `/manage/services` - 서비스 관리
  - [x] `/manage/services/create` - 서비스 생성
  - [x] `/manage/services/<service_id>` - 서비스 관리
    - [x] `/manage/services/<service_id>/update` - 서비스 수정
    - [x] `/manage/services/<service_id>/delete` - 서비스 삭제
  - [ ] `/manage/ads` - 광고 관리
  - [ ] `/manage/announcements` - 공지사항 관리
  - [ ] `/manage/feedbacks` - 피드백 관리

- [ ] `/service` - 서비스 (유저)
  - [X] `/service/permission` - 서비스 연결 페이지

- [ ] `/api` - API (전체)
  - [ ] `/api/sso` - SSO API (전체)
    - [X] `/api/sso/token/get` - 토큰 발급
    - [ ] `/api/sso/token/info` - 토큰 정보
  
### 3. 기술 스택

- Python
  - FastAPI
  - SQLAlchemy
  - FastAPI-Users

- Web
  - HTML
  - CSS
  - JavaScript
  - Bootstrap

- Database
  - SQLite (추후 PostgreSQL로 변경 예정)

### 4. 개발자 

- 기획/설계: 20기 [soumt](https://github.com/soumt-r)
- 내부 시스템: 20기 [soumt](https://github.com/soumt-r)
- 디자인: 20기 [wenna](https://github.com/chunzhi23)
- 프론트앤드 개발: 20기 [wenna](https://github.com/chunzhi23)
