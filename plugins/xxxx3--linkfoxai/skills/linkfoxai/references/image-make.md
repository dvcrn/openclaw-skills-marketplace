# AI 作图 - 全部接口完整说明

本文档为 LinkFoxAI Skill 内置参考，涵盖开放平台 AI 作图全部能力、完整参数与注意事项。

所有接口均为 **POST**，请求体 **Content-Type: application/json**，响应体 application/json。

---

## 一、通用作图流程

1. **可选**：调用「作图素材」获取预设素材地址（模特、场景等）。
2. **可选**：本地图片需先调用「图片上传」得到可访问 URL。
3. 调用具体作图接口，得到 **任务 ID**（`data.id`）。
4. 轮询「获取作图结果」直到 `data.status` 为 3(成功) 或 4(失败)，取 `data.resultList[].url` 得到结果图。
5. 结果图为**临时地址，有效期约 8 小时**；过期后调用「刷新结果图片地址」传入**图片 ID**（`resultList[].id`，非任务 ID）获取新 URL。

**注意事项：**
- 用户图片需外网可访问、链接稳定，建议使用国内图床（阿里云 OSS、腾讯云 COS 等）。
- 作图素材地址通过「作图素材」接口获得，用作预设资源。
- 本地图片上传支持 base64 编码，无需单独传 OSS。

---

## 二、通用响应结构

所有作图创建任务接口的响应结构一致：

| 参数 | 说明 | 类型 |
|------|------|------|
| traceId | 链路 ID | string |
| code | 状态码，200 为成功 | string |
| msg | 成功/错误描述 | string |
| msgKey | 错误码，code 非 200 时存在 | string |
| data.id | 任务 ID（用于轮询结果） | number |

响应示例：
```json
{"traceId":"f6e0fe4f360f78445c2c5d52f2414dea","code":"200","msg":"成功","data":{"id":123456}}
```

---

## 三、作图素材

**路径**：`/linkfox-ai/image/v2/material/list`

**注意**：此接口可用于连通性测试，无需上传图片。

| 参数 | 说明 | 必填 | 类型 |
|------|------|------|------|
| type | 类型：1=AI换模特-预设模特，2=模特图通用-预设场景，3=AI换模特固定脸-预设模特，4=模特图通用-场景素材，5=AI穿衣姿势-上下装素材，6=AI穿衣姿势-连体衣素材，7=AI穿戴-模特素材，8=手持商品-姿势素材，9=姿势裂变素材，10=套图-排版素材 | 是 | string |
| pageNum | 页数，默认 1 | 否 | number |
| pageSize | 单页条数，默认 10 | 否 | number |

响应 data 含 list（url/name/tagList）、total、hasMore。

```json
{"type":"1"}
```

---

## 四、图片上传

### 4.1 base64 上传

**路径**：`/linkfox-ai/image/v2/uploadByBase64`

**注意**：全局 QPS 100（不分 IP 不分用户）。适用于没有图片存储服务或无法外网访问的场景。

| 参数 | 说明 | 必填 | 类型 |
|------|------|------|------|
| fileName | 文件名（带扩展名），支持 jpeg/jpg/png/webp | 是 | string |
| base64 | 图片 base64 编码，文件不超过 10MB，最长边不超过 4096 | 是 | string |

响应 data 含 viewUrl（上传后图片访问地址）。

### 4.2 生成上传地址（OSS 直传）

**路径**：`/linkfox-ai/image/v1/generateUploadUrl`

**注意**：QPS 由阿里控制，并发能力高于 base64 方式。

| 参数 | 说明 | 必填 | 类型 |
|------|------|------|------|
| fileName | 文件名（主要取后缀） | 是 | string |

响应 data 含 viewUrl（上传成功后可用地址）、policy（url/signature/policy/key/OSSAccessKeyId，用于客户端直传 OSS）。

---

## 五、获取作图结果

**路径**：`/linkfox-ai/image/v2/make/info`

**注意**：需轮询此接口直到 status 变为 3（成功）或 4（失败）。建议轮询间隔 3-5 秒。

| 参数 | 说明 | 必填 | 类型 |
|------|------|------|------|
| id | 作图任务 ID | 是 | number |
| format | 结果格式，目前仅支持 jpg | 否 | string |

响应 data：

