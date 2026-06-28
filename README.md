# InkOS-RE

InkOS-RE 是一个面向 ESP32-C3 + MicroPython + 黑白墨水屏设备的轻量级系统框架。项目目标是在资源受限的嵌入式设备上提供一个可启动、可扩展、可插件化的微型运行环境，包含应用启动器、系统设置、HTTP 文件服务、联网对时、屏保、字体渲染、按键输入、SD 卡访问和墨水屏刷新策略等基础能力。

本仓库中的 `re` 目录是整理后的 GitHub 发布目录，已排除 `apps/txt_reader` 文本阅读器模块，其余核心系统、系统插件、示例应用、字体资源和硬件参考资料均以复制方式保留。

## 项目特性

- MicroPython 启动流程：`boot.py` 负责早期目录准备，`main.py` 负责启动内核。
- 模块化内核：由 `inkos.kernel.Kernel` 统一初始化显示、输入、SD 卡、设置、日志、插件和系统服务。
- 插件化应用模型：应用和插件通过 `manifest.json` 声明元数据，并通过 `create_app(context)` 暴露入口。
- 多来源发现：支持从 `/apps`、`/plugins`、`/sd/plugins` 扫描应用或插件。
- 墨水屏显示抽象：优先使用 2.13 寸 E-Paper 驱动，无法加载硬件驱动时回退到控制台显示。
- 中文点阵字体：支持外部 GB2312 HZK16 字库，按字符读取，降低 RAM 占用。
- Web 文件服务：设备可启动 Wi-Fi AP，并通过浏览器上传、下载和管理文件。
- 系统设置：支持显示、刷新、电源、安全模式等配置项。
- 屏保扩展：支持文本屏保和 1-bit 图片屏保。
- 联网对时：通过 Wi-Fi 和 NTP 同步时间。

## 硬件目标

当前代码主要面向以下硬件组合：

- MCU：ESP32-C3
- 固件：MicroPython
- 屏幕：2.13 寸黑白墨水屏，逻辑画布 `212 x 104`
- 显示接口：SPI
- 默认墨水屏引脚：
  - CS：GPIO3
  - DC：GPIO4
  - RST：GPIO5
  - SCK：GPIO6
  - MOSI：GPIO7
  - BUSY：GPIO8
- 输入按键：由 `inkos.hal.input_gpio.InputGPIO` 管理
- 外部存储：SD 卡，用于插件、数据、日志和用户文件

## 目录结构

```text
re/
  boot.py
  main.py
  pymakr.conf
  inkos/
    app/                 # 应用基类与运行上下文
    apps/                # 系统启动器
    hal/                 # 显示、输入、电源、SD 卡等硬件抽象
    services/            # 设置、日志、插件、HTTP、文件服务、时钟等服务
    ui/                  # 状态栏、对话框、分页、图标、字体渲染
    config.py            # 默认硬件和刷新配置
    events.py            # 输入事件定义
    kernel.py            # 系统内核
  apps/
    hello/               # 示例应用
  plugins/
    http_server/         # 文件服务入口
    screensaver/         # 屏保插件
    settings/            # 系统设置
    time_sync/           # Wi-Fi / NTP 对时
  fonts/
    HZK16
    GB2312.TBL
    README.md
  sd/
    sample.txt
    你好UTF8test.txt
  doc/
    *.png
    *.zip
    *.7z
    *.bin
    InkOS_MicroPython_OS_Architecture.md
  插件开发指南.md
```

## 启动流程

1. 设备上电后执行 `boot.py`。
2. `boot.py` 尝试设置 CPU 频率，并创建 `/apps`、`/plugins`、`/sd`、`/sd/plugins`、`/sd/data`、`/sd/data/logs` 等目录。
3. `main.py` 创建 `Kernel` 实例。
4. `Kernel.boot()` 初始化日志、显示、输入、SD 卡、设置、电源、时钟、HTTP 文件服务和插件管理器。
5. `PluginManager.discover()` 扫描应用和插件清单。
6. 系统创建 Launcher，并启动 `autostart=true` 的后台插件。
7. 进入事件循环，持续轮询按键和 HTTP 文件服务。

## 应用与插件加载规则

插件管理器扫描以下目录：

```text
/apps
/plugins
/sd/plugins
```

