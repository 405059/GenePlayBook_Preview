import json
import os
import config


def upload_folder(local_dir, game_name):
    for data_root, _, data_files in os.walk(local_dir):
        for file in data_files:
            local_data_path = os.path.join(data_root, file)
            oss_path = f"GenePlayStory/{config.secret_key}/{game_name}/{file}"  # 明文路径规则
            print(f"正在遍历文件:{local_data_path},上传OSS:{oss_path}")
            config.bucket.put_object_from_file(oss_path, local_data_path)


def upload(local_game_root):
    config_dict = {}
    all_dirs = []
    gid = 0
    for root, dirs, files in os.walk(local_game_root):
        for direction in dirs:
            game_data = os.path.join(local_game_root, direction)
            print(f"正在遍历目录:{game_data}")
            all_dirs.append(direction)
            gid += 1
            upload_folder(game_data, direction)
    game_str = "|".join(all_dirs)
    config_dict["game_str"] = game_str
    config_dict["game_id"] = gid
    # 创建配置文件路径
    config_path = os.path.join(local_game_root, "config.txt")
    # 写入配置文件
    with open(config_path, 'w', encoding='utf-8') as f:
        f.write(json.dumps(config_dict))  # 应该写入config_dict而不是config
    # 上传配置文件到OSS
    oss_path = f"GenePlayStory/{config.secret_key}/config.txt"
    config.bucket.put_object_from_file(oss_path, config_path)





