# Godot Best Practices

Godot 4.x 게임 개발 모범 사례 가이드

## 🏗️ 프로젝트 구조

### 권장 폴더 구조
```
MyGame/
├── scenes/              # 씬 파일 (.tscn)
│   ├── characters/      # 캐릭터 씬
│   │   ├── player.tscn
│   │   └── enemy.tscn
│   ├── levels/          # 레벨 씬
│   │   ├── level_1.tscn
│   │   └── level_2.tscn
│   ├── ui/              # UI 씬
│   │   ├── main_menu.tscn
│   │   └── hud.tscn
│   └── main.tscn        # 메인 씬
├── scripts/             # GDScript 파일
│   ├── player.gd
│   ├── enemy.gd
│   └── game_manager.gd
├── assets/              # 에셋
│   ├── sprites/         # 이미지
│   ├── sounds/          # 사운드
│   ├── fonts/           # 폰트
│   └── materials/       # 머티리얼
├── autoload/            # 전역 스크립트 (싱글톤)
│   ├── global.gd
│   └── audio_manager.gd
└── project.godot
```

### 파일 이름 규칙
- **씬**: `snake_case.tscn` (예: `player_character.tscn`)
- **스크립트**: `snake_case.gd` (예: `game_manager.gd`)
- **클래스**: `PascalCase` (예: `class_name PlayerController`)
- **상수**: `UPPER_SNAKE_CASE` (예: `const MAX_SPEED = 500`)

---

## 📝 코딩 스타일

### 네이밍
```gdscript
# 변수: snake_case
var player_speed = 100.0
var current_health = 100

# 상수: UPPER_SNAKE_CASE
const MAX_BULLETS = 10
const GRAVITY = 980.0

# 함수: snake_case
func calculate_damage():
    pass

# 클래스: PascalCase
class_name PlayerController

# 신호: past tense + snake_case
signal health_changed
signal player_died

# 프라이빗 변수: _snake_case
var _internal_state = 0

func _private_function():
    pass
```

### 코드 구조 순서
```gdscript
extends Node2D

# 1. class_name (있을 경우)
class_name MyNode

# 2. signals
signal health_changed(new_health)

# 3. enums
enum State { IDLE, WALK, RUN }

# 4. constants
const MAX_SPEED = 500

# 5. @export 변수
@export var speed: float = 100.0

# 6. public 변수
var health: int = 100

# 7. private 변수
var _state: State = State.IDLE

# 8. @onready 변수
@onready var sprite = $Sprite2D

# 9. _init() / _ready()
func _init():
    pass

func _ready():
    pass

# 10. 내장 콜백 (_process, _physics_process 등)
func _process(delta):
    pass

# 11. public 함수
func take_damage(amount: int):
    health -= amount

# 12. private 함수
func _update_animation():
    pass

# 13. 신호 핸들러
func _on_timer_timeout():
    pass

# 14. 내부 클래스
class Weapon:
    var damage: int = 10
```

---

## 🎯 씬 설계

### 씬 분리 원칙
- **재사용 가능한 단위로 분리** (예: Player, Enemy, Bullet)
- **각 씬은 독립적으로 테스트 가능해야 함**
- **큰 레벨은 여러 씬으로 분할** (씬 인스턴스 활용)

### 루트 노드 선택
- **2D 게임**: Node2D
- **3D 게임**: Node3D
- **UI**: Control
- **로직 전용**: Node

### 노드 계층 구조
```
Player (CharacterBody2D)
├── Sprite2D
├── CollisionShape2D
├── Camera2D
├── AnimationPlayer
└── Audio (Node)
    ├── FootstepSound (AudioStreamPlayer2D)
    └── JumpSound (AudioStreamPlayer2D)
```

**원칙**:
- 논리적 그룹핑 (Audio, Effects 등)
- 깊이 제한 (3~4단계 이내 권장)

---

## 🔧 스크립트 작성

### @onready 활용
```gdscript
# ❌ Bad: _ready()에서 매번 get_node()
func _ready():
    var sprite = get_node("Sprite2D")
    sprite.texture = load("res://...")

# ✅ Good: @onready로 초기화
@onready var sprite = $Sprite2D

func _ready():
    sprite.texture = load("res://...")
```

### 타입 힌트 사용
```gdscript
# ❌ Bad: 타입 미지정
var speed = 100
func move(dir):
    pass

# ✅ Good: 타입 명시
var speed: float = 100.0
func move(dir: Vector2) -> void:
    pass
```

### Signal vs Call
```gdscript
# ❌ Bad: 직접 호출 (결합도 높음)
# player.gd
func take_damage(amount):
    health -= amount
    get_parent().get_node("UI").update_health(health)  # 나쁨!

# ✅ Good: Signal 사용 (디커플링)
# player.gd
signal health_changed(new_health)

func take_damage(amount):
    health -= amount
    health_changed.emit(health)

# ui.gd
func _ready():
    $Player.health_changed.connect(_on_player_health_changed)

func _on_player_health_changed(new_health):
    $HealthBar.value = new_health
```

### Null 체크
```gdscript
# ❌ Bad: Null 체크 없음
var player = get_tree().get_first_node_in_group("player")
player.take_damage(10)  # player가 null이면 에러!

# ✅ Good: Null 체크
var player = get_tree().get_first_node_in_group("player")
if player:
    player.take_damage(10)
```

