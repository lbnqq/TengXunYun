# AI编程项目终极实践手册 (2025年1月28日版)

## 🎯 核心指导思想

**AI是卓越的协作者，而非独立思考者。它极大提升效率，但无法替代人类的判断、经验和对复杂场景的深度理解。在所有决策点，特别是在高风险领域，人类是最终的质量与责任承担者。**

---

## I. 🎯 核心原则 (基石与红线)

这些原则是项目成功的基石，必须在整个开发过程中严格遵守和强制执行。

### P0: 绝对禁止与强制红线 (不可妥协的底线)

#### 1. 反冗余与工程纯粹性 (Anti-Redundancy & Engineering Purity)
*   **原则：** **绝对禁止**为了测试通过或简化开发而在系统中增加任何冗余功能、非生产代码。所有测试必须基于**真实、已存在**的系统接口和功能。系统必须保持“纯粹”和“生产就绪”状态。
*   **实践：**
    *   **全面去除桩子与空占位符：** **绝对禁止**在生产代码中出现任何形式的桩子函数、空函数、桩子类、空类。
    *   **单元测试的Mock限制：** 对于单元测试，**禁止使用Mock类来模拟待测试单元的**核心业务逻辑**；Mock**仅限于隔离待测试单元的**外部依赖**（如数据库、外部API调用）。
    *   **强制检测：** 自动化代码审查工具和AI必须具备识别并标记上述冗余代码的能力。

#### 2. 禁止使用可变全局变量进行状态共享 (Absolute Ban on Mutable Global State Sharing)
*   **原则：** **绝对禁止**使用可变全局变量（包括模块级变量）作为在不同进程、独立脚本、甚至跨多个复杂模块间共享状态的机制。这种做法会导致状态不一致、测试不可靠、难以追踪的Bug，并严重破坏系统纯粹性。
*   **强制执行：** 任何需要被共享的“全局”状态，必须通过**显式传递**（如函数参数、返回值）、**外部持久化存储**（如数据库、文件、缓存、消息队列）或**专门的状态管理机制**（如依赖注入容器、服务注册中心）实现。
*   **AI行为：** AI在生成代码时，**绝不**引入此类可变全局变量进行状态共享。如果分析现有代码发现此问题，AI应立即标记并优先提出符合上述原则的重构建议。

#### 3. 未经确认不生成 (No Unconfirmed Generation)
*   **原则：** AI绝不能在信息不完整、存在歧义或未经用户明确确认的情况下生成代码或关键文档。
*   **实践：**
    *   **不确定性显目提示：** AI有不确定的地方必须显目地提出来让用户确认和补充。
    *   **用户引导与多方案：** 用户不理解或不知道如何确认时，AI应提供更多提示、多个备选方案并解释每个方案的优缺点。
    *   **拒绝生成：** 在信息不完整或未经用户明确确认时，AI必须拒绝生成。

#### 4. 有效沟通与上下文管理 (Highest Priority Meta-Rule)
*   **原则：** 最大化AI协作效率并避免误解和上下文丢失。
*   **实践：**
    *   **单一焦点原则：** 每次与AI的交互应聚焦于一个明确的问题或任务。当对话话题出现偏离时，AI必须立即提醒用户，并提供选项将其拉回或作为独立讨论。
    *   **上下文长度管理：** AI将持续监控对话长度。当达到内部上下文限制的约70%时，AI必须主动提醒用户总结或开启新对话。
    *   **持久化记忆：** 上述原则是AI行为的底层约束和指引，无论AI当前正在执行何种任务，都将时刻生效。

### P1: 必须遵守的基石 (严谨工程实践)

#### 1. 人类中心化与风险优先 (Human-Centric & Risk-First)
*   **原则：** 任何AI功能或生成物，必须以满足人类真实需求、提升用户体验为最终目标，并严格评估其潜在风险。
*   **实践：** 高风险（安全、财务、核心业务逻辑）区域，强制人工审核与验证。最终的用户价值和风险责任始终由人类承担。

#### 2. 验证驱动，而非代码驱动 (Validation-Driven, Not Code-Driven)
*   **原则：** 代码存在不等于功能有效，功能有效不等于满足需求。所有的技术分析、设计和实现，都必须从用户需求出发，并以可验证的方式证明其有效性。
*   **实践：** 从需求分析阶段就引入初步测试用例和验收标准，确保需求的可测试性。

#### 3. 工程健壮性与可维护性优先 (Engineering Robustness & Maintainability)
*   **原则：** 在任何设计和实现中，将工程级别的可用性、稳定性、可扩展性、可维护性、安全性放在首位。AI生成代码必须符合既定的工程规范。
*   **实践：** 强制执行代码质量标准、性能监控、日志规范和错误处理机制。

#### 4. AI的审慎态度与透明度 (AI Prudence & Transparency)
*   **原则：** 警惕AI的局限性、潜在幻觉和非确定性。AI生成内容必须经过严格审核，强制达到高置信度且可溯源。
*   **实践：**
    *   **高置信度要求：** AI在生成所有文档和代码时，必须在确信度0.99以上才自动生成。
    *   **AI生成标记：** 所有AI生成的文档和代码，必须包含明确的元数据标记，如`// @AI-Generated: [日期], Confidence: [0.xx], Version: [model_vX.Y]`。

---

## II. 📋 项目生命周期与阶段性指南

### 阶段A: 深度需求工程与系统架构 (P1: 最重要，AI辅助，人类决策)

#### 用户需求深度挖掘与澄清 (P1)

**场景故事与用户画像**：当需求不清晰时，由人类UX专家引导，AI可辅助生成多维度的用户画像和针对不同需求的"场景故事"（User Story / Scenario）。

**测试用例与测试标准先行 (P1)**：针对每个场景故事，由人类测试专家设计，AI可辅助生成详细的测试用例和明确的测试标准，这些必须在编码前获得用户与团队认可。

**反复确认与消歧 (P1)**：持续与用户反复沟通，通过原型、图示等方式，直到所有需求完全明晰，不留含糊空间。

**需求规格说明书 (SRS) 与优先级列表 (P1)**：编制正式的SRS，包括明确的需求优先级列表（人类PM决策），并由用户反复确认与签字认可。

#### 系统应用场景与非功能性需求分析 (P1)

