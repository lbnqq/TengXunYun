import os
import sys
import json
import uuid
import traceback
from datetime import datetime
from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.agent.agent_orchestrator import AgentOrchestrator
from src.llm_clients.xingcheng_llm import XingchengLLMClient
from src.llm_clients.multi_llm import MultiLLMClient
from src.core.tools.format_alignment_coordinator import FormatAlignmentCoordinator
from src.core.tools.document_fill_coordinator import DocumentFillCoordinator
from src.core.tools.writing_style_analyzer import WritingStyleAnalyzer

# Load environment variables
load_dotenv()

# 获取当前文件所在目录
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)

# 创建Flask应用，指定模板和静态文件路径
app = Flask(__name__, 
           template_folder=os.path.join(project_root, 'templates'),
           static_folder=os.path.join(project_root, 'static'))
CORS(app)

# Configuration
app.config['UPLOAD_FOLDER'] = os.path.join(project_root, 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['ALLOWED_EXTENSIONS'] = {'txt', 'pdf', 'docx'}

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(os.path.join(project_root, 'output'), exist_ok=True)

# 全局变量存储协调器实例
orchestrator_instance = None
format_coordinator = None
fill_coordinator = None
style_analyzer = None

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def initialize_agent(api_type="xingcheng", model_name=None):
    """Initialize the document agent with specified LLM client."""
    KB_PATH = os.path.join(project_root, "src/core/knowledge_base")
    
    if api_type == "multi":
        # 使用多API客户端
        try:
            llm_client = MultiLLMClient()
            print("MultiLLMClient initialized successfully")
            return AgentOrchestrator(llm_client=llm_client, kb_path=KB_PATH)
        except Exception as e:
            print(f"Error initializing MultiLLMClient: {e}")
            print("Falling back to mock mode")
            return None
    elif api_type == "xingcheng":
        # 使用讯飞星火API
        XINGCHENG_API_KEY = os.getenv("XINGCHENG_API_KEY")
        XINGCHENG_API_SECRET = os.getenv("XINGCHENG_API_SECRET")
        LLM_MODEL_NAME = model_name or os.getenv("LLM_MODEL_NAME", "x1")
        
        if not XINGCHENG_API_KEY:
            print("Warning: Xingcheng API key not configured, using mock mode")
            return None
        
        try:
            llm_client = XingchengLLMClient(
                api_key=XINGCHENG_API_KEY,
                api_secret=XINGCHENG_API_SECRET,
                model_name=LLM_MODEL_NAME
            )
            return AgentOrchestrator(llm_client=llm_client, kb_path=KB_PATH)
        except Exception as e:
            print(f"Error initializing XingchengLLMClient: {e}")
            print("Falling back to mock mode")
            return None
    else:
        print(f"Unknown API type: {api_type}, using mock mode")
        return None

def analyze_document_scenario(content):
    """智能分析文档场景和类型"""
    if not content:
        return '通用文档', '办公文档', ['文档内容分析', '结构优化建议']

    content_lower = content.lower()

    # 会议文档检测
    meeting_keywords = ['会议', 'meeting', '议程', '决议', '讨论', '参会', '会议纪要', '决策']
    if any(keyword in content_lower for keyword in meeting_keywords):
        return '会议文档', '这是一份会议相关文档，记录了会议议程、讨论内容和决策结果', [
            '会议主题和目标', '参会人员信息', '讨论的关键议题', '达成的决策和共识', '后续行动计划'
        ]

    # 技术文档检测
    tech_keywords = ['技术', 'technical', '系统', '架构', '开发', '代码', 'api', '数据库', '算法']
    if any(keyword in content_lower for keyword in tech_keywords):
        return '技术文档', '这是一份技术文档，涉及系统设计、开发规范或技术实现', [
            '技术架构设计', '核心功能模块', '性能和安全要求', '开发和部署流程', '维护和优化建议'
        ]

    # 产品文档检测
    product_keywords = ['产品', 'product', '功能', '需求', '用户', '市场', '竞品', '规划']
    if any(keyword in content_lower for keyword in product_keywords):
        return '产品文档', '这是一份产品相关文档，描述了产品功能、需求或市场策略', [
            '产品核心功能', '目标用户群体', '市场定位分析', '功能优先级', '产品发展路线图'
        ]

    # 分析报告检测
    report_keywords = ['报告', 'report', '分析', '总结', '数据', '统计', '趋势', '结论']
    if any(keyword in content_lower for keyword in report_keywords):
        return '分析报告', '这是一份分析报告，包含数据分析、趋势总结和结论建议', [
            '关键数据指标', '趋势分析结果', '问题识别和原因', '改进建议方案', '预期效果评估'
        ]

    # 商业文档检测
    business_keywords = ['商业', 'business', '合同', '协议', '方案', '提案', '预算', '成本']
    if any(keyword in content_lower for keyword in business_keywords):
        return '商业文档', '这是一份商业文档，涉及商业计划、合同协议或财务分析', [
            '商业目标和策略', '财务预算分析', '风险评估', '合作伙伴关系', '执行时间表'
        ]

    return '通用文档', '这是一份通用办公文档，包含多种类型的信息和内容', [
        '文档主要内容', '关键信息要点', '重要观点总结', '行动建议事项'
    ]

def generate_content_summary(content, max_length=200):
    """智能生成内容摘要"""
    if not content:
        return "文档内容为空，无法生成摘要。"

    # 分句处理
    sentences = content.replace('。', '。\n').replace('！', '！\n').replace('？', '？\n').split('\n')
    sentences = [s.strip() for s in sentences if s.strip() and len(s.strip()) > 5]

    if not sentences:
        return content[:max_length] + ("..." if len(content) > max_length else "")

    # 识别关键句子（包含重要关键词的句子）
    important_keywords = [
        '决策', '决定', '结论', '建议', '计划', '目标', '重要', '关键',
        '核心', '主要', '首先', '其次', '最后', '总结', '概述',
        '问题', '解决', '方案', '策略', '措施', '行动', '执行'
    ]

    # 给句子打分
    sentence_scores = []
    for i, sentence in enumerate(sentences):
        score = 0
        # 位置权重：开头和结尾的句子更重要
        if i == 0:
            score += 3
        elif i == len(sentences) - 1:
            score += 2
        elif i < len(sentences) * 0.3:  # 前30%
            score += 1

        # 关键词权重
        for keyword in important_keywords:
            if keyword in sentence:
                score += 2

        # 长度权重：适中长度的句子更可能包含重要信息
        if 20 <= len(sentence) <= 100:
            score += 1

        # 数字权重：包含数字的句子通常更重要
        import re
        if re.search(r'\d+', sentence):
            score += 1

        sentence_scores.append((sentence, score))

    # 按分数排序，选择最重要的句子
    sentence_scores.sort(key=lambda x: x[1], reverse=True)

    # 构建摘要
    summary_sentences = []
    current_length = 0

    for sentence, score in sentence_scores:
        if current_length + len(sentence) <= max_length - 20:  # 留一些余量
            summary_sentences.append(sentence)
            current_length += len(sentence)
        else:
            break

    # 如果没有选中任何句子，使用前几句
    if not summary_sentences:
        summary_sentences = sentences[:2]

    # 按原文顺序重新排列
    final_sentences = []
    for sentence in sentences:
        if sentence in summary_sentences:
            final_sentences.append(sentence)

    summary = '。'.join(final_sentences)
    if not summary.endswith('。'):
        summary += '。'

    # 如果还是太长，截断
    if len(summary) > max_length:
        summary = summary[:max_length-3] + "..."

    return summary

def extract_key_entities(content):
    """智能提取关键实体和概念"""
    if not content:
        return []

    import re
    entities = []

    # 1. 时间实体提取
    time_patterns = [
        (r'\d{4}年\d{1,2}月\d{1,2}日', '具体日期'),
        (r'\d{1,2}月\d{1,2}日', '月日'),
        (r'\d{4}-\d{1,2}-\d{1,2}', '日期'),
        (r'\d{1,2}:\d{2}', '时间'),
        (r'下周|本周|上周|下月|本月|上月', '相对时间')
    ]

    for pattern, type_name in time_patterns:
        matches = re.findall(pattern, content)
        for match in matches[:2]:  # 限制每种类型最多2个
            entities.append({'type': type_name, 'value': match})

    # 2. 数值实体提取
    number_patterns = [
        (r'\d+%', '百分比'),
        (r'\d+万元?', '金额(万)'),
        (r'\d+亿元?', '金额(亿)'),
        (r'￥\d+', '人民币'),
        (r'\$\d+', '美元'),
        (r'\d+人', '人数'),
        (r'\d+个', '数量'),
        (r'\d+项', '项目数')
    ]

    for pattern, type_name in number_patterns:
        matches = re.findall(pattern, content)
        for match in matches[:2]:
            entities.append({'type': type_name, 'value': match})

    # 3. 人名提取（简单的中文人名模式）
    name_patterns = [
        r'[张王李赵刘陈杨黄周吴徐孙胡朱高林何郭马罗梁宋郑谢韩唐冯于董萧程曹袁邓许傅沈曾彭吕苏卢蒋蔡贾丁魏薛叶阎余潘杜戴夏钟汪田任姜范方石姚谭廖邹熊金陆郝孔白崔康毛邱秦江史顾侯邵孟龙万段雷钱汤尹黎易常武乔贺赖龚文][一-龯]{1,2}',
    ]

    for pattern in name_patterns:
        matches = re.findall(pattern, content)
        # 过滤掉一些常见的非人名词汇
        filtered_matches = [m for m in matches if len(m) >= 2 and m not in ['会议', '项目', '公司', '部门', '产品', '技术', '市场', '方案']]
        for match in filtered_matches[:3]:
            entities.append({'type': '人员', 'value': match})

    # 4. 组织机构提取
    org_patterns = [
        r'[一-龯]*部门?',
        r'[一-龯]*公司',
        r'[一-龯]*团队',
        r'[一-龯]*小组',
        r'[一-龯]*中心'
    ]

    for pattern in org_patterns:
        matches = re.findall(pattern, content)
        filtered_matches = [m for m in matches if len(m) >= 3 and '部门' in m or '公司' in m or '团队' in m or '小组' in m or '中心' in m]
        for match in filtered_matches[:2]:
            entities.append({'type': '组织', 'value': match})

    # 5. 关键概念提取
    concept_keywords = [
        '产品', '项目', '方案', '计划', '策略', '目标', '任务', '功能',
        '系统', '平台', '服务', '技术', '架构', '设计', '开发', '测试',
        '市场', '用户', '客户', '需求', '反馈', '体验', '满意度',
        '预算', '成本', '收入', '利润', '投资', '回报', '风险'
    ]

    found_concepts = []
    for keyword in concept_keywords:
        if keyword in content and keyword not in found_concepts:
            found_concepts.append(keyword)
            entities.append({'type': '关键概念', 'value': keyword})
            if len(found_concepts) >= 5:  # 最多5个概念
                break

    # 6. 如果实体太少，添加一些从内容中提取的重要词汇
    if len(entities) < 3:
        # 提取出现频率较高的词汇
        words = re.findall(r'[一-龯]{2,4}', content)
        word_count = {}
        for word in words:
            if len(word) >= 2 and word not in ['这个', '那个', '可以', '需要', '进行', '实现', '完成', '建议']:
                word_count[word] = word_count.get(word, 0) + 1

        # 选择出现次数最多的词汇
        sorted_words = sorted(word_count.items(), key=lambda x: x[1], reverse=True)
        for word, count in sorted_words[:3]:
            if count >= 2:  # 至少出现2次
                entities.append({'type': '重要词汇', 'value': f"{word}(出现{count}次)"})

    # 去重并限制数量
    seen = set()
    unique_entities = []
    for entity in entities:
        key = f"{entity['type']}:{entity['value']}"
        if key not in seen:
            seen.add(key)
            unique_entities.append(entity)

    return unique_entities[:10]  # 最多返回10个实体

def analyze_content_depth(content, key_points):
    """深度分析文档内容特征"""
    if not content:
        return {
            'main_topics': [],
            'sentiment': '无内容',
            'complexity': '无内容',
            'language': '未知',
            'formality': '未知',
            'urgency': '无',
            'completeness': '不完整'
        }

    import re

    # 1. 主要话题分析
    main_topics = key_points[:3] if key_points else ['文档内容']

    # 2. 情感倾向分析
    positive_words = ['成功', '优秀', '良好', '满意', '赞同', '支持', '同意', '批准', '通过', '完成', '达成', '实现', '提升', '改善', '优化']
    negative_words = ['失败', '问题', '困难', '挑战', '风险', '延迟', '推迟', '取消', '拒绝', '反对', '不满', '投诉', '错误', '缺陷', '不足']
    neutral_words = ['讨论', '分析', '考虑', '建议', '计划', '安排', '准备', '进行', '实施', '执行']

    positive_count = sum(1 for word in positive_words if word in content)
    negative_count = sum(1 for word in negative_words if word in content)
    neutral_count = sum(1 for word in neutral_words if word in content)

    if positive_count > negative_count and positive_count > 0:
        sentiment = '积极'
    elif negative_count > positive_count and negative_count > 0:
        sentiment = '消极'
    elif neutral_count > 0:
        sentiment = '中性'
    else:
        sentiment = '客观'

    # 3. 复杂度分析
    word_count = len(content.split())
    sentence_count = len([s for s in re.split(r'[。！？]', content) if s.strip()])
    avg_sentence_length = word_count / max(sentence_count, 1)

    # 检查专业术语
    technical_terms = ['系统', '架构', '技术', '算法', '数据库', '接口', 'API', '框架', '模块', '组件']
    business_terms = ['战略', '策略', '市场', '客户', '用户', '产品', '服务', '收益', '成本', '预算']
    complex_terms = technical_terms + business_terms

    term_count = sum(1 for term in complex_terms if term in content)

    if word_count > 500 or avg_sentence_length > 20 or term_count > 5:
        complexity = '复杂'
    elif word_count > 200 or avg_sentence_length > 15 or term_count > 2:
        complexity = '中等'
    elif word_count > 50:
        complexity = '简单'
    else:
        complexity = '极简'

    # 4. 语言特征分析
    chinese_chars = len(re.findall(r'[一-龯]', content))
    total_chars = len(content)
    chinese_ratio = chinese_chars / max(total_chars, 1)

    if chinese_ratio > 0.7:
        language = '中文为主'
    elif chinese_ratio > 0.3:
        language = '中英混合'
    else:
        language = '英文为主'

    # 5. 正式程度分析
    formal_words = ['您', '敬请', '谨此', '特此', '兹', '据此', '综上', '鉴于', '基于']
    informal_words = ['你', '咱们', '大家', '哈哈', '嗯', '呃', '哦']

    formal_count = sum(1 for word in formal_words if word in content)
    informal_count = sum(1 for word in informal_words if word in content)

    if formal_count > informal_count and formal_count > 0:
        formality = '正式'
    elif informal_count > 0:
        formality = '非正式'
    else:
        formality = '中性'

    # 6. 紧急程度分析
    urgent_words = ['紧急', '立即', '马上', '尽快', '急需', '火急', '加急', '优先', '重要', '关键']
    urgent_count = sum(1 for word in urgent_words if word in content)

    if urgent_count >= 3:
        urgency = '高'
    elif urgent_count >= 1:
        urgency = '中'
    else:
        urgency = '低'

    # 7. 完整性分析
    structure_indicators = ['目标', '背景', '方案', '结论', '建议', '计划', '时间', '责任人']
    structure_count = sum(1 for indicator in structure_indicators if indicator in content)

    if structure_count >= 5:
        completeness = '完整'
    elif structure_count >= 3:
        completeness = '较完整'
    elif structure_count >= 1:
        completeness = '基本完整'
    else:
        completeness = '不完整'

    return {
        'main_topics': main_topics,
        'sentiment': sentiment,
        'complexity': complexity,
        'language': language,
        'formality': formality,
        'urgency': urgency,
        'completeness': completeness,
        'word_count': word_count,
        'sentence_count': sentence_count,
        'avg_sentence_length': round(avg_sentence_length, 1)
    }

def analyze_content_gaps(content, doc_type):
    """分析文档内容缺失和改进点"""
    if not content:
        return ["文档内容为空，需要添加实质性内容"]

    content_lower = content.lower()
    gaps = []

    # 通用内容分析
    if len(content) < 100:
        gaps.append("文档内容过于简短，建议补充更多详细信息")

    if '。' not in content and '!' not in content and '?' not in content:
        gaps.append("建议使用标点符号提高文档可读性")

    # 检查是否有标题结构
    if not any(marker in content for marker in ['#', '一、', '1.', '（一）', '第一']):
        gaps.append("建议添加清晰的标题和章节结构")

    # 根据文档类型进行具体分析
    if doc_type == '会议文档':
        if '时间' not in content_lower and '日期' not in content_lower:
            gaps.append("缺少会议时间信息，建议补充具体的会议日期和时间")
        if '参会' not in content_lower and '参与' not in content_lower and '出席' not in content_lower:
            gaps.append("缺少参会人员信息，建议明确记录参会人员名单")
        if '决策' not in content_lower and '决定' not in content_lower and '结论' not in content_lower:
            gaps.append("缺少明确的决策结果，建议补充会议达成的具体决策")
        if '行动' not in content_lower and '执行' not in content_lower and '负责' not in content_lower:
            gaps.append("缺少后续行动计划，建议明确责任人和执行时间节点")

    elif doc_type == '技术文档':
        if '架构' not in content_lower and '设计' not in content_lower:
            gaps.append("缺少技术架构说明，建议补充系统设计和架构图")
        if 'api' not in content_lower and '接口' not in content_lower:
            gaps.append("缺少接口文档，建议补充API接口说明和示例")
        if '测试' not in content_lower and '验证' not in content_lower:
            gaps.append("缺少测试说明，建议补充测试方法和验证步骤")

    elif doc_type == '产品文档':
        if '用户' not in content_lower and '客户' not in content_lower:
            gaps.append("缺少用户分析，建议补充目标用户群体和需求分析")
        if '功能' not in content_lower and '特性' not in content_lower:
            gaps.append("缺少功能说明，建议详细描述产品核心功能")
        if '竞品' not in content_lower and '市场' not in content_lower:
            gaps.append("缺少市场分析，建议补充竞品分析和市场定位")

    elif doc_type == '分析报告':
        if '数据' not in content_lower and '统计' not in content_lower:
            gaps.append("缺少数据支撑，建议补充具体的数据和统计信息")
        if '图表' not in content_lower and '图' not in content_lower:
            gaps.append("缺少可视化展示，建议添加图表和数据可视化")
        if '结论' not in content_lower and '建议' not in content_lower:
            gaps.append("缺少明确结论，建议补充分析结论和改进建议")

    return gaps if gaps else ["文档结构完整，建议进一步优化内容表达和格式规范"]

def generate_improvement_suggestions(content, doc_type):
    """根据文档实际内容生成智能改进建议"""
    if not content:
        return ["文档内容为空，请添加实质性内容"]

    # 分析内容缺失
    content_gaps = analyze_content_gaps(content, doc_type)

    # 分析内容质量
    quality_suggestions = []

    # 检查内容长度和结构
    sentences = content.replace('。', '。\n').replace('！', '！\n').replace('？', '？\n').split('\n')
    sentences = [s.strip() for s in sentences if s.strip()]

    if len(sentences) < 3:
        quality_suggestions.append("建议扩展内容，增加更多详细说明和背景信息")

    # 检查是否有具体的数字、时间等关键信息
    import re
    has_numbers = bool(re.search(r'\d+', content))
    has_dates = bool(re.search(r'\d{4}年|\d{1,2}月|\d{1,2}日', content))

    if not has_numbers and doc_type in ['分析报告', '技术文档']:
        quality_suggestions.append("建议补充具体的数字和量化指标")

    if not has_dates and doc_type in ['会议文档', '分析报告']:
        quality_suggestions.append("建议添加明确的时间信息和时间节点")

    # 检查是否有行动导向的内容
    action_words = ['计划', '执行', '实施', '完成', '负责', '安排', '推进']
    has_actions = any(word in content for word in action_words)

    if not has_actions and doc_type in ['会议文档', '产品文档']:
        quality_suggestions.append("建议添加具体的行动计划和执行步骤")

    # 合并建议并去重
    all_suggestions = content_gaps + quality_suggestions

    # 限制建议数量，选择最重要的
    return all_suggestions[:6] if all_suggestions else ["文档质量良好，建议继续保持"]

def mock_process_document(file_path):
    """Mock document processing for testing without API."""
    print(f"🎭 MOCK PROCESSING STARTED")
    print(f"🎭 File path: {file_path}")

    try:
        content = ""
        file_exists = os.path.exists(file_path)
        print(f"🎭 File exists: {file_exists}")

        if file_exists:
            # 根据文件类型选择合适的读取方法
            try:
                file_extension = os.path.splitext(file_path)[1].lower()
                file_size = os.path.getsize(file_path)
                print(f"🎭 File extension: {file_extension}")
                print(f"🎭 File size: {file_size} bytes")

                if file_extension == '.docx':
                    print(f"🎭 Processing Word document...")
                    # 使用python-docx读取Word文档
                    try:
                        print(f"🎭 Importing python-docx...")
                        from docx import Document
                        print(f"🎭 Creating Document object...")
                        doc = Document(file_path)
                        print(f"🎭 Document loaded, extracting paragraphs...")
                        content_parts = []
                        paragraph_count = 0
                        for paragraph in doc.paragraphs:
                            paragraph_count += 1
                            if paragraph.text.strip():
                                content_parts.append(paragraph.text.strip())
                        print(f"🎭 Found {paragraph_count} paragraphs, {len(content_parts)} with content")
                        content = '\n'.join(content_parts)
                        if not content:
                            content = "Word文档解析成功，但内容为空。"
                        print(f"🎭 Word document processed successfully: {len(content)} characters")
                    except Exception as docx_error:
                        print(f"❌ Error reading DOCX file: {docx_error}")
                        print(f"❌ Error type: {type(docx_error).__name__}")
                        import traceback
                        print(f"❌ Traceback: {traceback.format_exc()}")
                        content = "Word文档格式，但解析失败。使用模拟内容进行演示。"

                elif file_extension == '.pdf':
                    # 使用PyPDF2读取PDF文档
                    try:
                        import PyPDF2
                        content_parts = []
                        with open(file_path, 'rb') as f:
                            reader = PyPDF2.PdfReader(f)
                            for page in reader.pages:
                                page_text = page.extract_text()
                                if page_text.strip():
                                    content_parts.append(page_text.strip())
                        content = '\n'.join(content_parts)
                        if not content:
                            content = "PDF文档解析成功，但内容为空。"
                    except Exception as pdf_error:
                        print(f"Error reading PDF file: {pdf_error}")
                        content = "PDF文档格式，但解析失败。使用模拟内容进行演示。"

                else:
                    # 文本文件，尝试不同的编码
                    encodings = ['utf-8', 'gbk', 'gb2312', 'latin-1']
                    for encoding in encodings:
                        try:
                            with open(file_path, 'r', encoding=encoding) as f:
                                content = f.read()
                            break
                        except UnicodeDecodeError:
                            continue

                    if not content:
                        content = "文本文件读取失败，使用模拟内容进行演示。"

            except Exception as read_error:
                print(f"Error reading file: {read_error}")
                content = f"文件读取失败 ({file_extension})，使用模拟内容进行演示。"
        else:
            content = "文件不存在，使用模拟内容进行演示。"

        # 分析文档内容
        lines = content.count('\n') + 1 if content else 1
        paragraphs = max(content.count('\n\n') + 1, 1) if content else 1
        characters = len(content) if content else 0

        # 使用AI分析功能进行智能文档分析
        print(f"🎭 Starting intelligent document analysis...")
        doc_type, scenario, key_points = analyze_document_scenario(content)
        print(f"🎭 Document type identified: {doc_type}")

        # 生成内容摘要
        content_summary = generate_content_summary(content)
        print(f"🎭 Content summary generated: {len(content_summary)} characters")

        # 提取关键实体
        entities = extract_key_entities(content)
        print(f"🎭 Extracted {len(entities)} key entities")

        # 生成改进建议
        improvement_suggestions = generate_improvement_suggestions(content, doc_type)
        print(f"🎭 Generated {len(improvement_suggestions)} improvement suggestions")

        # 生成智能建议
        suggestions = [
            '建议增加更多具体数据支撑',
            '可以添加图表和可视化内容',
            '文档结构可以进一步优化',
            '建议添加目录和索引',
            '考虑增加总结和要点提炼'
        ]

        # 根据文档类型调整建议
        if doc_type == '会议文档':
            suggestions = [
                '建议明确会议决策和责任人',
                '添加后续行动时间节点',
                '完善会议参与者信息'
            ]
        elif doc_type == '技术文档':
            suggestions = [
                '建议添加技术架构图',
                '补充性能测试数据',
                '增加代码示例和配置说明'
            ]

        # 生成完整的AI分析结果
        print(f"🎭 Generating comprehensive AI analysis result...")
        print(f"🎭 Content length: {len(content)} characters")
        print(f"🎭 Document type: {doc_type}")
        print(f"🎭 Lines: {lines}, Paragraphs: {paragraphs}")

        result = {
            # 原始文档内容
            'text_content': content,
            'content_summary': content_summary,

            # 文档结构信息
            'structure_info': {
                'lines': lines,
                'paragraphs': paragraphs,
                'characters': characters,
                'words': len(content.split()) if content else 0,
                'file_exists': file_exists,
                'file_readable': bool(content and content != "无法读取文件内容，使用模拟内容进行演示。"),
                'estimated_reading_time': f"{max(1, len(content.split()) // 200)} 分钟" if content else "0 分钟"
            },

            # 智能场景分析
            'scenario_analysis': {
                'document_type': doc_type,
                'scenario': scenario,
                'key_points': key_points,
                'confidence': 0.85 if content else 0.5,
                'analysis_depth': 'comprehensive'
            },

            # 关键实体提取
            'key_entities': entities,

            # 智能内容分析
            'content_analysis': analyze_content_depth(content, key_points),

            # 改进建议
            'suggestions': improvement_suggestions,

            # 质量评估
            'quality_assessment': {
                'completeness': 0.8 if len(content.split()) > 50 else 0.5,
                'clarity': 0.7,
                'structure': 0.6 if paragraphs > 1 else 0.4,
                'overall_score': 0.7,
                'areas_for_improvement': ['结构优化', '内容补充', '格式规范']
            },

            # 处理状态
            'processing_status': 'completed',
            'mock_mode': True,
            'processing_time': '模拟处理时间: 2.3秒',
            'ai_features_used': [
                '智能文档分类',
                '内容摘要生成',
                '关键实体提取',
                '场景分析',
                '改进建议生成',
                '质量评估'
            ]
        }

        print(f"🎭 Mock result generated successfully")
        print(f"🎭 Result keys: {list(result.keys())}")
        return result

    except Exception as e:
        print(f"❌ MOCK PROCESSING ERROR:")
        print(f"   - Error type: {type(e).__name__}")
        print(f"   - Error message: {str(e)}")
        import traceback
        print(f"   - Full traceback:")
        print(traceback.format_exc())

        # 返回基本的错误恢复结果
        print(f"🎭 Returning error recovery result...")
        return {
            'text_content': '处理过程中发生错误，返回基本模拟结果',
            'structure_info': {
                'lines': 1,
                'paragraphs': 1,
                'characters': 20,
                'error': str(e)
            },
            'scenario_analysis': {
                'document_type': '错误恢复模式',
                'scenario': '系统异常',
                'key_points': ['处理异常', '错误恢复'],
                'confidence': 0.1
            },
            'suggestions': [
                '请检查文件格式是否正确',
                '尝试重新上传文件',
                '联系技术支持'
            ],
            'processing_status': 'error_recovery',
            'mock_mode': True,
            'error': str(e)
        }

@app.route('/')
def index():
    """Serve the main web interface."""
    return render_template('index.html')

@app.route('/demo')
def demo():
    """Serve the demo page."""
    return render_template('demo.html')

@app.route('/examples/<filename>')
def download_example(filename):
    """Download example files."""
    try:
        examples_dir = os.path.join(project_root, 'examples')
        return send_from_directory(examples_dir, filename, as_attachment=True)
    except Exception as e:
        return jsonify({'error': f'文件下载失败: {str(e)}'}), 404

@app.route('/debug_frontend.html')
def debug_frontend():
    """Serve the debug frontend page."""
    try:
        with open('debug_frontend.html', 'r', encoding='utf-8') as f:
            content = f.read()
        return content
    except FileNotFoundError:
        return "Debug frontend page not found", 404

@app.route('/test_ai_features.html')
def test_ai_features():
    """Serve the AI features test page."""
    try:
        with open('test_ai_features.html', 'r', encoding='utf-8') as f:
            content = f.read()
        return content
    except FileNotFoundError:
        return "AI features test page not found", 404

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """Handle file upload and processing."""
    print("=" * 80)
    print("🚀 UPLOAD REQUEST RECEIVED")
    print("=" * 80)

    try:
        # Debug request information
        print(f"📋 Request method: {request.method}")
        print(f"📋 Request content type: {request.content_type}")
        print(f"📋 Request files: {list(request.files.keys())}")
        print(f"📋 Request form data: {dict(request.form)}")
        print(f"📋 Request headers: {dict(request.headers)}")

        if 'file' not in request.files:
            print("❌ ERROR: No file provided in request")
            return jsonify({'error': 'No file provided'}), 400

        file = request.files['file']
        if file.filename == '':
            print("❌ ERROR: No file selected")
            return jsonify({'error': 'No file selected'}), 400

        print(f"📄 File info:")
        print(f"   - Filename: {file.filename}")
        print(f"   - Content type: {file.content_type}")

        # Check file size
        file.seek(0, 2)  # Seek to end
        file_size = file.tell()
        file.seek(0)  # Reset to beginning
        print(f"   - File size: {file_size} bytes")

        if not allowed_file(file.filename):
            print(f"❌ ERROR: File type not allowed: {file.filename}")
            return jsonify({'error': 'Unsupported file type'}), 400

        # 获取API类型和模型名称
        api_type = request.form.get('api_type', 'xingcheng')
        model_name = request.form.get('model_name', None)

        print(f"🔧 Processing configuration:")
        print(f"   - API type: {api_type}")
        print(f"   - Model name: {model_name}")
        
        # Generate unique filename
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4().hex}_{filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        
        print(f"Processing file: {filename}")
        print(f"File path: {filepath}")
        print(f"API type: {api_type}, Model: {model_name}")
        
        # Save file
        print(f"💾 Saving file to: {filepath}")
        file.save(filepath)
        print(f"✅ File saved successfully")

        # Verify file exists and is readable
        if os.path.exists(filepath):
            file_size_on_disk = os.path.getsize(filepath)
            print(f"✅ File verified on disk: {file_size_on_disk} bytes")
        else:
            print(f"❌ ERROR: File not found on disk after save!")
            return jsonify({'error': 'File save failed'}), 500

        # Process document
        print(f"🔄 Starting document processing...")
        try:
            # 检查是否明确选择了模拟模式
            if api_type == 'mock':
                print("🎭 Using explicit mock processing mode")
                print(f"🎭 Calling mock_process_document with: {filepath}")
                result = mock_process_document(file_path=filepath)
                print(f"🎭 Mock processing returned: {type(result)}")
                if isinstance(result, dict):
                    print(f"🎭 Result keys: {list(result.keys())}")
                    if 'error' in result:
                        print(f"❌ Mock processing error: {result['error']}")
                else:
                    print(f"❌ Unexpected result type: {type(result)}")
            else:
                print(f"🌐 Initializing real API: {api_type}")
                orchestrator = initialize_agent(api_type, model_name)

                if orchestrator is None:
                    # 使用模拟模式作为回退
                    print("🎭 API not available, using mock processing mode as fallback")
                    result = mock_process_document(file_path=filepath)
                else:
                    # 使用真实API
                    print("🌐 Using real API processing")
                    result = orchestrator.process_document(file_path=filepath)

            # 详细检查处理结果
            print(f"📊 Processing result analysis:")
            print(f"   - Result type: {type(result)}")
            if isinstance(result, dict):
                print(f"   - Result keys: {list(result.keys())}")
                status = result.get('processing_status', 'unknown')
                mock_mode = result.get('mock_mode', False)
                error = result.get('error', None)
                print(f"   - Status: {status}")
                print(f"   - Mock mode: {mock_mode}")
                if error:
                    print(f"   - Error: {error}")

                # Check if result has required fields
                required_fields = ['text_content', 'structure_info', 'scenario_analysis']
                missing_fields = [field for field in required_fields if field not in result]
                if missing_fields:
                    print(f"⚠️  Missing required fields: {missing_fields}")
            else:
                print(f"❌ Result is not a dictionary: {result}")

            print(f"✅ Processing completed successfully")
            
            # Clean up uploaded file
            print(f"🧹 Cleaning up file: {filepath}")
            os.remove(filepath)
            print(f"✅ File cleaned up successfully")

            # Prepare response
            response_data = {
                'success': True,
                'result': result,
                'filename': filename,
                'processed_at': datetime.now().isoformat(),
                'api_type': api_type,
                'model_name': model_name
            }

            print(f"📤 Preparing JSON response:")
            print(f"   - Success: {response_data['success']}")
            print(f"   - Filename: {response_data['filename']}")
            print(f"   - API type: {response_data['api_type']}")
            print(f"   - Result type: {type(response_data['result'])}")

            # Try to serialize to JSON to catch any issues
            try:
                import json
                json_str = json.dumps(response_data, ensure_ascii=False, default=str)
                print(f"✅ JSON serialization successful: {len(json_str)} characters")
            except Exception as json_error:
                print(f"❌ JSON serialization failed: {json_error}")
                return jsonify({'error': f'Response serialization failed: {str(json_error)}'}), 500

            print(f"🎉 Returning successful response")
            print("=" * 80)
            return jsonify(response_data)
            
        except Exception as e:
            print(f"❌ PROCESSING ERROR OCCURRED:")
            print(f"   - Error type: {type(e).__name__}")
            print(f"   - Error message: {str(e)}")
            print(f"   - Full traceback:")
            print(traceback.format_exc())

            # Clean up file on error
            if os.path.exists(filepath):
                print(f"🧹 Cleaning up file after error: {filepath}")
                os.remove(filepath)
                print(f"✅ File cleaned up after error")
            
            # 如果是网络错误，尝试使用模拟模式
            if "timeout" in str(e).lower() or "connection" in str(e).lower() or "network" in str(e).lower():
                print("Network error detected, trying mock mode")
                try:
                    # 重新读取文件内容进行模拟处理
                    if os.path.exists(filepath):
                        result = mock_process_document(file_path=filepath)
                    else:
                        # 如果文件已被删除，创建一个基本的模拟结果
                        result = {
                            'text_content': 'Mock content for network error fallback',
                            'structure_info': {'lines': 1, 'paragraphs': 1, 'characters': 40},
                            'scenario_analysis': {
                                'document_type': '通用文档',
                                'scenario': '网络错误回退模式',
                                'key_points': ['网络连接问题', '使用模拟模式'],
                                'confidence': 0.5
                            },
                            'suggestions': ['检查网络连接', '稍后重试'],
                            'processing_status': 'completed_with_fallback',
                            'mock_mode': True,
                            'fallback_reason': 'network_error'
                        }

                    return jsonify({
                        'success': True,
                        'result': result,
                        'filename': filename,
                        'processed_at': datetime.now().isoformat(),
                        'note': 'Used mock mode due to network issues',
                        'api_type': 'mock_fallback',
                        'model_name': 'fallback'
                    })
                except Exception as mock_error:
                    return jsonify({'error': f'Processing failed: {str(e)} (Mock mode also failed: {str(mock_error)})'}), 500
            
            return jsonify({'error': f'Processing failed: {str(e)}'}), 500
            
    except Exception as e:
        print(f"❌ UPLOAD ERROR OCCURRED:")
        print(f"   - Error type: {type(e).__name__}")
        print(f"   - Error message: {str(e)}")
        print(f"   - Full traceback:")
        print(traceback.format_exc())
        print("=" * 80)
        return jsonify({'error': f'Upload failed: {str(e)}'}), 500

@app.route('/api/health')
def health_check():
    """Health check endpoint."""
    try:
        # Test different API types
        api_status = {}
        
        # Test Xingcheng API
        try:
            orchestrator = initialize_agent("xingcheng")
            api_status['xingcheng'] = {
                'status': 'available' if orchestrator else 'unavailable',
                'mock_mode': orchestrator is None
            }
        except Exception as e:
            api_status['xingcheng'] = {'status': 'error', 'error': str(e)}
        
        # Test Multi API
        try:
            orchestrator = initialize_agent("multi")
            api_status['multi'] = {
                'status': 'available' if orchestrator else 'unavailable',
                'mock_mode': orchestrator is None
            }
        except Exception as e:
            api_status['multi'] = {'status': 'error', 'error': str(e)}
        
        return jsonify({
            'status': 'healthy',
            'api_status': api_status,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/config')
def get_config():
    """Get current configuration (without sensitive data)."""
    return jsonify({
        'allowed_extensions': list(app.config['ALLOWED_EXTENSIONS']),
        'max_file_size_mb': app.config['MAX_CONTENT_LENGTH'] // (1024 * 1024),
        'api_types': ['xingcheng', 'multi', 'mock'],
        'xingcheng_configured': bool(os.getenv("XINGCHENG_API_KEY")),
        'qiniu_configured': bool(os.getenv("QINIU_API_KEY")),
        'together_configured': bool(os.getenv("TOGETHER_API_KEY")),
        'openrouter_configured': bool(os.getenv("OPENROUTER_API_KEY")),
        'mock_mode_available': True,
        'format_alignment_available': True,
        'document_fill_available': True
    })

@app.route('/api/format-alignment', methods=['POST'])
def format_alignment():
    """处理文档格式对齐请求"""
    global format_coordinator

    try:
        # 初始化格式协调器
        if format_coordinator is None:
            format_coordinator = FormatAlignmentCoordinator()

        # 获取请求数据
        data = request.get_json()
        user_input = data.get('user_input', '')
        uploaded_files = data.get('uploaded_files', {})

        # 处理用户请求
        result = format_coordinator.process_user_request(user_input, uploaded_files)

        return jsonify(result)

    except Exception as e:
        return jsonify({'error': f'格式对齐处理失败: {str(e)}'}), 500

@app.route('/api/format-templates', methods=['GET'])
def list_format_templates():
    """获取所有格式模板"""
    global format_coordinator

    try:
        if format_coordinator is None:
            format_coordinator = FormatAlignmentCoordinator()

        templates = format_coordinator.format_extractor.list_format_templates()

        return jsonify({
            'success': True,
            'templates': templates,
            'count': len(templates)
        })

    except Exception as e:
        return jsonify({'error': f'获取模板列表失败: {str(e)}'}), 500

@app.route('/api/format-templates/<template_id>', methods=['GET'])
def get_format_template(template_id):
    """获取特定格式模板"""
    global format_coordinator

    try:
        if format_coordinator is None:
            format_coordinator = FormatAlignmentCoordinator()

        template_data = format_coordinator.format_extractor.load_format_template(template_id)

        if 'error' in template_data:
            return jsonify(template_data), 404

        return jsonify({
            'success': True,
            'template': template_data
        })

    except Exception as e:
        return jsonify({'error': f'获取模板失败: {str(e)}'}), 500

@app.route('/api/format-templates/<template_id>/apply', methods=['POST'])
def apply_format_template(template_id):
    """应用格式模板到文档"""
    global format_coordinator

    try:
        if format_coordinator is None:
            format_coordinator = FormatAlignmentCoordinator()

        data = request.get_json()
        document_name = data.get('document_name', '')
        document_content = data.get('document_content', '')

        if not document_name or not document_content:
            return jsonify({'error': '缺少文档名称或内容'}), 400

        # 添加文档到会话
        format_coordinator.add_document(document_name, document_content)

        # 应用模板
        result = format_coordinator.use_saved_template(template_id, document_name)

        return jsonify(result)

    except Exception as e:
        return jsonify({'error': f'应用模板失败: {str(e)}'}), 500

@app.route('/api/models')
def get_available_models():
    """Get available models for each API type."""
    try:
        # 获取多API客户端的可用模型
        multi_client = MultiLLMClient()
        available_models = multi_client.get_available_models()
        
        models_by_api = {
            'xingcheng': ['x1', 'x2', 'x3'],
            'multi': available_models,
            'mock': ['mock-model']
        }
        
        return jsonify({
            'models': models_by_api,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'error': str(e),
            'models': {
                'xingcheng': ['x1'],
                'mock': ['mock-model']
            }
        }), 500

@app.route('/api/document-fill/start', methods=['POST'])
def start_document_fill():
    """开始文档填充流程"""
    global fill_coordinator

    try:
        if fill_coordinator is None:
            fill_coordinator = DocumentFillCoordinator()

        data = request.get_json()
        document_content = data.get('document_content', '')
        document_name = data.get('document_name', '')

        if not document_content:
            return jsonify({'error': '缺少文档内容'}), 400

        result = fill_coordinator.start_document_fill(document_content, document_name)

        return jsonify(result)

    except Exception as e:
        return jsonify({'error': f'启动文档填充失败: {str(e)}'}), 500

@app.route('/api/document-fill/respond', methods=['POST'])
def respond_to_fill_question():
    """响应文档填充问题"""
    global fill_coordinator

    try:
        if fill_coordinator is None:
            return jsonify({'error': '文档填充会话未初始化'}), 400

        data = request.get_json()
        user_input = data.get('user_input', '')

        if not user_input:
            return jsonify({'error': '缺少用户输入'}), 400

        result = fill_coordinator.process_user_response(user_input)

        return jsonify(result)

    except Exception as e:
        return jsonify({'error': f'处理用户回复失败: {str(e)}'}), 500

@app.route('/api/document-fill/status', methods=['GET'])
def get_fill_status():
    """获取文档填充状态"""
    global fill_coordinator

    try:
        if fill_coordinator is None:
            return jsonify({'error': '文档填充会话未初始化'}), 400

        status = fill_coordinator.get_session_status()

        return jsonify({
            'success': True,
            'status': status
        })

    except Exception as e:
        return jsonify({'error': f'获取状态失败: {str(e)}'}), 500

@app.route('/api/document-fill/result', methods=['GET'])
def get_fill_result():
    """获取文档填充结果"""
    global fill_coordinator

    try:
        if fill_coordinator is None:
            return jsonify({'error': '文档填充会话未初始化'}), 400

        result = fill_coordinator.get_fill_result()

        if not result:
            return jsonify({'error': '填充结果不可用'}), 404

        return jsonify({
            'success': True,
            'result': result
        })

    except Exception as e:
        return jsonify({'error': f'获取填充结果失败: {str(e)}'}), 500

@app.route('/api/document-fill/download', methods=['GET'])
def download_filled_document():
    """下载填充后的文档"""
    global fill_coordinator

    try:
        if fill_coordinator is None:
            return jsonify({'error': '文档填充会话未初始化'}), 400

        result = fill_coordinator.get_fill_result()

        if not result or not result.get('html_content'):
            return jsonify({'error': '填充结果不可用'}), 404

        html_content = result['html_content']

        # 创建响应
        from flask import make_response
        response = make_response(html_content)
        response.headers['Content-Type'] = 'text/html; charset=utf-8'
        response.headers['Content-Disposition'] = 'attachment; filename=filled_document.html'

        return response

    except Exception as e:
        return jsonify({'error': f'下载失败: {str(e)}'}), 500

@app.route('/api/document-fill/add-material', methods=['POST'])
def add_supplementary_material():
    """添加补充材料"""
    global fill_coordinator

    try:
        if fill_coordinator is None:
            return jsonify({'error': '文档填充会话未初始化'}), 400

        data = request.get_json()
        material_name = data.get('material_name', '')
        material_content = data.get('material_content', '')

        if not material_name or not material_content:
            return jsonify({'error': '缺少材料名称或内容'}), 400

        result = fill_coordinator.add_supplementary_material(material_name, material_content)

        return jsonify(result)

    except Exception as e:
        return jsonify({'error': f'添加补充材料失败: {str(e)}'}), 500

@app.route('/api/writing-style/analyze', methods=['POST'])
def analyze_writing_style():
    """分析文档写作风格"""
    global style_analyzer

    try:
        if style_analyzer is None:
            style_analyzer = WritingStyleAnalyzer()

        data = request.get_json()
        document_content = data.get('document_content', '')
        document_name = data.get('document_name', '')

        if not document_content:
            return jsonify({'error': '缺少文档内容'}), 400

        result = style_analyzer.analyze_writing_style(document_content, document_name)

        return jsonify(result)

    except Exception as e:
        return jsonify({'error': f'文风分析失败: {str(e)}'}), 500

@app.route('/api/writing-style/save-template', methods=['POST'])
def save_writing_style_template():
    """保存文风模板"""
    global style_analyzer, fill_coordinator

    try:
        if style_analyzer is None:
            style_analyzer = WritingStyleAnalyzer()

        data = request.get_json()
        reference_content = data.get('reference_content', '')
        reference_name = data.get('reference_name', '')

        if not reference_content:
            return jsonify({'error': '缺少参考文档内容'}), 400

        # 如果有活跃的填充会话，使用会话中的方法
        if fill_coordinator is not None:
            result = fill_coordinator.analyze_and_save_writing_style(reference_content, reference_name)
        else:
            # 直接使用分析器
            analysis_result = style_analyzer.analyze_writing_style(reference_content, reference_name)
            if "error" in analysis_result:
                return jsonify(analysis_result), 500

            result = style_analyzer.save_style_template(analysis_result)

        return jsonify(result)

    except Exception as e:
        return jsonify({'error': f'保存文风模板失败: {str(e)}'}), 500

@app.route('/api/writing-style/templates', methods=['GET'])
def list_writing_style_templates():
    """获取所有文风模板"""
    global style_analyzer

    try:
        if style_analyzer is None:
            style_analyzer = WritingStyleAnalyzer()

        templates = style_analyzer.list_style_templates()

        return jsonify({
            'success': True,
            'templates': templates,
            'count': len(templates)
        })

    except Exception as e:
        return jsonify({'error': f'获取文风模板列表失败: {str(e)}'}), 500

@app.route('/api/writing-style/templates/<template_id>', methods=['GET'])
def get_writing_style_template(template_id):
    """获取特定文风模板"""
    global style_analyzer

    try:
        if style_analyzer is None:
            style_analyzer = WritingStyleAnalyzer()

        template_data = style_analyzer.load_style_template(template_id)

        if 'error' in template_data:
            return jsonify(template_data), 404

        return jsonify({
            'success': True,
            'template': template_data
        })

    except Exception as e:
        return jsonify({'error': f'获取文风模板失败: {str(e)}'}), 500

@app.route('/api/document-fill/set-style', methods=['POST'])
def set_writing_style_template():
    """设置文档填充的文风模板"""
    global fill_coordinator

    try:
        if fill_coordinator is None:
            return jsonify({'error': '文档填充会话未初始化'}), 400

        data = request.get_json()
        template_id = data.get('template_id', '')

        if not template_id:
            return jsonify({'error': '缺少模板ID'}), 400

        result = fill_coordinator.set_writing_style_template(template_id)

        return jsonify(result)

    except Exception as e:
        return jsonify({'error': f'设置文风模板失败: {str(e)}'}), 500

if __name__ == '__main__':
    print("Starting Office Document Agent Web Server...")
    print(f"Project root: {project_root}")
    print(f"Template folder: {app.template_folder}")
    print(f"Static folder: {app.static_folder}")
    print("Web interface will be available at: http://localhost:5000")
    print("API endpoints:")
    print("  - GET  /api/health     - Health check")
    print("  - GET  /api/config     - Configuration info")
    print("  - GET  /api/models     - Available models")
    print("  - POST /api/upload     - Upload and process document")
    
    # 检查API配置
    api_keys = {
        'XINGCHENG_API_KEY': os.getenv("XINGCHENG_API_KEY"),
        'QINIU_API_KEY': os.getenv("QINIU_API_KEY"),
        'TOGETHER_API_KEY': os.getenv("TOGETHER_API_KEY"),
        'OPENROUTER_API_KEY': os.getenv("OPENROUTER_API_KEY")
    }
    
    configured_apis = [name for name, key in api_keys.items() if key]
    if configured_apis:
        print(f"Configured APIs: {', '.join(configured_apis)}")
    else:
        print("Warning: No API keys found in .env file")
        print("The system will use mock mode for testing")
    
    app.run(debug=True, host='0.0.0.0', port=5000) 