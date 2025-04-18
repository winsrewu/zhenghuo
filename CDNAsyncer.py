import os
import boto3
from botocore.exceptions import ClientError
import hashlib
import argparse
from collections import defaultdict

def calculate_md5(file_path, chunk_size=8*1024*1024):
    """计算文件的MD5哈希值（兼容S3/R2的大文件计算方式）"""
    md5s = []
    
    with open(file_path, 'rb') as f:
        while True:
            data = f.read(chunk_size)
            if not data:
                break
            md5s.append(hashlib.md5(data).digest())
    
    if len(md5s) == 1:
        return hashlib.md5(md5s[0]).hexdigest()
    
    # 对于多分段文件，计算分段MD5的MD5
    combined_md5 = hashlib.md5(b''.join(md5s))
    return combined_md5.hexdigest() + "-" + str(len(md5s))

def calculate_regular_md5(file_path):
    """计算文件的常规MD5哈希值"""
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def get_sync_plan(local_dir, bucket_name, s3):
    """
    获取同步计划（不实际执行操作）
    :return: 包含待上传、待更新和待删除文件的字典
    """
    # 获取R2中现有的对象列表
    remote_objects = {}
    paginator = s3.get_paginator('list_objects_v2')
    for page in paginator.paginate(Bucket=bucket_name):
        for obj in page.get('Contents', []):
            remote_objects[obj['Key']] = obj['ETag'].strip('"')

    # 遍历本地目录
    local_files = {}
    for root, _, files in os.walk(local_dir):
        for file in files:
            local_path = os.path.join(root, file)
            relative_path = os.path.relpath(local_path, local_dir)
            s3_key = relative_path.replace(os.sep, '/')
            
            # 获取文件大小决定使用哪种MD5计算方式
            file_size = os.path.getsize(local_path)
            if file_size > 8 * 1024 * 1024:  # 大于8MB使用S3兼容方式
                file_md5 = calculate_md5(local_path)
            else:
                file_md5 = calculate_regular_md5(local_path)
            
            local_files[s3_key] = file_md5

    # 分析差异
    sync_plan = defaultdict(list)
    
    # 需要上传的新文件
    for s3_key in set(local_files.keys()) - set(remote_objects.keys()):
        sync_plan['upload'].append(s3_key)
    
    # 需要更新的文件（MD5不同）
    for s3_key in set(local_files.keys()) & set(remote_objects.keys()):
        if remote_objects[s3_key] != local_files[s3_key]:
            sync_plan['update'].append(s3_key)
    
    # 需要删除的文件
    for s3_key in set(remote_objects.keys()) - set(local_files.keys()):
        sync_plan['delete'].append(s3_key)
    
    return sync_plan

def display_sync_plan(sync_plan):
    """显示同步计划"""
    print("\n=== 同步计划 ===")
    if sync_plan['upload']:
        print("\n以下文件将被上传:")
        for file in sync_plan['upload']:
            print(f"+ {file}")
    
    if sync_plan['update']:
        print("\n以下文件将被更新:")
        for file in sync_plan['update']:
            print(f"* {file}")
    
    if sync_plan['delete']:
        print("\n以下文件将被删除:")
        for file in sync_plan['delete']:
            print(f"- {file}")
    
    total_operations = sum(len(v) for v in sync_plan.values())
    print(f"\n总计: {total_operations} 项操作")

def get_content_type(file_path):
    """获取文件内容类型"""
    content_type = 'application/octet-stream'
    if file_path.endswith('.html'):
        content_type = 'text/html'
    elif file_path.endswith('.css'):
        content_type = 'text/css'
    elif file_path.endswith('.js'):
        content_type = 'application/javascript'
    elif file_path.endswith('.png'):
        content_type = 'image/png'
    elif file_path.endswith('.jpg'):
        content_type = 'image/jpeg'
    return content_type