| 字段 | 说明 | 类型 |
|------|------|------|
| id | 作图任务 ID | number |
| status | 1=排队中 2=生成中 3=成功 4=失败 | integer |
| errorCode | 错误码 | string |
| errorMsg | 错误描述 | string |
| resultList | 结果图片数组 | array |
| resultList[].id | **图片 ID**（用于刷新地址） | number |
| resultList[].status | 0=生成中 1=成功 2=失败 | integer |
| resultList[].url | 高清图临时地址（有效期 8 小时） | string |
| resultList[].width | 宽 | integer |
| resultList[].height | 高 | integer |
| resultList[].format | 格式 | string |
| resultList[].size | 大小（字节） | integer |
| resultList[].extendField | 扩展参数（如 maskUrl、requestId 等） | object |

---

## 六、刷新结果图片地址

**路径**：`/linkfox-ai/image/v2/info`

**注意**：ID 是**图片 ID**（resultList[].id），不是作图任务 ID。

| 参数 | 说明 | 必填 | 类型 |
|------|------|------|------|
| id | 图片 ID | 是 | number |
| downloadFormat | 下载格式，如 jpg、png | 否 | string |

响应 data 含 url（新的图片访问地址）。

---

## 七、AI 换模特

**路径**：`/linkfox-ai/image/v2/make/changeModel`

**注意**：与 AI 换模特 2.0 的差异——生成的模特脸部更随机，使用同一个头部图，生成的模特脸部有细微变化。

| 参数 | 说明 | 必填 | 类型 |
|------|------|------|------|
| imageUrl | 模特原图。格式：jpg/jpeg/png/webp，20M 以内，最小 385x385，最大 8192x8192 | 是 | string |
| imageSegUrl | 模特原图保留区抠图结果 | 否 | string |
| modelHeadImageUrl | 模特头部图。格式：jpg/jpeg/png/webp，5M 以内，最小 512x512，最大 2048x2048。或调用作图素材(type=1) | 是 | string |
| sceneImgUrl | 场景参考图。格式：jpg/jpeg/png/webp，10M 以内，最小 768x768，最大 4096x4096。或调用作图素材(type=2 预设场景/type=4 场景素材)。建议使用场景素材，效果稳定 | 否 | string |
| sceneStrength | 场景相似度，值越大越相似，[0,1]，默认 0.7 | 否 | string |
| modelPrompt | 模特特征参数，多选用逗号拼接 | 否 | string |
| customPrompt | 自定义描述，最多 600 字符 | 否 | string |
| customNegPrompt | 画面中不需要的元素 | 否 | string |
| genOriRes | 是否生成原分辨率图，默认 false | 否 | boolean |
| realModel | 原图是否真人模特（false 为人台），默认 true | 否 | boolean |
| outputNum | 输出张数 [1,4]，默认 1 | 否 | number |

**模特特征参数字典：**

| 类型 | 可选值 |
|------|--------|
| 表情 | 微笑、大笑 |
| 姿势 | 坐着、躺着 |
| 体型 | 肥胖、微胖、苗条 |
| 角度 | 侧身、侧脸 |
| 其他 | 背面、光头 |

---

## 八、AI 换模特-2.0

**路径**：`/linkfox-ai/image/v2/make/changeModelFixed`

**注意**：与 AI 换模特的差异——生成的模特脸部更固定，使用同一个头部图，脸部变化很小。

| 参数 | 说明 | 必填 | 类型 |
|------|------|------|------|
| imageUrl | 模特原图。格式：jpg/jpeg/png/webp，20M 以内，最小 385x385，最大 8192x8192 | 是 | string |
| imageSegUrl | 模特原图保留区抠图结果 | 否 | string |
| modelImageUrl | 模特头部图。或调用作图素材(type=3) | 是 | string |
| sceneImgUrl | 场景图。或调用作图素材(type=4) | 否 | string |
| sceneStrength | 场景相似度 [0,1]，默认 0.7 | 否 | string |
| genOriRes | 是否生成原分辨率图，默认 false | 否 | boolean |
| realModel | 原图是否真人模特，默认 true | 否 | boolean |
| outputNum | 输出张数 [1,4]，默认 1 | 否 | number |

---

## 九、模特换场景

**路径**：`/linkfox-ai/image/v2/make/modelChangeScene`

**注意**：sceneImgUrl 与 scenePrompt 二选一必填。建议使用场景素材（type=4），效果稳定。

