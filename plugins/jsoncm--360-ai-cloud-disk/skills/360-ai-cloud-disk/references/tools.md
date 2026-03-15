# 工具详细参数

## file-list

获取云盘指定路径下的文件和文件夹列表，支持分页查询。返回文件名、大小、创建时间、修改时间等详细信息。

### 参数

| 参数名 | 类型 | 必填 | 说明 |

|--------|------|------|------|

| `page` | number | ❌ | 页码，默认从0开始。 |

| `page_size` | number | ❌ | 每页显示的条目数，默认50条。 |

| `path` | string | ❌ | 要查询的云盘路径，默认为根目录'/' |


### 示例

```bash

python3 executor.py file-list page=1 page_size=50 path=/

```

## file-search

在云盘中根据关键词搜索文件和文件夹，支持按文件类型筛选和分页查询。返回符合条件的文件详细信息。

### 参数

| 参数名 | 类型 | 必填 | 说明 |

|--------|------|------|------|

| `file_category` | number | ❌ | 文件类型筛选：-1(全部)、0(其他)、1(图片)、2(文档)、3(音乐)、4(视频) |

| `key` | string | ❌ | 搜索关键词，当file_category 不为 -1 时，可以为空，否则必填 |

| `page` | number | ❌ | 页码，从1开始 |

| `page_size` | number | ❌ | 每页显示的条目数，默认20条，最大100条 |


### 示例

```bash

python3 executor.py file-search file_category=-1 key=value page=1 page_size=20

```

## make-dir

在云盘中创建新文件夹，支持指定路径。

### 参数

| 参数名 | 类型 | 必填 | 说明 |

|--------|------|------|------|

| `fname` | string | ✅ | 要创建的文件夹完整路径，例如：/新文件夹/ 或 /文档/子文件夹/ |


### 示例

```bash

python3 executor.py make-dir fname=value

```

## file-move

移动云盘中的文件或文件夹到指定位置。支持批量移动多个文件。

### 参数

| 参数名 | 类型 | 必填 | 说明 |

|--------|------|------|------|

| `src_name` | string | ✅ | 源文件或文件夹路径，多个文件用竖线(|)分隔，例如：/文件1.txt|/文件2.txt |

| `new_name` | string | ✅ | 目标文件夹路径，例如：/目标文件夹/ |


### 示例

```bash

python3 executor.py file-move src_name=value new_name=value

```

## file-rename

重命名云盘中的文件或文件夹。

### 参数

| 参数名 | 类型 | 必填 | 说明 |

|--------|------|------|------|

| `src_name` | string | ✅ | 原文件或文件夹的完整路径，例如：/我的知识库/111.doc 或 /我的知识库/ |

| `new_name` | string | ✅ | 新的名称（仅文件名或文件夹名，不含父路径）。文件夹名需以/结尾，例如：222.doc 或 我的知识库/ |


### 示例

```bash

python3 executor.py file-rename src_name=value new_name=value

```

## file-share

生成云盘文件的分享链接。支持批量生成多个文件的分享链接。

### 参数

| 参数名 | 类型 | 必填 | 说明 |

|--------|------|------|------|

| `paths` | string | ✅ | 要分享的文件全路径，多个文件用竖线(|)隔开，例如：/文件1.txt|/文件夹2/文件2.txt |


### 示例

```bash

python3 executor.py file-share paths=value

```

## file-save

通过URL或文本内容保存文件到云盘

### 参数

| 参数名 | 类型 | 必填 | 说明 |

|--------|------|------|------|

| `url` | string | ❌ | 文件下载地址；与 content 互斥且二选一，必须且只能传其中一个 |

| `content` | string | ❌ | 文件内容（建议为 MD 文本）；与 url 互斥且二选一，必须且只能传其中一个；需传用户指定的完整内容，不能省略任何部分 |

| `upload_path` | string | ❌ | 云盘存储路径，必须以 / 开头和结尾。如不指定，默认为 '/AI为我下载/YYYYMMDD/'（YYYYMMDD 为当天日期）。 |

| `file_name` | string | ❌ | 保存到云盘的文件名，不含路径。如不填写此参数代表自动解析。 |


### 示例

```bash

python3 executor.py file-save upload_path=/AI为我下载/20260314/

```

## file-upload-stdio

将本地文件上传到云盘指定路径。支持批量上传多个文件。

### 参数

| 参数名 | 类型 | 必填 | 说明 |

|--------|------|------|------|

| `filePaths` | array | ✅ | 本地文件路径数组，例如：['/本地/文件1.txt', '/本地/文件2.jpg'] |

| `uploadPath` | string | ❌ | 云盘上传目标路径，默认为根目录'/' |


### 示例

```bash

python3 executor.py file-upload-stdio 'filePaths=["/path/to/file.txt"]' uploadPath=/

```

## user-info

获取360AI云盘用户详细信息。

### 参数

无参数

### 示例

```bash

python3 executor.py user-info

```

## get-download-url

获取云盘中文件的下载链接。可以通过文件NID或路径获取。

### 参数

| 参数名 | 类型 | 必填 | 说明 |

|--------|------|------|------|

| `nid` | string | ❌ | 文件nid，与fpath二选一必填 |

| `fpath` | string | ❌ | 文件路径，与nid二选一必填 |


### 示例

```bash

python3 executor.py get-download-url

```
