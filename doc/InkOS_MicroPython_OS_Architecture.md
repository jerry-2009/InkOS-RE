# InkOS MicroPython 微型操作系统框架架构设计

## 1. 目标与边界

InkOS 的目标是在 ESP32-C3 + MicroPython 上提供一个高度模块化的微型操作系统框架，面向低功耗墨水屏设备。系统内核负责硬件抽象、事件循环、UI 渲染、应用生命周期和插件加载；用户可将 `.py` 插件放入 SD 卡，由系统发现、运行和卸载。

本设计以当前项目已有硬件与代码为基线：

- MCU：ESP32-C3。
- 屏幕：2.13 寸黑白墨水屏，物理分辨率 104x212，当前画布逻辑分辨率 212x104。
- 显示接口：SPI，现有引脚为 CS GPIO3、DC GPIO4、RST GPIO5、SCK GPIO6、MOSI GPIO7、BUSY GPIO8。
- 显示能力：全局刷新、局部刷新、睡眠。
- 运行环境：MicroPython 固件。
- 外部存储：SD 卡，用于插件、资源、用户数据和日志。

设计重点不是把 MicroPython 伪装成完整桌面 OS，而是在资源受限设备上提供稳定的运行时框架。内核 API 应保持小而清晰，插件能力通过显式服务对象获得，避免插件直接散乱访问硬件。

## 2. 总体架构

系统分为六层：

```text
+--------------------------------------------------------------+
| 用户插件层 plugins/*.py                                      |
| ClockApp, ReaderApp, SettingsApp, 用户自定义插件             |
+--------------------------------------------------------------+
| 应用框架层 inkos.app                                         |
| 插件生命周期、页面栈、命令、菜单、应用间消息                 |
+--------------------------------------------------------------+
| UI 与渲染层 inkos.ui / inkos.render                          |
| Widget 树、布局、脏区、Canvas、字体、主题、刷新策略          |
+--------------------------------------------------------------+
| 系统服务层 inkos.services                                    |
| FS、配置、事件、定时器、日志、电源、时间、网络、存储         |
+--------------------------------------------------------------+
| 硬件抽象层 inkos.hal                                         |
| EPD、按键、SD、RTC、Wi-Fi、SPI、I2C、电池/电源管理           |
+--------------------------------------------------------------+
| MicroPython + ESP32-C3                                       |
+--------------------------------------------------------------+
```

核心原则：

- 内核最小化：`boot.py` 和 `main.py` 只完成挂载、初始化和进入调度循环。
- 驱动可替换：屏幕、按键、SD、网络都通过 HAL 接口暴露。
- UI 与设备解耦：UI 层只面向 `Canvas` 与 `DisplayDriver` 协议，不依赖具体墨水屏驱动。
- 插件受控运行：插件必须声明 manifest，必须通过系统传入的 `context` 使用服务。
- 刷新策略集中管理：插件不能随意直接刷新屏幕，所有刷新请求进入 render scheduler 合并。
- SD 卡优先可扩展：系统只内置基础应用，用户插件与资源放在 SD 卡。

## 3. 推荐目录结构

设备内部 Flash：

```text
/
  boot.py
  main.py
  inkos/
    __init__.py
    kernel.py
    config.py
    errors.py
    hal/
      display_epd2in13.py
      input_gpio.py
      sdcard.py
      power.py
      rtc.py
      wifi.py
    services/
      event_bus.py
      timer.py
      fs.py
      settings.py
      logger.py
      plugin_manager.py
      resource.py
      clock.py
    ui/
      canvas.py
      widget.py
      layout.py
      controls.py
      screen.py
      theme.py
      font.py
    render/
      renderer.py
      dirty_region.py
      refresh_policy.py
    app/
      base.py
      context.py
      router.py
      menu.py
```

SD 卡：

```text
/sd/
  plugins/
    clock/
      manifest.json
      main.py
      assets/
    notes/
      manifest.json
      main.py
      assets/
  data/
    settings.json
    plugin_state/
    logs/
  cache/
    render/
```

