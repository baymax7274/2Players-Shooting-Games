# v1.1.0 修复分屏右侧玩家视角 — 实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 修复分屏模式下玩家2视角缺失——渲染偏移计算时忽略视口位置的问题

**Architecture:** 单行改动，在 `battle.py` 的 `render()` 方法中，`offset_draw` 计算时减去摄像机视口的屏幕偏移 (`cam.vp.x`, `cam.vp.y`)

**Tech Stack:** Python 3.10+, Pygame 2.x

---

### Task 1: 修复摄像机渲染偏移

**Files:**
- Modify: `src/scenes/battle.py:523`

- [ ] **Step 1: 修改 offset_draw 计算**

将第 523 行：
```python
offset_draw = Vec2(cam.offset.x + shake_off.x, cam.offset.y + shake_off.y)
```

改为：
```python
offset_draw = Vec2(cam.offset.x - cam.vp.x + shake_off.x, cam.offset.y - cam.vp.y + shake_off.y)
```

- [ ] **Step 2: 运行游戏验证**

```bash
python main.py
```

验证步骤：
1. 选择"开始对战" → 选择任意地图（推荐训练靶场）
2. 两个玩家朝相反方向移动，拉开距离触发分屏
3. 确认左侧显示玩家1视角、右侧显示玩家2视角
4. 拉近距离确认合并为全屏正常

- [ ] **Step 3: 提交**

```bash
git add src/scenes/battle.py
git commit -m "fix: 修复分屏右侧玩家视角缺失 — offset_draw 减去视口偏移"
```

---

### Task 2: 更新 CHANGELOG

**Files:**
- Modify: `CHANGELOG.md`

- [ ] **Step 1: 在 CHANGELOG 顶部新增 v1.1.0 条目**

在文件开头 `# 更新日志` 之后、`## v1.0.0` 之前插入：

```markdown
## v1.1.0 (2026-05-10)

### 修复
- 分屏模式下右侧玩家视角缺失 —— 渲染偏移计算未考虑视口屏幕位置

```

- [ ] **Step 2: 提交**

```bash
git add CHANGELOG.md
git commit -m "更新 CHANGELOG — v1.1.0 修复记录"
```