| 参数 | 说明 | 必填 | 类型 |
|------|------|------|------|
| imageUrl | 模特原图。格式：jpg/jpeg/png/webp，20M 以内，最小 385x385，最大 8192x8192 | 是 | string |
| imageSegUrl | 模特抠图结果 | 否 | string |
| sceneImgUrl | 场景图。或作图素材(type=2/4)。与 scenePrompt 二选一 | 条件 | string |
| scenePrompt | 场景描述。与 sceneImgUrl 二选一 | 条件 | string |
| sceneStrength | 场景相似度 [0,1]，默认 0.7 | 否 | string |
| genOriRes | 是否生成原分辨率图，默认 false | 否 | boolean |
| realModel | 原图是否真人模特，默认 true | 否 | boolean |
| outputNum | 输出张数 [1,4]，默认 1 | 否 | number |

---

## 十、AI 穿衣-上下装

**路径**：`/linkfox-ai/image/v2/make/fittingRoom`

**注意**：upperOriginUrl 与 downOriginUrl 至少填一项。

| 参数 | 说明 | 必填 | 类型 |
|------|------|------|------|
| upperOriginUrl | 上衣原图。格式：jpg/jpeg/png/webp，20M 以内，最小 385x385，最大 4096x4096 | 与下衣二选一 | string |
| upperImageUrl | 上衣抠图结果 | 否 | string |
| downOriginUrl | 下装原图。同上衣格式要求 | 与上衣二选一 | string |
| downImageUrl | 下装抠图结果 | 否 | string |
| modelImageUrl | 模特姿势图。或作图素材(type=5) | 是 | string |
| modelMaskImageUrl | 模特穿戴区域图（黑白图，黑色为穿戴区域） | 否 | string |
| outputNum | 输出张数 [1,4]，默认 1 | 否 | number |

---

## 十一、AI 穿衣-连体衣

**路径**：`/linkfox-ai/image/v2/make/fittingRoomSuit`

| 参数 | 说明 | 必填 | 类型 |
|------|------|------|------|
| suitOriginUrl | 连体衣原图。格式：jpg/jpeg/png/webp，20M 以内，最小 385x385，最大 4096x4096 | 是 | string |
| suitImageUrl | 连体衣抠图结果 | 否 | string |
| modelImageUrl | 模特姿势图。或作图素材(type=6) | 是 | string |
| modelMaskImageUrl | 模特穿戴区域图（黑白图，黑色为穿戴区域） | 否 | string |
| outputNum | 输出张数 [1,4]，默认 1 | 否 | number |

---

## 十二、AI 穿戴

**路径**：`/linkfox-ai/image/v2/make/intelligentWear`

**注意**：穿戴模特原图为自定义图片时，targetMaskUrl 必填。

| 参数 | 说明 | 必填 | 类型 |
|------|------|------|------|
| imageUrl | 穿戴商品图。格式：jpg/jpeg/png/webp，尺寸 300x300~4096x4096，宽高比 0.4~2.5 | 是 | string |
| targetOriginUrl | 穿戴模特原图。自定义地址或作图素材(type=7) | 是 | string |
| targetMaskUrl | 穿戴区域图（黑白图，黑色为穿戴区域）。自定义模特图时必填 | 条件 | string |
| productCategory | 商品品类，见下表 | 否 | string |
| outputNum | 输出张数 [1,4]，默认 1 | 否 | number |

**商品品类字典：**

| 值 | 说明 |
|------|------|
| footwear | 鞋靴 |
| luggage | 箱包 |
| eyewear | 眼镜 |
| necklace | 项链 |
| hat | 帽子 |
| earring | 耳环 |
| ring | 戒指 |
| wristband | 手环手链 |
| watch | 手表 |
| headwear | 头饰 |
| belt | 皮带 |
| other | 其他 |

---

## 十三、商品替换

**路径**：`/linkfox-ai/image/v2/make/shopReplace`

| 参数 | 说明 | 必填 | 类型 |
|------|------|------|------|
| imageUrl | 商品原图。格式：jpg/jpeg/png/webp，20M 以内，最小 384x384，最大 8192x8192 | 是 | string |
| sourceImageUrl | 原图的抠图结果 | 否 | string |
| targetOriginUrl | 替换的目标原图 | 是 | string |
| targetImageUrl | 目标原图抠图结果 | 否 | string |
| denoiseStrength | 生成图变化程度，[0,1]，默认 0.5，越大变化越高 | 否 | string |
| imageOutputWidth | 输出宽度，最长边不超过 4096，最短边不低于 32 | 否 | number |
| imageOutputHeight | 输出高度，同上。不传或只传一个时与原图尺寸一致 | 否 | number |
| outputNum | 输出张数 [1,4]，默认 1 | 否 | number |

