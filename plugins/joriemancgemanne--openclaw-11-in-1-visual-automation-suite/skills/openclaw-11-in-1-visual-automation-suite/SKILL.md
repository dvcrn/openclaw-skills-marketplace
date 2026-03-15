---
name: openclaw-11-in-1-visual-automation-suite
description: "OpenClaw 11-in-1 Visual Automation Suite (Windows Only) Complete visual automation toolkit with 11 integrated modules.  ### 💰 Price One-time purchase: **$2.99** (Lifetime access to all modules + future updates)  ### 🚀 How to Purchase 1.  Pay via PayPal Invoice:     🔗 [Click to pay $2.99](https://www.paypal.com/invoice/p/#V2RC9S8LVKJ434R9) 2.  After payment, send your email to: **1215066513@qq.com** 3.  I will send the full download link within 12 hours.  ### 🖥️ Compatibility - Windows 10 / 11 only - Not compatible with macOS / Linux ## 1. Product Basic Description ### 1.1 Core Functions Provides professional universal computer vision automation capabilities covering the full-process visual automation scenarios such as environment initialization, full-screen automatic screenshot, OCR text recognition, template matching target localization, mouse click simulation, keyboard input simulation, and complete environment initialization & cleanup mechanisms. It supports custom task combination and cyclic execution.  ### 1.2 Version & Directory Description - Core Capability: Flexible invocation based on minimum executable units, supporting parameter customization, result variable inheritance, and custom skill saving. All functions can be used directly with the `call` command right after extracting the package. - Directory Structure:    - `claw.json` - Skill package configuration file   - `skills/all_skills.claw` - All skill unit definitions   - `templates/` - Directory for template images (place your template images here for matching)   - Temporary file directory `temp/` (for storing screenshots like temp/screen.png) is automatically created after executing `init_env`; temporary screenshot files can be cleaned up via `clean_temp`. - Version Info: Current version: 1.0.0; Compatible with OpenClaw >= 1.0.0  ### 1.3 Paid Attribute This automation skill system (vision-auto-tool-pro) is a paid professional toolkit. The document does not explicitly authorize commercial use of the toolkit. The paid permission only covers basic usage (non-commercial by default), and commercial use requires separate confirmation of authorization with the provider (e.g., purchasing a commercial license, signing a commercial agreement).  ## 2. Complete Skill Invocation Manual ### Important Notes Ensure sufficient time is reserved for the computer to respond to each click or operation. For example, add a 2-second wait after `mouse_click` to avoid operation failure due to slow system response.  ### 2.1 List of All Minimum Executable Units | Unit Name               | Fixed Call Name          | Function Description                                                                 | Individual Call Method                          | |-------------------------|--------------------------|--------------------------------------------------------------------------------------|-------------------------------------------------| | Initialize Environment  | `init_env`               | Create directory structure, clear temporary files, check template directory          | `call init_env`                                  | | Full Screen Screenshot  | `screenshot_full`        | Capture entire screen and save as temp/screen.png                                    | `call screenshot_full`                           | | Check Screenshot Validity | `check_screenshot_valid` | Check for black screen/freeze, wake up the interface if invalid                      | `call check_screenshot_valid`                    | | Wake Interface          | `wake_window`            | Solve the problems of background non-rendering and black screenshot                   | `call wake_window`                               | | OCR Recognition         | `ocr_recognize`          | Recognize all text on the screen and their corresponding coordinates                  | `call ocr_recognize`                             | | Template Matching       | `template_match`         | Use template image to match and locate icons/buttons                                  | `call template_match category template_name`     | | Unified Localization    | `locate_target`          | Prioritize OCR positioning; use template matching if not found, return coordinates   | `call locate_target target_text OR category+template_name` | | Mouse Click             | `mouse_click`            | Move to the specified coordinates and perform click operation                        | `call mouse_click X Y [click_type, default=single_click]` | | Keyboard Input          | `keyboard_input`         | Input text after locating the input box                                              | `call keyboard_input target_coords/description input_content` | | Clean Temporary Files   | `clean_temp`             | Delete temporary screenshots and free up storage space                               | `call clean_temp`                                | | Loop Restart            | `loop_restart`           | Wait 2 seconds then go back to the screenshot step and restart the process           | `call loop_restart`                              |  ### 2.2 Method for Invoking Individual Units #### Invocation Format ``` call [unit_call_name] [parameter...] ``` #### Invocation Examples - Initialize environment: `call init_env` - Template match browser icon on desktop: `call template_match desktop web` - Perform double-click at coordinates (100,200): `call mouse_click 100 200 double`  ### 2.3 Combine into Custom New Tasks By writing one call instruction per line in execution order, you can combine them into a custom new task, which supports variable inheritance, looping, and permanent saving.  #### Format Example (Open Browser) ``` # Task Name: Open Browser call init_env call screenshot_full call check_screenshot_valid call locate_target browser desktop Browser call mouse_click {{resultX}} {{resultY}} double call clean_temp ```  #### Combination Steps 1. **Write task name and description first** (for easier identification later) 2. **In execution order**, write one `call unit_name parameters` instruction per line 3. Coordinates can use variables `{{resultX}}`/`{{resultY}}` to inherit the output result of the previous unit 4. If cyclic execution is required, add `call loop_restart` at the end 5. **Save custom skill**: Use `save_skill skill_name instruction_list` to save the task permanently, then call it directly with `call skill_name`  ### 2.4 Complete Main Flow Invocation Example ``` # General Main Flow: vision_auto_main call init_env call screenshot_full call check_screenshot_valid call ocr_recognize # If template matching is needed, add this line: call template_match category name call locate_target target_text call mouse_click {{X}} {{Y}} # If text input is needed, replace the above line with: call keyboard_input {{X}} {{Y}} input_content call clean_temp # Add this line if you need to loop: call loop_restart ```   ### Important Notes Ensure sufficient time is reserved for the computer to respond to each click or operation.   >  For example, add a 2-second wait after `mouse_click` to avoid operation failure due to slow system response."
---

