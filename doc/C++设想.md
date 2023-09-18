本项目中各类有着非常强烈的属性性质, 可以较为自然地转换成C++项目. 然而, 也有一些特定于python的特性, 我们将在这里说明一些细节.

## Element统一

我们将统一Element的代数记号, 以让DMGType, DiceType,Aura三者统一记号, 而非Python代码中拧巴的记号.

## 分派

C++ 支持单分派. 

## type()

代码中使用了大量type()函数. 实际上, 其本意是对于不同类型的Event执行不同操作(它们的数据结构也不一样). 这里我们要用到双分派技术. 简单来说

```cpp
std::vector<event> execute(GI* g, Event* event){
    event->handle(g)
}
```

然而这不符合开闭原则, 如要添加一个新角色, 甚至需要修改它关联的事件类, 这是不可接受的. 为此, 我们可以使用`dynamic_cast`安全向下转换. 我们添加一个clstype变量, 由程序员在编程时手动填写



## 拷贝

python中拷贝非常简单, 就是pickle.loads(pickle.dumps). 不过这有点慢. 

在C++中我们将对必要的类重写拷贝函数. 实际上这样的类应当较少(如果不储存外部指针的话, 无需重写).

## 反射

在本项目中, 唯一涉及到反射的地方是加载角色/卡牌. 

我们使用一种十分简单的方法解决它: 手动编写一个头文件, 包含一个map, 将string映射到一个工厂函数上, 该函数会产生一个实例. 

不使用更复杂的自动注册等技术是因为项目本身并不关注这些, 且用不上高级特性.

## Py接口

py接口仍然很必要, 因为用户交互和AI代码仍然以Python编写较为方便.

### pybind

我们将使用pybind提供python接口, 以保证Observer和AI代码仍以Python形式编写, 享受高度优化的Python神经网络库.

### Json

或者, 我们将GameInstance序列化为Json提供给Python(HTTP或者动态链接). 