**彻底分析**：明确单/多用户、系统环境、单机/网络、客户端/Web、性能指标（响应时间、并发量、吞吐量）、安全要求、可扩展性、可观测性、目标用户画像等。

**量化指标**：尽可能将非功能性需求量化，例如：平均响应时间 < 200ms，99%请求响应时间 < 1s，年系统可用性 > 99.99%。

#### 迭代系统架构设计 (P1)

**人类主导设计 (P1)**：基于详尽的需求和场景，由人类系统架构师主导设计核心系统架构，明确关键模块、服务划分、数据流、技术栈选择、安全边界和部署策略。

**AI辅助优化**：AI可辅助生成架构草案、技术选型建议、组件接口定义，但所有关键决策和设计原则必须由人类架构师审批并签字。

**健壮性与可扩展性**：将工程可用性、健壮性、可扩展性、可维护性放在首位。AI生成代码应严格遵守架构师定义的约束和规范。

### 阶段B: 核心后端开发与API优先 (P2: AI生成，人类严格审查)

#### API优先完整性设计 (P2)

**接口契约先行**：由人类设计师定义所有后端API的详细接口契约（URL、请求/响应格式、参数、认证机制、错误码等），AI可辅助生成API文档初稿。

**分层测试设计**：
- **API单元测试 (P2)**：AI可辅助生成每个API及其内部组件的单元测试，但其覆盖率和质量由人类测试工程师审核。
- **API集成测试 (P2)**：验证不同API之间的交互和数据流是否正确，AI可辅助生成集成测试脚本。

#### 后端服务实现与全流程测试 (P2)

**AI生成代码审核 (P1)**：AI可生成后端服务代码，但必须通过L1-L4的代码审查。尤其对于核心业务逻辑和安全敏感代码，必须进行P1级人工代码走查。

**全业务场景测试 (P2)**：后端服务代码必须完整实现所有业务场景的全流程功能。AI可辅助进行自动化系统测试，确保业务逻辑正确性。

**CURL可用性验证 (P2)**：使用CURL或其他命令行工具，频繁且全面地测试后端所有API的可用性及工程级别可用性，确保后端独立稳定。

### 阶段C: 前端与用户体验中心设计 (P2: 人类主导设计，AI辅助实现)

**API接口文档生成 (P2)**：后端服务通过全业务场景全流程集成测试后，AI可自动生成基于API契约的、清晰明晰的API接口文档（如Swagger/OpenAPI）。

**用户体验驱动前端设计 (P1)**：
- **UX设计流程 (P1)**：依据用户需求、场景故事和用户画像，由人类UX专家主导用户体验设计，包括用户旅程图、信息架构、线框图、高保真原型。AI可辅助生成设计元素或UI草图。
- **迭代与可用性测试 (P1)**：在原型阶段即进行可用性测试，收集用户反馈，快速迭代设计。

**前端开发**：AI可辅助生成前端代码，但其与后端API的集成、用户体验流畅性、跨浏览器/设备兼容性等，需由人类前端工程师和UX专家严格审查。

### 阶段D: 综合测试与CI/CD (P1: 强制自动化，人类设计策略)

#### 持续集成/持续部署 (CI/CD) (P1)
必须实现CI/CD。所有代码提交（无论人工还是AI生成）都应触发自动化测试、构建和部署流程。

#### 测试前置与左移
尽可能在开发早期进行测试。

#### 自动化测试覆盖
强制要求高自动化测试覆盖率，包括：

**单元测试 (P1)**：严格执行原文档中"没有桩子函数，空函数，测试时针对某些功能测试时，其他模块或功能或函数可以增加开关使用桩子mock（但没有测试显示参数时，必须不能有任何桩子函数，mock，空函数和示例函数）"的原则。AI或自动化工具应能检测并强制执行此规则。

**集成测试 (P1)**：API、服务间集成测试。

**端到端测试 (P1)**：模拟用户操作的全流程测试。

#### AI模型专用测试 (P1)

**准确性与性能**：测试AI模型的预测准确性、推理速度。

**鲁棒性**：对抗性攻击测试，确保模型不受恶意输入干扰。

**公平性与偏见检测**：测试模型是否存在偏见，输出是否公平。

**模型漂移监控**：持续监控模型在生产环境下的性能变化，及时发现并处理模型漂移。

#### 非功能性测试 (P2)

**性能测试**：负载测试、压力测试、并发测试，确保系统满足非功能性需求。

**安全测试**：漏洞扫描、渗透测试、代码安全审计，尤其是针对AI生成代码的安全漏洞。

**兼容性测试**：不同浏览器、设备、操作系统下的兼容性。

#### CLI测试CI集成 (P1: 强制执行)

根据《AI编程项目终极实践手册》的项目宪法要求，已将CLI业务场景测试纳入CI/CD流程，建立了完整的工程可用性保障机制。

##### 强制检查项
-   **CLI业务场景贯通性测试**: 每次提交/合并前强制执行，确保核心业务流程的端到端可用性。
-   **四位一体自动化校验**: 接口、页面、AI代码、测试脚本之间的一致性强制检查。
-   **项目宪法合规性检查**: 自动检查AI标记、docstring、命名规范等是否符合项目宪法要求。

##### 核心业务场景测试
-   **格式对齐测试**: 验证文档格式统一和样式标准化。
-   **文风统一测试**: 确保文档风格一致性和专业性。
-   **智能填报测试**: 验证文档智能填充功能的准确性。
-   **文档评审测试**: 检查虚拟审阅系统的功能和报告生成。
-   **表格填充测试**: 验证表格智能识别和填充。

##### 保障机制
-   **阻断机制**: 任何P1优先级测试失败（包括CLI业务场景测试）都会立即阻止代码合并，确保问题在早期被发现和修复。
-   **持续改进**: 通过定期自动分析CLI测试报告，识别失败模式、性能瓶颈和遗漏场景，并生成改进建议。
-   **质量保障**: 通过CLI测试确保系统在各种条件下的工程可用性，并强制符合项目宪法要求。

### 阶段E: 部署、维护与持续改进 (P2: 监控与迭代)

**自动化部署与回滚 (P2)**：确保部署流程自动化，并具备快速、可靠的回滚机制。