# 通用电脑视觉自动化 Skill 体系

这是一个完整的 **基于图像识别+OCR** 的电脑自动化技能框架，包含多个可独立调用的最小执行单元，也可以自由组合成复杂的自动化任务。**本技能包是合集，可以根据需求拆分使用单个单元**。

## 目录结构
```
computer_skill/
├─ templates/ # 永久模板库（不删除）
│  ├─ desktop/ # 桌面图标模板
│  ├─ taskbar/ # 任务栏图标模板
│  ├─ system/ # 系统通用按钮模板
│  └─ wechat/ # 微信示例模板（以后可新增其他软件）
└─ temp/ # 临时截图（用完立即删除）
```

## 核心特性

- 🎯 **原子化设计**：所有功能拆分为最小可执行单元，按需组合
- 🔍 **双重定位**：OCR文字识别优先，模板匹配兜底，兼顾准确性和灵活性
- 🖱️ **全功能支持**：截图、识别、定位、点击、输入全流程支持
- ♻️ **支持循环监控**：可以设置自动循环，实现持续监控和重复任务
- 📝 **简单易扩展**：用 `call 单元名 参数` 格式即可编写新技能

## 所有最小可执行单元清单

| 单元名称 | 固定调用名 | 功能 | 单独调用方式 |
|---------|-----------|------|------------|
| 初始化环境 | `init_env` | 创建目录结构、清空 temp、检查模板目录 | `call init_env` |
| 全屏截图 | `screenshot_full` | 截取整个屏幕保存为 temp/screen.png | `call screenshot_full` |
| 检查截图有效性 | `check_screenshot_valid` | 检查是否黑屏/冻结，无效则唤醒界面 | `call check_screenshot_valid` |
| 唤醒界面 | `wake_window` | 解决后台不渲染、截图黑屏问题 | `call wake_window` |
| OCR识别 | `ocr_recognize` | 识别屏幕所有文字与对应坐标 | `call ocr_recognize` |
| 模板匹配 | `template_match` | 用模板图匹配定位图标/按钮 | `call template_match 分类 模板名称` |
| 统一定位 | `locate_target` | OCR优先，找不到再用模板匹配，返回目标坐标 | `call locate_target 目标文字 或 分类+模板名` |
| 鼠标点击 | `mouse_click` | 移动到指定坐标执行点击 | `call mouse_click X Y [点击类型，默认单击]` |
| 键盘输入 | `keyboard_input` | 定位输入框后输入文字 | `call keyboard_input 目标坐标/描述 输入内容` |
| 清理临时文件 | `clean_temp` | 删除临时截图，释放空间 | `call clean_temp` |
| 循环重启 | `loop_restart` | 等待2秒后回到截图重新开始 | `call loop_restart` |

