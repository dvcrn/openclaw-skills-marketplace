# 3D Game Patterns

Godot 4.x 3D 게임 공통 패턴 모음

## 🎮 FPS 플레이어 컨트롤러

### 기본 FPS 이동
```gdscript
extends CharacterBody3D

@export var speed: float = 5.0
@export var jump_velocity: float = 4.5
@export var mouse_sensitivity: float = 0.003

var gravity = ProjectSettings.get_setting("physics/3d/default_gravity")

@onready var camera = $Camera3D

func _ready():
    Input.mouse_mode = Input.MOUSE_MODE_CAPTURED

func _input(event):
    if event is InputEventMouseMotion:
        # 마우스 Y축: 카메라 상하
        camera.rotation.x -= event.relative.y * mouse_sensitivity
        camera.rotation.x = clamp(camera.rotation.x, -PI/2, PI/2)
        
        # 마우스 X축: 몸체 좌우
        rotation.y -= event.relative.x * mouse_sensitivity

func _physics_process(delta):
    # 중력
    if not is_on_floor():
        velocity.y -= gravity * delta
    
    # 점프
    if Input.is_action_just_pressed("ui_accept") and is_on_floor():
        velocity.y = jump_velocity
    
    # WASD 이동
    var input_dir = Input.get_vector("ui_left", "ui_right", "ui_up", "ui_down")
    var direction = (transform.basis * Vector3(input_dir.x, 0, input_dir.y)).normalized()
    
    if direction:
        velocity.x = direction.x * speed
        velocity.z = direction.z * speed
    else:
        velocity.x = move_toward(velocity.x, 0, speed)
        velocity.z = move_toward(velocity.z, 0, speed)
    
    move_and_slide()
```

### 헤드 밥 (걷기 흔들림)
```gdscript
extends Camera3D

@export var bob_frequency: float = 2.0
@export var bob_amplitude: float = 0.08
var bob_time: float = 0.0

func _process(delta):
    var velocity = get_parent().velocity  # CharacterBody3D 속도
    
    if velocity.length() > 0:
        bob_time += delta * velocity.length() * bob_frequency
        position.y = sin(bob_time) * bob_amplitude
    else:
        bob_time = 0
        position.y = lerp(position.y, 0.0, delta * 10.0)
```

---

## 🎯 TPS (3인칭) 카메라

### 플레이어 따라가기
```gdscript
# CameraRig (Node3D)
# ├── CameraTarget (Node3D) - 플레이어 위치
# └── Camera3D

extends Node3D

@export var target: Node3D
@export var distance: float = 5.0
@export var height: float = 2.0
@export var rotation_speed: float = 0.003

@onready var camera = $Camera3D

func _ready():
    Input.mouse_mode = Input.MOUSE_MODE_CAPTURED

func _input(event):
    if event is InputEventMouseMotion:
        rotation.y -= event.relative.x * rotation_speed
        camera.rotation.x -= event.relative.y * rotation_speed
        camera.rotation.x = clamp(camera.rotation.x, -PI/4, PI/4)

func _process(delta):
    if target:
        global_position = target.global_position
        
        # 카메라를 뒤로 배치
        var offset = -transform.basis.z * distance + Vector3.UP * height
        camera.position = offset
```

---

## 🚶 캐릭터 이동

### 이동 + 회전
```gdscript
extends CharacterBody3D

@export var speed: float = 5.0
@export var rotation_speed: float = 10.0
var gravity = ProjectSettings.get_setting("physics/3d/default_gravity")

func _physics_process(delta):
    if not is_on_floor():
        velocity.y -= gravity * delta
    
    var input_dir = Input.get_vector("ui_left", "ui_right", "ui_up", "ui_down")
    
    if input_dir.length() > 0:
        var direction = Vector3(input_dir.x, 0, input_dir.y).normalized()
        
        # 카메라 방향 기준으로 이동
        var camera_basis = $Camera3D.global_transform.basis
        direction = camera_basis * direction
        direction.y = 0
        direction = direction.normalized()
        
        velocity.x = direction.x * speed
        velocity.z = direction.z * speed
        
        # 이동 방향으로 회전
        var target_rotation = atan2(direction.x, direction.z)
        rotation.y = lerp_angle(rotation.y, target_rotation, rotation_speed * delta)
    else:
        velocity.x = move_toward(velocity.x, 0, speed)
        velocity.z = move_toward(velocity.z, 0, speed)
    
    move_and_slide()
```

---

## 🎯 총 발사 (Raycast)