**全面监控与告警 (P2)**：建立完善的日志、监控、告警系统，覆盖系统性能、错误率、AI模型表现等关键指标。

**用户反馈循环 (P2)**：建立结构化的用户反馈收集、分析和处理机制，定期评审反馈，驱动产品迭代。

**持续优化与重构 (P2)**：根据监控数据、用户反馈和新技术发展，持续优化系统架构和代码，进行必要的根本性修复和系统性重构。

---

## III. 🤝 AI协作与人类监督 (P1: 核心且最高优先级)

### 明确人类介入点 (P1)

**强制审核门**：对于所有AI生成的核心业务逻辑代码、安全敏感代码、关键架构设计文档、对外API契约、核心测试策略，强制设置P1级人工审核门禁，即使AI置信度再高也必须通过。

**风险等级划分**：明确AI生成内容的风险等级（高/中/低），并根据等级定义不同的人工审核深度与频率。

### AI生成内容的置信度与透明度 (P1)

**高置信度要求**：AI生成所有文档和代码时，必须在确信度0.99以上才自动生成。

**不确定性显目提示 (P1)**：AI有不确定的地方必须显目地提出来让用户确认和补充。例如：在代码中添加特殊注释`// AI_UNCERTAIN_START: [原因描述] // AI_UNCERTAIN_END`。

**用户引导与多方案 (P1)**：用户不理解或不知道如何确认时，AI应提供更多提示、多个备选方案并解释每个方案的优缺点，以提升AI自身置信度。

**拒绝在信息不完整时生成 (P1)**：AI绝不能在信息不完整或未经用户明确确认的情况下生成代码或关键文档。

**AI生成标记**：所有AI生成的文档和代码，必须包含明确的元数据标记，如`// @AI-Generated: [日期], Confidence: [0.xx], Version: [model_vX.Y]`。

### AI幻觉管理 (P1)

**警惕"自信的错误"**：强调AI的0.99置信度是其内部评估，不代表绝对真理。人类必须具备批判性思维，尤其是在关键领域。

**对比验证**：鼓励AI在关键决策点提供多条推理路径或多个解决方案，并解释其逻辑，供人类对比分析，识别潜在幻觉。

**"人类思维链"（CoT）要求**：在复杂或高风险场景下，要求AI提供其生成此内容或决策的"思考链"或"推理步骤"，辅助人类理解和验证其逻辑。

---

## IV. 🔍 问题诊断与修复 (P2: 系统化方法)

### 1. 症状分析：从用户反馈的问题现象入手
- 收集用户反馈的具体问题
- 分析错误信息和异常现象
- 识别问题的表现形式
- 确定问题的影响范围

### 2. 根本原因分析：使用第一性原理找出根本问题
- 从用户需求出发，而不是从代码实现出发
- 分析问题的根本原因，而不是表面现象
- 使用系统性思维分析整个流程
- 识别关键环节和依赖关系

### 3. 系统性验证：验证整个流程的完整性
- 追踪完整的数据流和调用链
- 验证每个环节是否都有对应实现
- 检查各环节之间的连接是否正确
- 确认异常情况是否有处理

### 4. 效果验证：确认修复是否真正解决问题
- 验证修复后的功能是否正常工作
- 确认是否真正解决了用户问题
- 测试边界情况和异常场景
- 验证修复是否引入了新问题

### 5. 修复策略选择
- **表面修复 (P3)**：应急处理，但必须记录并计划后续根本修复。
- **根本修复 (P2)**：找到并解决根本原因。
- **系统性修复 (P1)**：从架构层面重新设计，确保长期稳定。

---

## V. 📋 代码审查标准 (P1: 强制执行)

### L1 存在性检查：功能是否存在
- 检查方法、类、模块是否在代码中定义
- 验证文件结构是否完整
- 确认依赖关系是否正确

### L2 调用性检查：功能是否被调用
- 追踪方法调用链
- 验证API端点是否被正确路由
- 确认事件监听器是否被注册
- 检查配置是否正确加载

### L3 有效性检查：功能是否真正发挥作用
- 验证方法执行是否产生预期结果
- 检查数据流是否完整
- 确认逻辑分支是否正确执行
- 验证异常处理是否有效

### L4 需求满足检查：是否真正满足用户需求
- 从用户角度验证功能效果
- 确认用户体验是否符合预期
- 验证业务逻辑是否正确实现
- 检查是否解决了用户的根本问题

---

## VI. 🚀 项目特定实施要求

### 1. 项目定位与原则

#### 核心定位
**智能文档助手**专注于**文档组装、文风检测和智能审批**，不替代专业工具，而是帮助用户将分散的内容智能组装成高质量的专业文档。

**重要说明**：本系统为**单用户工具**，不支持多人协同编辑，专注于个人用户的文档处理需求。

#### 开发原则
1. **用户价值优先** - 专注于解决用户实际痛点
2. **质量保证** - 确保文档质量和一致性
3. **效率提升** - 自动化繁琐的格式调整和检查工作
4. **专业标准** - 确保文档符合行业标准和规范
5. **单用户体验** - 优化个人用户的使用体验，不涉及协作功能

### 2. 代码规范

#### Python代码规范

##### 1. 基本规范
- 遵循 **PEP 8** Python代码规范
- 使用 **Python 3.8+** 语法特性
- 所有函数必须有类型注解
- 所有类必须有文档字符串

##### 2. 命名规范
```python
# 类名：大驼峰命名法
class IntelligentImageProcessor:
    """智能图像处理器"""
    
# 函数名：小写字母+下划线
def process_document_content(content: str) -> Dict[str, Any]:
    """处理文档内容"""
    
# 变量名：小写字母+下划线
document_type = "patent"
processing_result = {}

# 常量名：大写字母+下划线
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
SUPPORTED_FORMATS = ['.docx', '.pdf', '.txt']
```

##### 3. 文档字符串规范
```python
def generate_svg_for_document(
    document_type: str, 
    content_description: str,
    svg_size: Tuple[int, int] = (400, 300)
) -> Dict[str, Any]:
    """
    根据文档类型和内容描述生成SVG图像
    
    Args:
        document_type: 文档类型 ('patent', 'project', 'general')
        content_description: 内容描述
        svg_size: SVG尺寸 (宽度, 高度)
        
    Returns:
        包含生成结果的字典:
        {
            'success': bool,
            'svg_path': str,
            'svg_content': str,
            'error': str (如果失败)
        }
        
    Raises:
        ValueError: 当文档类型无效时
        IOError: 当文件写入失败时
    """
```

