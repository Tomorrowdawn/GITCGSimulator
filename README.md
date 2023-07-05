# GITCGSimulator
Simulator for GeniusInvokation TCG, tailor-made for ai training. 


## RoadMap

- [x] 从纯字符串装载游戏
- [x] GameState内部组织完毕
- [ ] GameState API完善(Doing)

- [ ] 骰子系统
  - [x]  V1:全万能

- [ ] 完善Event处理系统.
  - [x] 定义必要的Event类 
  - [x] EventHub完成递归事件处理
  - [ ] 所有Event的执行逻辑(Doing)
    - [x] 充能, 交换行动, 使用技能
    - [ ] 伤害, 治疗, 死亡处理
    - [ ] 切换角色
    - [ ] 打出手牌
    - [ ] 调和手牌

- [ ] Instruction交互系统
   - [ ] Instruction翻译成Event(Doing) 