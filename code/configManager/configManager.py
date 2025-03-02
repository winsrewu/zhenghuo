import os
import sys
import argparse

class ConfigManager:
    def __init__(self, config_file):
        self.config_file = config_file
        self.configs = {}  # 存储别名和对应的配置文件路径
        self.fields = set()  # 要管理的字段
        self.load_configs()

    def load_configs(self):
        """加载主配置文件，读取所有别名和路径"""
        if not os.path.exists(self.config_file):
            return
        with open(self.config_file, 'r') as f:
            for line in f:
                alias, path = line.strip().split()
                self.configs[alias] = path

    def save_configs(self):
        """保存主配置文件"""
        with open(self.config_file, 'w') as f:
            for alias, path in self.configs.items():
                f.write(f"{alias} {path}\n")

    def add_config(self, path, alias):
        """添加一个新的配置文件"""
        if alias in self.configs:
            print(f"Error: Alias '{alias}' already exists.")
            return
        if not os.path.exists(path):
            print(f"Error: File '{path}' does not exist.")
            return
        self.configs[alias] = path
        self.save_configs()
        print(f"Added config '{alias}' at '{path}'.")

    def remove_config(self, alias):
        """删除一个配置文件"""
        if alias not in self.configs:
            print(f"Error: Alias '{alias}' does not exist.")
            return
        del self.configs[alias]
        self.save_configs()
        print(f"Removed config '{alias}'.")

    def rename_config(self, old_alias, new_alias):
        """重命名一个配置文件的别名"""
        if old_alias not in self.configs:
            print(f"Error: Alias '{old_alias}' does not exist.")
            return
        if new_alias in self.configs:
            print(f"Error: Alias '{new_alias}' already exists.")
            return
        self.configs[new_alias] = self.configs.pop(old_alias)
        self.save_configs()
        print(f"Renamed '{old_alias}' to '{new_alias}'.")

    def reload_configs(self):
        """重新加载所有配置文件"""
        self.load_configs()
        print("Reloaded all configs.")

    def add_field(self, field):
        """添加要管理的字段"""
        self.fields.add(field)
        print(f"Added field '{field}'.")

    def edit_field(self, field, alias, value):
        """编辑某个配置文件中的字段值"""
        if alias not in self.configs:
            print(f"Error: Alias '{alias}' does not exist.")
            return
        if field not in self.fields:
            print(f"Error: Field '{field}' is not being managed.")
            return
        config_path = self.configs[alias]
        if not os.path.exists(config_path):
            print(f"Error: Config file '{config_path}' does not exist.")
            return
        # 读取并更新配置文件
        updated = False
        lines = []
        with open(config_path, 'r') as f:
            for line in f:
                key, val = line.strip().split(':', 1)
                key = key.strip()
                val = val.strip()
                if key == field:
                    lines.append(f"{field}: {value}\n")
                    updated = True
                else:
                    lines.append(line)
        if not updated:
            lines.append(f"{field}: {value}\n")
        with open(config_path, 'w') as f:
            f.writelines(lines)
        print(f"Updated field '{field}' in config '{alias}' to '{value}'.")

    def list_configs(self):
        """列出所有配置文件及其字段，并标记冲突"""
        field_values = {}
        for alias, path in self.configs.items():
            if not os.path.exists(path):
                print(f"Warning: Config file '{path}' does not exist.")
                continue
            print(f"\nConfig: {alias} ({path})")
            with open(path, 'r') as f:
                for line in f:
                    key, val = line.strip().split(':', 1)
                    key = key.strip()
                    val = val.strip()
                    if key in self.fields:
                        print(f"  {key}: {val}")
                        if key not in field_values:
                            field_values[key] = {}
                        field_values[key][val] = field_values[key].get(val, []) + [alias]

        # 检查冲突
        print("\nConflicts:")
        has_conflict = False
        for field, values in field_values.items():
            for value, aliases in values.items():
                if len(aliases) > 1:
                    has_conflict = True
                    print(f"  Field '{field}' has value '{value}' in configs: {', '.join(aliases)}")
        if not has_conflict:
            print("  No conflicts found.")

def main():
    parser = argparse.ArgumentParser(description="Config Manager")
    parser.add_argument("--config", required=False, default="configManager.config", help="Path to the main config file")
    args = parser.parse_args()

    manager = ConfigManager(args.config)

    while True:
        try:
            command = input("> ").strip().split()
            if not command:
                continue
            cmd = command[0].lower()

            if cmd in ('a', 'add'):
                if len(command) != 3:
                    print("Usage: a(add) <config_file_path> <alias>")
                else:
                    manager.add_config(command[1], command[2])

            elif cmd == 'rm':
                if len(command) != 2:
                    print("Usage: rm(remove) <alias>")
                else:
                    manager.remove_config(command[1])

            elif cmd == 'rn':
                if len(command) != 3:
                    print("Usage: rn(rename) <old_alias> <new_alias>")
                else:
                    manager.rename_config(command[1], command[2])

            elif cmd == 'reload':
                manager.reload_configs()

            elif cmd == 'af':
                if len(command) != 2:
                    print("Usage: af(addfield) <field_name>")
                else:
                    manager.add_field(command[1])

            elif cmd == 'e':
                if len(command) != 4:
                    print("Usage: e(edit) <field_name> <alias> <value>")
                else:
                    manager.edit_field(command[1], command[2], command[3])

            elif cmd == 'ls':
                manager.list_configs()

            elif cmd in ('q', 'quit', 'exit'):
                print("Exiting...")
                break

            elif cmd == 'help':
                print("""
Config Manager Help:

This program helps you manage multiple configuration files and ensures that specified fields do not conflict.

Commands:
  a(add) <config_file_path> <alias>
    Add a new configuration file with the given alias.

  rm(remove) <alias>
    Remove a configuration file by its alias.

  rn(rename) <old_alias> <new_alias>
    Rename an existing alias to a new one.

  reload
    Reload all configuration files from the main config file.

  af(addfield) <field_name>
    Add a field to be managed across all configuration files.

  e(edit) <field_name> <alias> <value>
    Edit the value of a specific field in a configuration file.

  ls(list)
    List all configuration files and their managed fields. Conflicts (same field value in multiple configs) will be highlighted.

  q(quit) or exit
    Exit the program.

Example Usage:
  > a configs/server1.conf server1
  > af port
  > e port server1 8080
  > ls

Notes:
- The main config file stores aliases and paths to other config files.
- Fields added via 'af' are tracked for conflicts when using 'ls'.
- Ensure the main config file and individual config files exist before adding them.
""")

            else:
                print("Unknown command. Available commands: help, a(add), rm(remove), rn(rename), reload, af(addfield), e(edit), ls(list), q(quit)")

        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()