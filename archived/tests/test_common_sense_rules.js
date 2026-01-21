#!/usr/bin/env node
/**
 * 测试前端的常识规则函数
 */

// applyCommonSenseRules函数定义
function applyCommonSenseRules(detectedFeatures, selectedVariations) {
  // 如果检测到了性别特征（feature 0），应用相应的头发长度约束
  if (detectedFeatures && detectedFeatures[0]) {
    const detectedGender = detectedFeatures[0];
    
    // 检查是否是男孩
    if (detectedGender.includes('男孩') || detectedGender.includes('男')) {
      // 男孩通常短发，所以移除可能被随机生成的"长发"
      selectedVariations = selectedVariations.filter(v => v !== '长发' && v !== '中长发' && v !== '齐肩发' && v !== '及肩');
    }
    
    // 检查是否是女孩
    if (detectedGender.includes('女孩') || detectedGender.includes('女')) {
      // 女孩通常长发，所以移除可能被随机生成的"短发"
      selectedVariations = selectedVariations.filter(v => v !== '短发');
    }
  }
  
  return selectedVariations;
}

// 测试用例
const testCases = [
  {
    name: "男孩检测 + 长发变化",
    detectedFeatures: {0: '男孩', 5: '大眼睛'},
    selectedVariations: ['胖胖的', '长发', '卷发'],
    expected: ['胖胖的', '卷发'],
    description: "应该移除'长发'因为男孩通常短发"
  },
  {
    name: "女孩检测 + 短发变化",
    detectedFeatures: {0: '女孩'},
    selectedVariations: ['短发', '直发', '瘦瘦的'],
    expected: ['直发', '瘦瘦的'],
    description: "应该移除'短发'因为女孩通常长发"
  },
  {
    name: "男孩检测 + 多个长发变化",
    detectedFeatures: {0: '男'},
    selectedVariations: ['齐肩发', '卷发', '中长发', '直发'],
    expected: ['卷发', '直发'],
    description: "应该移除'齐肩发'和'中长发'"
  },
  {
    name: "无性别检测",
    detectedFeatures: {1: '胖胖的', 5: '大眼睛'},
    selectedVariations: ['长发', '短发', '直发'],
    expected: ['长发', '短发', '直发'],
    description: "没有检测到性别，所以不过滤头发长度"
  },
  {
    name: "空detectedFeatures",
    detectedFeatures: {},
    selectedVariations: ['长发', '短发', '卷发'],
    expected: ['长发', '短发', '卷发'],
    description: "detectedFeatures为空，不应用任何过滤"
  }
];

// 运行测试
console.log("=" . repeat(80));
console.log("测试常识规则函数");
console.log("=" . repeat(80));

let passCount = 0;
let failCount = 0;

testCases.forEach((testCase, index) => {
  console.log(`\n[测试 ${index + 1}] ${testCase.name}`);
  console.log("-".repeat(80));
  console.log(`说明: ${testCase.description}`);
  console.log(`输入特征: ${JSON.stringify(testCase.detectedFeatures)}`);
  console.log(`输入变化: ${JSON.stringify(testCase.selectedVariations)}`);
  
  const result = applyCommonSenseRules(
    testCase.detectedFeatures,
    [...testCase.selectedVariations]  // 创建副本，避免修改原数组
  );
  
  console.log(`输出结果: ${JSON.stringify(result)}`);
  console.log(`期望结果: ${JSON.stringify(testCase.expected)}`);
  
  // 验证结果
  const match = JSON.stringify(result) === JSON.stringify(testCase.expected);
  if (match) {
    console.log(`✅ 通过`);
    passCount++;
  } else {
    console.log(`❌ 失败`);
    failCount++;
  }
});

console.log(`\n${"=" . repeat(80)}`);
console.log(`测试总结: ${passCount}个通过, ${failCount}个失败`);
console.log(`${"=" . repeat(80)}`);

process.exit(failCount > 0 ? 1 : 0);