### Raycast 슈팅
```gdscript
extends Node3D

@export var damage: int = 10
@export var max_range: float = 100.0

@onready var raycast = $RayCast3D
@onready var muzzle = $Muzzle

func _process(delta):
    if Input.is_action_just_pressed("shoot"):
        shoot()

func shoot():
    raycast.target_position = Vector3(0, 0, -max_range)
    raycast.force_raycast_update()
    
    if raycast.is_colliding():
        var collider = raycast.get_collider()
        if collider.has_method("take_damage"):
            collider.take_damage(damage)
        
        # 총알 구멍 이펙트
        spawn_bullet_hole(raycast.get_collision_point())

func spawn_bullet_hole(pos: Vector3):
    # 총알 구멍 파티클 또는 데칼
    pass
```

---

## 🏃 적 AI (3D)

### 플레이어 추적 (NavMesh)
```gdscript
extends CharacterBody3D

@export var speed: float = 3.0
@export var chase_range: float = 10.0

var player: Node3D
var nav_agent: NavigationAgent3D

func _ready():
    player = get_tree().get_first_node_in_group("player")
    nav_agent = $NavigationAgent3D
    nav_agent.target_position = player.global_position

func _physics_process(delta):
    if not player:
        return
    
    var distance = global_position.distance_to(player.global_position)
    
    if distance < chase_range:
        nav_agent.target_position = player.global_position
        
        var next_position = nav_agent.get_next_path_position()
        var direction = (next_position - global_position).normalized()
        
        velocity = direction * speed
        move_and_slide()
        
        # 플레이어 방향으로 회전
        look_at(player.global_position, Vector3.UP)
```

---

## 📦 오브젝트 상호작용

### Raycast 상호작용 (E키)
```gdscript
extends Camera3D

@export var interaction_range: float = 3.0

@onready var raycast = $RayCast3D

func _process(delta):
    raycast.target_position = Vector3(0, 0, -interaction_range)
    raycast.force_raycast_update()
    
    if raycast.is_colliding():
        var collider = raycast.get_collider()
        if collider.has_method("interact"):
            # UI: "Press E to interact" 표시
            if Input.is_action_just_pressed("interact"):
                collider.interact()
```

### 상호작용 오브젝트
```gdscript
# door.gd
extends StaticBody3D

func interact():
    print("Door opened!")
    # 문 열기 애니메이션
    $AnimationPlayer.play("open")
```

---

## 💥 물리 오브젝트

### RigidBody3D 충격
```gdscript
extends RigidBody3D

func apply_explosion_force(origin: Vector3, force: float, radius: float):
    var direction = (global_position - origin).normalized()
    var distance = global_position.distance_to(origin)
    
    if distance < radius:
        var strength = force * (1.0 - distance / radius)
        apply_central_impulse(direction * strength)
```

---

## 🎬 애니메이션

### AnimationTree (캐릭터)
```gdscript
@onready var anim_tree = $AnimationTree
@onready var state_machine = anim_tree.get("parameters/playback")

func _process(delta):
    if velocity.length() > 0.1:
        state_machine.travel("walk")
    else:
        state_machine.travel("idle")
    
    # Blend 파라미터
    anim_tree.set("parameters/walk_speed/scale", velocity.length() / speed)
```

---

## 📷 카메라 효과

### 카메라 쉐이크 (3D)
```gdscript
extends Camera3D

@export var shake_intensity: float = 0.3

func shake(duration: float = 0.3):
    var original_pos = position
    var tween = create_tween()
    
    for i in range(int(duration / 0.05)):
        var offset = Vector3(
            randf_range(-shake_intensity, shake_intensity),
            randf_range(-shake_intensity, shake_intensity),
            0
        )
        tween.tween_property(self, "position", original_pos + offset, 0.05)
    
    tween.tween_property(self, "position", original_pos, 0.05)
```

---

## 🌍 환경 & 조명

### 주야 사이클
```gdscript
extends DirectionalLight3D

@export var day_duration: float = 120.0  # 2분

var time: float = 0.0

func _process(delta):
    time += delta / day_duration
    if time > 1.0:
        time = 0.0
    
    # 태양 회전 (0 = 정오, 0.5 = 자정)
    rotation_degrees.x = lerp(-90.0, 90.0, time)
    
    # 조명 색상 변화
    if time < 0.25:  # 아침
        light_color = Color(1.0, 0.9, 0.7)
    elif time < 0.75:  # 낮
        light_color = Color(1.0, 1.0, 1.0)
    else:  # 저녁
        light_color = Color(1.0, 0.6, 0.4)
```

---

## 🎯 크로스헤어 (UI)

### 간단한 크로스헤어
```gdscript
# crosshair.gd (Control 노드)
extends Control

func _ready():
    # 화면 중앙에 배치
    position = get_viewport_rect().size / 2
```

---

## 🚗 차량 컨트롤러