Flash 保存稳定内核，SD 卡保存可变内容。这样用户更新插件时不需要重新刷写固件，也降低错误插件破坏启动流程的概率。

## 4. 启动流程

### 4.1 `boot.py`

`boot.py` 只做必须的早期初始化：

1. 设置 CPU 频率和基础异常输出。
2. 初始化串口日志。
3. 尝试挂载 SD 卡到 `/sd`。
4. 建立必要目录：`/sd/plugins`、`/sd/data`、`/sd/data/logs`。
5. 读取安全启动标记。如果上次启动在插件加载阶段崩溃，则进入 safe mode。
6. 交给 `main.py`。

### 4.2 `main.py`

`main.py` 构造内核并进入主循环：

```python
from inkos.kernel import Kernel

kernel = Kernel()
kernel.boot()
kernel.run_forever()
```

`Kernel.boot()` 的建议顺序：

1. 初始化 HAL：屏幕、输入、RTC、电源、SD、可选 Wi-Fi。
2. 初始化系统服务：日志、设置、事件总线、定时器、资源管理。
3. 初始化 UI 和渲染器。
4. 加载内置应用，例如 Launcher、Settings、SafeMode。
5. 扫描 SD 卡插件并注册到 PluginManager。
6. 显示启动页或直接进入 Launcher。

### 4.3 Safe Mode

Safe Mode 用于处理插件导致的启动失败：

- 插件加载前写入 `/sd/data/boot_state.json`，状态为 `loading_plugins`。
- 插件加载完成后改为 `ok`。
- 如果下次启动发现状态仍是 `loading_plugins`，跳过所有第三方插件，只启动系统设置。
- Safe Mode 页面提供查看日志、禁用插件、清理缓存、重启设备等操作。

## 5. 内核与事件循环

MicroPython 在 ESP32-C3 上资源有限，不建议为每个插件创建复杂并发模型。InkOS 使用单线程协作式事件循环，必要时结合 `uasyncio`，但内核 API 不强制插件直接依赖 `uasyncio`。

### 5.1 核心循环

```text
while running:
  read_input_events()
  poll_timers()
  dispatch_events()
  run_pending_plugin_tasks()
  layout_if_needed()
  render_dirty_regions()
  apply_refresh_policy()
  enter_idle_or_light_sleep()
```

事件类型：

- `InputEvent`：按键短按、长按、双击、旋钮、触摸等。
- `TimerEvent`：一次性定时器、周期定时器。
- `SystemEvent`：SD 卡插拔、电量变化、网络状态、时间同步完成。
- `AppEvent`：应用启动、暂停、恢复、退出、命令执行。
- `RenderEvent`：UI 失效、脏区提交、全刷请求。

### 5.2 调度原则

- 事件处理函数必须快速返回。
- 插件执行耗时任务时应使用生成器或异步任务分片。
- 内核维护 watchdog 计数，单次插件回调超过阈值时记录警告。
- 屏幕刷新由渲染器统一节流，避免多个插件连续触发墨水屏刷新。

### 5.3 推荐接口

```python
class Kernel:
    def boot(self): ...
    def run_forever(self): ...
    def post_event(self, event): ...
    def call_later(self, ms, callback, *args): ...
    def request_render(self, region=None, reason="ui"): ...
    def shutdown(self): ...
```

## 6. 硬件抽象层

### 6.1 DisplayDriver

屏幕驱动封装现有 `EPD2in13V2` 能力，向上暴露统一接口：

```python
class DisplayDriver:
    width = 212
    height = 104

    def init(self): ...
    def clear(self, color=1): ...
    def full_refresh(self, buffer): ...
    def partial_refresh(self, buffer, region=None): ...
    def sleep(self): ...
    def wake(self): ...
    def busy(self): ...
```

底层仍使用物理缓冲区 104x212，并在 `Canvas` 中完成旋转和镜像。当前项目已有的 `MonoCanvas(212, 104, rotate=270, mirror_vertical=True)` 可以作为第一版实现基础。

### 6.2 InputDriver

