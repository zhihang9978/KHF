# Teamgram Android Client (Private Backend Fork)

本仓库是基于 Telegram Android 源码进行的私有化改造版本，用于连接私有 Teamgram Server 后端。

本 README 是“对外可公开版本”，不包含任何敏感信息（服务器 IP、私钥、完整 API 凭据、内部域名等）。

## 项目目标

- 保持客户端与 Telegram 公共 TL/MTProto 语义兼容。
- 对接私有后端并支持可控部署。
- 在不泄露基础设施信息的前提下提供可复现构建说明。

## 已做改动（脱敏说明）

以下是目前 fork 的核心改动方向与落点文件：

1. 私有后端连接改造
- 改动文件：`TMessagesProj/jni/tgnet/ConnectionsManager.cpp`
- 改动内容：
  - 默认数据中心改为私有后端 DC（不再依赖官方引导地址）。
  - 初始化地址使用私有 TCP 主端口 + 备用端口。
  - 关闭部分动态地址回填路径，避免回落到非私有链路。

2. 握手参数对齐
- 改动文件：`TMessagesProj/jni/tgnet/Handshake.cpp`
- 改动内容：
  - 客户端侧 RSA 指纹与私有后端网关配置对齐。
  - 避免因指纹不匹配导致握手失败。

3. 登录稳定性（Passkey 容错）
- 改动文件：`TMessagesProj/src/main/java/org/telegram/messenger/PasskeysController.java`
- 改动内容：
  - 对 `publicKey` 缺失场景做防御性解析。
  - 缺失时静默降级，不向用户弹出不必要错误。

4. 构建与包配置
- 改动文件：`TMessagesProj_App/build.gradle`、`gradle.properties`、`TMessagesProj/src/main/java/org/telegram/messenger/BuildVars.java`
- 改动内容：
  - 使用项目私有包名和版本策略。
  - 区分 debug/release 包标识。
  - 使用当前项目需要的 API 参数（发布前需替换为你自己的生产参数）。

## 敏感信息处理规范（必须遵守）

以下信息禁止提交到公共仓库：

- 服务器公网 IP / 内网拓扑 / SSH 凭据
- 私钥文件（例如 `server_pkcs1.key`）
- 完整 `api_hash` / 签名密钥 / Firebase 生产密钥
- 内部域名和运维脚本中的真实地址

建议做法：

- 用占位符替换：`<PRIVATE_DC_HOST>`、`<PRIVATE_API_HASH>`、`<PRIVATE_RSA_FINGERPRINT>`
- 通过部署环境注入敏感参数，不写死到源码
- 提交前执行一次敏感词扫描

## 构建目标

- `TMessagesProj_App:assembleAfatDebug`
- `TMessagesProj_App:assembleAfatRelease`

APK 输出路径（示例）：

- `TMessagesProj_App/build/outputs/apk/afat/debug/app.apk`
- `TMessagesProj_App/build/outputs/apk/afat/release/app.apk`

## 最小构建步骤

1. 准备 JDK / Android SDK / NDK（版本以 `build.gradle` 为准）
2. 配置签名参数（`gradle.properties`）
3. 放置对应渠道配置（如 `google-services.json`，按需）
4. 执行 Gradle 构建命令
5. 通过 ADB 安装到测试设备验证链路

## 连接配置模板（示例，脱敏）

```text
APP_ID=<YOUR_APP_ID>
APP_HASH=<YOUR_APP_HASH>
PRIVATE_DC_HOST=<PRIVATE_DC_HOST>
PRIVATE_DC_PORT=<PRIVATE_DC_PORT>
PRIVATE_DC_PORT_FALLBACK=<PRIVATE_DC_PORT_FALLBACK>
RSA_FINGERPRINT=<PRIVATE_RSA_FINGERPRINT_UINT64>
```

## 公开仓库发布说明

- 本仓库用于代码协作与审计，不代表生产参数。
- 任何涉及真实基础设施信息的内容必须保留在私有仓库或服务器端。
- 若需对外说明改动，请引用本 README 的“已做改动（脱敏说明）”部分。

## 协议参考

- Telegram API: https://core.telegram.org/api
- MTProto: https://core.telegram.org/mtproto

## 许可证

保持上游许可证约束，遵循原项目许可和开源义务。
