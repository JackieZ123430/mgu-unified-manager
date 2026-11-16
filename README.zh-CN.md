# MGU Unified Manager 中文说明

[English](README.md) · [原项目](https://github.com/nic0pane/mgu-unified-manager)

MGU Unified Manager 将 BMW MGU iDrive 7／8 的 SSH 配置工具与 MGU Store 管理入口整合到一个 Tkinter 桌面界面。原项目代码保留在 `vendors/` 中，通过适配器调用。

**简体中文汉化：小白151／小白科技杂物社（[JackieZ123430](https://github.com/JackieZ123430)）。** 原软件、SSH 工具和商店的作者、版权及许可证归各原项目所有，见 [LICENSES.md](LICENSES.md)。

## 功能

- **总览**：检查 Python、Node.js、OpenSSH 和原项目模块。
- **车辆与 SSH**：ENET 发现、VIN／网关检测、只读状态、启用／修复、刷写并启用、修复密钥、关闭 SSH。
- **MGU Store**：首次安装或修复、部署状态、备份列表、组件回退和卸载、备份恢复。
- **设置**：选择共用的 root SSH 私钥，查看原项目位置。
- **操作日志**：显示原工具输出并保留结构化轮转日志。

应用浏览、安装和更新仍在车机商店中完成。原工具返回的诊断信息保留原文，便于和上游排障说明对照。

## 运行与语言

需要 Python 3.9 或更新版本、Tkinter、Node.js 18 或更新版本以及 PATH 中的 OpenSSH 客户端。支持 Windows 10／11、macOS、Linux；Linux 可能需要安装系统的 `python3-tk` 包。

```sh
python -m pip install -r requirements.txt
python run.py
```

简体中文系统自动使用中文，其他系统使用英文。也可以在启动前指定 `MGU_UI_LANGUAGE=zh-CN` 或 `en`。Windows PowerShell：

```powershell
$env:MGU_UI_LANGUAGE = 'zh-CN'
python run.py
```

macOS／Linux：`MGU_UI_LANGUAGE=zh-CN python run.py`。语言设置在启动时决定固定界面文字，修改后请重新启动程序。Windows 还可运行 `run.bat`，macOS／Linux 可运行 `./run.sh`。

## 首次使用

1. 用 ENET 连接车辆并唤醒主机，在“车辆与 SSH”中选择正确主机类型。
2. 检测 VIN／网关，或手动填写 VIN。
3. 如果 SSH 已配置，先读取状态，并在 `vendors/idrive7-8-ssh-root/data/enrollments/<VIN>/` 找到生成的私钥。
4. 如果需要首次配置，先阅读原版 SSH 项目说明并备份编码，再明确选择相应操作。
5. 在“设置”或“MGU Store”选择私钥，然后安装／修复商店。

刷写可能清除主机编码／CAFD 和数字钥匙配对，甚至使主机无法使用。请备份编码并保证稳定供电。本工具不会自动刷写；刷写与密钥修复需要确认。电脑能连接 SSH，不代表所有车机功能已验证。

## 构建与验证

打包说明见 [PACKAGING.md](PACKAGING.md)。中文语言层是随 Python 模块一起打包的 `app/i18n.py`，不需要额外外部语言文件。

```sh
python -m unittest discover -s tests -p test_i18n.py -v
```

汉化验证在电脑上进行，不代表已完成真实车辆测试。

<!-- Localization provenance: XIAOBAI-ZHCN-20261116; translation by 小白151 / JackieZ123430. -->