建议至少支持三个输入动作：

- `BACK`
- `SELECT`
- `NEXT`

如果硬件只有一个按键，可以映射为：

- 短按：`SELECT`
- 长按：`BACK`
- 双击：`NEXT`

输入驱动应处理消抖、长按阈值、重复触发，向事件总线发布语义事件，而不是暴露 GPIO 抖动细节。

### 6.3 SDCardDriver

职责：

- 挂载 `/sd`。
- 检查目录完整性。
- 提供只读/读写状态。
- 在异常时降级到无 SD 模式。

SPI SD 卡与墨水屏共用 SPI 时，需要 HAL 统一管理片选和总线频率。建议抽象 `SpiBusManager`，每次设备访问前切换目标设备配置。

### 6.4 PowerDriver

电源管理包含：

- 墨水屏空闲后 sleep。
- Wi-Fi 用完即关闭。
- 无事件时 light sleep。
- 插件可请求短期保持唤醒，但必须带超时时间。
- 低电量事件触发只读模式或禁止 Wi-Fi。

## 7. UI 库设计

UI 库面向黑白低刷新屏，不追求动画，重点是稳定布局、少刷新和可读性。

### 7.1 UI 对象模型

```text
Screen
  RootWidget
    Header
    Content
    Footer / StatusBar
```

基础类：

```python
class Widget:
    def measure(self, constraints): ...
    def layout(self, rect): ...
    def draw(self, canvas): ...
    def handle_event(self, event): ...
    def invalidate(self, region=None): ...
```

推荐控件：

- `Label`：单行/多行文本。
- `Button`：可聚焦命令。
- `ListView`：插件列表、菜单、文件列表。
- `MenuBar`：软键菜单。
- `StatusBar`：时间、电量、SD 状态。
- `Dialog`：确认、错误、输入提示。
- `ProgressBar`：加载或同步进度。
- `TextView`：阅读文本或日志。
- `Icon`：小尺寸位图图标。

### 7.2 布局系统

为降低实现复杂度，第一版建议只提供以下布局：

- `BoxLayout`：垂直或水平排列。
- `StackLayout`：覆盖层，用于对话框。
- `ListLayout`：固定行高列表。
- `AbsoluteLayout`：底层系统页面可用，不建议普通插件依赖。

约束模型：

```python
class Constraints:
    min_w: int
    max_w: int
    min_h: int
    max_h: int

class Rect:
    x: int
    y: int
    w: int
    h: int
```

2.13 寸屏幕空间有限，推荐系统标准区域：

```text
212x104 logical screen

0,0   +--------------------------------+
      | status/header: 212x14          |
0,14  +--------------------------------+
      | content: 212x76                |
0,90  +--------------------------------+
      | footer/actions: 212x14         |
      +--------------------------------+
```

### 7.3 主题

黑白屏主题不应复杂化。建议定义：

```python
class Theme:
    bg = WHITE
    fg = BLACK
    border = BLACK
    disabled = BLACK
    focus_bg = BLACK
    focus_fg = WHITE
    padding = 2
    line_height = 12
```

所有控件通过主题获得颜色、间距、边框和焦点样式，插件不直接硬编码大量像素值。必要时允许插件使用 `canvas` 自绘。

### 7.4 字体与文本

第一阶段：

- 内置 5x7 数字字体，用于时间。
- 内置 8x8 ASCII 字体，用于英文和基础符号。
- 可选支持外部 bitmap 字体文件，例如 `/sd/fonts/*.bin`。

第二阶段：

- 增加中文点阵字体，建议按常用字子集拆包加载，避免一次性占用过多 Flash/RAM。
- 文本渲染服务提供缓存，避免重复解码字模。

## 8. 渲染框架

### 8.1 双层职责

- `Canvas`：像素、线、矩形、文本、位图等绘图原语。
- `Renderer`：遍历 UI 树、计算脏区、决定全刷/局刷。

插件不直接调用 `epd.display_part()`。插件只调用 `widget.invalidate()` 或 `context.request_render()`。

### 8.2 脏区管理

