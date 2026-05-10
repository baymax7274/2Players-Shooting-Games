# 双人枪战游戏 v1.1.0 — 设计文档

**日期：** 2026-05-10
**类型：** Bug 修复

---

## 1. 概述

修复分屏模式下右侧玩家（玩家2）视角缺失的问题。

## 2. 问题分析

### 根因

`battle.py` 渲染方法中，`offset_draw` 的计算未考虑摄像机视口（viewport）的屏幕偏移位置：

- **摄像机1**：视口 `Rect(0, 0, 640, 720)`，vp.x=0，无影响
- **摄像机2**：视口 `Rect(640, 0, 640, 720)`，vp.x=640，渲染坐标落在 0~640 范围，被 clip 裁剪

### 表现

- 两玩家距离近时（合并画面）：正常
- 两玩家距离远时（分屏）：左侧正常显示玩家1视角，右侧全黑/空白

## 3. 修复方案

### 修改文件

`src/scenes/battle.py` 第 523 行

### 修改内容

```python
# 修改前
offset_draw = Vec2(cam.offset.x + shake_off.x, cam.offset.y + shake_off.y)

# 修改后
offset_draw = Vec2(cam.offset.x - cam.vp.x + shake_off.x, cam.offset.y - cam.vp.y + shake_off.y)
```

### 原理

摄像机 offset 的目标是让跟踪目标出现在视口中心。`Camera.update()` 计算：
```
offset = target_pos - vp.size / 2
```

这正确地将目标放在视口中心（相对视口原点），但渲染时需要将世界坐标映射到**屏幕绝对坐标**：
```
screen_pos = world_pos - offset + vp.origin
```

由于 entity/map 的 render 接口统一使用 `world_pos - camera_offset` 的形式，只需在传入的 `camera_offset` 中减去 `vp.origin` 即可。

### 影响范围

- 仅修改 1 行
- 摄像机1（vp.x=0, vp.y=0）计算结果不变
- 所有实体（地图、玩家、子弹、粒子、特效等）统一受益

## 4. 测试验证

1. 启动游戏，进入本地双人对战
2. 选择任意地图
3. 两个玩家朝相反方向移动，触发分屏
4. 确认：
   - 左侧画面跟随玩家1
   - 右侧画面跟随玩家2
   - 距离拉近时合并为全屏画面正常
   - HUD/分隔线渲染正常
