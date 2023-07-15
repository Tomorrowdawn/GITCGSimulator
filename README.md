# GITCGSimulator
Simulator for GeniusInvokation TCG, tailor-made for ai training. 


## RoadMap

- [x] 从纯字符串装载游戏
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
    - [ ] 伤害, 治疗, 死亡处理
    - [ ] 切换角色
    - [ ] 打出手牌
    - [ ] 调和手牌
    - [ ] 投掷阶段, 开始阶段, 结束阶段
    - [ ] 元素反应

- [ ] Instruction交互系统, AI接口
   - [ ] Instruction翻译成Event(Doing)
   - [x] 可读出GameState格式的游戏状态 
   - [ ] Numpy格式的游戏状态(已定义, 未实现)

- [ ] CLI 交互系统