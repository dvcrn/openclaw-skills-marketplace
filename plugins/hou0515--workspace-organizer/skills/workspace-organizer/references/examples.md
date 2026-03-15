# Workspace Structure Examples

**Important**: These are *illustrative examples* showing structure diversity, **NOT templates** to be copied. Each real task should have its own unique structure derived from its specific requirements.

## Example 1: Document Analysis Task

**Task**: Analyze multiple document formats and generate standardized templates

```
workspace/
├── input/
│   └── 2026-03-13_文档格式分析/
│       ├── 15378776-dd84-408e-afbb-feb2ba6d1597.docx
│       ├── 1e35f26d-0dc4-432a-8897-78b2cd2781c9.docx
│       └── (6 more GUID-named .docx files)
├── output/
│   └── 2026-03-13_文档格式分析/
│       ├── 01_文档读取与内容提取/
│       │   ├── read_full_doc.py
│       │   ├── check_doc.py
│       │   ├── view_doc_content.py
│       │   ├── extract_content.py
│       │   └── screen.png
│       ├── 02_文档结构与样式分析/
│       │   ├── extract_detailed.py
│       │   ├── extract_full_content.py
│       │   ├── deep_content_analysis.py
│       │   └── check_styles.py
│       ├── 03_模板匹配与模式识别/
│       │   ├── analyze_tables.py
│       │   ├── analyze_templates.py
│       │   └── identify_files.py
│       ├── 04_最终文档生成/
│       │   ├── fix_and_generate.py
│       │   ├── generate_correct_format.py
│       │   ├── generate_final.py
│       │   ├── generate_final_correct.py
│       │   ├── generate_final_doc.py
│       │   ├── generate_final_fixed.py
│       │   ├── generate_simple_doc.py
│       │   ├── 产品开发规范_v1.0.docx
│       │   └── 模板标准文档.docx
│       └── 05_结果验证与整理/
│           ├── document_analysis.json
│           ├── coding_std_sections.json
│           └── draft_sections.json
└── (root config files)
```

**Why this structure works**:
- Steps reflect actual workflow: read → analyze → match → generate → validate
- Files are placed where they're primarily used
- Output documents are in the generation step where they're created
- Analysis results are in the validation step for review

## Example 2: Competitive Pricing Analysis

**Task**: Analyze competitor pricing strategies and generate recommendations

```
workspace/
├── input/
│   └── 2026-03-15_竞品定价分析/
│       ├── competitor_prices.csv
│       ├── market_research.pdf
│       ├── product_catalog.xlsx
│       └── historical_trends.json
├── output/
│   └── 2026-03-15_竞品定价分析/
│       ├── 01_数据收集与清洗/
│       │   ├── scrape_competitor_prices.py
│       │   ├── clean_price_data.py
│       │   └── normalized_prices.csv
│       ├── 02_价格趋势分析/
│       │   ├── analyze_price_trends.py
│       │   ├── visualize_trends.py
│       │   ├── price_trend_chart.png
│       │   └── seasonal_patterns.json
│       ├── 03_定价策略识别/
│       │   ├── identify_strategies.py
│       │   ├── competitor_strategies.md
│       │   └── strategy_comparison.csv
│       ├── 04_策略建议生成/
│       │   ├── generate_recommendations.py
│       │   ├── pricing_recommendations.docx
│       │   └── implementation_roadmap.md
│       └── 05_执行模拟验证/
│           ├── simulate_price_changes.py
│           ├── impact_analysis.xlsx
│           └── risk_assessment.md
└── (root config files)
```

**Note the differences from Example 1**:
- Steps are data-focused: collect → analyze → identify → recommend → simulate
- File types reflect data analysis work (CSV, JSON, charts)
- Includes simulation and risk assessment steps specific to business analysis

## Example 3: Web Scraping & Data Pipeline

**Task**: Build a web scraping pipeline with data transformation and storage

```
workspace/
├── input/
│   └── 2026-03-16_网页数据抓取管道/
│       ├── target_urls.txt
│       ├── data_schema.json
│       └── scraping_config.yaml
├── output/
│   └── 2026-03-16_网页数据抓取管道/
│       ├── 01_页面解析开发/
│       │   ├── parse_html_structure.py
│       │   ├── extract_selectors.py
│       │   └── test_parsers.py
│       ├── 02_数据提取实现/
│       │   ├── scrape_data.py
│       │   ├── handle_pagination.py
│       │   └── raw_data.jsonl
│       ├── 03_数据清洗转换/
│       │   ├── clean_extracted_data.py
│       │   ├── transform_formats.py
│       │   └── clean_data.csv
│       ├── 04_数据存储设计/
│       │   ├── database_schema.sql
│       │   ├── load_to_db.py
│       │   └── data_validation.py
│       └── 05_监控与维护/
│           ├── monitoring_dashboard.py
│           ├── error_handling.py
│           └── maintenance_guide.md
└── (root config files)
```

**Pipeline-specific structure**:
- Development → Implementation → Transformation → Storage → Monitoring
- Includes testing and validation steps
- Has maintenance considerations for ongoing operations

## Example 4: Creative Content Project

**Task**: Create marketing content with multiple formats

```
workspace/
├── input/
│   └── 2026-03-17_营销内容创作/
│       ├── brand_guidelines.pdf
│       ├── product_info.docx
│       ├── target_audience.md
│       └── competitor_content/
├── output/
│   └── 2026-03-17_营销内容创作/
│       ├── 01_素材收集研究/
│       │   ├── research_competitors.py
│       │   ├── gather_references.py
│       │   └── content_inspiration.md
│       ├── 02_内容策略规划/
│       │   ├── define_messaging.py
│       │   ├── content_calendar.xlsx
│       │   └── tone_voice_guide.md
│       ├── 03_多格式内容创作/
│       │   ├── write_blog_post.py
│       │   ├── create_social_media.py
│       │   ├── design_infographic.py
│       │   ├── blog_post.md
│       │   ├── social_media_posts.json
│       │   └── infographic.ai
│       ├── 04_内容优化调整/
│       │   ├── seo_optimization.py
│       │   ├── a_b_testing.py
│       │   └── feedback_incorporation.py
│       └── 05_发布与分发/
│           ├── schedule_posts.py
│           ├── cross_platform_posting.py
│           └── performance_tracking.md
└── (root config files)
```

**Creative workflow differences**:
- Research → Planning → Creation → Optimization → Distribution
- Mixed file types: text, design files, spreadsheets
- Includes SEO and performance tracking

## Pattern Recognition vs. Template Application

### What to DO:
- Analyze each task's unique requirements
- Identify natural workflow phases
- Create step names that describe actual work
- Place files where they're logically used
- Adjust structure as understanding deepens

### What NOT to DO:
- Copy these examples directly
- Force tasks into predefined categories
- Use generic step names like "Processing" or "Step1"
- Ignore task-specific workflow needs
- Treat structure as immutable once created

## Evolution in Practice

As you use this system:
1. **First tasks**: Might resemble these examples
2. **Intermediate use**: Develop your own patterns
3. **Advanced use**: Create entirely novel structures for unique tasks
4. **Expert use**: Structure becomes intuitive reflection of work

The system's value is in **adapting to your work**, not making your work adapt to it.