每个应用或插件必须是一个独立目录，并包含 `manifest.json`。默认入口文件是 `main.py`。入口文件必须提供：

```python
def create_app(context):
    return MyApp(context)
```

应用实例建议继承 `inkos.app.base.App`，并按需实现生命周期方法：

```python
on_start()
on_resume()
on_pause()
on_stop()
on_event(event)
render(display)
```

详细规则见 [插件开发指南.md](./插件开发指南.md)。

## 内置应用与系统插件

| 目录 | ID | 类型 | 说明 |
| --- | --- | --- | --- |
| `apps/hello` | `system.hello` | 示例应用 | 最小应用示例 |
| `plugins/settings` | `system.settings` | 系统插件 | 系统设置界面 |
| `plugins/http_server` | `system.http` | 系统插件 | 开启或关闭文件服务 |
| `plugins/time_sync` | `system.time_sync` | 系统插件 | Wi-Fi 配置与 NTP 对时 |
| `plugins/screensaver` | `system.screensaver` | 系统插件 | 屏保渲染与网页配置 |

## 字体说明

中文渲染依赖 GB2312 HZK16 点阵字库。设备上建议放置在以下任一路径：

```text
/fonts/HZK16
/sd/fonts/HZK16
```

完整 HZK16 文件约 267 KB。InkOS 渲染中文时只读取单个字符所需的 32 字节点阵数据，不会一次性加载完整字库。

## Web 文件服务

`system.http` 插件可开启设备 AP 热点和 HTTP 文件服务：

- 默认 SSID：`InkOS-File`
- 默认密码：`12345678`
- 默认端口：`80`

开启后可在浏览器访问设备显示的 IP 地址，管理 `/sd` 或 Flash 文件，并访问已注册的插件网页配置页。

注意：文件服务提供上传、下载和删除能力，应仅在可信环境中启用。

## 本地开发与调试

在普通 CPython 环境中运行时，如果无法导入 MicroPython 的 `machine`、`network` 等模块，系统会尽量回退到控制台显示或捕获异常。这适合做部分结构验证，但硬件相关功能仍需在目标设备上测试。

推荐开发流程：

1. 在本地编辑 `re/` 目录下的代码。
2. 将 `boot.py`、`main.py`、`inkos/`、`apps/`、`plugins/`、`fonts/` 上传到设备 Flash 或 SD 卡对应路径。
3. 通过串口 REPL 查看启动日志。
4. 若插件加载失败，检查 `manifest.json`、入口文件编码、`create_app(context)` 是否存在。
5. 使用 HTTP 文件服务上传或替换 SD 卡插件。

## 配置项

主要默认配置位于 `inkos/config.py` 和 `inkos/services/settings.py`：

- `display.font_scale`
- `display.line_height`
- `display.status_bar`
- `refresh.mode`
- `refresh.partial_limit`
- `refresh.full_interval_ms`
- `power.battery_adc_pin`
- `power.divider_ratio`
- `wifi.ssid`
- `wifi.password`
- `time.ntp_host`
- `time.timezone_offset`
- `screensaver.title`
- `screensaver.subtitle`
- `screensaver.mode`

运行期设置默认保存到：

```text
/sd/data/settings.json
```

## GitHub 发布建议

建议将 `re` 目录作为仓库根目录上传，或将 `re` 内文件移动到 GitHub 仓库根目录后发布。

上传前建议补充：

- `LICENSE`：明确开源许可证，例如 MIT、Apache-2.0 或 GPL。
- 真实硬件照片或接线图：可引用 `doc/` 中已有图片。
- 已验证的 MicroPython 固件版本。
- 设备刷写和文件上传步骤截图。

## 当前状态

该项目处于早期原型和重构整理阶段。核心架构已经具备应用生命周期、插件发现、基础 UI、墨水屏显示和 Web 文件服务能力，但仍建议在公开发布前完成以下验证：

- 在目标 ESP32-C3 设备上完整启动测试。
- 验证 2.13 寸墨水屏全刷和局刷稳定性。
- 验证 SD 卡挂载、字体读取和 HTTP 文件上传。
- 修复源文件中可能存在的中文编码显示问题。
- 为插件 API 增加版本兼容策略和更严格的 manifest 校验。