def execute_sync(sync_plan, local_dir, bucket_name, s3):
    """执行同步操作"""
    print("\n开始执行同步...")
    
    # 上传新文件
    for s3_key in sync_plan['upload']:
        local_path = os.path.join(local_dir, s3_key.replace('/', os.sep))
        print(f"上传: {s3_key}")
        try:
            s3.upload_file(
                local_path,
                bucket_name,
                s3_key,
                ExtraArgs={'ContentType': get_content_type(local_path)}
            )
        except Exception as e:
            print(f"上传 {s3_key} 失败: {e}")
    
    # 更新文件
    for s3_key in sync_plan['update']:
        local_path = os.path.join(local_dir, s3_key.replace('/', os.sep))
        print(f"更新: {s3_key}")
        try:
            s3.upload_file(
                local_path,
                bucket_name,
                s3_key,
                ExtraArgs={'ContentType': get_content_type(local_path)}
            )
        except Exception as e:
            print(f"更新 {s3_key} 失败: {e}")
    
    # 删除文件
    for s3_key in sync_plan['delete']:
        print(f"删除: {s3_key}")
        try:
            s3.delete_object(Bucket=bucket_name, Key=s3_key)
        except Exception as e:
            print(f"删除 {s3_key} 失败: {e}")
    
    print("\n同步完成!")

def confirm_action(prompt="是否继续? (y/n): "):
    """获取用户确认"""
    while True:
        answer = input(prompt).lower()
        if answer in ['y', 'yes']:
            return True
        elif answer in ['n', 'no']:
            return False
        else:
            print("请输入 y(是) 或 n(否)")

def sync_directory_to_r2(local_dir, bucket_name, endpoint_url, access_key_id, secret_access_key, all_files):
    """
    同步本地目录到Cloudflare R2存储（带确认）
    """
    # 初始化S3客户端
    s3 = boto3.client(
        's3',
        endpoint_url=endpoint_url,
        aws_access_key_id=access_key_id,
        aws_secret_access_key=secret_access_key
    )

    try:
        # 验证存储桶是否存在
        s3.head_bucket(Bucket=bucket_name)
    except ClientError as e:
        if e.response['Error']['Code'] == '404':
            print(f"存储桶 {bucket_name} 不存在，请先创建")
            return
        else:
            print(f"访问存储桶时出错: {e}")
            return

    sync_plan = {}

    if all_files:
        # 同步所有文件
        sync_plan = {'upload': [], 'update': [], 'delete': []}
        for root, _, files in os.walk(local_dir):
            for file in files:
                local_path = os.path.join(root, file)
                relative_path = os.path.relpath(local_path, local_dir)
                s3_key = relative_path.replace(os.sep, '/')
                sync_plan['upload'].append(s3_key)
    else:
        # 获取同步计划
        sync_plan = get_sync_plan(local_dir, bucket_name, s3)
    
    # 显示计划
    display_sync_plan(sync_plan)
    
    # 如果没有需要同步的内容
    if not any(sync_plan.values()):
        print("\n没有需要同步的内容，本地和远程已同步!")
        return
    
    # 获取用户确认
    if not confirm_action("\n是否确认执行上述更改? (y/n): "):
        print("同步已取消")
        return
    
    # 执行同步
    execute_sync(sync_plan, local_dir, bucket_name, s3)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='同步本地目录到Cloudflare R2存储')
    parser.add_argument('--local-dir', help='本地目录路径')
    parser.add_argument('--bucket', help='R2存储桶名称')
    parser.add_argument('--endpoint', help='R2 S3 API端点URL')
    parser.add_argument('--access-key', help='R2访问密钥ID')
    parser.add_argument('--secret-key', help='R2秘密访问密钥')
    parser.add_argument('--all', help='同步所有文件', default=False, action='store_true')

    args = parser.parse_args()

    sync_directory_to_r2(
        args.local_dir,
        args.bucket,
        args.endpoint,
        args.access_key,
        args.secret_key,
        args.all
    )