### 기본 차량 (VehicleBody3D)
```gdscript
extends VehicleBody3D

@export var max_rpm: float = 500.0
@export var max_torque: float = 200.0
@export var steering_limit: float = 0.5

func _physics_process(delta):
    # 가속/브레이크
    var throttle = Input.get_axis("brake", "accelerate")
    engine_force = throttle * max_torque
    
    # 스티어링
    var steer = Input.get_axis("steer_right", "steer_left")
    steering = steer * steering_limit
```

---

## 🎮 비행 컨트롤러

### 기본 비행
```gdscript
extends RigidBody3D

@export var thrust: float = 100.0
@export var pitch_speed: float = 2.0
@export var yaw_speed: float = 1.5
@export var roll_speed: float = 2.5

func _physics_process(delta):
    # 전진 추진력
    if Input.is_action_pressed("accelerate"):
        apply_central_force(-transform.basis.z * thrust)
    
    # Pitch (위/아래)
    var pitch = Input.get_axis("pitch_down", "pitch_up")
    apply_torque(transform.basis.x * pitch * pitch_speed)
    
    # Yaw (좌/우 회전)
    var yaw = Input.get_axis("yaw_right", "yaw_left")
    apply_torque(transform.basis.y * yaw * yaw_speed)
    
    # Roll (좌/우 기울기)
    var roll = Input.get_axis("roll_right", "roll_left")
    apply_torque(transform.basis.z * roll * roll_speed)
```

---

## 🗺️ 미니맵

### 톱다운 미니맵
```gdscript
# MinimapCamera (Camera3D)
extends Camera3D

@export var target: Node3D
@export var height: float = 50.0

func _process(delta):
    if target:
        global_position = target.global_position + Vector3.UP * height
        rotation_degrees = Vector3(-90, 0, 0)  # 아래 보기
```

---

## 💾 3D 세이브

### 플레이어 위치 저장
```gdscript
func save_game():
    var data = {
        "position": global_position,
        "rotation": rotation,
        "health": health
    }
    SaveManager.save_game(data)

func load_game():
    var data = SaveManager.load_game()
    if data:
        global_position = data.get("position", Vector3.ZERO)
        rotation = data.get("rotation", Vector3.ZERO)
        health = data.get("health", 100)
```

---

## 🌊 물리 영역 (중력, 물)

### 물 영역 (Area3D)
```gdscript
extends Area3D

@export var water_drag: float = 0.5

func _ready():
    body_entered.connect(_on_body_entered)
    body_exited.connect(_on_body_exited)

func _on_body_entered(body):
    if body is RigidBody3D:
        body.linear_damp = water_drag
        body.gravity_scale = 0.1  # 부력

func _on_body_exited(body):
    if body is RigidBody3D:
        body.linear_damp = 0.0
        body.gravity_scale = 1.0
```

---

## 🎯 레이저 포인터

### 레이저 비주얼
```gdscript
extends Node3D

@onready var raycast = $RayCast3D
@onready var line = $Line3D  # MeshInstance3D with CylinderMesh

func _process(delta):
    raycast.force_raycast_update()
    
    if raycast.is_colliding():
        var hit_point = raycast.get_collision_point()
        var distance = global_position.distance_to(hit_point)
        
        # 레이저 길이 조정
        line.scale.y = distance / 2
        line.position.z = -distance / 2
```

---

## 🚀 로켓/미사일

### 유도 미사일
```gdscript
extends RigidBody3D

@export var thrust: float = 50.0
@export var turn_speed: float = 2.0
var target: Node3D

func _physics_process(delta):
    if target:
        var direction = (target.global_position - global_position).normalized()
        
        # 목표 방향으로 회전
        var target_basis = Basis.looking_at(direction, Vector3.UP)
        var current_basis = global_transform.basis
        global_transform.basis = current_basis.slerp(target_basis, turn_speed * delta)
        
        # 전진 추진
        apply_central_force(-transform.basis.z * thrust)
```

---

## 🎮 그래플링 훅

### 그래플 (RayCast)
```gdscript
extends CharacterBody3D

@export var grapple_speed: float = 20.0
var is_grappling: bool = false
var grapple_point: Vector3

@onready var raycast = $Camera3D/RayCast3D

func _process(delta):
    if Input.is_action_just_pressed("grapple"):
        start_grapple()

func start_grapple():
    raycast.force_raycast_update()
    if raycast.is_colliding():
        grapple_point = raycast.get_collision_point()
        is_grappling = true

func _physics_process(delta):
    if is_grappling:
        var direction = (grapple_point - global_position).normalized()
        velocity = direction * grapple_speed
        move_and_slide()
        
        if global_position.distance_to(grapple_point) < 1.0:
            is_grappling = false
```

---

**추가 참고**: [Godot 3D 튜토리얼](https://docs.godotengine.org/en/stable/tutorials/3d/index.html)
