# InkOS-RE

InkOS-RE 是一个面向 ESP32-C3、MicroPython 和黑白墨水屏设备的轻量级插件化系统框架。它把启动流程、硬件抽象、应用生命周期、插件发现、基础 UI、系统设置、文件服务、联网对时和屏保能力组织成一个适合小型嵌入式设备运行的微型系统。

当前仓库已经按 GitHub 根目录整理，`apps/txt_reader` 文本阅读器模块未包含在本仓库中。

## 项目定位

InkOS-RE 不是完整桌面操作系统，而是一个面向低功耗墨水屏设备的 MicroPython 运行框架。它的核心目标是：

- 在 ESP32-C3 上提供稳定的启动和主循环。
- 通过 HAL 层隔离墨水屏、按键、电源和 SD 卡等硬件差异。
- 通过 `manifest.json` 和 `create_app(context)` 提供简单的应用/插件机制。
- 用统一的渲染入口管理墨水屏全刷和局刷。
- 允许用户把扩展插件放到 Flash 或 SD 卡中运行。

## 主要功能

- MicroPython 启动入口：`boot.py` 和 `main.py`
- 内核调度：`inkos/kernel.py`
- 应用生命周期：`inkos/app/base.py`
- 插件发现和加载：`inkos/services/plugin_manager.py`
- Launcher 启动器：`inkos/apps/launcher.py`
- 2.13 寸墨水屏驱动：`inkos/hal/display_epd2in13.py`
- 控制台显示回退：`inkos/hal/display_console.py`
- GPIO 输入、SD 卡、电源抽象：`inkos/hal/`
- 设置、日志、时钟、HTTP 文件服务：`inkos/services/`
- 状态栏、对话框、分页和图标工具：`inkos/ui/`
- HZK16 中文点阵字库支持：`fonts/`
- 内置系统插件：设置、文件服务、联网对时、屏保
- 示例应用：`apps/hello`

## 硬件目标

当前代码主要面向以下硬件组合：

| 项目 | 说明 |
| --- | --- |
| MCU | ESP32-C3 |
| 运行环境 | MicroPython |
| 屏幕 | 2.13 寸黑白墨水屏 |
| 逻辑画布 | `212 x 104` |
| 显示接口 | SPI |
| 外部存储 | SD 卡 |

默认墨水屏引脚：

| 信号 | GPIO |
| --- | --- |
| CS | GPIO3 |
| DC | GPIO4 |
| RST | GPIO5 |
| SCK | GPIO6 |
| MOSI | GPIO7 |
| BUSY | GPIO8 |

## 仓库结构

```text
.
├── boot.py
├── main.py
├── pymakr.conf
├── README.md
├── 插件开发指南.md
├── apps/
│   └── hello/
├── plugins/
│   ├── http_server/
│   ├── screensaver/
│   ├── settings/
│   └── time_sync/
├── inkos/
│   ├── app/
│   ├── apps/
│   ├── hal/
│   ├── services/
│   ├── ui/
│   ├── config.py
│   ├── events.py
│   └── kernel.py
├── fonts/
│   ├── HZK16
│   ├── GB2312.TBL
│   └── README.md
├── sd/
│   ├── sample.txt
│   └── 你好UTF8test.txt
└── doc/
    ├── InkOS_MicroPython_OS_Architecture.md
    ├── ESP32_GENERIC_C3-20260406-v1.28.0.bin
    ├── E-Paper_ESP32_Driver_Board_Code.7z
    └── hardware reference files
```

## 启动流程

1. 设备上电后执行 `boot.py`。
2. `boot.py` 尝试设置 CPU 频率，并创建 `/apps`、`/plugins`、`/sd`、`/sd/plugins`、`/sd/data`、`/sd/data/logs` 等目录。
3. `main.py` 创建 `inkos.kernel.Kernel`。
4. `Kernel.boot()` 初始化显示、输入、SD 卡、设置、文件服务、电源、时钟、状态栏和插件管理器。
5. `PluginManager.discover()` 扫描 `/apps`、`/plugins` 和 `/sd/plugins`。
6. 系统启动 Launcher，并加载 `autostart=true` 的插件。
7. `Kernel.run_forever()` 进入事件循环，轮询按键和 HTTP 文件服务。

