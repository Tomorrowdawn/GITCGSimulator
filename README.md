# GITCGSimulator
Simulator for GeniusInvokation TCG, tailor-made for ai training. 


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
    - [x] 元素反应
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