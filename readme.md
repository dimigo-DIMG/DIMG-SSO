
## DIMG-SSO (codename: `somang`)

### 1. 개요

- DIMG-SSO는 한국디지털미디어고등학교 학생들을 위한 SSO(Single Sign On) 서비스입니다.
- DIMG 계정으로 로그인하여 DIMG 동아리의 서비스를 이용할 수 있습니다.
- 한국디지털미디어고등학교 학생들은 학교의 Google 계정을 사용하여 학생 인증과 동시에 회원가입할 수 있으며, 추후 로그인을 위한 이메일/비밀번호를 설정할 수 있습니다.
- DIMG-SSO는 인증과 각 서비스의 편의성을 위한 최소한의 정보만을 수집합니다.
- kaist의 sparcs 동아리의 [sparcssso](https://github.com/sparcs-kaist/sparcssso)를 참고하여 제작되었습니다. (MIT License)

### 2. 목표 기능 (route)

- [x] `/` - 메인 페이지
- [ ] `/account` - 계정 관련 루트
  - [x] `/account/register` - 회원가입
  - [x] `/account/login` - 로그인
  - [x] `/account/logout` - 로그아웃
  - [ ] `/account/verify` - 이메일 인증
  - [ ] `/account/password` - 비밀번호 변경
- [ ] `/api` - API 루트
  - [ ] `/api/sso`` - SSO API 루트
    - [ ] `/api/sso/token` - 토큰 발급
  
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
- 페이지 디자인: 20기 [chunzhi](https://github.com/chunzhi23)