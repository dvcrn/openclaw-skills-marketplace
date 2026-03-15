# Godot Engine Skill

Godot 4.x 게임 엔진 개발을 위한 종합 스킬 패키지

## 📁 구조

```
godot/
├── SKILL.md                          # 메인 스킬 문서
├── README.md                         # 이 파일
├── scripts/                          # 헬퍼 스크립트
│   ├── new_project.sh               # 신규 프로젝트 생성
│   └── build_game.sh                # 게임 빌드 (헤드리스)
├── references/                       # 레퍼런스 문서
│   ├── gdscript-cheatsheet.md       # GDScript 치트시트
│   ├── nodes-reference.md           # 노드 레퍼런스
│   ├── best-practices.md            # 베스트 프랙티스
│   ├── 2d-patterns.md               # 2D 게임 패턴
│   └── 3d-patterns.md               # 3D 게임 패턴
└── assets/                           # (향후 템플릿 프로젝트)
```

## 🚀 빠른 시작

### 1. 신규 프로젝트 생성 (MiniPC)
```bash
# MiniPC에서 실행
cd $HOME/
bash /path/to/godot/scripts/new_project.sh MyGame
```

### 2. 프로젝트 열기
```bash
cd MyGame
godot4 -e .  # 에디터 열기
godot4 .     # 실행
```

### 3. 빌드 (Web)
```bash
bash /path/to/godot/scripts/build_game.sh . Web export
```

## 📖 문서 활용

### SKILL.md
- Godot 프로젝트 작업 시 자동으로 로드되는 메인 가이드
- Quick Start, GDScript 기본, 2D/3D 워크플로우 포함

### references/
- **gdscript-cheatsheet.md**: GDScript 문법 빠른 참조
- **nodes-reference.md**: 자주 쓰는 노드 목록 + 사용법
- **best-practices.md**: 프로젝트 구조, 코딩 스타일, 최적화
- **2d-patterns.md**: 플레이어 이동, 적 AI, 발사체, 충돌 등
- **3d-patterns.md**: FPS, TPS, 물리, 차량, 비행 등

## 🛠️ 헬퍼 스크립트 사용법

### new_project.sh
```bash
# 기본 사용
./scripts/new_project.sh MyGame

# 커스텀 경로
./scripts/new_project.sh MyGame /custom/path

# 자동으로 생성되는 것:
# - project.godot (WASD 입력 설정 포함)
# - scenes/, scripts/, assets/ 폴더 구조
# - East Sea Games 부트 스플래시 (있을 경우)
```

### build_game.sh
```bash
# Web 빌드
./scripts/build_game.sh . Web export

# Linux 빌드
./scripts/build_game.sh . Linux export

# Android 빌드 (Export Templates 필요)
./scripts/build_game.sh . Android export
```

## 🎯 사용 시나리오

### 시나리오 1: 2D 플랫포머 제작
1. `SKILL.md` → "2D Game Workflows" 참조
2. `references/2d-patterns.md` → "플랫포머 이동" 패턴 복사
3. `references/nodes-reference.md` → CharacterBody2D 사용법 확인

### 시나리오 2: FPS 게임 제작
1. `SKILL.md` → "3D Game Workflows" 참조
2. `references/3d-patterns.md` → "FPS 플레이어 컨트롤러" 복사
3. `references/3d-patterns.md` → "Raycast 슈팅" 패턴 추가

### 시나리오 3: 프로젝트 설계
1. `references/best-practices.md` → "프로젝트 구조" 참조
2. `references/best-practices.md` → "씬 설계" 원칙 적용
3. `references/gdscript-cheatsheet.md` → 네이밍 규칙 준수

## 🔗 외부 참고 자료

- [Godot 공식 문서](https://docs.godotengine.org/en/stable/)
- [GDQuest 튜토리얼](https://www.gdquest.com/tutorial/godot/)
- [Godot Asset Library](https://godotengine.org/asset-library/asset)

## ⚙️ MiniPC 환경

- **Godot 버전**: 4.6 stable
- **경로**: `$HOME/godot4/Godot_v4.6-stable_linux.x86_64`
- **Export Templates**: 설치됨 (Web, Linux, Android)
- **커스텀 부트 스플래시**: `$HOME/godot-demo/boot_splash.png`

## 📝 버전 히스토리

- **1.0.0** (2026-02-05): 초기 릴리즈
  - SKILL.md, 5개 레퍼런스 문서
  - 2개 헬퍼 스크립트 (new_project, build_game)
  - Godot 4.6 기준

---

**Maintained by**: Miss Kim  
**Last Updated**: 2026-02-05