---

## 十四、场景裂变

**路径**：`/linkfox-ai/image/v2/make/sceneFission`

| 参数 | 说明 | 必填 | 类型 |
|------|------|------|------|
| imageUrl | 原图。格式：jpg/jpeg/png/webp，20M 以内，最小 385x385，最大 8192x8192 | 是 | string |
| segImageUrl | 保留区域图 | 否 | string |
| strength | 相似度 [0.1,1]，默认 0.5，越大越相似，浮点数小数点后一位 | 否 | string |
| prompt | 强化内容描述，不传则自动提取，最长 600 字符 | 否 | string |
| imageOutputWidth | 输出宽度，最长不超过 2048，最短不低于 32 | 否 | number |
| imageOutputHeight | 输出高度，同上。不传时最长边固定 1024，最短边按原图比例调整 | 否 | number |
| provider | 模式：SCENE_FISSION_REALISTIC=写实（默认），SCENE_FISSION_SIMPLE=简约，SCENE_FISSION_INTELLIGENT=智能 | 否 | string |
| outputNum | 输出张数 [1,4]，默认 1 | 否 | number |

---

## 十五、场景图生成（AI 绘图）

**路径**：`/linkfox-ai/image/v2/make/aiDraw`

| 参数 | 说明 | 必填 | 类型 |
|------|------|------|------|
| prompt | 生图描述 | 是 | string |
| imageUrl | 参考图 | 否 | string |
| style | 生图风格，可选：场景素材/人物素材/古韵国风/传神素描/赛博朋克/像素插画/静谧水墨/动漫线稿/新海诚/宫崎骏/CG/黑白插画/复古日漫/Q版人物/写实油画/C4D剪纸/灵韵水彩/清新日漫 | 否 | string |
| scale | 宽高比，默认 1:1，可选 1:1/16:9/9:16 | 否 | string |
| outputNum | 输出张数 [1,4]，默认 4 | 否 | number |

---

## 十六、相似图裂变

**路径**：`/linkfox-ai/image/v2/make/imageToImage`

**注意**：自定义尺寸（width+height）与 scale 二选一。宽高只传一个时取原图对应值。

| 参数 | 说明 | 必填 | 类型 |
|------|------|------|------|
| imageUrl | 参考图。格式：jpg/png/webp，10M 以内，最大 4096x4096 | 是 | string |
| prompt | 生图描述，不填则自动提取，最多 600 字符 | 否 | string |
| weight | 相似度 [0,2]，默认 2 | 否 | integer |
| width | 自定义宽度，最小 384，最大 4096 | 否 | integer |
| height | 自定义高度，最小 384，最大 4096 | 否 | integer |
| scale | 宽高比字符串（如 16:9），与自定义尺寸二选一 | 否 | string |
| outputNum | 输出张数 [1,4]，默认 4 | 否 | number |

---

## 十七、自动抠图

**路径**：`/linkfox-ai/image/v2/make/cutout`

**注意**：clothClass 仅在 subType=9（服饰）时生效，可多选以逗号分割，多选会合并抠图结果。

| 参数 | 说明 | 必填 | 类型 |
|------|------|------|------|
| imageUrl | 原图。格式：jpg/jpeg/png/webp，20M 以内，最小 385x385，最大 8192x8192 | 是 | string |
| subType | 抠图类型：1=通用，2=人像，3=商品，9=服饰，12=头发，13=人脸 | 是 | integer |
| clothClass | 服饰抠图分类（subType=9 时生效），可多选逗号分割：tops/coat/skirt/pants/bag/shoes/hat | 否 | string |

---

## 十八、精细抠图-创建任务

**路径**：`/linkfox-ai/v2/process/result/interactCutout/create`

**注意**：pointList 中 x/y 为归一化坐标（0~1），isSelect 1=选中 0=不选中。

| 参数 | 说明 | 必填 | 类型 |
|------|------|------|------|
| imageUrl | 原图 | 是 | string |
| scoreUrl | 概率图（迭代时传入上一次返回的 scoreUrl） | 否 | string |
| featureUrl | 全局分割图（同上） | 否 | string |
| pointList | 点位操作列表 | 是 | array |
| pointList[].x | 与左边缘距离 / 图片宽度，0~1 | 是 | number |
| pointList[].y | 与上边缘距离 / 图片高度，0~1 | 是 | number |
| pointList[].isSelect | 0=不选中，1=选中 | 是 | integer |

---

## 十九、精细抠图-获取结果

