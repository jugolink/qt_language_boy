<p align="center">
  <img width="18%" align="center" src="https://pic1.imgdb.cn/item/684c2db058cb8da5c84af201.jpg" alt="logo">
</p>
  <h1 align="center">
  Language Boy
</h1>
<p align="center">
  PyQt多语言转换工具,为没有安装Qt完整开发环境的PyQt开发者提供便捷生成和编辑ts、qm文件的解决方案。
</p>

![](https://i.imgur.com/waxVImv.png)

![PixPin_2025-06-12_22-16-28](https://github.com/user-attachments/assets/be22c6eb-1f00-4823-a4ed-b7eaab044eb0)

#### 开发背景
个人在使用PyQt开发应用时，需要多语言支持的功能，一般会在项目根目录创建并将需要翻译的``.ui``或``.py``文件路径以及需要生成多种语言的``.ts``路径一并添加到``.pro``文件中。这样就可以通过``lupdate.exe``一键生成所需的``.ts``文件。

但由于PyQt的虚拟环境中包含的`pylupdate.exe`不能直接对`.pro`文件进行处理，却也不想使用命令行调用一个个转，于是就有了这个便捷的转换工具。


#### 功能描述
- 关键信息缓存配置文件，下一次重启自动加载。
- 递归查找项目根目录下所有`.py`，`.ui`文件，自定义选择需要翻译的文件
- 一键生成多种语言的`.ts`文件，并支持双击使用`linguist.exe`打开或右键生成`.qm`文件

#### 依赖和构建
安装依赖：
```python
pip install PyQt6 pyqt6-tools nuitka
```

构建：
运行`scripts/build.py`，使用nuitka构建。使用nuitka构建的好处这里就不多说了。

#### 致谢
感谢`Jaxon Chen`让我有想要捣鼓这么一个软件的想法。一定程度上，这个软件能帮助那些使用PyQt开发而没有Qt环境，却又希望能像操作`.pro`一样方便快捷的多语言转换的开发者。
