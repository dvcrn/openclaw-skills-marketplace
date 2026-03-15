#!/usr/bin/env python3
import os
import sys
import shutil
import argparse
import tarfile
import zipfile
import gzip
import logging
import subprocess
import importlib.util
from pathlib import Path

# ================= 配置日志 =================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [%(levelname)s] - %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

# ================= 自动依赖安装 =================
def install_and_import(package_name, import_name=None):
    """
    尝试导入库，如果失败则自动通过 pip 安装并重新导入。
    """
    if import_name is None:
        import_name = package_name
    
    if importlib.util.find_spec(import_name) is None:
        logger.warning(f"Library '{package_name}' not found. Installing automatically...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
            logger.info(f"Successfully installed '{package_name}'.")
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to install '{package_name}'. Rar/7z support may be limited. Error: {e}")
            return None
    
    try:
        module = importlib.import_module(import_name)
        return module
    except ImportError:
        logger.error(f"Failed to import '{import_name}' even after installation.")
        return None

# 尝试加载 patoolib
patoolib = install_and_import("patool")
PATOOL_AVAILABLE = patoolib is not None

# ================= 配置与常量 =================
MARKER_FILE = ".extracted_success"

# 支持的扩展名映射
# 键为后缀，值为内部处理类型
# 注意：字典序在 Python 3.7+ 是保留插入顺序的，但为了稳健，我们在使用时会显式按长度排序
SUPPORTED_EXTS = {
    # 复合后缀 (必须优先匹配)
    ".tar.gz": "tar",
    ".tar.bz2": "tar",
    ".tar.xz": "tar",
    ".tgz": "tar",
    ".tbz": "tar",
    # 单后缀
    ".zip": "zip",
    ".tar": "tar",
    ".gz": "gzip",   # 新增 gzip 支持
    ".rar": "patool",
    ".7z": "patool",
}

# ================= 核心逻辑 =================

def get_archive_type_and_stem(path: Path):
    """
    判断文件类型并获取解压后的目标目录名（Stem）。
    逻辑：按后缀长度降序匹配，确保 .tar.gz 优先于 .gz
    """
    name_lower = path.name.lower()
    # 关键：按后缀长度倒序排列，防止 .tar.gz 被 .gz 截胡
    sorted_exts = sorted(SUPPORTED_EXTS.items(), key=lambda x: len(x[0]), reverse=True)
    
    for ext, type_name in sorted_exts:
        if name_lower.endswith(ext):
            # 获取去除后缀后的文件名作为目录名
            # 例如 data.tar.gz -> data
            # 例如 file.txt.gz -> file.txt
            stem_name = path.name[:-len(ext)]
            
            # 边界情况：如果文件名就是 .tar.gz (虽然少见)，stem 为空
            if not stem_name:
                stem_name = path.name + "_extracted"
                
            return type_name, stem_name
    return None, None

def is_archive(path: Path) -> bool:
    if not path.is_file():
        return False
    typ, _ = get_archive_type_and_stem(path)
    return typ is not None

def safe_tar_extract(tar: tarfile.TarFile, path: Path):
    """兼容 Python 3.12+ 的 tarfile 安全解压"""
    if hasattr(tarfile, 'data_filter'):
        try:
            tar.extractall(path, filter='data')
        except TypeError:
            # 部分旧版本即使有属性也可能行为不一致，回退
            tar.extractall(path)
    else:
        tar.extractall(path)

def extract_gzip_file(archive_path: Path, dest_dir: Path, stem_name: Path):
    """
    处理单文件 .gz 解压
    注意：gzip 解压出来是单文件流，没有文件名信息，通常取掉 .gz 后缀作为文件名
    """
    # 目标文件路径：dest_dir/stem_name
    # 例如：archive_path = /tmp/log.txt.gz
    # dest_dir = /tmp/log.txt/ (由 extract_archive 创建)
    # stem_name = log.txt
    # 最终解压为 = /tmp/log.txt/log.txt
    target_file = dest_dir / stem_name
    
    with gzip.open(archive_path, 'rb') as f_in:
        with open(target_file, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)
    return target_file

def extract_archive(archive_path: Path, dest_parent: Path, force: bool):
    """
    执行解压动作
    :return: 解压成功的目录 Path对象，失败返回 None
    """
    archive_type, stem_name = get_archive_type_and_stem(archive_path)
    
    # 构造专属解压目录，防止文件散落
    final_out_dir = dest_parent / stem_name
    marker = final_out_dir / MARKER_FILE

    # --- 状态检查 ---
    if final_out_dir.exists():
        if not force and marker.exists():
            logger.info(f"[SKIP] Already extracted: {archive_path.name}")
            return final_out_dir
        
        if force:
            logger.info(f"[FORCE] Re-extracting: {archive_path.name}")
            try:
                shutil.rmtree(final_out_dir)
            except OSError as e:
                logger.error(f"Cannot clean directory {final_out_dir}: {e}")
                return None
        elif not marker.exists():
             logger.info(f"[RESUME] Found incomplete extraction: {archive_path.name}")

    final_out_dir.mkdir(parents=True, exist_ok=True)

    # --- 解压过程 ---
    logger.info(f"[EXTRACT] {archive_path.name} -> {final_out_dir.name}/")
    try:
        if archive_type == "zip":
            if not zipfile.is_zipfile(archive_path):
                raise ValueError("Not a valid zip file")
            with zipfile.ZipFile(archive_path, "r") as z:
                z.extractall(final_out_dir)
                
        elif archive_type == "tar":
            if not tarfile.is_tarfile(archive_path):
                raise ValueError("Not a valid tar file")
            with tarfile.open(archive_path, "r:*") as t:
                safe_tar_extract(t, final_out_dir)

        elif archive_type == "gzip":
            # 单文件 gzip 处理
            extract_gzip_file(archive_path, final_out_dir, stem_name)

        elif archive_type == "patool":
            if not PATOOL_AVAILABLE:
                logger.error(f"Skipping {archive_path}: patool not installed/loadable.")
                return None
            # Patool 通常需要外部命令(unrar, 7z)支持，这里只负责调用
            patoolib.extract_archive(str(archive_path), outdir=str(final_out_dir), verbosity=-1)
        
        else:
            logger.warning(f"Unknown type for {archive_path}")
            return None

        # --- 标记成功 ---
        marker.touch()
        return final_out_dir

    except Exception as e:
        logger.error(f"Failed to extract {archive_path.name}: {e}")
        # 失败时尝试清理半成品目录
        if final_out_dir.exists():
            shutil.rmtree(final_out_dir, ignore_errors=True)
        return None

def process_recursively(current_path: Path, force: bool, level=0):
    """
    深度优先递归处理
    """
    if level > 20: 
        logger.warning(f"Recursion depth limit reached at {current_path}")
        return

    try:
        # 获取当前目录下所有条目，排序以保证确定性
        items = sorted(list(current_path.iterdir()))
    except (PermissionError, NotADirectoryError):
        return

    for p in items:
        if p.name == MARKER_FILE:
            continue

        if p.is_dir():
            # 递归目录
            process_recursively(p, force, level)
            
        elif p.is_file() and is_archive(p):
            # 发现压缩包 -> 原地解压到同名文件夹
            # 这里的 p.parent 就是 current_path
            extracted_dir = extract_archive(p, p.parent, force)
            
            if extracted_dir:
                # 立即递归扫描新生成的目录
                process_recursively(extracted_dir, force, level + 1)

# ================= 主程序入口 =================

def main():
    parser = argparse.ArgumentParser(description="Auto Recursive Extractor with Dependency Management")
    parser.add_argument("path", help="File pattern (glob) or directory to scan")
    parser.add_argument("-f", "--force", action="store_true", help="Force re-extraction even if success marker exists")
    parser.add_argument("-d", "--dest", help="Optional output directory (default: extract alongside original)")
    
    args = parser.parse_args()
    
    # 路径解析逻辑
    import glob
    targets = []
    
    # 1. 尝试 Glob 匹配
    if any(char in args.path for char in "*?[]"):
        # recursive=True 需要 Python 3.5+
        files = glob.glob(args.path, recursive=True)
        targets = [Path(f) for f in files]
    else:
        # 2. 普通路径处理
        input_path = Path(args.path)
        if input_path.is_dir():
            # 如果是目录，将目录本身作为起始点进行递归扫描
            # 注意：process_recursively 会遍历目录内容
            targets = [input_path] 
        elif input_path.exists():
            targets = [input_path]
        else:
            logger.error(f"Path not found: {args.path}")
            sys.exit(1)

    if not targets:
        logger.warning("No targets found.")
        sys.exit(0)

    logger.info(f"Starting processing on {len(targets)} targets...")

    for target in targets:
        if target.is_file() and is_archive(target):
            # 如果目标直接是一个文件
            parent = Path(args.dest) if args.dest else target.parent
            if args.dest:
                parent.mkdir(parents=True, exist_ok=True)
                
            out_dir = extract_archive(target, parent, args.force)
            if out_dir:
                process_recursively(out_dir, args.force)
                
        elif target.is_dir():
            # 如果目标是目录，开始递归扫描
            process_recursively(target, args.force)

if __name__ == "__main__":
    main()