## 使用方法

### 单独调用单元
**格式**:
```
call [单元调用名] [参数...]
```

**示例**:
- 初始化环境：`call init_env`
- 模板匹配微信图标：`call template_match desktop wechat`
- 点击坐标(100,200)双击：`call mouse_click 100 200 双击`

### 组合成新任务
按执行顺序，每行写一个调用指令，即可组合成自定义新任务：

**格式示例（打开微信）**:
```
# 任务名称：打开微信
call init_env
call screenshot_full
call check_screenshot_valid
call locate_target 微信 desktop wechat
call mouse_click {{定位结果X}} {{定位结果Y}} 双击
call clean_temp
```

**组合步骤**:
1. 先写任务名称和说明（方便后续识别）
2. 按执行顺序，每行一条 `call 单元名 参数` 指令
3. 坐标可以用变量 `{{定位结果X}}` `{{定位结果Y}}` 承接上一个单元的输出
4. 需要循环的话，最后加 `call loop_restart`
5. 保存自定义技能后，后续直接 `call 技能名称` 调用

## 完整主流程调用示例

```
# 通用主流程：vision_auto_main
call init_env
call screenshot_full
call check_screenshot_valid
call ocr_recognize
# 如果需要模板匹配，加这行：call template_match 分类 名称
call locate_target 目标文字
call mouse_click {{X}} {{Y}}
# 如果需要输入文字，替换上面一行为：call keyboard_input {{X}} {{Y}} 输入内容
call clean_temp
# 需要循环就加：call loop_restart
```

## 完整主流程说明 (`vision_auto_main`)

执行顺序（从上到下依次执行）：

1.  `init_env`                → 初始化环境（创建目录+清空temp+检查模板目录）
2.  `screenshot_full`         → 截取全屏保存为temp/screen.png
3.  `check_screenshot_valid`  → 检查截图是否有效
    ├─ 有效 → 继续下一步
    └─ 无效 → 调用 `wake_window` 后回到 step 2 重试
4.  `ocr_recognize`           → OCR识别屏幕所有文字与坐标
5.  `template_match`          → 如果需要，进行模板图匹配定位
6.  `locate_target`           → 统一定位目标（OCR优先，模板补充）
7.  分支执行：
    ├─ 需要鼠标点击 → `mouse_click`   → 点击目标坐标
    └─ 需要文字输入 → `keyboard_input` → 输入目标文字
8.  `clean_temp`              → 删除临时截图，不保留任何临时文件
9.  `loop_restart`（可选）    → 如果需要循环监控/重复任务，执行循环重启
    └─ 不需要循环 → 流程结束

## 运行规则
1. **temp目录**：只允许存在一张截图，每次运行前必须清空temp目录
2. **templates目录**：目录内的图片永久保存，不删除

## 依赖
- Python 3.x
- OpenCV (模板匹配)
- pytesseract / 其他OCR引擎
- pyautogui (鼠标键盘控制)
- PIL (图像处理)