## 插件机制

每个应用或插件都是一个独立目录，并包含 `manifest.json`：

```json
{
  "id": "example.hello",
  "name": "Hello",
  "version": "1.0.0",
  "entry": "main.py",
  "api": 1,
  "author": "InkOS",
  "category": "app",
  "permissions": [],
  "autostart": false,
  "min_inkos": "0.1.0"
}
```

入口文件需要提供 `create_app(context)`：

```python
from inkos.app.base import App


class HelloApp(App):
    def render(self, display):
        display.line("Hello InkOS")


def create_app(context):
    return HelloApp(context)
```

更完整的插件 API、生命周期、HTTP 路由、权限声明和示例代码见 [插件开发指南.md](./插件开发指南.md)。

## 内置应用和插件

| 目录 | ID | 类型 | 说明 |
| --- | --- | --- | --- |
| `apps/hello` | `system.hello` | 示例应用 | 最小应用示例 |
| `plugins/settings` | `system.settings` | 系统插件 | 系统设置界面 |
| `plugins/http_server` | `system.http` | 系统插件 | HTTP 文件服务开关 |
| `plugins/time_sync` | `system.time_sync` | 系统插件 | Wi-Fi 配置和 NTP 对时 |
| `plugins/screensaver` | `system.screensaver` | 系统插件 | 文本/图片屏保 |

## 字体

中文渲染依赖 GB2312 HZK16 点阵字库。设备上建议放置在：

```text
/fonts/HZK16
/sd/fonts/HZK16
```

完整 HZK16 文件约 267 KB。InkOS 渲染中文时只读取单个字符所需的 32 字节点阵数据，不会一次性加载完整字库到 RAM。

## HTTP 文件服务

`system.http` 插件可以开启设备 AP 热点和 HTTP 文件服务：

| 项目 | 默认值 |
| --- | --- |
| SSID | `InkOS-File` |
| 密码 | `12345678` |
| 端口 | `80` |

开启后可在浏览器访问设备显示的 IP 地址，管理 `/sd` 或 Flash 文件，并访问已注册的插件配置页面。

注意：文件服务包含上传、下载和删除能力，只建议在可信网络环境中启用。

## 部署到设备

推荐将以下内容上传到设备根目录或对应的 MicroPython 文件系统路径：

```text
boot.py
main.py
inkos/
apps/
plugins/
fonts/
```

如果使用 SD 卡扩展插件，可将用户插件放到：

```text
/sd/plugins/
```

运行期设置默认保存到：

```text
/sd/data/settings.json
```

## 开发和调试

- 在本地修改代码后，通过串口、WebREPL、Pymakr 或设备文件管理工具上传到 ESP32-C3。
- 如果墨水屏硬件驱动导入失败，系统会尝试回退到 `ConsoleDisplay`，便于观察启动流程。
- 插件加载失败时，优先检查 `manifest.json`、`entry` 路径和 `create_app(context)`。
- 耗时操作不应放在 `render()` 或模块 import 阶段执行。
- 墨水屏刷新应由内核统一触发，插件不要直接调用 `display.show()`。

## 当前状态

该项目仍处于早期整理和反向工程验证阶段。核心框架已经具备可运行结构，但公开使用前建议继续完成：

- 在目标 ESP32-C3 硬件上完整启动测试。
- 验证 2.13 寸墨水屏全刷、局刷和休眠唤醒。
- 验证 SD 卡挂载、字体读取和 HTTP 文件上传。
- 清理历史源文件中可能存在的中文编码显示问题。
- 为插件 API 增加更严格的版本兼容和 manifest 校验。
- 增加许可证文件，例如 MIT、Apache-2.0 或 GPL。

## 参考资料

- [插件开发指南.md](./插件开发指南.md)
- [字体说明](./fonts/README.md)
- [系统架构设计文档](./doc/InkOS_MicroPython_OS_Architecture.md)