墨水屏局部刷新并不等于任意小区域都可靠，第一版可采用“逻辑脏区、整帧提交”的折中策略：

1. UI 控件标记脏区。
2. Renderer 合并脏区。
3. Canvas 仍生成完整 framebuffer。
4. RefreshPolicy 根据脏区面积和刷新次数决定局刷或全刷。

策略示例：

```python
class RefreshPolicy:
    partial_limit = 30
    full_refresh_interval_ms = 60000
    max_dirty_ratio_for_partial = 0.40

    def choose(self, dirty_regions, partial_count, elapsed_ms):
        ...
```

建议规则：

- 启动、页面切换、对话框关闭：全刷。
- 时间、电量、列表焦点移动：局刷。
- 连续局刷达到 30 次：强制全刷。
- 脏区面积超过屏幕 40%：全刷。
- 距离上次全刷超过 60 秒：全刷。

当前 demo 中“每 60 次局刷后全刷”可迁移为默认策略。

### 8.3 Framebuffer

当前屏幕 framebuffer 大小：

```text
104 * 212 / 8 = 2756 bytes
```

ESP32-C3 可以承受一个主 framebuffer。第二阶段可增加一个 shadow buffer，用于差分和局部区域检测，但会增加约 2.7 KB RAM 占用。

第一版建议：

- 单 framebuffer。
- UI 重绘时清空并重画整棵当前 Screen。
- 由 RefreshPolicy 决定全刷/局刷。

第二版再引入：

- 控件级脏区裁剪。
- 局部 framebuffer 更新。
- shadow buffer 差异检测。

## 9. 插件系统

### 9.1 插件包格式

每个插件是 SD 卡上的一个目录：

```text
/sd/plugins/example/
  manifest.json
  main.py
  assets/
    icon.pbm
    data.txt
```

`manifest.json` 示例：

```json
{
  "id": "example.clock",
  "name": "Clock",
  "version": "1.0.0",
  "entry": "main.py",
  "api": 1,
  "author": "user",
  "permissions": ["time", "settings"],
  "autostart": false,
  "min_inkos": "0.1.0"
}
```

字段说明：

- `id`：全局唯一，建议反域名或短命名空间。
- `name`：Launcher 显示名称。
- `version`：语义化版本。
- `entry`：入口文件，只允许插件目录内相对路径。
- `api`：目标 InkOS 插件 API 版本。
- `permissions`：申请的系统能力。
- `autostart`：是否开机后台启动。
- `min_inkos`：最低系统版本。

### 9.2 插件入口协议

插件必须提供 `create_app(context)`：

```python
from inkos.app.base import App

class ExampleApp(App):
    def on_start(self): ...
    def on_stop(self): ...
    def on_pause(self): ...
    def on_resume(self): ...
    def on_event(self, event): ...
    def build(self):
        return self.screen

def create_app(context):
    return ExampleApp(context)
```

生命周期：

```text
discover -> load -> create_app -> on_start -> on_resume
                                  -> on_pause -> on_stop -> unload
```

约束：

- 插件不得在 import 阶段访问硬件或长时间执行。
- 插件不得在 import 阶段进入死循环。
- 插件不得直接修改 `sys.path` 到系统目录。
- 插件资源路径必须通过 `context.resources` 获取。

### 9.3 PluginManager

职责：

1. 扫描 `/sd/plugins/*/manifest.json`。
2. 校验 manifest。
3. 检查 API 版本和权限。
4. 注册到 Launcher。
5. 按需加载插件模块。
6. 管理插件实例生命周期。
7. 捕获异常并写入日志。
8. 支持禁用插件。

推荐状态：

- `DISCOVERED`
- `LOADED`
- `RUNNING`
- `PAUSED`
- `STOPPED`
- `FAILED`
- `DISABLED`

插件导入建议使用临时 `sys.path`：

```python
def load_plugin(plugin_dir, entry):
    old_path = sys.path[:]
    try:
        sys.path.insert(0, plugin_dir)
        module = __import__(entry_without_py)
        return module
    finally:
        sys.path = old_path
```