**路径**：`/linkfox-ai/v2/process/result/interactCutout/info`

**注意**：status 1=已创建 2=执行中 3=成功 4=失败。

| 参数 | 说明 | 必填 | 类型 |
|------|------|------|------|
| id | 精细抠图任务 ID | 是 | string |

响应 data：id、status、result（maskUrl/scoreUrl/imageUrl/featureUrl）。

---

## 二十、图片高清放大

**路径**：`/linkfox-ai/image/v2/make/superResolution`

**注意**：放大后结果图最长边最大 8192。例如 3000x3000 放大 4 倍 → 8192x8192。

| 参数 | 说明 | 必填 | 类型 |
|------|------|------|------|
| imageUrl | 原图。格式：jpg/jpeg/png/webp，最大 4096x4096 | 是 | string |
| magnification | 放大倍数 [1,4]（浮点数），只高清不放大传 1 | 是 | float |
| enhanceQuality | 是否高清化 | 否 | boolean |

---

## 二十一、智能扩图

**路径**：`/linkfox-ai/image/v2/make/expandImage`

**注意**：原图尺寸 300x300~4096x4096，宽高比 0.4~2.5。

| 参数 | 说明 | 必填 | 类型 |
|------|------|------|------|
| imageUrl | 原图。格式：jpg/jpeg/png/webp | 是 | string |
| width | 期望扩图后宽度 | 是 | number |
| height | 期望扩图后高度 | 是 | number |
| prompt | 提示词，最多 600 字符 | 否 | string |
| outputNum | 输出张数 [1,4]，默认 1 | 否 | number |

---

## 二十二、图片翻译

**路径**：`/linkfox-ai/image/v3/make/imageTransl`

**注意**：原图最大 3000x3000，4M 以内。

| 参数 | 说明 | 必填 | 类型 |
|------|------|------|------|
| imageUrl | 原图。格式：jpg/jpeg/png/webp，4M 以内，最小 385x385，最大 3000x3000 | 是 | string |
| translationPlatform | 翻译源：deepl / chatgpt | 是 | string |
| sourceLanguage | 源语种代码 | 是 | string |
| targetLanguage | 目标语种代码 | 是 | string |

**源语种代码：** CHS(中文)、ENG(英文)、CHT(繁体中文)、ESP(西班牙语)、JPN(日语)、KOR(韩语)、PT(葡萄牙语)、ROM(罗马尼亚语)、RUS(俄语)、VIN(越南语)、DEU(德语)

**目标语种代码：** AR(阿拉伯语)、BG(保加利亚语)、BN(孟加拉语)、CHS(中文)、CHT(繁体中文)、CKB(中库尔德语)、CSY(捷克语)、DA(丹麦语)、DEU(德语)、EL(希腊语)、ENG(英语)、ESP(西班牙语)、ET(爱沙尼亚语)、FA(波斯语)、FI(芬兰语)、FIL(菲律宾语)、FRA(法语)、GU(古吉拉特语)、HE(希伯来语)、HI(印地语)、HR(克罗地亚语)、HUN(匈牙利语)、ID(印尼语)、ITA(意大利语)、JPN(日语)、JW(爪哇语)、KOR(韩语)、LO(老挝语)、LT(立陶宛语)、LV(拉脱维亚语)、MR(马拉地语)、MS(马来语)、MY(缅甸语)、NLD(荷兰语)、NO(挪威语)、PLK(波兰语)、PT(葡萄牙语)、PTB(葡萄牙语)、ROM(罗马尼亚语)、RUS(俄语)、SK(斯洛伐克语)、SL(斯洛文尼亚语)、SV(瑞典语)、SW(斯瓦希里语)、TA(泰米尔语)、TE(泰卢固语)、TG(塔吉克语)、TH(泰语)、TL(他加禄语)、TRK(土耳其语)、UK(乌克兰语)、UR(乌尔都语)、VIN(越南语)

---

## 二十三、手部修复

**路径**：`/linkfox-ai/image/v2/make/handRepair`

| 参数 | 说明 | 必填 | 类型 |
|------|------|------|------|
| imageUrl | 原图。格式：jpg/jpeg/png/webp，尺寸 300x300~4096x4096，宽高比 0.4~2.5 | 是 | string |
| personType | 人物类型：0=女孩，1=男孩，2=成年女性，3=成年男性 | 是 | number |
| maskUrl | 修复区域（黑白图，白色为修复区域） | 否 | string |
| outputNum | 输出张数 [1,4]，默认 1 | 否 | number |