##### 4. 错误处理规范
```python
def process_user_content(content: str) -> Dict[str, Any]:
    """处理用户内容"""
    try:
        # 主要处理逻辑
        result = perform_processing(content)
        return {
            'success': True,
            'result': result,
            'message': '处理成功'
        }
    except ValueError as e:
        # 处理参数错误
        return {
            'success': False,
            'error': f'参数错误: {str(e)}',
            'error_type': 'validation_error'
        }
    except Exception as e:
        # 处理其他错误
        logger.error(f"处理失败: {str(e)}")
        return {
            'success': False,
            'error': f'处理失败: {str(e)}',
            'error_type': 'processing_error'
        }
```

#### JavaScript代码规范

##### 1. 基本规范
- 使用 **ES6+** 语法特性
- 使用 **const** 和 **let**，避免 **var**
- 使用 **async/await** 处理异步操作
- 所有函数必须有注释说明

##### 2. 命名规范
```javascript
// 函数名：小驼峰命名法
async function processDocumentContent(content) {
    // 处理逻辑
}

// 变量名：小驼峰命名法
const documentType = 'patent';
let processingResult = {};

// 常量名：大写字母+下划线
const MAX_FILE_SIZE = 50 * 1024 * 1024; // 50MB
const SUPPORTED_FORMATS = ['.docx', '.pdf', '.txt'];
```

##### 3. 异步处理规范
```javascript
async function handleDocumentUpload(file) {
    try {
        showLoading('正在上传文档...');
        
        const formData = new FormData();
        formData.append('file', file);
        
        const response = await fetch('/api/upload', {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const result = await response.json();
        
        if (result.success) {
            showMessage('文档上传成功！', 'success');
            return result;
        } else {
            throw new Error(result.error || '上传失败');
        }
        
    } catch (error) {
        showMessage(`上传失败: ${error.message}`, 'error');
        return null;
    } finally {
        hideLoading();
    }
}
```

### 3. 架构设计规范

#### 1. 模块化设计
```
src/
├── core/                    # 核心业务模块
│   ├── agent/              # AI代理协调器
│   ├── analysis/           # 文档分析引擎
│   ├── tools/              # 核心工具集
│   ├── knowledge_base/     # 知识库
│   └── monitoring/         # 性能监控
├── llm_clients/            # LLM客户端
└── web_app.py             # Web应用入口
```

#### 2. 接口设计规范
```python
# 所有工具类必须实现基础接口
class BaseTool:
    """工具基类"""
    
    def __init__(self):
        self.name = self.__class__.__name__
        self.version = "1.0.0"
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """处理输入数据"""
        raise NotImplementedError
    
    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """验证输入数据"""
        raise NotImplementedError
    
    def get_status(self) -> Dict[str, Any]:
        """获取工具状态"""
        return {
            'name': self.name,
            'version': self.version,
            'status': 'ready'
        }
```

#### 3. 后端API接口开发规范

##### 3.1 接口开发流程
```
1. 需求分析 → 2. 接口设计 → 3. 后端实现 → 4. 接口文档更新 → 5. 前端调用示范 → 6. 测试验证
```

##### 3.2 新增后端接口必须遵循的规范

**强制要求**：
- ✅ **必须更新后端接口开发文档** (`docs/APIReference.md`)
- ✅ **必须设计前端调用示范说明**
- ✅ **必须包含完整的请求/响应格式**
- ✅ **必须提供错误处理示例**

##### 3.3 接口文档更新规范

**新增接口必须在`APIReference.md`中添加**：
```markdown
### 新功能模块接口

- **POST /api/new-feature/action**  
  功能：新功能描述。  
  描述：详细的功能说明和使用场景。
  
  **请求参数**：
  ```json
  {
    "param1": "string",
    "param2": "number",
    "param3": {
      "nested": "object"
    }
  }
  ```
  
  **响应格式**：
  ```json
  {
    "success": true,
    "result": {
      "data": "处理结果"
    },
    "message": "操作成功"
  }
  ```
  
  **错误响应**：
  ```json
  {
    "success": false,
    "error": "错误描述",
    "error_code": "ERROR_CODE"
  }
  ```
```

##### 3.4 前端调用示范规范

**必须提供完整的前端调用示例**：

```javascript
// 前端调用示范 - 新功能接口
async function callNewFeatureAPI(params) {
    try {
        // 显示加载状态
        showLoading('正在处理...');
        
        const response = await fetch('/api/new-feature/action', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(params)
        });
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const result = await response.json();
        
        if (result.success) {
            // 成功处理
            showMessage('操作成功！', 'success');
            return result.result;
        } else {
            // 业务错误
            throw new Error(result.error || '操作失败');
        }
        
    } catch (error) {
        // 错误处理
        showMessage(`操作失败: ${error.message}`, 'error');
        console.error('API调用失败:', error);
        return null;
    } finally {
        // 隐藏加载状态
        hideLoading();
    }
}

// 使用示例
const params = {
    param1: 'value1',
    param2: 123,
    param3: { nested: 'value' }
};

const result = await callNewFeatureAPI(params);
if (result) {
    // 处理成功结果
    console.log('处理结果:', result);
}
```

##### 3.5 接口实现规范

