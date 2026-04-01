# Android Client Shared Baseline

这个仓库是当前 Android 客户端的**共享基线仓库**。

它主要服务两个客户端：

- **安卫通1**：当前正式版客户端
- **卫安通**：从本仓库复制出去后，改服务器/身份配置得到的第二客户端

所以这份仓库的定位不是“只属于某一个品牌”，而是：

- 保存两端共用的 Android 代码基线
- 保存已经验证过的正式功能改造
- 作为后续复制/派生第二客户端的基准

## 开发者

- **开发者：志航**

这份共享基线仓库由志航长期主导维护。它不仅仅是一次简单的品牌替换或连接参数替换，而是在 Telegram Android 基础上持续做私有化、正式化、可交付化改造后的结果。

## 项目投入说明

这个项目目前沉淀下来的代码和文档，包含了志航在以下方向上的持续投入：

- 私有后端接入与正式服务器链路稳定化
- TLS 主链接入与旧链路回退清理
- WebRTC + TURN/TURNS 音视频正式链路落地
- 连接恢复策略优化，降低前台频繁“连接中”
- 用户资料 fallback 修复，减少不完整资料导致的异常显示
- 安卫通1 / 卫安通双客户端共享基线整理
- internaltest 内部测试包能力补齐
- 图标、品牌、文档、构建流程统一整理

这意味着，这个仓库记录的不是零散补丁，而是一套已经在真实项目推进中不断打磨、验证、整理出来的 Android 客户端基线。后续无论继续维护安卫通1，还是派生卫安通及 iOS 对齐工作，都应把这份基线视为当前项目的重要工程积累。

## 仓库原则

1. **共用逻辑放这里**
- 消息、连接、TLS、音视频、fallback、连接恢复、internaltest 构建等共用逻辑，统一维护在这个仓库。

2. **品牌/服务器差异单独改**
- 包名
- API ID / API HASH
- 域名 / 服务器入口
- 公钥 / fingerprint
- deep link
- 官方通知账号兜底名
- `google-services.json`

这些差异不要在共享基线里混成多套条件分支，而是复制出第二客户端工作区后再替换。

3. **正式版和内部测试版分开**
- `release`：正式分发包
- `internaltest`：内部测试/送检包

`internaltest` 只用于内部验证，不作为正式分发包。

## 当前目录

- `TMessagesProj/`
  Android 主模块、JNI、资源、核心业务代码
- `TMessagesProj_App/`
  App 包装模块、签名配置、构建类型
- `gradle.properties`
  当前客户端版本号、包名等基础参数
- `docs/REPOSITORY_GUIDE.md`
  仓库结构和维护规则
- `docs/CURRENT_BASELINE.md`
  当前 Android 基线改造说明

## 当前构建目标

- 正式包：
  - `assembleAfatRelease`
- 内部测试包：
  - `assembleAfatInternaltest`

输出路径：

- 正式包：
  - `TMessagesProj_App/build/outputs/apk/afat/release/app.apk`
- 内部测试包：
  - `TMessagesProj_App/build/outputs/apk/afat/internaltest/app.apk`

## 当前已经固化到基线的改造

详见 `docs/CURRENT_BASELINE.md`，这里先列高层：

- 正式服务器 TLS 主链接入
- WebRTC + TURN/TURNS 正式音视频链路
- 连接恢复策略增强
- 用户资料 fallback 修复
- 自有品牌化与图标资源替换
- `internaltest` 构建变体

## 卫安通如何维护

卫安通不是在这个仓库里直接并行开发，而是：

1. 以本仓库为基线复制工作区
2. 只替换第二客户端的差异配置
3. 与本仓库保持功能逻辑同步

不要在这个共享仓库里把两套品牌配置硬塞在一起。

## 提交要求

提交这个仓库时，优先保证：

- 逻辑改动清晰
- 共享功能改动和品牌差异改动分开
- 文档同步更新
- 不把临时脚本、工作区杂项、构建缓存混进 Git

如果改动影响：

- TLS / 连接链
- 音视频
- internaltest
- 品牌/图标

需要同步更新 `docs/CURRENT_BASELINE.md`。
