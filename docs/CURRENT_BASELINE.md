# Current Android Baseline

这份文档描述的是**当前共享 Android 基线**里已经做过的主要改造。

它不记录第二客户端的独有参数，只记录共用能力和实现方向。

## 1. 客户端身份与品牌

安卫通1 当前已经完成：

- 自有应用名
- 自有包名
- 自有 deep link
- 自有 intent/action 前缀
- 自有 launcher 图标
- 官方通知账号本地兜底品牌化

这些属于已经落地的正式方向。

## 2. TLS 主链

当前共享基线已经支持正式服务器 TLS 主链。

主要点：

- 启用真 TLS 连接
- 以正式 TLS 主入口为主
- 处理旧地址缓存问题
- 避免旧配置重新灌回旧链路

涉及核心文件：

- `TMessagesProj/jni/tgnet/ConnectionsManager.cpp`
- `TMessagesProj/jni/tgnet/ConnectionSocket.cpp`

## 3. WebRTC / TURN / TURNS

共享基线当前音视频正式方向是：

- 呼叫信令仍保留 MTProto 风格
- 媒体层使用 `phoneConnectionWebrtc`
- 运行链按 WebRTC + TURN/TURNS

已经落地的能力：

- `phoneConnectionWebrtc.flags.2 = tcp`
- TURN UDP / TURN TCP / TURNS TLS 区分
- Java -> JNI -> native 的 rtc endpoint 传递
- ICE restart

核心文件：

- `TMessagesProj/src/main/java/org/telegram/messenger/voip/VoIPService.java`
- `TMessagesProj/src/main/java/org/telegram/tgnet/TLRPC.java`
- `TMessagesProj/jni/voip/org_telegram_messenger_voip_Instance.cpp`
- `TMessagesProj/jni/voip/tgcalls/v2/NativeNetworkingImpl.cpp`

## 4. 连接恢复策略

当前共享基线已做一轮稳定性优化，目标是减少前台频繁“连接中”。

已经实现：

- TCP keepalive
- 更快但受控的重连退避
- 网络变化检测增强
- 区分硬切换和软刷新
- 软刷新先探活，再决定是否强制重连
- 防止后台误唤醒
- 防止重复广播导致重连风暴

核心文件：

- `TMessagesProj/jni/tgnet/Connection.cpp`
- `TMessagesProj/jni/tgnet/ConnectionSocket.cpp`
- `TMessagesProj/src/main/java/org/telegram/messenger/ApplicationLoader.java`
- `TMessagesProj/src/main/java/org/telegram/tgnet/ConnectionsManager.java`

## 5. 用户资料 fallback 修复

当前共享基线已经补了用户资料 fallback。

核心点：

- 不完整 `User` 不再覆盖本地完整资料
- 消息更新链里遇到缺失用户会主动补拉
- 聊天页发现空壳用户时会触发轻量刷新

核心文件：

- `TMessagesProj/src/main/java/org/telegram/messenger/MessagesController.java`
- `TMessagesProj/src/main/java/org/telegram/ui/ChatActivity.java`

## 6. internaltest 构建

当前共享基线提供两个构建方向：

- `release`
- `internaltest`

`internaltest` 特点：

- 功能逻辑和正式版保持一致
- 仅用于内部测试/送检
- 关闭完整性拦截

对应配置：

- `TMessagesProj/build.gradle`
- `TMessagesProj_App/build.gradle`

## 7. 第二客户端如何继承

卫安通不是在这个仓库里直接做条件分支，而是：

1. 复制这份共享基线
2. 替换第二客户端自己的差异配置
3. 继续复用本文件里记录的共用能力

也就是说：

- 这份文档是“共享能力基线”
- 不是“某一个客户端的全部差异说明”