---

## 🎮 물리 처리

### _process vs _physics_process
```gdscript
# _process: 렌더링, 입력, 애니메이션
func _process(delta):
    if Input.is_action_just_pressed("shoot"):
        shoot()
    update_animation()

# _physics_process: 물리, 이동
func _physics_process(delta):
    velocity = Vector2(100, 0)
    move_and_slide()
```

### Delta Time 사용
```gdscript
# ❌ Bad: 프레임 의존
func _process(delta):
    position.x += 5  # 프레임레이트에 따라 속도 변함

# ✅ Good: Delta 곱하기
func _process(delta):
    position.x += 100 * delta  # 초당 100픽셀
```

---

## 🗂️ 리소스 관리

### Preload vs Load
```gdscript
# Preload: 컴파일 타임에 로드 (상수)
const ENEMY_SCENE = preload("res://scenes/enemy.tscn")

func spawn_enemy():
    var enemy = ENEMY_SCENE.instantiate()
    add_child(enemy)

# Load: 런타임에 로드 (동적)
func load_level(level_name: String):
    var scene = load("res://scenes/%s.tscn" % level_name)
    var level = scene.instantiate()
    add_child(level)
```

### 씬 인스턴스 생성
```gdscript
# ✅ Good: 재사용 패턴
const BULLET_SCENE = preload("res://scenes/bullet.tscn")

func shoot():
    var bullet = BULLET_SCENE.instantiate()
    bullet.position = $Muzzle.global_position
    get_parent().add_child(bullet)  # 부모에 추가 (플레이어가 죽어도 총알 유지)
```

### 메모리 관리
```gdscript
# 씬 제거 시 queue_free() 사용
$Enemy.queue_free()  # 프레임 끝에 안전하게 제거

# free()는 즉시 제거 (위험할 수 있음)
```

---

## 🎨 성능 최적화

### 그룹 활용
```gdscript
# 씬에서 그룹 설정 (Inspector → Node → Groups)
# 또는 코드로 추가
func _ready():
    add_to_group("enemies")

# 그룹 검색 (빠름)
var enemies = get_tree().get_nodes_in_group("enemies")
for enemy in enemies:
    enemy.take_damage(10)
```

### 불필요한 _process 제거
```gdscript
# ❌ Bad: 빈 _process
func _process(delta):
    pass  # 불필요한 오버헤드

# ✅ Good: 필요 없으면 삭제 또는 비활성화
func _ready():
    set_process(false)  # _process 비활성화
```

### VisibleOnScreenNotifier2D 활용
```gdscript
# 화면 밖 객체 비활성화
@onready var notifier = $VisibleOnScreenNotifier2D

func _ready():
    notifier.screen_exited.connect(_on_screen_exited)
    notifier.screen_entered.connect(_on_screen_entered)

func _on_screen_exited():
    set_process(false)

func _on_screen_entered():
    set_process(true)
```

---

## 🧪 테스트 & 디버깅

### Breakpoint 사용
```gdscript
func take_damage(amount):
    breakpoint  # 디버거 중단점 (코드에 저장됨)
    health -= amount
```

### Assert 활용
```gdscript
func set_health(value: int):
    assert(value >= 0, "Health cannot be negative")
    health = value
```

### 디버그 출력
```gdscript
# print: 일반 출력
print("Health: ", health)

# print_debug: 파일/라인 정보 포함
print_debug("Something went wrong")

# push_warning: 경고 (에디터에 표시)
push_warning("Low health!")

# push_error: 에러
push_error("Critical error!")
```

---

## 🌐 Autoload (싱글톤)

### 전역 스크립트 생성
```gdscript
# autoload/global.gd
extends Node

var score: int = 0
var player_name: String = "Player"

func reset_game():
    score = 0
```

### Autoload 등록
1. Project → Project Settings → Autoload
2. Path: `res://autoload/global.gd`
3. Node Name: `Global`

### 사용
```gdscript
# 어디서든 접근 가능
Global.score += 10
print(Global.player_name)
```

---

## 🚫 피해야 할 패턴

### ❌ 글로벌 변수 남용
```gdscript
# global.gd에 모든 것을 넣지 말 것
# 대신 관련 기능별로 분리 (AudioManager, SaveManager 등)
```

### ❌ 긴 함수
```gdscript
# 함수는 한 가지 일만 (Single Responsibility)
# 50줄 이상이면 분리 고려
```

### ❌ 매직 넘버
```gdscript
# ❌ Bad
if health < 20:
    play_low_health_sound()

# ✅ Good
const LOW_HEALTH_THRESHOLD = 20

if health < LOW_HEALTH_THRESHOLD:
    play_low_health_sound()
```

---

## 📚 추가 자료

- [GDScript 스타일 가이드](https://docs.godotengine.org/en/stable/tutorials/scripting/gdscript/gdscript_styleguide.html)
- [Godot 성능 최적화](https://docs.godotengine.org/en/stable/tutorials/performance/index.html)

---

**원칙 요약**:
1. 씬을 재사용 가능한 단위로 분리
2. Signal로 디커플링
3. 타입 힌트 사용
4. Delta time 고려
5. 그룹 활용
6. Autoload 최소화
7. 명확한 네이밍