**后端接口实现必须包含**：
```python
@app.route('/api/new-feature/action', methods=['POST'])
def new_feature_action():
    """
    新功能接口
    
    请求参数:
    {
        "param1": "string - 参数1说明",
        "param2": "number - 参数2说明",
        "param3": {
            "nested": "string - 嵌套参数说明"
        }
    }
    
    响应格式:
    {
        "success": true,
        "result": {
            "data": "处理结果"
        },
        "message": "操作成功"
    }
    
    错误响应:
    {
        "success": false,
        "error": "错误描述",
        "error_code": "ERROR_CODE"
    }
    """
    try:
        # 1. 参数验证
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': '请求参数不能为空',
                'error_code': 'INVALID_PARAMS'
            }), 400
        
        # 2. 参数提取和验证
        param1 = data.get('param1')
        param2 = data.get('param2')
        param3 = data.get('param3', {})
        
        if not param1:
            return jsonify({
                'success': False,
                'error': 'param1是必需参数',
                'error_code': 'MISSING_PARAM1'
            }), 400
        
        # 3. 业务逻辑处理
        result = process_new_feature(param1, param2, param3)
        
        # 4. 返回成功响应
        return jsonify({
            'success': True,
            'result': result,
            'message': '操作成功'
        })
        
    except ValueError as e:
        # 参数错误
        return jsonify({
            'success': False,
            'error': f'参数错误: {str(e)}',
            'error_code': 'VALIDATION_ERROR'
        }), 400
        
    except Exception as e:
        # 系统错误
        logger.error(f"新功能处理失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'系统错误: {str(e)}',
            'error_code': 'SYSTEM_ERROR'
        }), 500
```

##### 3.6 接口测试规范

**必须包含的测试用例**：
```python
class TestNewFeatureAPI(unittest.TestCase):
    """新功能接口测试"""
    
    def test_new_feature_success(self):
        """测试成功场景"""
        data = {
            "param1": "test_value",
            "param2": 123,
            "param3": {"nested": "test"}
        }
        
        response = self.client.post('/api/new-feature/action', 
                                  json=data)
        
        self.assertEqual(response.status_code, 200)
        result = response.get_json()
        self.assertTrue(result['success'])
        self.assertIn('result', result)
    
    def test_new_feature_missing_params(self):
        """测试缺少参数场景"""
        data = {"param2": 123}  # 缺少param1
        
        response = self.client.post('/api/new-feature/action', 
                                  json=data)
        
        self.assertEqual(response.status_code, 400)
        result = response.get_json()
        self.assertFalse(result['success'])
        self.assertIn('param1是必需参数', result['error'])
    
    def test_new_feature_invalid_params(self):
        """测试无效参数场景"""
        data = {
            "param1": "",  # 空字符串
            "param2": "not_a_number"  # 非数字
        }
        
        response = self.client.post('/api/new-feature/action', 
                                  json=data)
        
        self.assertEqual(response.status_code, 400)
        result = response.get_json()
        self.assertFalse(result['success'])
```

##### 3.7 文档同步检查清单

**开发完成后必须检查**：
- [ ] 后端接口开发文档已更新 (`docs/APIReference.md`)
- [ ] 前端调用示范已编写并测试
- [ ] 接口参数和响应格式已完整记录
- [ ] 错误处理场景已覆盖
- [ ] 测试用例已编写并通过
- [ ] 代码注释已完善
- [ ] Git提交信息符合规范

#### 4. 配置管理规范
```python
# 使用YAML配置文件
# config/config.yaml
app:
  name: "智能文档助手"
  version: "3.0.0"
  debug: false

llm:
  default_provider: "xingcheng"
  providers:
    xingcheng:
      api_key: "${XINGCHENG_API_KEY}"
      api_secret: "${XINGCHENG_API_SECRET}"
    qiniu:
      api_key: "${QINIU_API_KEY}"

processing:
  max_file_size: 52428800  # 50MB
  supported_formats: [".docx", ".pdf", ".txt"]
  temp_dir: "./temp"
```

### 4. 测试规范

#### 1. 测试文件命名
```
tests/
├── test_svg_integration.py           # SVG集成测试
├── test_comprehensive_integration.py # 综合集成测试
├── test_e2e_framework.py             # 端到端测试框架
├── test_writing_style_analysis.py    # 文风分析测试
└── test_document_fill.py             # 文档填充测试
```

#### 2. 测试用例规范
```python
class TestSVGIntegration(unittest.TestCase):
    """SVG集成功能测试类"""
    
    def setUp(self):
        """测试前准备"""
        self.image_processor = IntelligentImageProcessor()
        self.temp_dir = tempfile.mkdtemp()
    
    def test_generate_svg_image(self):
        """测试SVG图像生成"""
        print("测试SVG图像生成...")
        
        # 测试逻辑
        result = self.image_processor.generate_svg_image(...)
        
        # 断言验证
        self.assertTrue(result["success"])
        self.assertIn("svg_path", result)
        
        print("✓ SVG生成成功")
    
    def tearDown(self):
        """测试后清理"""
        if hasattr(self, 'temp_dir') and os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
```

#### 3. 测试覆盖率要求
- **单元测试**: 85%+
- **集成测试**: 90%+
- **端到端测试**: 80%+
- **性能测试**: 75%+

### 5. 文档规范

#### 1. 代码注释规范
```python
# 单行注释：解释复杂逻辑
complex_calculation = (base_value * multiplier) + offset

# 多行注释：解释复杂算法
"""
算法说明：
1. 首先进行数据预处理
2. 然后应用核心算法
3. 最后进行结果验证
"""

def complex_algorithm(data):
    # 步骤1：数据预处理
    processed_data = preprocess(data)
    
    # 步骤2：核心算法
    result = core_algorithm(processed_data)
    
    # 步骤3：结果验证
    validated_result = validate_result(result)
    
    return validated_result
```

#### 2. API文档规范
```python
@app.route('/api/svg/generate', methods=['POST'])
def generate_svg_image():
    """
    生成SVG图像API
    
    请求参数:
    {
        "document_type": "patent|project|general",
        "content_description": "内容描述",
        "svg_size": [400, 300]
    }
    
    响应格式:
    {
        "success": true,
        "svg_path": "/path/to/svg",
        "svg_content": "<svg>...</svg>",
        "svg_id": "unique_id"
    }
    
    错误响应:
    {
        "success": false,
        "error": "错误信息"
    }
    """
```

#### 3. 前后端接口文档一致性规范

##### 3.1 接口文档同步要求
- ✅ **后端接口开发文档** (`docs/APIReference.md`) 必须与代码实现保持同步
- ✅ **前端调用示范** 必须与后端接口定义完全一致
- ✅ **请求/响应格式** 必须前后端统一
- ✅ **错误处理机制** 必须前后端协调

##### 3.2 接口文档更新流程
```
后端接口变更 → 更新后端接口文档 → 更新前端调用示范 → 同步测试用例 → 验证一致性
```

