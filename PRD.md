# 需求文档

## 1. 项目名称

订单信息自动提取与验证助手

------

## 2. 目标定义（必须严格遵守）

系统只实现以下3个核心能力：

1. 从订单数据中自动提取关键信息
2. 对订单进行基础业务校验
3. 输出清晰的处理结果与建议

------

## 3. 输入定义（标准化）

系统仅支持两类输入：

### 3.1 邮件输入

```
{
  "type": "email",
  "subject": "string",
  "body": "string",
  "attachments": [
    {
      "fileName": "string",
      "fileContent": "binary or text"
    }
  ]
}
```

------

### 3.2 Excel输入

```
{
  "type": "excel",
  "fileName": "string",
  "fileContent": "binary"
}
```

------

## 4. 核心处理流程（不可改变）

```
输入 → 内容解析 → AI提取 → 数据校验 → 结果输出
```

------

## 5. 功能定义（最小可用集）

------

# 5.1 内容解析

## 输入

原始邮件或Excel

## 处理规则

- 邮件：提取正文文本 + 附件内容
- Excel：读取所有数据行
- 输出统一为文本内容

## 输出

```
{
  "rawText": "string"
}
```

------

# 5.2 订单信息提取（通过AI API实现）

## 输入

```
{
  "rawText": "string"
}
```

## 处理规则

- 调用外部AI接口
- 将非结构化内容转换为结构化订单数据

## 输出（必须符合以下结构）

```
{
  "customerName": "string",
  "items": [
    {
      "productCode": "string",
      "quantity": "number",
      "price": "number"
    }
  ],
  "deliveryDate": "string",
  "confidence": "number"
}
```

## 判定规则

- confidence < 0.8 → 标记为“需人工确认”

------

# 5.3 数据校验

系统只做3种校验，不允许扩展复杂逻辑：

------

## 5.3.1 客户校验

### 输入

```
{
  "customerName": "string"
}
```

### 校验逻辑

- 客户是否存在
- 客户是否有效

------

## 5.3.2 库存校验

### 输入

```
{
  "productCode": "string",
  "quantity": "number"
}
```

### 校验逻辑

- 当前库存 ≥ 订单数量

------

## 5.3.3 价格校验

### 输入

```
{
  "productCode": "string",
  "price": "number"
}
```

### 校验逻辑

- 价格在允许范围内（由外部系统提供标准价格）

------

# 5.4 校验结果汇总

## 输出结构（统一格式）

```
{
  "finalStatus": "pass | fail | manual",
  "confidence": "number",
  "issues": [
    "string"
  ]
}
```

## 判定规则（必须遵守）

```
IF confidence < 0.8 → finalStatus = manual

ELSE IF 任一校验失败 → finalStatus = fail

ELSE → finalStatus = pass
```

------

# 5.5 最终输出

系统必须输出一个完整结果对象：

```
{
  "extractedData": {
    "customerName": "",
    "items": [],
    "deliveryDate": "",
    "confidence": 0
  },
  "validationResult": {
    "finalStatus": "",
    "issues": []
  },
  "suggestion": "string"
}
```

------

## suggestion生成规则

| 状态   | suggestion             |
| ------ | ---------------------- |
| pass   | 建议创建订单           |
| fail   | 存在异常，需人工处理   |
| manual | 信息不完整，需人工确认 |

------

## 6. 外部依赖（必须通过接口）

系统不实现以下能力，仅调用外部接口：

------

### 6.1 AI解析接口

输入：rawText
 输出：结构化订单数据

------

### 6.2 客户查询接口

输入：customerName
 输出：是否存在 + 状态

------

### 6.3 库存查询接口

输入：productCode
 输出：库存数量

------

### 6.4 价格查询接口

输入：productCode
 输出：标准价格

------

## 7. 错误处理规则

必须统一返回以下格式：

```
{
  "error": true,
  "message": "string"
}
```

------

## 8. 非功能约束（简化）

- 单次处理时间 ≤ 3秒
- 所有输入必须可重复处理（幂等）
- 不允许丢失原始数据

------

## 9. 不包含范围（必须忽略）

以下内容禁止实现：

- 审批流程
- 工作流引擎
- 自动下单
- AI模型训练
- 复杂规则系统
- UI复杂交互

------

# 最终说明

本系统是一个**“输入 → 解析 → 校验 → 输出”的轻量工具**，
 核心目标是：

👉 **减少人工录入与审核成本，而不是替代ERP系统**