MicroPython 对模块卸载能力有限。卸载插件时可从 `sys.modules` 删除插件模块名，并释放插件实例引用，但不能保证所有内存立即回收。系统应限制同时运行插件数量，建议前台只运行一个应用。

### 9.4 权限模型

MicroPython 无法提供强隔离沙箱，因此权限模型是“框架约束 + API 约定 + 审计日志”，不是强安全边界。仍建议实现权限声明，便于用户理解插件能力。

权限建议：

- `display`：请求 UI 渲染，普通前台插件默认拥有。
- `input`：接收输入事件，普通前台插件默认拥有。
- `fs.read`：读取插件自身目录。
- `fs.write`：写入插件私有数据目录。
- `time`：读取 RTC、注册定时器。
- `network`：使用 Wi-Fi。
- `settings`：读取系统设置。
- `power`：请求保持唤醒、读取电量。
- `system`：重启、清缓存、系统级操作，仅内置应用允许。

插件文件访问应通过虚拟文件服务：

```python
context.fs.open_data("state.json", "w")
context.fs.open_resource("assets/icon.pbm", "rb")
```

对应真实路径：

```text
/sd/data/plugin_state/<plugin_id>/state.json
/sd/plugins/<plugin_dir>/assets/icon.pbm
```

## 10. 应用框架

### 10.1 App 基类

```python
class App:
    def __init__(self, context):
        self.context = context

    def on_start(self): pass
    def on_resume(self): pass
    def on_pause(self): pass
    def on_stop(self): pass
    def on_event(self, event): pass
    def build(self): return None
```

### 10.2 AppContext

`context` 是插件访问系统的唯一入口：

```python
class AppContext:
    app_id: str
    ui: UIService
    fs: PluginFS
    events: EventBus
    timers: TimerService
    logger: Logger
    settings: SettingsService
    resources: ResourceService
    clock: ClockService
```

### 10.3 页面栈

内核维护一个前台页面栈：

```text
Launcher -> Plugin Screen -> Dialog
```

`BACK` 行为：

- Dialog：关闭对话框。
- Plugin Screen：暂停插件，返回 Launcher。
- Launcher：首页时进入睡眠或显示关机菜单。

## 11. 系统服务

### 11.1 SettingsService

设置文件：

```text
/sd/data/settings.json
```

建议结构：

```json
{
  "system": {
    "timezone": 28800,
    "full_refresh_interval": 60,
    "sleep_timeout": 120
  },
  "display": {
    "rotation": 270,
    "mirror_vertical": true
  },
  "plugins": {
    "disabled": []
  }
}
```

写设置时使用临时文件 + rename：

```text
settings.json.tmp -> settings.json
```

避免断电导致配置损坏。

### 11.2 Logger

日志目标：

- 串口 REPL。
- `/sd/data/logs/inkos.log`。

日志应限制大小，例如超过 64 KB 轮转为 `inkos.log.1`。插件日志自动带上插件 id：

```text
[123456][INFO][example.clock] started
```

### 11.3 TimerService

提供：

- `call_later(ms, callback)`
- `call_every(ms, callback)`
- `cancel(handle)`

定时器回调进入事件循环执行，不在中断中直接运行插件代码。

### 11.4 ResourceService

资源加载能力：

- PBM/XBM 单色图标。
- 字体文件。
- 文本文件。
- 插件 assets。

资源服务可加入小型 LRU 缓存，但必须能在内存紧张时清理。

## 12. 错误处理与恢复

错误分类：

- `DriverError`：硬件初始化或通信失败。
- `StorageError`：SD 挂载、读写、空间不足。
- `PluginError`：manifest、加载、生命周期回调异常。
- `RenderError`：控件绘制异常。
- `ConfigError`：配置解析失败。

恢复策略：

- 屏幕驱动失败：串口输出错误，尝试重新初始化，失败后进入最小 REPL 模式。
- SD 失败：以内置应用运行，显示“SD unavailable”。
- 插件失败：标记为 `FAILED`，返回 Launcher，不影响系统。
- 渲染失败：显示系统错误页，并记录 traceback。
- 配置失败：备份损坏配置，恢复默认配置。