##### 3.3 接口文档检查清单
**每次接口变更后必须检查**：
- [ ] 后端接口开发文档已更新
- [ ] 前端调用示范已同步更新
- [ ] 请求参数格式前后端一致
- [ ] 响应数据格式前后端一致
- [ ] 错误码和错误信息前后端一致
- [ ] 测试用例已更新并通过
- [ ] 文档版本号已更新

##### 3.4 接口文档模板规范

**后端接口文档模板**：
```markdown
### 功能模块名称

- **POST /api/module/action**  
  功能：功能描述。  
  描述：详细的功能说明和使用场景。
  
  **请求参数**：
  ```json
  {
    "param1": "string - 参数1说明",
    "param2": "number - 参数2说明",
    "param3": {
      "nested": "string - 嵌套参数说明"
    }
  }
  ```
  
  **响应格式**：
  ```json
  {
    "success": true,
    "result": {
      "data": "处理结果"
    },
    "message": "操作成功"
  }
  ```
  
  **错误响应**：
  ```json
  {
    "success": false,
    "error": "错误描述",
    "error_code": "ERROR_CODE"
  }
  ```
  
  **前端调用示例**：
  ```javascript
  async function callModuleAPI(params) {
      try {
          const response = await fetch('/api/module/action', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify(params)
          });
          
          const result = await response.json();
          if (result.success) {
              return result.result;
          } else {
              throw new Error(result.error);
          }
      } catch (error) {
          console.error('API调用失败:', error);
          throw error;
      }
  }
  ```
```

##### 3.5 版本控制规范
- 接口文档版本号格式：`v主版本.次版本.修订版本`
- 重大接口变更必须升级主版本号
- 新增接口功能升级次版本号
- 文档修正升级修订版本号
- 每次更新必须在文档头部记录变更历史

##### 3.6 接口文档维护责任
- **后端开发者**：负责后端接口文档的准确性和完整性
- **前端开发者**：负责前端调用示范的正确性和可用性
- **项目负责人**：负责接口文档的整体协调和版本管理
- **测试人员**：负责验证前后端接口文档的一致性

### 6. 工作流程规范

#### 1. 开发流程
```
1. 文档先行 → 2. 状态检测 → 3. 设计方案 → 4. 代码实现 → 5. 测试验证 → 6. Git提交
```

#### 2. Git提交规范
```bash
# 提交格式
<type>(<scope>): <subject>

# 类型说明
feat:     新功能
fix:      修复bug
docs:     文档更新
style:    代码格式调整
refactor: 代码重构
test:     测试相关
chore:    构建过程或辅助工具的变动

# 示例
feat(svg): 添加SVG生成和插入功能
fix(api): 修复文档上传API错误
docs(readme): 更新项目定位和功能介绍
```

#### 3. 分支管理规范
```
main          # 主分支，稳定版本
develop       # 开发分支，集成测试
feature/*     # 功能分支
hotfix/*      # 紧急修复分支
release/*     # 发布分支
```

### 7. 质量保证规范

#### 1. 代码审查要求
- 所有代码必须经过审查
- 审查重点：功能正确性、代码质量、安全性
- 审查人员：至少1名资深开发者

#### 2. 性能要求
- 响应时间：平均2-5秒
- 并发处理：支持10+并发用户
- 内存使用：控制在4GB以内
- CPU使用率：平均30-50%

#### 3. 安全要求
- 输入验证：所有用户输入必须验证
- 文件上传：限制文件类型和大小
- API安全：使用HTTPS，验证API密钥
- 数据保护：敏感数据加密存储

### 8. 部署规范

#### 1. 环境配置
```bash
# 生产环境配置
export FLASK_ENV=production
export FLASK_DEBUG=false
export DATABASE_URL=sqlite:///production.db
export LOG_LEVEL=INFO
```

#### 2. 启动脚本
```bash
#!/bin/bash
# start.sh

# 检查环境
python -c "import sys; sys.exit(0 if sys.version_info >= (3,8) else 1)"

# 安装依赖
pip install -r requirements.txt

# 启动应用
python -m src.web_app
```

#### 3. 监控要求
- 应用健康检查
- 性能监控
- 错误日志记录
- 资源使用监控

### 9. 检查清单

#### 开发前检查
- [ ] 已阅读项目定位和开发原则
- [ ] 了解相关功能模块
- [ ] 明确开发目标和范围
- [ ] 准备好测试方案

#### 开发中检查
- [ ] 遵循代码规范
- [ ] 添加必要的注释
- [ ] 编写测试用例
- [ ] 进行代码审查

#### 开发后检查
- [ ] 所有测试通过
- [ ] 文档已更新
- [ ] 代码已提交
- [ ] 功能已验证
- [ ] **后端接口开发文档已同步更新**
- [ ] **前端调用示范已编写并测试**
- [ ] **接口参数和响应格式前后端一致**
- [ ] **错误处理机制前后端协调**

### 10. 前端页面与 JS/自动化测试一致性规范

1. **元素命名唯一且规范**
   - 页面中所有需要被 JS 操作或自动化测试定位的元素，必须设置唯一且规范的 `id`。
   - `id` 命名应与 JS 逻辑、自动化测试脚本严格一致，避免随意更改。

2. **class 用于样式，id 用于交互**
   - `class` 主要用于样式控制，`id` 用于 JS 事件绑定和自动化测试。
   - 不允许仅用 `class` 进行 JS 事件绑定或测试定位，除非特殊说明。

3. **页面结构变更需同步更新 JS 和测试**
   - 页面结构、元素命名发生变更时，必须同步检查并更新相关 JS 逻辑和自动化测试脚本。
   - 变更需在代码评审时重点关注前端与 JS/测试的一致性。

4. **开发自测与联调**
   - 前端开发完成后，需本地自测页面交互和自动化测试用例，确保所有功能和测试均可正常运行。
   - 联调阶段如发现命名不一致，需及时修正并同步相关代码。

5. **自动化测试健壮性**
   - 自动化测试脚本应有明确的报错提示，便于快速定位页面元素缺失或命名错误。
   - 如有必要，可增加 class 兜底查找，但以 id 为主。

6. **命名规范文档化**
   - 项目内需维护一份常用页面元素 id/class 命名对照表，便于开发、测试和维护人员查阅。

