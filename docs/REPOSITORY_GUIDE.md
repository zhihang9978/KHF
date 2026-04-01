# Repository Guide

## 1. 仓库定位

这个仓库是 Android 客户端的**共享基线**，不是“安卫通1 专属仓库”，也不是“卫安通专属仓库”。

它保存的是：

- 两个客户端共用的核心代码
- 已验证稳定的正式改造
- 后续复制第二客户端时要沿用的基线

当前工作方式：

- 安卫通1：直接从本仓库构建
- 卫安通：从本仓库复制出独立工作区，再替换身份/服务器差异

## 2. 目录职责

- `TMessagesProj/`
  - Java 业务逻辑
  - JNI / tgnet / voip
  - 资源文件
- `TMessagesProj_App/`
  - App module
  - 签名与构建类型
- `gradle.properties`
  - 版本号
  - 包名
  - 签名参数
- `README.md`
  - 仓库入口说明
- `docs/CURRENT_BASELINE.md`
  - 当前共享功能基线说明

## 3. 什么应该改在共享基线里

这类改动应该直接进本仓库：

- 消息处理逻辑
- 用户 fallback
- tgnet/TLS/连接恢复
- WebRTC/TURN/TURNS 音视频
- `internaltest` 构建能力
- 共用资源结构调整
- 共用图标替换

## 4. 什么不应该直接混进共享基线

这类改动属于品牌/环境差异，应在复制出的第二客户端工作区里单独改：

- 第二客户端包名
- 第二客户端 API ID / API HASH
- 第二客户端域名 / 服务器
- 第二客户端公钥 / fingerprint
- 第二客户端 deep link
- 第二客户端官方通知账号兜底名
- 第二客户端 `google-services.json`

## 5. 推荐维护方式

### 更新共享逻辑

1. 在本仓库改共用逻辑
2. 构建并验证安卫通1
3. 提交并推送本仓库
4. 需要同步卫安通时，再把这份基线复制到第二工作区

### 更新第二客户端

1. 从最新共享基线复制工作区
2. 应用第二客户端差异配置
3. 单独构建验证

## 6. 当前构建说明

### 正式包

- 任务：`assembleAfatRelease`
- 输出：
  - `TMessagesProj_App/build/outputs/apk/afat/release/app.apk`

### 内部测试包

- 任务：`assembleAfatInternaltest`
- 输出：
  - `TMessagesProj_App/build/outputs/apk/afat/internaltest/app.apk`

### internaltest 用途

`internaltest` 仅用于：

- 内部送检
- 动态分析
- 不校验完整性的测试场景

它不用于正式分发。

## 7. 提交规范

每次提交尽量满足：

- 一个提交只做一组相关改动
- 品牌差异不要混进共享逻辑提交
- 资源替换要说明来源
- 影响连接/音视频时要同步更新文档

## 8. 当前仓库应保持的状态

理想状态：

- Git 工作区干净
- 顶层只有必要文件和目录
- 构建缓存不进仓库
- 说明文档和当前实现一致

如果文档和代码不一致，以代码为准，但要尽快补文档。