插件异常处理示例：

```python
try:
    app.on_event(event)
except Exception as exc:
    logger.exception("plugin callback failed", exc)
    plugin_manager.fail(plugin_id, exc)
    router.back_to_launcher()
```

## 13. 性能与内存预算

ESP32-C3 运行 MicroPython 时应保守使用 RAM。建议预算：

```text
framebuffer            2.7 KB
UI tree                2-8 KB
plugin instance        2-16 KB
resource cache         0-16 KB
logs/settings buffers  1-4 KB
```

优化原则：

- 只运行一个前台插件。
- 字体按需加载。
- 图标使用 1-bit PBM。
- 列表控件只绘制可见行。
- 插件切换后主动 `gc.collect()`。
- 大文件读取使用流式读取。
- 网络功能用完立即释放。

建议在关键路径加内存日志：

```python
import gc
logger.debug("mem_free=%d", gc.mem_free())
```

## 14. 电源策略

墨水屏适合低刷新、长待机。建议策略：

- 无输入 30 秒：屏幕进入低功耗状态，系统保持轻睡眠。
- 无输入 120 秒：进入深度空闲，保留 RTC 唤醒。
- Wi-Fi 仅在同步时间、下载数据时打开。
- 插件后台任务必须声明周期，默认不允许高频后台任务。
- 低电量时禁止非必要局刷，增加全刷间隔，关闭网络。

插件请求唤醒锁：

```python
handle = context.power.keep_awake("sync", timeout_ms=10000)
...
context.power.release(handle)
```

超时后内核自动释放。

## 15. 插件开发示例

### 15.1 最小插件

```python
from inkos.app.base import App
from inkos.ui.controls import Label
from inkos.ui.screen import Screen

class HelloApp(App):
    def build(self):
        return Screen(
            title="Hello",
            content=Label("Hello InkOS")
        )

def create_app(context):
    return HelloApp(context)
```

### 15.2 定时刷新插件

```python
from inkos.app.base import App
from inkos.ui.controls import Label
from inkos.ui.screen import Screen

class ClockApp(App):
    def on_start(self):
        self.label = Label("--:--:--")
        self.timer = self.context.timers.call_every(1000, self.update_time)

    def on_stop(self):
        self.context.timers.cancel(self.timer)

    def update_time(self):
        self.label.text = self.context.clock.local_time_text()
        self.label.invalidate()

    def build(self):
        return Screen(title="Clock", content=self.label)

def create_app(context):
    return ClockApp(context)
```

插件只更新控件状态并 invalidate，屏幕刷新由系统合并处理。

## 16. 版本与兼容性

建议定义两个版本：

- `INKOS_VERSION`：系统版本，例如 `0.1.0`。
- `PLUGIN_API_VERSION`：插件 API 整数版本，例如 `1`。

兼容策略：

- patch/minor 版本尽量保持插件 API 兼容。
- 破坏性 API 变更时提升 `PLUGIN_API_VERSION`。
- PluginManager 拒绝加载 `api` 高于系统支持版本的插件。
- 系统可为旧 API 提供兼容适配层，但不要长期保留过多分支。

## 17. 分阶段实现计划

### 阶段 1：可运行内核骨架

目标：把现有 demo 拆成驱动、Canvas、Kernel、App。

交付：

- `inkos.hal.display_epd2in13.DisplayDriver`
- `inkos.ui.canvas.MonoCanvas`
- `inkos.render.Renderer`
- `inkos.kernel.Kernel`
- 内置 `ClockApp`
- 保持当前“hello world + 时间局刷”的行为。

验收：

- 上电后能显示基础页面。
- 时间区域每秒局刷。
- 每 60 次局刷后全刷。
- 屏幕驱动代码不被插件直接调用。

### 阶段 2：基础 UI 与事件

目标：形成最小可用 UI 框架。

交付：