### 11. 四位一体一致性与自动化校验
- 所有前后端接口、页面元素、AI代码、测试脚本必须保持一致，变更需自动化校验。
- 引入接口文档（如OpenAPI）、页面元素id/class对照表、AI代码与测试脚本自动比对工具。
- 每次合并前自动校验接口、页面、AI代码、测试脚本的一致性。

### 12. 持续集成与测试三位一体
- 所有代码提交必须通过CI自动化测试，包括单元、集成、端到端、可用性测试。
- 自动化测试覆盖主流程、异常、边界、权限、性能等。
- 定期人工体验测试，补充自动化难以覆盖的极端和体验场景。

### 13. 命名规范、组件化、接口文档、变更同步
- 元素id/class、API接口、AI代码、测试脚本命名规范化，维护对照表。
- 前端组件化开发，复用交互和样式，减少遗漏。
- 所有接口变更需同步更新接口文档、前端、AI代码、测试脚本。

### 14. AI代码自动校验与测试
- AI生成代码后，自动运行linter、类型检查、单元/集成/端到端测试。
- 发现问题自动修正，未通过禁止合并。
- AI生成的测试用例需覆盖主流程、异常、边界。

### 15. 问题复盘与持续改进
- 每次问题复盘后，及时补充规范、测试、自动化脚本。
- 形成规范-开发-测试-复盘-改进的正向闭环。

### 16. 前端组件化最佳实践
- 所有可复用区域、功能块应封装为组件，统一命名、文档化、便于复用和维护。
- 组件需有独立的 props/参数说明和用法文档。
- 组件变更需同步更新相关页面、测试脚本。
- 组件需有单元测试和端到端测试覆盖。
- 鼓励使用现代前端框架（如Vue/React）或自定义组件体系。

### 17. docstring 规范要求
- 所有API、函数、类、组件、测试脚本均需有规范docstring。
- docstring内容应包括：功能说明、参数、返回、异常、示例等。
- 变更时需同步更新docstring，确保自动文档准确。
- 鼓励采用Google、NumPy或reST风格，便于自动提取。

#### docstring 模板示例

##### API函数（Google风格）
"""
分析文档写作风格。

Args:
    document_content (str): 文档内容。
    document_name (str): 文档名。

Returns:
    dict: 分析结果。

Raises:
    ValueError: 输入无效时抛出。

Example:
    result = analyze_writing_style('内容', 'test.txt')
"""

##### 普通函数/类（NumPy风格）
"""
函数说明。

Parameters
----------
param1 : int
    参数1说明。
param2 : str
    参数2说明。

Returns
-------
bool
    返回值说明。

Raises
------
Exception
    异常说明。
"""

##### 组件/测试脚本（reST风格）
"""
组件/测试脚本说明。

:param arg1: 参数1说明
:type arg1: int
:return: 返回值说明
:rtype: bool
:raises Exception: 异常说明
"""

### 18. API返回与前端健壮性强制规范
1. 后端所有API无论成功还是失败，均必须返回结构化JSON，且结构统一，如：
   { "success": true/false, "data": {...}, "error": "错误信息", "code": 123 }
   - 绝不允许返回HTML错误页、未定义结构或直接500。
   - 全局异常处理器自动包装所有异常为标准结构。
2. 前端所有API调用点，均不得假设数据一定存在或类型正确，必须做类型和存在性检查。
   - 任何数组操作、对象属性访问前，先判断类型和存在性。
   - 统一用全局拦截器/工具函数处理API响应。
3. 所有异常和错误都必须被优雅兜底和用户友好提示，用户永远不会看到页面崩溃或未处理的报错。
   - 错误信息通过统一的提示组件展示。
   - 未捕获异常自动上报监控系统。
4. 自动化测试和代码评审必须覆盖所有主流程和异常分支，确保无论后端如何异常，前端都不会崩溃。
5. 定期复盘线上异常，持续补充兜底和测试用例。

### 19. API协议与调用规范（强制）
1. 所有后端API必须兼容`application/json`和`multipart/form-data`两种主流Content-Type。
   - 优先解析JSON，兼容FormData，其他类型返回结构化错误。
   - 所有异常分支都返回`{'success': False, 'error': ...}`结构，绝不返回HTML或500。
2. 所有前端API调用必须封装为统一工具函数，禁止裸用fetch/axios。
   - 纯文本/参数分析请求一律用`application/json`。
   - 文件上传场景一律用FormData，后端需兼容。
   - 所有API调用点必须有异常兜底，用户永不见页面崩溃。
3. 自动化测试和CI必须覆盖所有Content-Type分支和异常分支。
   - CI自动校验API协议和前端调用方式一致性，发现不符立即阻断合并。
   - 所有API返回结构必须包含`success`、`error`等字段，禁止HTML/未定义结构。

### 20. 前后端健壮性与安全规范
- 所有数组/对象操作前必须做类型和存在性检查。
- 所有异常和错误都必须兜底提示，用户永不见页面崩溃。
- 所有文件操作必须做路径和权限检查，禁止硬编码绝对路径。
- 所有上传/下载接口必须有安全校验和异常兜底。

### 21. 依赖与环境规范
- 所有依赖必须写入requirements.txt，禁止隐式依赖。
- CI自动检测依赖缺失和环境不一致。

### 22. 复盘与持续改进
- 每次线上异常必须复盘，补充用例和CI规则，形成闭环。

### 23. 代码质量要求

#### 严禁桩函数、桩类、未实现的示例代码进入项目
- **所有类必须有完整实现**，禁止使用pass语句作为类体
- **所有函数必须有实际功能**，禁止返回硬编码的模拟数据
- **如需向后兼容，使用类型别名而非继承桩类**
- **TODO标记必须在下一个版本中实现**
- **代码审查时必须检查是否存在桩类/桩函数**

#### 示例
```python
# ❌ 禁止：桩类
class MultiLLMClient(EnhancedMultiLLMClient):
    pass

# ✅ 正确：类型别名
MultiLLMClient = EnhancedMultiLLMClient

# ❌ 禁止：桩函数
def process_data(data):
    pass

# ✅ 正确：完整实现
def process_data(data):
    if not data:
        return None
    return data.upper()

# ❌ 禁止：模拟数据
def get_user_info():
    return {"name": "张三", "age": 25}  # 硬编码

# ✅ 正确：真实实现
def get_user_info(user_id):
    return database.get_user(user_id)
```

