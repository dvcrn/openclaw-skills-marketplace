# OSS 上传（供 EMO/AA 使用）

本地文件需要先上传 OSS，再把公网 URL 传给 DashScope。

## 环境变量
```bash
export ALIBABA_CLOUD_ACCESS_KEY_ID=xxx
export ALIBABA_CLOUD_ACCESS_KEY_SECRET=xxx
export OSS_BUCKET=your-bucket
export OSS_ENDPOINT=oss-cn-beijing.aliyuncs.com
```

## Python 示例
```python
import os
import oss2


def upload_to_oss(local_path: str, oss_key: str) -> str:
    auth = oss2.Auth(
        os.environ["ALIBABA_CLOUD_ACCESS_KEY_ID"],
        os.environ["ALIBABA_CLOUD_ACCESS_KEY_SECRET"],
    )
    bucket_name = os.environ["OSS_BUCKET"]
    endpoint = os.environ.get("OSS_ENDPOINT", "oss-cn-beijing.aliyuncs.com")
    bucket = oss2.Bucket(auth, f"https://{endpoint}", bucket_name)
    bucket.put_object_from_file(oss_key, local_path)
    return f"https://{bucket_name}.{endpoint}/{oss_key}"
```

## 注意
- URL 必须公网可访问（http/https）
- 私有 bucket 可用签名 URL，但过期时间要覆盖任务耗时
- 建议为临时素材配置 OSS 生命周期规则自动清理
