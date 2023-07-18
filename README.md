# GITCGSimulator
Simulator for GeniusInvokation TCG, tailor-made for ai training


## 使用教程

如果你只关心AI开发的话:

```py
from src.core.GameInstance import apply_react, reaction, GameInstance
from src.core.GameState import Location, Aura, GameState, Box
from src.game import activate, Game
b1 = Box(['Diluc','Diluc','Diluc'],[])
b2 = Box(['Diluc','Diluc','Diluc'],[])
state = GameState(b1,b2)
g = Game()
g.initiate(state)
```

如此, 就可以完成基本的初始化. 注意目前版本暂时不准备适配手牌(尽管我们的框架已经为此准备好了,但是比较缺人).

对于AI开发而言,`g.proceed`和`g.getIns`是最重要的两个方法, 我们在此作简单介绍:

proceed(ins, new_game, callback). ins是一条指令Instruction, new_game是一个布尔变量, 如果为真, 则proceed将返回一个深拷贝Game(同时保持现有Game不变), 这很有利于搜索. callback是一个接受两参数`gameinstance, event`的函数, 当死亡,掷骰时会调用该函数. callback并未区分玩家, 因此需要在callback内部进行判断(通常根据event.player_id进行区分). 注意, GITCGSim中玩家id为1或者2.

getIns(player_id, ins)接受player_id和一个字符串, 返回None(如果行动非法)或者Instruction(但DiceInstance及可能的其他参数(譬如胡桃拆哪个)需要在外部指明). ins字符串如下:

```
na,skill,burst, sp1,sp2
switch next, switch previous
end round
play card X
tune card X
```

X是手牌下标. sp1,sp2对应的是非标准技能, 例如甘雨,纯水和草神的5费技能. 目前可用的选项是na,skill,burst, switch next, switch previous, end round. 这些构成了你的AI的动作空间.

关于GameInstance的更多细节将在之后补充.

## RoadMap

- [x] 从纯字符串装载游戏
  - [x]  使用pickle的状态拷贝(特别适用于alphabeta,cfr等不需要格式化数据的算法. 大约200us一次拷贝)
  - [ ]  使用export-restore的状态拷贝(该方法比pickle要慢(大约慢100us),但是可以导出矩阵形式数据).
  - [ ] 使用Cython进行加速(pypy已测试过, 从0.3ms/copy 优化到了6ms/copy. 有陷阱, 停止优化)
- [x] GameState内部组织完毕
- [ ] GameState API完善(Doing)

- [ ] 骰子系统
  - [x]  V1:全万能
  
- [ ] 卡牌系统
  - [x] 定义好所有抽象类
  - [x] 字符串反射
  - [ ] 已实现卡牌(暂空) 

- [ ] 完善Event处理系统.
  - [x] 定义必要的Event类 
  - [x] EventHub完成递归事件处理
  - [ ] 所有Event的执行逻辑(Doing)(包括history维护)
    - [x] 充能, 交换行动, 使用技能
    - [ ] 召唤物
    - [ ] 状态
    - [x] 伤害, 治疗, 死亡处理
    - [x] 切换角色
    - [ ] 打出手牌
    - [ ] 调和手牌
    - [x] 投掷阶段, 开始阶段, 结束阶段
    - [ ] 元素反应
      - [x] 无副作用反应
      - [ ] 有副作用反应(草反应, 结晶, 超载)
  - [ ] 回调系统
    - [ ] 定义统一的回调接口避免参数过多. 需要定义一个成员变量告知回调函数现在需求什么回调.
    - [ ] Roll回调
    - [x] DeathSwitch回调
    - [ ] ExchangeCard回调(须弥共鸣)

- [ ] Instruction交互系统, AI接口
   - [x] Instruction翻译成Event
   - [x] 可读出GameState格式的游戏状态 
   - [ ] Numpy格式的游戏状态(已定义, 未实现)

- [ ] CLI 交互系统