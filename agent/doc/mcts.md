## callback, Branch node and MCTS

除了通常的Node以外,需要加入BranchNode

BranchNode不包含游戏状态, 但是包含一组分支, 分支后是正常的Node.

BranchNode可用于callback也可用于随机场景.

### 搜索BranchNode

当遇到一个BranchNode时, 我们引入一个BranchPlayer. BP可以是随机的, 也可以是确定的(这通常根据分支数来确定). BP执行一步后转移到一个正常Node, 继续执行蒙特卡洛即可.

BP可以聚合(也可以不聚合)所有已知分支节点的信息, 例如取最大值. 对于分支较小的BN来说, 可以直接搜索所有分支, 然后返回最好的分支, 直接消除掉其他所有分支. 对于分支较大的BN或者带随机性的BN, 可以采取蒙特卡洛. 但请注意, MCTS每次选择到BN时都会触发该蒙特卡洛, 因此需要限制次数.

### Callback设计下的BranchNode搜索