- Widget 基类。
- Label、Button、ListView、StatusBar。
- 输入事件驱动。
- Launcher 页面。
- SettingsService 和 Logger。

验收：

- 可用按键在 Launcher 中移动焦点和启动内置应用。
- UI 控件 invalidate 后由 Renderer 刷新。
- 日志可写入 SD 卡或串口。

### 阶段 3：SD 插件加载

目标：用户可以从 SD 卡运行 `.py` 插件。

交付：

- SDCardDriver。
- PluginManager。
- manifest 校验。
- AppContext。
- 插件私有数据目录。
- Safe Mode。

验收：

- `/sd/plugins/demo/main.py` 可被发现并在 Launcher 显示。
- 启动插件后可以显示自己的 UI。
- 插件异常不会导致系统死机。
- 禁用插件后不再加载。

### 阶段 4：资源、字体与电源

目标：提升可用性和续航。

交付：

- ResourceService。
- 单色图标加载。
- 外部字体。
- PowerDriver。
- Wi-Fi/NTP 服务化。
- 日志轮转。

验收：

- 插件可以加载自身 assets。
- 长时间无输入后进入低功耗。
- Wi-Fi 同步后自动关闭。

### 阶段 5：稳定化

目标：让系统可长期运行。

交付：

- 插件 watchdog。
- 内存统计。
- 配置损坏恢复。
- 插件 API 文档。
- 示例插件集合。

验收：

- 连续运行 24 小时无内存失控。
- 插件反复打开/关闭后可回收主要内存。
- 异常日志足够定位问题。

## 18. 关键设计取舍

### 18.1 为什么采用单前台应用

ESP32-C3 + MicroPython 的内存和 CPU 都有限，墨水屏也不适合多窗口和复杂动画。单前台应用可以显著降低生命周期、输入焦点和渲染冲突的复杂度。后台能力通过定时器和系统事件提供，但默认限制频率。

### 18.2 为什么插件不直接刷新屏幕

墨水屏全刷慢、局刷有残影，多个插件直接调用显示驱动会导致闪烁、残影和状态不同步。集中渲染器可以合并刷新请求，并统一执行“局刷若干次后全刷”的策略。

### 18.3 为什么权限不是强沙箱

MicroPython 本身不提供可靠的模块级安全隔离。插件如果恶意导入底层模块，理论上可以绕过约定。因此 InkOS 的插件权限主要用于能力声明、用户提示和框架内 API 限制。真正的安全边界应来自只安装可信插件，以及 Safe Mode/禁用机制。

### 18.4 为什么 Flash 放内核、SD 放插件

内核更新频率低，应保持稳定；插件和资源更新频率高，应允许用户直接替换 SD 卡文件。Flash 与 SD 分层还可以在 SD 卡缺失或插件损坏时启动最小系统。

## 19. 建议的首版 API 清单

首版应控制 API 数量：

```python
# App
App.on_start()
App.on_stop()
App.on_pause()
App.on_resume()
App.on_event(event)
App.build()

# Context
context.logger
context.timers
context.fs
context.settings
context.clock
context.request_render()
context.show_dialog()
context.exit_app()

# UI
Screen(title, content, actions=None)
Label(text)
Button(text, command)
ListView(items, on_select)
StatusBar()
Dialog(title, message, actions)

# Canvas for custom widgets
canvas.pixel(x, y, color)
canvas.hline(x, y, w, color)
canvas.vline(x, y, h, color)
canvas.rect(x, y, w, h, color)
canvas.fill_rect(x, y, w, h, color)
canvas.text(text, x, y, color)
canvas.bitmap(bitmap, x, y)
```

## 20. 总结

InkOS 应以“小内核、清晰 HAL、集中渲染、受控插件”为核心。当前项目已经具备 MicroPython 墨水屏驱动、画布和时间局刷 demo，可作为阶段 1 的基础。后续演进时，优先把现有 demo 拆成稳定模块，再引入 UI 树、事件循环和 SD 插件加载。这样可以在不牺牲可运行性的前提下逐步形成真正可扩展的微型操作系统框架。