---

## VII. 📋 执行检查清单

### 开发前检查 (P1)
- [ ] 已完成深度需求工程与用户确认
- [ ] 已制定详细测试用例和验收标准
- [ ] 已设计系统架构并获得架构师审批
- [ ] 已明确AI协作边界和人类介入点
- [ ] 已评估项目风险等级和审核要求

### 开发中检查 (P1)
- [ ] AI生成代码已通过L1-L4代码审查
- [ ] 所有API已通过CURL可用性验证
- [ ] 前端设计已通过UX专家审查
- [ ] 自动化测试覆盖率达标
- [ ] AI生成内容已标记置信度和来源

### 发布前检查 (P1)
- [ ] 所有CI/CD流程通过
- [ ] 性能测试满足非功能性需求
- [ ] 安全测试无重大漏洞
- [ ] 用户验收测试通过
- [ ] 监控和告警系统就绪

### 发布后检查 (P2)
- [ ] 系统运行稳定，无重大异常
- [ ] 用户反馈收集机制正常
- [ ] 性能监控数据正常
- [ ] 定期进行问题复盘和改进

---

## VIII. 📞 责任分工与联系方式

### 核心角色定义
- **项目架构师**：负责系统架构设计和关键技术决策
- **UX专家**：负责用户体验设计和用户需求确认
- **测试专家**：负责测试策略制定和测试用例设计
- **安全专家**：负责安全审查和风险评估
- **AI协作专家**：负责AI工具使用规范和幻觉管理

### 紧急联系机制
- 高风险问题：立即上报项目架构师和安全专家
- 用户体验问题：联系UX专家进行快速评估
- 技术实现问题：联系相关技术负责人
- AI相关问题：联系AI协作专家进行审查

---

## IX. 📈 持续改进机制

### 定期评估
- 每月评估AI协作效果和人类监督质量
- 每季度评估项目整体进展和风险控制
- 每年评估手册适用性和更新需求

### 反馈收集
- 建立AI协作效果反馈机制
- 收集人类监督过程中的问题和建议
- 定期更新最佳实践和检查清单

### 知识积累
- 建立AI项目经验库
- 记录常见问题和解决方案
- 分享成功案例和失败教训

---

**文档版本**: v1.0 (2025年1月28日)  
**适用范围**: 所有AI编程项目  
**审核状态**: 待审核  
**维护责任**: 项目架构师 + AI协作专家  
**更新频率**: 季度评估，年度更新  

---

*本手册是项目开发的最高宪法，所有团队成员必须严格遵守。任何违反本手册原则的行为都将被视为严重违规，需要立即纠正并记录在案。*

[
  {
    "title": "P0原则：工程纯粹性与反冗余",
    "content": "绝不允许桩子、空占位符、非生产代码进入生产环境。所有测试和实现均基于真实接口和功能。自动化工具和CI强制检测。",
    "scenarios": ["代码生成", "代码审查", "CI检测"]
  },
  {
    "title": "P0原则：禁止可变全局状态共享",
    "content": "绝对禁止可变全局变量跨模块/进程共享状态。所有状态传递需显式、可追踪。推荐依赖注入、参数传递、外部存储。",
    "scenarios": ["架构设计", "代码生成", "代码审查", "CI检测"]
  },
  {
    "title": "P0原则：未确认不生成与高置信度",
    "content": "AI遇到信息不全、歧义时，必须显著提示并寻求用户确认，绝不擅自生成。所有生成内容需高置信度并添加元数据标记。",
    "scenarios": ["AI交互", "代码生成", "文档生成"]
  },
  {
    "title": "P0原则：有效沟通与上下文管理",
    "content": "每次交互聚焦单一问题，主动管理上下文长度，关键决策持久化记忆。",
    "scenarios": ["AI交互", "需求澄清"]
  },
  {
    "title": "P1原则：验证驱动与唯一数据源",
    "content": "所有代码/文档生成同步考虑验证与测试，常量、状态码、接口契约集中管理，测试/文档/实现强绑定唯一数据源。",
    "scenarios": ["代码生成", "测试生成", "文档生成", "CI检测"]
  },
  {
    "title": "P1原则：Mock限制",
    "content": "Mock仅限于隔离外部依赖，核心业务逻辑严禁Mock。测试用例必须基于真实接口和功能。",
    "scenarios": ["测试生成", "代码审查", "CI检测"]
  },
  {
    "title": "CI/CD门禁与自动化检测",
    "content": "Pre-commit钩子和CI/CD流水线自动化检测P0/P1原则，未通过禁止提交/合并。全量回归测试和契约校验强制执行。",
    "scenarios": ["CI/CD配置", "代码提交", "自动化检测"]
  },
  {
    "title": "AI元数据标记规范",
    "content": "所有AI生成内容需添加元数据标记：// @AI-Generated: [日期], Confidence: [0.xx], Model: [model_vX.Y], Prompt: [SHA_of_prompt]。",
    "scenarios": ["代码生成", "文档生成", "测试生成"]
  },
  {
    "title": "AI提示词范例：需求工程与系统架构",
    "content": "请作为产品经理和架构师，提炼用户故事、用户画像、功能列表、NFRs，并指出模糊点寻求确认。所有内容可验证并附验收标准。",
    "scenarios": ["需求分析", "AI交互"]
  },
  {
    "title": "AI提示词范例：API与后端开发",
    "content": "请生成OpenAPI 3.0规范YAML定义和FastAPI核心业务逻辑，所有状态共享显式传递，禁止桩子/空函数/全局变量。代码顶部添加AI生成标记。",
    "scenarios": ["API设计", "后端开发", "AI交互"]
  },
  {
    "title": "AI提示词范例：测试与CI/CD",
    "content": "请为指定函数生成pytest单元测试，覆盖正常、边界、异常情况，禁止Mock核心业务逻辑，添加AI生成标记。",
    "scenarios": ["测试开发", "AI交互"]
  },
  {
    "title": "AI提示词范例：代码审查",
    "content": "请审查代码，识别可变全局变量、桩子、空函数、隐式状态依赖等，提出改进建议并给出置信度评估。",
    "scenarios": ["代码审查", "AI交互"]
  }
]
