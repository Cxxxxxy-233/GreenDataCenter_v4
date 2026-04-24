## 项目记录
### 记录1
在src\greendatacenter\coordinator_v2.py和src\greendatacenter\graph\nodes.py中有这样一段关于io的代码：
```python
# 强制UTF-8输出（仅在交互式控制台模式下）
# 这个会影响终端输出不要解开注释
# if sys.platform == "win32" and sys.stdout.isatty():
#     import io
#     sys.stdout = io.TextIOWrapper(sys.stdout, encoding="utf-8")
#     sys.stderr = io.TextIOWrapper(sys.stderr, encoding="utf-8")
```
这里需要注释掉，否则会影响终端输出