---

## 二十四、局部重绘

**路径**：`/linkfox-ai/image/v2/make/areaRepair`

| 参数 | 说明 | 必填 | 类型 |
|------|------|------|------|
| imageUrl | 原图。格式：jpg/jpeg/png/webp，尺寸 300x300~4096x4096，宽高比 0.4~2.5 | 是 | string |
| prompt | 提示词，最多 600 字符 | 是 | string |
| maskUrl | 重绘区域图（黑白图，白色为重绘区域） | 是 | string |
| outputNum | 输出张数 [1,4]，默认 1 | 否 | number |

---

## 二十五、印花提取

**路径**：`/linkfox-ai/image/v2/make/printExtract`

| 参数 | 说明 | 必填 | 类型 |
|------|------|------|------|
| imageUrl | 原图。格式：jpg/jpeg/png/webp，20M 以内，最小 385x385，最大 8192x8192 | 是 | string |

---

## 二十六、消除笔

**路径**：`/linkfox-ai/image/v2/make/interactErase`

**注意**：原图尺寸 300x300~4096x4096，宽高比 0.4~2.5。

| 参数 | 说明 | 必填 | 类型 |
|------|------|------|------|
| imageUrl | 原图。格式：jpg/jpeg/png/webp | 是 | string |
| maskImageUrl | 消除区域图（黑白图，白色为消除区域） | 是 | string |

---

## 二十七、手持商品

**路径**：`/linkfox-ai/image/v2/make/handHeld`

**注意**：手持姿势图为自定义图片时 targetMaskUrl 必填。

| 参数 | 说明 | 必填 | 类型 |
|------|------|------|------|
| imageUrl | 手持商品图。格式：jpg/jpeg/png/webp，20M 以内，最小 385x385，最大 8192x8192 | 是 | string |
| targetOriginUrl | 手持姿势图。自定义地址或作图素材(type=8) | 是 | string |
| targetMaskUrl | 手持区域图（黑白图，尺寸与姿势图一致）。自定义姿势图时必填 | 条件 | string |
| outputNum | 输出张数 [1,4]，默认 1 | 否 | number |

---

## 二十八、饰品文字

**路径**：`/linkfox-ai/image/v2/make/linkedWord`

| 参数 | 说明 | 必填 | 类型 |
|------|------|------|------|
| fontname | 字体名称（见下方列表） | 是 | string |
| fontSize | 输出字体大小 | 是 | integer |
| left | 左边加环，默认 false | 否 | boolean |
| right | 右边加环，默认 false | 否 | boolean |
| prompt | 饰品文字内容 | 是 | string |

**可选字体：** Caitlyn、ItaliannoRob、Alison、ALSScript、WhiteAngelica、Milkshake、ScriptMTBold、PassionsConflictROB、Sacramento、Cervanttis、Notera 2 PERSONAL USE ONLY、UyghurMerdane、OldEnglishText、Halimun、AlexBrush、Scriptina、CounselorScript、EliannaBoldItalic、AutumnChant、MagnoliaScript

---

## 二十九、商品精修

**路径**：`/linkfox-ai/image/v2/make/productRepair`

| 参数 | 说明 | 必填 | 类型 |
|------|------|------|------|
| imageUrl | 商品原图。格式：jpg/jpeg/png/webp，20M 以内，最小 385x385，最大 8192x8192 | 是 | string |

---

## 三十、图片获取描述词-创建任务

**路径**：`/linkfox-ai/v2/process/result/imageToPrompt/create`

| 参数 | 说明 | 必填 | 类型 |
|------|------|------|------|
| type | 应用类型：5=相似图裂变，13=场景裂变，69=穿衣套图卖点分析，71=商品套图卖点分析 | 是 | string |
| imageUrlList | 图片地址列表（只有套图卖点分析支持多张） | 是 | List\<string\> |
| keyword | 关键字。场景裂变时有效；套图卖点分析时可传入商品信息 | 否 | string |
| provider | 套图模式提取类型：API_PRE_POINT=卖点分析（默认），API_LAYOUT_DESC=排版描述 | 否 | string |

---

## 三十一、图片获取描述词-获取结果

**路径**：`/linkfox-ai/v2/process/result/imageToPrompt/info`

**注意**：status 1=已创建 2=执行中 3=成功 4=失败。

| 参数 | 说明 | 必填 | 类型 |
|------|------|------|------|
| id | 任务 ID | 是 | string |

