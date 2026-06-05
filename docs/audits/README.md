# Audits

本目录承载独立审计记录。

Audit 的职责不是重复实现者的完成声明，而是基于仓库证据重新判断计划是否真正达到收口条件。

## Rules

- 审计必须独立于实现上下文。
- 审计必须引用 evidence。
- 审计结果必须明确为 pass、fail 或 partial。
- evidence 不足时不能 pass。

## Semantic Conservation

审计还必须检查语义承诺是否守恒：计划范围内的承诺不能在实现、文档同步或关闭过程中消失、弱化，或移动到非权威 artifact 中。

- J-flow-only evidence 只能说明承诺被路由、复述或转交，不能单独证明不确定性已经降低。
- R-flow evidence 必须通过可检查的代码、测试、验证、审计、owner docs 或明确决策降低不确定性。
- 如果承诺没有守恒，finding 应引用仓库 evidence，并说明需要恢复、绑定到权威 owner doc，或创建后续计划。
