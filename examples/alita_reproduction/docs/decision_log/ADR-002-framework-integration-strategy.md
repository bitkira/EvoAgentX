# ADR-002: EvoAgentX框架深度集成策略

## 状态
**接受** - 2025-08-12

## 背景
基于专家咨询建议，制定EvoAgentX框架深度集成策略，最大化利用框架现有能力，避免重复开发。

## 决策

### 1. 工具集成策略
**决策**: 优先使用EvoAgentX提供的工具包

**具体选择**:
- **搜索**: GoogleFreeSearchToolkit (而非自建搜索)
- **执行**: DockerInterpreterToolkit (而非自建sandbox)  
- **存储**: StorageHandler (而非文件系统)
- **优化**: TextGrad/MIPRO/AFlow (而非自建进化算法)

**理由**:
- 框架工具包经过生产验证，稳定性高
- 避免重复造轮子，专注业务逻辑
- 获得框架生态的持续更新和支持

### 2. 抽象接口设计
**决策**: 为所有框架集成点设计抽象接口

**设计原则**:
- **ToolAdapter**: 统一工具调用接口
- **StorageHandler**: 抽象存储操作
- **ExecutionEngine**: 抽象代码执行
- **PromptManager**: 中心化提示词管理

**理由**:
- 降低框架耦合度
- 便于测试和模拟
- 支持未来的框架迁移

### 3. 配置管理策略
**决策**: 基于EvoAgentX的配置系统扩展

**实现方式**:
```python
class ALITAConfig(BaseModel):
    # EvoAgentX基础配置
    llm_config: OpenAILLMConfig
    
    # ALITA特定配置
    max_iterations: int = 10
    cost_limit: float = 10.0
    docker_config: DockerConfig
    storage_config: StorageConfig
```

**理由**:
- 保持配置一致性
- 便于框架升级适配
- 支持环境变量和配置文件

## 集成风险评估

### 高风险点
1. **框架版本依赖**: EvoAgentX更新可能破坏兼容性
2. **性能瓶颈**: 框架抽象层可能影响性能
3. **功能限制**: 框架功能可能不满足特定需求

### 风险缓解
1. **版本锁定**: 锁定框架版本，定期评估升级
2. **性能监控**: 建立性能基准测试
3. **降级方案**: 关键路径保留直接实现选项

### 低风险点
1. **文档支持**: EvoAgentX有完整文档
2. **社区支持**: 活跃的开发社区
3. **代码质量**: 框架代码质量较高

## 实施计划

### Phase 1: 基础集成
- Commit 2: 集成PythonInterpreterToolkit
- Commit 4: 集成GoogleFreeSearchToolkit
- Commit 6: 集成DockerInterpreterToolkit

### Phase 2: 存储集成  
- Commit 7: 基于StorageHandler实现MCPBox

### Phase 3: 优化集成
- Commit 16: 集成TextGrad/MIPRO优化器

## 成功指标
- **开发效率**: 相比自建方案，开发时间减少20-30%
- **代码质量**: 单元测试覆盖率>80%
- **稳定性**: 框架组件0故障运行
- **性能**: 响应时间满足业务要求(<5s)

## 备选方案

### 方案A: 最小集成
仅使用框架的基础Agent和Action，其他自建
- 优点: 控制度高，依赖少
- 缺点: 开发工作量大，质量风险高

### 方案B: 完全自建
不使用EvoAgentX，基于原生Python开发
- 优点: 完全控制
- 缺点: 开发成本极高，偏离项目目标

**选择理由**: 深度集成方案平衡了开发效率和技术风险

## 合规性检查
- ✅ 符合DRY原则(Don't Repeat Yourself)
- ✅ 符合依赖倒置原则
- ✅ 符合开放封闭原则
- ✅ 支持单元测试
- ✅ 支持持续集成

---

**相关ADR**: ADR-001
**批准人**: 项目负责人  
**日期**: 2025-08-12