响应 data：id、status、result.content（描述词文本）。

---

## 三十二、智能修图

**路径**：`/linkfox-ai/image/v2/make/imageEdit`

**注意**：pro=true 时 flashV2 参数忽略。标准模式下 resolution 参数无效。

| 参数 | 说明 | 必填 | 类型 |
|------|------|------|------|
| imageUrl | 原图。格式：jpg/jpeg/png/webp，20M 以内，最小 385x385，最大 4096x4096 | 是 | string |
| prompt | 提示词，最多 2000 字符 | 是 | string |
| outputNum | 输出数量 [1,4]，默认 1 | 是 | int |
| pro | 是否高品质模式，默认 false | 否 | boolean |
| flashV2 | 是否增强模式，默认 false；pro=true 时忽略 | 否 | boolean |
| resolution | 输出分辨率：1K/2K/4K。高品质模式默认 2K，增强模式默认 1K，标准模式无效 | 否 | string |
| aspectRatio | 输出比例，如 16:9/9:16/1:1 | 否 | string |
| needOptimize | 是否需要提示词优化。传 template 时由模板决定 | 否 | boolean |
| supplyType | 供应模式：eco=经济，stable=稳定（默认） | 否 | string |
| template | 提示词模板：人台换模特/卡通插画/3D服装/服装平铺/生成场景/去除水印/白底图/改身材/文字消除/移除元素/海报制作/加人或物/添加水印/换动物/更换风格/搭配上身/精修白底图 | 否 | string |

---

## 三十三、智能修图-多图

**路径**：`/linkfox-ai/image/v2/make/multiImageFusion`

**注意**：最多支持 4 张图片。pro=true 时 flashV2 参数忽略。

| 参数 | 说明 | 必填 | 类型 |
|------|------|------|------|
| imageList | 原图列表（最多 4 张）。格式：jpg/jpeg/png/webp，20M 以内，最小 385x385，最大 4096x4096 | 是 | array |
| prompt | 强化内容描述，最多 2000 字符 | 是 | string |
| outputNum | 输出数量 [1,4]，默认 1 | 是 | int |
| pro | 是否高品质模式，默认 false | 否 | boolean |
| flashV2 | 是否增强模式，默认 false；pro=true 时忽略 | 否 | boolean |
| aspectRatio | 输出比例 | 否 | string |
| resolution | 输出分辨率：1K/2K/4K（仅 pro=true 时生效，默认 2K） | 否 | string |
| needOptimize | 是否提示词优化（有模版时不传） | 否 | boolean |
| supplyType | 供应模式：eco/stable（默认） | 否 | string |
| template | 提示词模板：搭配融图/搭配上身 | 否 | string |

---

## 三十四、商品套图

**路径**：`/linkfox-ai/image/v2/make/productMarketMaterialV2`

**注意**：
- imageList 最多 5 张，最小 800x800，最大 4096x4096，10M 以内。
- 各类型数量（aPlusNum/sellerTypeNum/sceneTypeNum 等）单项最大 8。
- aPlusStyles/pointStyles 传入时数量需等于对应图数量。
- brandKey 为 JSON 对象，总长度不超过 1000 字符。
- 结果通过获取作图结果接口轮询，resultList[].extendField.type 标识图片类型（APlusPro/APlusHasPhone/sellPoint/scene/closeUp/closeUpWhite/whiteBg）。

