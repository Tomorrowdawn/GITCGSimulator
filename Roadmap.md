### Roadmap

1. 实现基本的GameState,完成接口测试.
2. 实现事件处理框架, 完成单元测试. 
3. 实现Roll, Start phase.(包括掷骰, 结算, 抽牌)
4. 实现End Phase的结算.
5. 实现Combat phase. 支持基本的行动(包括切人, 使用技能, 打出手牌*). 
  - 伤害结算(包括附魔, 元素反应, 增伤 ,减伤)
  - 死亡结算(死亡时换人)
  - 监听器生成与取消.
  - 费用预计算.(发一条PreCal消息)
  - 元素反应
6. 实现Game End判定
7. 实现Game类接口.
8. 实现简单的GUI或者CLI以供调试/对战.
9.  补充角色卡和行动卡.