| 参数 | 说明 | 必填 | 类型 |
|------|------|------|------|
| imageList | 商品图片列表（最多 5 张） | 是 | array[string] |
| sellerPoint | 商品卖点描述，最多 2500 字符 | 是 | string |
| aPlusNum | 普通 A+ 数量，默认 0，最大 8 | 否 | integer |
| aPlusProNum | 高级 A+ 数量（Pro），默认 0，最大 8 | 否 | integer |
| aPlusHasPhone | 是否生成手机版 A+（基于高级 A+ 结果），默认 false | 否 | boolean |
| aPlusAspectRatio | A+ 宽高比（建议仅高级 A+ 使用），如 16:9/1:1 | 否 | string |
| aPlusStyles | A+ 排版列表，id（风格 id，通过作图素材接口获取）或 prompt（排版词，通过排版描述接口获取） | 否 | List |
| sellerTypeNum | 卖点图数量，默认 0，最大 8 | 否 | integer |
| isExtractPrePoint | 是否自动分析卖点，默认 false | 否 | boolean |
| sceneTypeNum | 场景图数量，默认 0，最大 8 | 否 | integer |
| closeUpTypeNum | 特写图数量，默认 0，最大 8 | 否 | integer |
| closeUpWhiteTypeNum | 白底特写图数量，默认 0，最大 8 | 否 | integer |
| whiteBgTypeNum | 白底图数量，默认 0，最大 8 | 否 | integer |
| pointStyles | 卖点图排版列表（同 aPlusStyles 格式） | 否 | List |
| isPro | 是否专业模式（适用于卖点图/场景图/特写图），默认 false | 否 | boolean |
| aspectRatio | 素材宽高比：1:1/3:2/2:3/4:3/3:4/4:5/5:4/16:9/9:16/21:9 | 否 | string |
| brandKey | 品牌基因 JSON：brandColor(#RRGGBB)/fontStyle/salesRegion/language/platform/customSettings | 否 | string |
| provider | 模型：GEMINI_FLASH_PRO=香蕉PRO（默认），GEMINI_31_FLASH_IMAGE=香蕉2 | 否 | string |
| resolution | 输出分辨率：2K（默认）/4K | 否 | string |

---

## 三十五、服装套图

**路径**：`/linkfox-ai/image/v2/make/wearCollection`

**注意**：
- imageList 最多 6 张，最小 384x384，最大 4096x4096，10M 以内。
- 上传标准：服装白底图（正面/背面/细节），尽量平整，可大大提升可用率。
- 支持服装搭配、鞋靴配饰、元素组合，模型智能组合。
- sellerPoint 中包含面料、卖点、目标人群、使用场景、尺码（markdown 格式）有助于更准确生成。

| 参数 | 说明 | 必填 | 类型 |
|------|------|------|------|
| imageList | 商品图片列表（最多 6 张） | 是 | array[string] |
| sellerPoint | 商品卖点描述，最多 2500 字符 | 是 | string |
| aPlusNum | 普通 A+ 数量，默认 0，最大 8 | 否 | integer |
| aPlusProNum | 高级 A+ 数量，默认 0，最大 8 | 否 | integer |
| aPlusHasPhone | 是否生成手机版 A+，默认 false | 否 | boolean |
| aPlusAspectRatio | A+ 宽高比 | 否 | string |
| aPlusStyles | A+ 排版列表（id 或 prompt） | 否 | List |
| modelTypeNum | 模特图数量，默认 0，最大 8 | 否 | integer |
| modelImageUrl | 模特参考图，未设置时启动智能模式 | 否 | string |
| sceneImageUrl | 场景参考图，未设置时启动智能模式 | 否 | string |
| isExactScene | 场景裂变模式：true=遵循背景（默认），false=相似裂变 | 否 | boolean |
| modelAndSceneInfo | 描述想要的场景内容和模特特征 | 否 | string |
| insTypeNum | 种草图数量，默认 0，最大 8 | 否 | integer |
| sellerTypeNum | 卖点图数量，默认 0，最大 8 | 否 | integer |
| isExtractPrePoint | 是否自动分析卖点，默认 false | 否 | boolean |
| pointStyles | 卖点图排版列表（同 aPlusStyles 格式） | 否 | List |
| sizeTypeNum | 尺码图数量，默认 0，最大 8 | 否 | integer |
| whiteTypeNum | 白底图数量，默认 0，最大 8 | 否 | integer |
| aspectRatio | 素材宽高比：1:1/3:2/2:3/4:3/3:4/4:5/5:4/16:9/9:16/21:9 | 否 | string |
| brandKey | 品牌基因 JSON（同商品套图） | 否 | string |
| provider | 模型：GEMINI_FLASH_PRO=香蕉PRO（默认），GEMINI_31_FLASH_IMAGE=香蕉2 | 否 | string |
| resolution | 输出分辨率：2K（默认）/4K | 否 | string |

---

## 三十六、姿势裂变

**路径**：`/linkfox-ai/image/v2/make/modelPoseFission`

**注意**：postureUrl（素材 type=9）与 prompt 二选一。

| 参数 | 说明 | 必填 | 类型 |
|------|------|------|------|
| imageUrl | 图片地址。格式：jpg/jpeg/png/webp，20M 以内，最小 385x385，最大 4096x4096 | 是 | string |
| prompt | 自定义姿势描述。与 postureUrl 二选一 | 否 | string |
| postureUrl | 姿势图片 URL。作图素材(type=9)或自定义。与 prompt 二选一 | 否 | string |
| outputNum | 输出数量 [1,4]，默认 1 | 否 | number |
